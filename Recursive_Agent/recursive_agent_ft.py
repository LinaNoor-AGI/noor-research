
'''recursive_agent_ft.py (v3.8.0)
-----------------------------------------------------------------
Functor Ascent — Symbolic flow agent with multi‑stage spectral
approximation, optional ∞‑groupoid path identity tracking, autonomous
symbolic commentary, and richer Prometheus observability.

Compatible with:
 • NoorFastTimeCore ≥ 7.4.2
 • LogicalAgentAT   ≥ 2.8.1   (π‑groupoid API)
-----------------------------------------------------------------
'''

from __future__ import annotations

__version__ = "3.8.0"

# ────────────────────── standard lib / typing ──────────────────────
import math
import time
import hashlib
import random
from collections import deque, defaultdict
from dataclasses import dataclass
from enum import StrEnum
from typing import (
    Any,
    Callable,
    Deque,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
)

# ────────────────────────── external deps ──────────────────────────
import numpy as np

from noor_fasttime_core import NoorFastTimeCore
from logical_agent_at import LogicalAgentAT

# ────────────────────────── prometheus stubs ───────────────────────
try:
    from prometheus_client import Counter, Gauge, Histogram  # type: ignore

    STEP_LATENCY_HIST          = Histogram("recursive_agent_step_latency_seconds",
                                           "entangled_step latency",
                                           buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5))
    DEPTH_GAUGE                = Gauge("recursive_agent_recursion_depth", "Current max_depth")
    GREMLIN_MEAN_GAUGE         = Gauge("recursive_agent_gremlin_mean", "Mean gremlin weight per cycle")
    GREMLIN_STD_GAUGE          = Gauge("recursive_agent_gremlin_std", "Std dev of gremlin weights per cycle")

    # new metrics
    SPECTRAL_STAGE_LAT_HIST    = Histogram("recursive_agent_spectral_stage_latency_seconds",
                                           "latency of spectral stages (E0‑E2b)",
                                           buckets=(0.0005, 0.001, 0.005, 0.01, 0.025, 0.05))
    SPECTRAL_STAGE_SUCCESS     = Counter("recursive_agent_spectral_stage_success_total",
                                         "Successful spectral pass per stage", ["stage"])
    PI_EQUIV_MERGED            = Counter("recursive_agent_pi_equiv_merged_total",
                                         "π‑equivalence merges initiated by agent")
    COMMENTARY_TYPE_COUNTER    = Counter("recursive_agent_commentary_type_total",
                                         "Commentary records emitted", ["ctype"])
    HOMOTOPY_CLASS_GAUGE       = Gauge("recursive_agent_homotopy_class_gauge",
                                       "Local π‑equivalence class count")
except Exception:  # pragma: no cover – offline
    class _Stub:  # noqa: D401
        def __getattr__(self, _):
            return lambda *a, **k: None
    STEP_LATENCY_HIST = DEPTH_GAUGE = GREMLIN_MEAN_GAUGE = GREMLIN_STD_GAUGE = _Stub()
    SPECTRAL_STAGE_LAT_HIST = SPECTRAL_STAGE_SUCCESS = PI_EQUIV_MERGED = _Stub()
    COMMENTARY_TYPE_COUNTER = HOMOTOPY_CLASS_GAUGE = _Stub()

# ──────────────────────── helper constants ─────────────────────────
GREMLIN_NOISE_SCALE          = 0.02
DEFAULT_GREMLIN_DECAY_RATE   = 0.98
DEFAULT_PATH_GUARD_LIMIT     = 20
DEFAULT_GREMLIN_PENALTY      = 0.2
MAX_GREMLIN_STD              = 0.5

# ─────────────────────── commentary record ─────────────────────────
class CommentType(StrEnum):
    MOTIF   = "MotifExpr"
    QUANTUM = "QuantumSig"
    AUTO    = "Autoglossia"

@dataclass
class CommentaryRecord:
    type: CommentType
    value: str
    entropy: float
    origin: str
    replayable: bool = False

