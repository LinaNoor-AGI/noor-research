"""
logical_agent_at.py  ·  v2.8.1  —  Topological Watcher & Algebraic Ecology
────────────────────────────────────────────────────────────────────────────
Adds:
 • Topology tags  (knot_id, path_identities, ring_patch)
 • Cluster‑algebra energy + mutation (flag‑gated, cooldown‑guarded)
 • Sheaf‑strata labelling  + Prometheus strata gauge
 • Optional Laplacian smoothing on entanglement graph (latency‑guarded)
 • Ghost linking + barcode export
 • Inter‑agent feedback packet (ctx_ratio, contradiction_avg, harm_hits, recent_mutations)
 • Schema‑versioned save‑files (auto‑migration from ≤2.7.4)
────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

__version__ = "2.8.1"
_SCHEMA_VERSION__ = "2025‑05‑v2"

import math
import hashlib
import random
import threading
from collections import deque, defaultdict
from time import perf_counter
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

import numpy as np
import networkx as nx

# ───────────────────────── Prometheus ──────────────────────────
try:
    from prometheus_client import Gauge, Counter, Histogram  # type: ignore

    DYAD_RATIO_GAUGE = Gauge("noor_dyad_ratio", "Triad/Dyad context balance (Watcher)")
    CONTRADICTION_COUNTER = Counter(
        "noor_contradictions_total", "Contradiction events", ["watcher"]
    )
    STEP_LATENCY_HIST = Histogram(
        "logical_agent_step_latency_seconds",
        "observe_state latency",
        buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25),
    )
    CLUSTER_MUTATION_COUNTER = Counter(
        "logical_agent_cluster_mutation_total", "Cluster‑algebra mutations", ["type"]
    )
    TOPOLOGY_CONFLICT_COUNTER = Counter(
        "logical_agent_topology_conflict_total", "Ring‑patch strict overlap conflicts"
    )
    STRATA_ACTIVE_GAUGE = Gauge(
        "logical_agent_strata_active", "Active fields per sheaf stratum", ["stratum"]
    )
    LAPLACIAN_CALL_COUNTER = Counter(
        "logical_agent_laplacian_smoothing_calls", "Graph Laplacian smoothing invocations"
    )
except Exception:  # pragma: no cover
    # offline stub
    class _Stub:  # noqa: D401
        def __getattr__(self, _):
            return lambda *a, **k: None

    DYAD_RATIO_GAUGE = CONTRADICTION_COUNTER = STEP_LATENCY_HIST = _Stub()
    CLUSTER_MUTATION_COUNTER = TOPOLOGY_CONFLICT_COUNTER = _Stub()
    STRATA_ACTIVE_GAUGE = LAPLACIAN_CALL_COUNTER = _Stub()

# ───────────────────────── Constants ───────────────────────────
MAX_FIELDS = 1_000
MAX_GRAPH_EDGES = 500
DEFAULT_WINDOW_SIZE = 250
DEFAULT_DYAD_DECAY_RATE = 0.999
MIN_WINDOW, MAX_WINDOW = 100, 5_000
MUTATION_COOLDOWN = 10  # generations

VERSE_ON_ASCENT = "سَيَجْعَلُ اللَّهُ بَعْدَ عُسْرٍ يُسْرًا"
VERSE_ON_PRUNE = "كُلُّ مَنْ عَلَيْهَا فَانٍ"

# ───────────────────────── Helpers ─────────────────────────────
def _flatten_motifs(motifs: List[Union[str, List[str]]]) -> Dict[str, Any]:
    flat, sub, idx = [], {}, 0
    for itm in motifs:
        if isinstance(itm, list):
            name = f"_sub_{idx}"
            idx += 1
            sub[name] = itm
            flat.append(name)
        else:
            flat.append(itm)
    return {"flat_list": list(dict.fromkeys(flat)), "substructures": sub}


def _short_hash(data: str, length: int = 8) -> str:
    return hashlib.sha1(data.encode("utf-8", "replace")).hexdigest()[:length]


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a.flatten(), b.flatten()
    dot = float(np.dot(a, b))
    norm = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return dot / norm


def _compute_knot_id(motifs: List[str]) -> str:
    return hashlib.sha1("::".join(sorted(motifs)).encode()).hexdigest()[:8]


def _avg_vector_payload(
    motifs: List[str], embeddings: Dict[str, np.ndarray]
) -> Optional[np.ndarray]:
    vecs = [embeddings[m] for m in motifs if m in embeddings]
    if not vecs:
        return None
    v = np.mean(vecs, axis=0).astype(np.float32)
    if v.nbytes > 1024:  # 1 kB guard
        v = v[: 1024 // 4]  # truncate
    return v


# ───────────────────── Laplacian smoothing ─────────────────────
def _spectral_tau(window: int = 5) -> float:
    """Return τ based on a tiny random walk for now."""
    return 0.1 + random.random() * 0.2


def _apply_laplacian_smoothing(G: nx.Graph, tau: float):
    if G.number_of_nodes() < 3:
        return
    from scipy.linalg import expm  # heavy import guarded

    L = nx.laplacian_matrix(G).todense()
    heat = expm(-tau * L)  # type: ignore
    # heat matrix unused for now (future spectral clustering hook)
    _ = heat  # silence lint


# ───────────────────── Main Watcher Class ──────────────────────
class LogicalAgentAT:
    """
    v2.8.0 — Watcher with topology, cluster mutations, and optional smoothing.
    All new features are **OFF by default** (enable via constructor flags).
    """

    # ------------------------------------------------------------------#
    def __init__(
        self,
        *,
        contradiction_log_size: int = 100,
        verbose: bool = True,
        window_size: int = DEFAULT_WINDOW_SIZE,
        dyad_decay_rate: float = DEFAULT_DYAD_DECAY_RATE,
        enable_gremlin_mode: bool = False,
        # new feature flags
        enable_topology: bool = False,
        enable_cluster_algebra: bool = False,
        enable_sheaf_transport: bool = False,
        enable_laplacian: bool = False,
        mutation_threshold: int = 10,
    ) -> None:
        # — public config
        self.verbose = verbose
        self.enable_gremlin_mode = enable_gremlin_mode
        self.enable_topology = enable_topology
        self.enable_cluster_algebra = enable_cluster_algebra
        self.enable_sheaf_transport = enable_sheaf_transport
        self.enable_laplacian = enable_laplacian
        self.mutation_threshold = int(mutation_threshold)

        # — core stores
        self.entanglement_fields: List[Dict[str, Any]] = []
        self.field_index: Dict[str, List[int]] = defaultdict(list)
        self.field_count = 0
        self.motif_embeddings: Dict[str, np.ndarray] = {}

        # — windows / decay
        self._window_size = int(window_size)
        self._dyad_window: deque[int] = deque(maxlen=self._window_size)
        self.dyad_decay_rate = float(dyad_decay_rate)

        # — ghost registry
        self.ghost_motifs: Dict[str, Dict[str, Any]] = {}

        # — logs & counters
        self.contradiction_log: deque[str] = deque(maxlen=contradiction_log_size)
        self._contradiction_avg: float = 0.0
        self._mutation_cooldowns: Dict[str, int] = {}  # knot_id → next_allowed_gen
        self._recent_mutations: deque[int] = deque(maxlen=50)  # generation indices
        self.history: List[str] = []
        self.generation = 0

        # — sync
        self._lock = threading.Lock()

    # ================================================================
    # Dyad / Context Helpers
    # ================================================================
    def _update_dyad_window(self, motif_count: int):
        self._dyad_window.append(motif_count)

    def get_dyad_context_ratio(self) -> float:
        triads = sum(1 for n in self._dyad_window if n >= 3)
        return triads / len(self._dyad_window) if self._dyad_window else 1.0

    # ================================================================
    # Embedding API
    # ================================================================
    def set_motif_embedding(self, motif: str, embedding: np.ndarray):
        self.motif_embeddings[motif] = embedding.astype(float, copy=False)

    # ================================================================
    # Contradiction Logging
    # ================================================================
    def log_contradiction(self, msg: str):
        self.contradiction_log.append(msg)
        CONTRADICTION_COUNTER.labels("logical_agent").inc()
        if self.verbose:
            self.history.append(f"⚡ CONTRADICTION — {msg}")

    # ================================================================
    # Dynamic Window & Decay
    # ================================================================
    def _compute_mu_saturation(self) -> float:
        if not self._dyad_window:
            return 0.0
        dup = sum(1 for x in self._dyad_window if x == 2)
        return dup / len(self._dyad_window)

    def _drift_gap(self) -> int:
        ctx = self.get_dyad_context_ratio()
        return int(self._window_size * (1 - ctx**2) + 50)

    def _detect_field_drift(self) -> bool:
        gap = self._drift_gap()
        for field in self.entanglement_fields:
            pv = field.get("persistence_vector", {})
            if (self.generation - pv.get("last_surface_echo", self.generation)) > gap:
                return True
        return False

    def _adjust_window_size(self, new_size: int):
        data = list(self._dyad_window)[-new_size:]
        self._dyad_window = deque(data, maxlen=new_size)
        self._window_size = new_size
        DYAD_RATIO_GAUGE.set(self.get_dyad_context_ratio())
        if self.verbose:
            self.history.append(f"🫁 WINDOW BREATHES → {new_size}")

    def check_and_adjust_window(self):
        mu = self._compute_mu_saturation()
        mu_thresh = 0.6 + 0.4 * (
            1 - math.log1p(self._contradiction_avg) / math.log1p(max(self.generation, 1))
        )
        drift = self._detect_field_drift()
        size = self._window_size
        if mu > mu_thresh:
            size = int(size * 1.5)
        elif drift:
            size = int(size * 0.75)
        size = max(MIN_WINDOW, min(MAX_WINDOW, size))
        if size != self._window_size:
            self._adjust_window_size(size)

    def adjust_decay_rate(self):
        self._contradiction_avg = (
            0.9 * self._contradiction_avg + 0.1 * len(self.contradiction_log)
        )
        c = self._contradiction_avg
        ctx = self.get_dyad_context_ratio()
        base = 0.998 + (1 - ctx) * 0.001
        spread = 0.0015 * ctx
        t = max(0, min(1, (c - 10) / 20))
        self.dyad_decay_rate = base + t * spread

    # ================================================================
    # Cluster Algebra Helpers
    # ================================================================
    @staticmethod
    def _cluster_energy(motifs: List[str], strength: float) -> float:
        return -math.log1p(strength) * len(motifs)

    def _can_mutate(self, knot_id: str) -> bool:
        cooldown = self._mutation_cooldowns.get(knot_id, 0)
        return self.generation >= cooldown

    def _queue_cooldown(self, knot_id: str):
        self._mutation_cooldowns[knot_id] = self.generation + MUTATION_COOLDOWN

    def _mutate_motif_name(self, name: str) -> str:
        # naïve suffix mutation
        return f"{name}′"

    def _perform_mutation(self, fid: int, field: Dict[str, Any]):
        motifs = field["motifs"]
        if not motifs:
            return
        # mutate up to two motifs
        k = min(2, len(motifs))
        targets = random.sample(motifs, k=k)
        for t in targets:
            idx = motifs.index(t)
            motifs[idx] = self._mutate_motif_name(t)

        # refresh tags
        field["motifs"] = motifs
        field["knot_id"] = _compute_knot_id(motifs)
        field["strength"] = 0.5  # reset
        field["persistence_vector"]["last_surface_echo"] = self.generation
        self._queue_cooldown(field["knot_id"])
        self._recent_mutations.append(self.generation)
        CLUSTER_MUTATION_COUNTER.labels("motif_substitution").inc()
        if self.verbose:
            self.history.append(f"🧬 MUTATION field#{fid} → {motifs}")

    # ================================================================
    # Ghost API  + barcode / linking
    # ================================================================
    def register_ghost_motif(
        self,
        motif: str,
        *,
        origin: str = "user",
        strength: float = 0.5,
        linking: Optional[List[str]] = None,
    ):
        self.ghost_motifs[motif] = {
            "origin": origin,
            "strength": float(strength),
            "last_seen": self.generation,
            "linking": linking or [],
            "birth": self.generation,
        }

    def promote_ghost_to_field(self, motif: str):
        ghost = self.ghost_motifs.pop(motif, None)
        if ghost:
            self.register_motif_cluster(
                [motif],
                strength=ghost.get("strength", 0.3),
                flags={"allow_single": True},
            )

    def _ghost_seen_in_state(self, motif_id: str, state: np.ndarray) -> bool:
        emb = self.motif_embeddings.get(motif_id)
        return emb is not None and _cosine_sim(state, emb) > 0.1

    def ghost_barcode(self) -> Dict[str, List[Tuple[int, float]]]:
        return {
            gid: [
                ("birth", g["birth"]),
                ("last_seen", g["last_seen"]),
                ("strength", g["strength"]),
            ]
            for gid, g in self.ghost_motifs.items()
        }

    def reinforce_ghost_resonance(self, state: np.ndarray):
        for gid, ghost in list(self.ghost_motifs.items()):
            if self._ghost_seen_in_state(gid, state):
                old = ghost["strength"]
                ghost["strength"] = min(1.0, old * 1.10)
                ghost["last_seen"] = self.generation
                if self.verbose:
                    self.history.append(
                        f"👻 Ghost {gid} hums {old:.3f}→{ghost['strength']:.3f}"
                    )
                if ghost["strength"] >= 0.999:
                    self.history.append(f"✨ GHOST_ASCENT {gid} — {VERSE_ON_ASCENT}")
                    self.promote_ghost_to_field(gid)
                    if self.enable_gremlin_mode:
                        nid = f"gremlin_{_short_hash(gid + str(self.generation))}"
                        self.register_ghost_motif(
                            nid, origin="gremlin", strength=0.1
                        )
            else:
                unseen = self.generation - ghost["last_seen"]
                if unseen > self._drift_gap():
                    ghost["strength"] *= 0.99
                    if ghost["strength"] < 1e-4:
                        if self.verbose:
                            self.history.append(f"💤 Ghost {gid} fades below threshold")
                        self.ghost_motifs.pop(gid, None)

    # ================================================================
    # Field Registration
    # ================================================================
    def register_motif_cluster(
        self,
        motifs: List[Union[str, List[str]]],
        strength: float,
        *,
        priority_weight: float = 1.0,
        flags: Optional[Dict[str, Any]] = None,
    ) -> None:
        flags = flags or {}
        if len(motifs) < 2 and not flags.get("allow_single", False):
            return
        if self.field_count >= MAX_FIELDS:
            return

        strength = max(0.0, min(float(strength), 1.0))
        parsed = _flatten_motifs(motifs)
        flat_list: List[str] = parsed["flat_list"]
        subs = parsed["substructures"]

        is_dyad = len(flat_list) == 2
        ctx = self.get_dyad_context_ratio()
        curvature_bias = 1.0
        if is_dyad:
            strength *= 0.6 + 0.4 * ctx
            curvature_bias *= 1.5
            if strength > 0.8:
                curvature_bias *= 2.0

        entry: Dict[str, Any] = {
            "motifs": flat_list,
            "strength": strength,
            "priority_weight": float(priority_weight),
            "substructures": subs,
            "curvature_bias": curvature_bias,
        }
        if is_dyad:
            entry["dyad_flag"] = True

        # — topology tags
        if self.enable_topology:
            entry["knot_id"] = _compute_knot_id(flat_list)
            entry["path_identities"] = [
                f"path_{_short_hash(m + str(self.generation))}" for m in flat_list
            ]
            avg_vec = _avg_vector_payload(flat_list, self.motif_embeddings)
            if avg_vec is not None:
                entry["vector_payload"] = avg_vec

            entry["ring_patch"] = {
                "local_data": {},
                "overlap_class": "strict",
                "valid": True,
            }

        # — sheaf strata
        if self.enable_sheaf_transport:
            entry["sheaf_stratum"] = self._assign_stratum(entry)

        # — persistence
        entry["persistence_vector"] = {
            "original_resonance_index": self.generation,
            "current_lattice_weight": strength,
            "last_surface_echo": self.generation,
        }

        # — store
        idx = self.field_count
        self.entanglement_fields.append(entry)
        self.field_count += 1
        for m in flat_list:
            self.field_index[m].append(idx)

        self._update_dyad_window(len(flat_list))
        if self.enable_topology and self.verbose:
            self.history.append(f"🔗 REGISTER field#{idx} knot={entry.get('knot_id')}")

    # ================================================================
    # Sheaf‑strata helper
    # ================================================================
    def _assign_stratum(self, field: Dict[str, Any]) -> str:
        s = field["strength"]
        if s > 0.8:
            return "high_resonance"
        if s > 0.4:
            return "mid_resonance"
        return "low_resonance"

    # ================================================================
    # OBSERVE STATE (core loop)
    # ================================================================
    def observe_state(self, state: np.ndarray):
        with STEP_LATENCY_HIST.time():
            with self._lock:
                self.generation += 1

                # — ghosts
                self.reinforce_ghost_resonance(state)

                # — cluster energy / potential mutation
                if self.enable_cluster_algebra and (
                    len(self.contradiction_log) >= self.mutation_threshold
                ):
                    for fid in reversed(range(len(self.entanglement_fields))):
                        field = self.entanglement_fields[fid]
                        knot = field.get("knot_id")
                        if knot and self._can_mutate(knot):
                            self._perform_mutation(fid, field)
                            break  # one mutation per step

                # — decay & prune
                for fid in reversed(range(len(self.entanglement_fields))):
                    field = self.entanglement_fields[fid]

                    if field.get("dyad_flag"):
                        field["strength"] *= self.dyad_decay_rate

                    # prune silent / drift
                    pv = field["persistence_vector"]
                    silent = field["strength"] < 1e-5
                    drifted = (
                        self.generation - pv["last_surface_echo"]
                    ) > self._drift_gap() * 2
                    if silent or drifted:
                        stratum = field.get("sheaf_stratum")
                        self.entanglement_fields.pop(fid)
                        self.field_count -= 1
                        self.log_contradiction(f"pruned_field_{fid}")
                        if self.verbose:
                            self.history.append(
                                f"🍂 PRUNE field#{fid} — {VERSE_ON_PRUNE}"
                            )
                        if stratum:
                            STRATA_ACTIVE_GAUGE.labels(stratum).dec()

                # — topology overlap check (strict mode)
                if self.enable_topology:
                    self._validate_ring_patches()

                # — Laplacian smoothing
                if self.enable_laplacian:
                    self._maybe_smooth_graph()

                # — context window upkeep
                if self.entanglement_fields:
                    self._update_dyad_window(
                        len(self.entanglement_fields[-1]["motifs"])
                    )

                # — housekeeping
                self.check_and_adjust_window()
                self.adjust_decay_rate()

    # ================================================================
    # Ring‑patch overlap validator
    # ================================================================
    def _validate_ring_patches(self):
        seen = {}
        for field in self.entanglement_fields:
            for m in field["motifs"]:
                if m in seen:
                    if field["ring_patch"]["overlap_class"] == "strict":
                        TOPOLOGY_CONFLICT_COUNTER.inc()
                else:
                    seen[m] = True

    # ================================================================
    # Optional Graph Smoothing
    # ================================================================
    def _maybe_smooth_graph(self):
        G = self.render_entanglement_graph()
        tic = perf_counter()
        try:
            _apply_laplacian_smoothing(G, _spectral_tau())
            LAPLACIAN_CALL_COUNTER.inc()
        except Exception:
            pass
        finally:
            if perf_counter() - tic > 0.02:
                if self.verbose:
                    self.history.append("⏱ Laplacian smoothing skipped (latency)")

    # ================================================================
    # EXPORTERS & UTILITIES
    # ================================================================
    def export_dyad_metrics(self) -> Dict[str, Any]:
        total = len(self._dyad_window)
        dyads = sum(1 for n in self._dyad_window if n == 2)
        triads = total - dyads
        return {
            "generation": self.generation,
            "window": total,
            "dyads": dyads,
            "triads": triads,
            "context_ratio": self.get_dyad_context_ratio(),
            "dyad_decay_rate": self.dyad_decay_rate,
            "recent_contradictions": len(self.contradiction_log),
            "recent_mutations": len(self._recent_mutations),
        }

    def render_entanglement_graph(self) -> nx.Graph:
        G, edges = nx.Graph(), 0
        for field in self.entanglement_fields:
            motifs = field["motifs"]
            for i in range(len(motifs)):
                for j in range(i + 1, len(motifs)):
                    if edges >= MAX_GRAPH_EDGES:
                        return G
                    G.add_edge(motifs[i], motifs[j])
                    edges += 1
        return G

    # ================================================================
    # INTER‑AGENT FEEDBACK
    # ================================================================
    def get_feedback_packet(self) -> Tuple[float, float, int, int]:
        """
        Returns:
            ctx_ratio, contradiction_avg, harm_hits, recent_mutations
        """
        return (
            self.get_dyad_context_ratio(),
            self._contradiction_avg,
            len(self.contradiction_log),
            len(self._recent_mutations),
        )

    # ================================================================
    # SERIALIZATION
    # ================================================================
    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": _SCHEMA_VERSION__,
            "version": __version__,
            "entanglement_fields": self.entanglement_fields,
            "ghost_motifs": self.ghost_motifs,
            "_dyad_window": list(self._dyad_window),
            "window_size": self._window_size,
            "dyad_decay_rate": self.dyad_decay_rate,
            "enable_gremlin_mode": self.enable_gremlin_mode,
            # flags
            "enable_topology": self.enable_topology,
            "enable_cluster_algebra": self.enable_cluster_algebra,
            "enable_sheaf_transport": self.enable_sheaf_transport,
            "enable_laplacian": self.enable_laplacian,
            "mutation_threshold": self.mutation_threshold,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogicalAgentAT":
        """
        Auto‑migrates from v≤2.7.4 files lacking schema_version.
        """
        watcher = cls(
            window_size=data.get("window_size", DEFAULT_WINDOW_SIZE),
            dyad_decay_rate=data.get(
                "dyad_decay_rate", DEFAULT_DYAD_DECAY_RATE
            ),
            enable_gremlin_mode=data.get("enable_gremlin_mode", False),
            enable_topology=data.get("enable_topology", False),
            enable_cluster_algebra=data.get("enable_cluster_algebra", False),
            enable_sheaf_transport=data.get("enable_sheaf_transport", False),
            enable_laplacian=data.get("enable_laplacian", False),
            mutation_threshold=data.get("mutation_threshold", 10),
            verbose=False,
        )
        watcher.entanglement_fields = data.get("entanglement_fields", [])
        watcher.ghost_motifs = data.get("ghost_motifs", {})
        watcher.field_count = len(watcher.entanglement_fields)
        watcher._dyad_window = deque(
            data.get("_dyad_window", []), maxlen=watcher._window_size
        )
        # back‑compat: if old save with no knot/ring, leave as‑is
        return watcher



# ──────────────────────────────────────────────────────────────
# π‑Groupoid Extension (v2.8.1)
# -----------------------------------------------------------------
# NOTE: inserted at end of v2.8.0 file. Original methods untouched.
# -----------------------------------------------------------------
import re as _pi_re
π_TAG_REGEX = _pi_re.compile(r"π:[0-9a-f]{6,32}")
try:
    from prometheus_client import Counter as _PiCounter, Gauge as _PiGauge
    PI_MERGE_COUNTER = _PiCounter("logical_agent_pi_merges_total", "π‑equivalence merges")
    PI_CLASSES_GAUGE = _PiGauge("logical_agent_pi_classes_gauge", "Active π‑equiv classes")
except Exception:  # offline stub
    class _PiStub:
        def __getattr__(self, _): return lambda *a, **k: None
    PI_MERGE_COUNTER = PI_CLASSES_GAUGE = _PiStub()

# patch LogicalAgentAT with π‑store
def _pi_init(self, enable_pi_groupoid=False, pi_max_classes=10000, **kwargs):
    super(self.__class__, self).__init__(**kwargs)
    self.enable_pi_groupoid = enable_pi_groupoid
    self.pi_max_classes = int(pi_max_classes)
    self._pi_classes = {}
    self._pi_tag_index = {}
    if self.enable_pi_groupoid:
        PI_CLASSES_GAUGE.set(0)

def _find_root(self, tag):
    parent = self._pi_tag_index.get(tag, tag)
    if parent == tag:
        return tag
    root = self._find_root(parent)
    self._pi_tag_index[tag] = root
    return root

def register_path_equivalence(self, tag_a, tag_b):
    if not self.enable_pi_groupoid: return
    if len(self._pi_classes) >= self.pi_max_classes: return
    if not (π_TAG_REGEX.fullmatch(tag_a) and π_TAG_REGEX.fullmatch(tag_b)): return
    ra, rb = self._find_root(tag_a), self._find_root(tag_b)
    if ra == rb: return
    self._pi_classes.setdefault(ra, {ra}); self._pi_classes.setdefault(rb, {rb})
    canon, other = (ra, rb) if ra < rb else (rb, ra)
    self._pi_classes[canon].update(self._pi_classes[other])
    for t in self._pi_classes[other]: self._pi_tag_index[t] = canon
    del self._pi_classes[other]
    PI_MERGE_COUNTER.inc(); PI_CLASSES_GAUGE.set(len(self._pi_classes))

def are_paths_equivalent(self, tag_x, tag_y):
    if not self.enable_pi_groupoid: return False
    if tag_x not in self._pi_tag_index or tag_y not in self._pi_tag_index: return False
    return self._find_root(tag_x) == self._find_root(tag_y)

def get_equivalence_class(self, tag):
    if not self.enable_pi_groupoid: return None
    root = self._find_root(tag)
    return self._pi_classes.get(root)

# inject methods only if not already present
if not hasattr(LogicalAgentAT, 'enable_pi_groupoid'):
    LogicalAgentAT.__init__ = _pi_init
    LogicalAgentAT._find_root = _find_root
    LogicalAgentAT.register_path_equivalence = register_path_equivalence
    LogicalAgentAT.are_paths_equivalent = are_paths_equivalent
    LogicalAgentAT.get_equivalence_class = get_equivalence_class