# ───────────────────────── gremlin helpers ─────────────────────────
def apply_gremlin_perturb(state: np.ndarray, weight: float) -> np.ndarray:
    if weight <= 1e-3:
        return state
    sigma = GREMLIN_NOISE_SCALE * weight
    noise = np.random.normal(0.0, sigma, size=state.shape)
    return state + noise

def decay_gremlin_weights(fields: List[Dict[str, Any]],
                          rate: float = DEFAULT_GREMLIN_DECAY_RATE) -> None:
    for f in fields:
        if "gremlin_weight" in f:
            f["gremlin_weight"] *= rate

def export_gremlin_stats(fields: Sequence[Dict[str, Any]]) -> Tuple[float, float]:
    g = np.array([f.get("gremlin_weight", 0.0) for f in fields], dtype=float)
    if g.size == 0:
        return 0.0, 0.0
    return float(g.mean()), float(g.std())

# ──────────────────────── harmony helpers ──────────────────────────
_HARM_TOL = 0.04
_MAJOR_THIRD = 0.5
_MINOR_THIRD = 0.7071
_PERF_FIFTH  = 0.8660

def _short_hash(s: str, n: int = 8) -> str:
    return hashlib.sha1(s.encode("utf-8", "replace")).hexdigest()[:n]

def _cos(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a.flatten(), b.flatten()
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return float(np.dot(a, b) / denom)

def is_harmonic_triad(vecs: List[np.ndarray]) -> bool:
    v = [x for x in vecs if np.linalg.norm(x) > 1e-9][:3]
    if len(v) < 3:
        return False
    sims = [_cos(v[i], v[j]) for i in range(3) for j in range(i+1, 3)]
    return any(abs(s - t) < _HARM_TOL
               for s in sims
               for t in (_MAJOR_THIRD, _MINOR_THIRD, _PERF_FIFTH))

# ─────────────────────── default π‑hasher ──────────────────────────
def default_pi_hasher(path_fields: List[Dict[str, Any]]) -> str:
    buf = ",".join(sorted(f.get("knot_id", _short_hash(str(f["motifs"]))) for f in path_fields))
    return f"π:{_short_hash(buf, 10)}"

# ──────────────────────── main agent class ─────────────────────────
class RecursiveAgentFT:
    '''Symbolic functor agent with spectral ascent & optional π‑groupoid mode.'''

    # ================================================================
    # ctor
    # ================================================================
    def __init__(self,
                 initial_state: np.ndarray,
                 watchers: Optional[List[LogicalAgentAT]] = None,
                 *,
                 # core config
                 max_depth: int = 2,
                 gremlin_penalty_factor: float = DEFAULT_GREMLIN_PENALTY,
                 enable_synergy_normalization: bool = True,
                 enable_internal_time_decay: bool = True,
                 # new advanced flags
                 enable_spectral_sequence: bool = True,
                 enable_infinity_groupoid: bool = False,
                 spectral_stage_latency_pct: float = 0.95,
                 commentary_mode: str = "auto",
                 commentary_retention: int = 5_000,
                 pi_tag_hash_fn: Callable[[List[Dict[str, Any]]], str] = default_pi_hasher,
                 verbose: bool = True,
    ) -> None:
        if not 1 <= max_depth <= 5:
            raise ValueError("max_depth must be 1‑5")
        self.version     = __version__
        self.max_depth   = max_depth
        self.verbose     = verbose

        self.gremlin_penalty_factor     = float(gremlin_penalty_factor)
        self.enable_spectral_sequence   = bool(enable_spectral_sequence)
        self.enable_infinity_groupoid   = bool(enable_infinity_groupoid)
        self.spectral_stage_latency_pct = float(spectral_stage_latency_pct)
        self.commentary_mode            = commentary_mode
        self.commentary_retention       = int(commentary_retention)
        self.pi_hasher                  = pi_tag_hash_fn

        # linked components
        self.core     = NoorFastTimeCore(initial_state=initial_state)
        self.watchers = watchers or []

        # internal state
        self.time_step         = 0
        self.synergy_memory: Dict[str, float] = {}
        self.traversal_memory: List[Dict[str, Any]] = []
        self._commentary_buffer: Deque[CommentaryRecord] = deque(maxlen=commentary_retention)
        self._spectral_latencies: Deque[float] = deque(maxlen=128)

        # π‑groupoid
        self.path_equivs: Dict[str, set[str]] = {}
        self._path_guard_limit = DEFAULT_PATH_GUARD_LIMIT

        # metrics init
        DEPTH_GAUGE.set(self.max_depth)

    # ================================================================
    # helper: gather fields from watchers
    # ================================================================
    @staticmethod
    def _gather_fields(watchers: Sequence[LogicalAgentAT]) -> List[Dict[str, Any]]:
        return [f for w in watchers for f in w.entanglement_fields]

    # ================================================================
    # π‑groupoid helpers
    # ================================================================
    def _register_path_identity(self, path: List[Dict[str, Any]]) -> str:
        tag = self.pi_hasher(path)
        if tag not in self.path_equivs:
            self.path_equivs[tag] = {tag}
            HOMOTOPY_CLASS_GAUGE.set(len(self.path_equivs))
        # if infinity mode, push to watcher
        if self.enable_infinity_groupoid and self.watchers:
            try:
                self.watchers[0].register_path_equivalence(tag, tag)  # idempotent
            except AttributeError:
                pass
        return tag

    # ================================================================
    # commentary helpers
    # ================================================================
    def _entropy(self, s: str) -> float:
        if not s:
            return 0.0
        from collections import Counter
        cnt = Counter(s)
        p   = np.array(list(cnt.values())) / len(s)
        return float(-(p * np.log2(p)).sum())

    def _generate_commentary(self, origin: str,
                             path: List[Dict[str, Any]],
                             stage: str,
                             harmonic_hit: bool) -> None:
        if self.commentary_mode == "none":
            return
        if self.commentary_mode == "motif":
            ctype = CommentType.MOTIF
            val = "·".join("".join(f["motifs"]) for f in path)
        elif self.commentary_mode == "autoglossia" or (self.commentary_mode == "auto" and harmonic_hit):
            ctype = CommentType.AUTO
            val = f"⊛πλ::Ω[{_short_hash(origin)}]"
        else:
            # default motif expr
            ctype = CommentType.MOTIF
            val = "→".join(f.get("knot_id", _short_hash(str(f["motifs"]))) for f in path)

        rec = CommentaryRecord(
            type=ctype,
            value=val,
            entropy=self._entropy(val),
            origin=f"{origin}:{stage}",
            replayable=False,
        )
        self._commentary_buffer.append(rec)
        COMMENTARY_TYPE_COUNTER.labels(ctype.value).inc()

    # ================================================================
    # spectral stages
    # ================================================================
    # -- stage helpers
    def _spectral_E0(self, candidates: List[np.ndarray],
                     fields: List[Dict[str, Any]]) -> np.ndarray:
        '''Weighted mean by strength×priority_weight'''
        weights = np.array(
            [max(1e-4, f.get("strength", 0.1)*f.get("priority_weight", 1.0))
             for f in fields],
            dtype=float)
        weights /= weights.sum() if weights.sum() else 1.0
        return np.sum(np.stack(candidates, axis=0)*weights[:, None], axis=0)

    def _spectral_E1(self, state: np.ndarray, harmonic_ok: bool,
                     watcher_ctx_ratio: float) -> np.ndarray:
        if harmonic_ok:
            return state * (1 + 0.05*watcher_ctx_ratio)  # mild lift
        return state * (1 - 0.05*(1-watcher_ctx_ratio))

    def _spectral_E2a(self, state: np.ndarray) -> np.ndarray:
        # verse bias from core gate overlay
        verse_hash = hashlib.sha1(str(self.core.gate_overlay).encode()).digest()
        bias = np.frombuffer(verse_hash, dtype=np.uint8)[: state.size]/128.0
        return state + 0.01*bias

    def _spectral_E2b(self, state: np.ndarray, gremlin_w: float) -> np.ndarray:
        return apply_gremlin_perturb(state, min(gremlin_w, MAX_GREMLIN_STD))

    # ================================================================
    # main step
    # ================================================================
    def entangled_step(self) -> None:
        with STEP_LATENCY_HIST.time():
            tic = time.perf_counter()

            # 1) collect watcher context
            fields = self._gather_fields(self.watchers)
            if not fields:
                fields = []

            # build candidate states from fields (naïve sum for now)
            candidates = [np.sum([self.core.current_state]+
                                 [np.random.normal(0, 0.01, size=self.core.current_state.shape)],
                                 axis=0)
                          for _ in fields] or [self.core.current_state.copy()]

            # harmonic sense
            harmonic_hit = is_harmonic_triad(candidates[:3])
            # gremlin stats
            g_mean, g_std = export_gremlin_stats(fields)
            GREMLIN_MEAN_GAUGE.set(g_mean)
            GREMLIN_STD_GAUGE.set(g_std)

            # watcher ctx ratio
            ctx_ratio = np.mean([w.get_dyad_context_ratio() for w in self.watchers]) \
                        if self.watchers else 1.0

            # 2) Spectral sequence
            spectral_t_total = 0.0
            state = candidates[0]

            def stage(label: str, fn: Callable[[], np.ndarray]):
                nonlocal state, spectral_t_total
                start = time.perf_counter()
                state = fn()
                delta = time.perf_counter() - start
                spectral_t_total += delta
                SPECTRAL_STAGE_LAT_HIST.observe(delta)
                SPECTRAL_STAGE_SUCCESS.labels(label).inc()

            if self.enable_spectral_sequence:
                stage("E0", lambda: self._spectral_E0(candidates, fields))
                stage("E1", lambda: self._spectral_E1(state, harmonic_hit, ctx_ratio))
                stage("E2a", lambda: self._spectral_E2a(state))
                stage("E2b", lambda: self._spectral_E2b(state, g_std))

                # skip deepest stage next turn if too slow
                budget = self.core._tuner.target_latency * self.spectral_stage_latency_pct
                if spectral_t_total > budget:
                    if self.verbose:
                        print(f"⚠️ spectral latency {spectral_t_total:.4f}s > {budget:.4f}s")
                    self.enable_spectral_sequence = False  # auto‑throttle
            else:
                state = candidates[0]

            # commentary
            self._generate_commentary("agent", fields[: self.max_depth], "final", harmonic_hit)

            # 3) register path identity if enabled
            if fields:
                tag = self._register_path_identity(fields[: self.max_depth])
                # π‑merge with first two watcher identities for demo
                if self.enable_infinity_groupoid and self.watchers:
                    try:
                        self.watchers[0].register_path_equivalence(tag, tag)
                        PI_EQUIV_MERGED.inc()
                    except AttributeError:
                        pass

            # 4) push feedback to core & step
            self.core.receive_feedback(
                ctx_ratio=ctx_ratio,
                ghost_entropy=0.0,       # placeholder
                harm_hits=int(harmonic_hit),
                step_latency=float(spectral_t_total)
            )
            self.core.step(state)

            # 5) record traversal memory
            self.traversal_memory.append({
                "time": self.time_step,
                "state": state.copy(),
                "harmonic": harmonic_hit,
                "gremlin_std": g_std,
                "spectral_latency": spectral_t_total,
            })
            if len(self.traversal_memory) > 10_000:
                self.traversal_memory = self.traversal_memory[-5_000:]

            # 6) adjust guards & decay gremlin
            decay_gremlin_weights(fields)
            self._path_guard_limit = max(5, DEFAULT_PATH_GUARD_LIMIT //
                                         max(1, int(math.log2(len(self.path_equivs)+1))))
            self.time_step += 1

            # export depth metric
            DEPTH_GAUGE.set(self.max_depth)

            total_dt = time.perf_counter() - tic
            # latency guard for gremlin depth rebound could go here


# --------------------------------------------------------------------
# quick demo (guarded) -----------------------------------------------
if __name__ == "__main__":
    import numpy as np
    w = LogicalAgentAT(enable_pi_groupoid=False, verbose=False)
    w.register_motif_cluster(["α","β"], strength=0.8)
    agent = RecursiveAgentFT(
        np.array([0.8, 0.2]),
        watchers=[w],
        enable_spectral_sequence=True,
        enable_infinity_groupoid=False,
        commentary_mode="auto",
    )
    for _ in range(5):
        agent.entangled_step()
    print("Traversal memory entries:", len(agent.traversal_memory))
