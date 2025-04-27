"""
logical_agent_at.py  (v2.7.0)
-----------------------------------------------------------------
Watcher module with Dynamic Window, Adaptive Dyad Decay, Ghost‑Resonance
Reinforcement, Motif‑Drift Correction, optional Musical Embeddings and
Prometheus observability.  Fully backward‑compatible with v2.6 save‑files.
"""

from __future__ import annotations

__version__ = "2.7.0"

import threading
import hashlib
import math
from collections import deque, defaultdict
from typing import List, Dict, Any, Optional, Union

import numpy as np
import networkx as nx

# ──────────────────────────────────────────────────────────────────────
# Prometheus metrics (safe stub fallback)
# ──────────────────────────────────────────────────────────────────────
try:
    from prometheus_client import Gauge, Counter  # type: ignore

    DYAD_RATIO_GAUGE = Gauge("noor_dyad_ratio", "Triad/Dyad context balance (Watcher)")
    CONTRADICTION_COUNTER = Counter("noor_contradictions_total", "Contradictions logged", ["agent"])
except Exception:  # pragma: no cover – keep package‑free

    class _Stub:  # pylint: disable=too-few-public-methods
        def __getattr__(self, _):
            return lambda *a, **k: None

    DYAD_RATIO_GAUGE = CONTRADICTION_COUNTER = _Stub()


# ──────────────────────────────────────────────────────────────────────
# Constants & Tunables
# ──────────────────────────────────────────────────────────────────────
MAX_FIELDS = 1000
MAX_META_FIELDS = 300
MAX_GRAPH_EDGES = 500

DEFAULT_DYAD_DECAY_RATE = 0.999
DEFAULT_WINDOW_SIZE = 250
CONTRADICTION_EMA_ALPHA = 0.1  # smoothing for adaptive decay

# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

def _flatten_motifs(motifs: List[Union[str, List[str]]]) -> Dict[str, Any]:
    flat, sub, idx = [], {}, 0
    for item in motifs:
        if isinstance(item, list):
            name = f"_sub_{idx}"
            idx += 1
            sub[name] = item
            flat.append(name)
        else:
            flat.append(item)
    return {"flat_list": list(dict.fromkeys(flat)), "substructures": sub}


def _short_hash(data: str, length: int = 8) -> str:
    return hashlib.sha1(data.encode("utf-8", "replace")).hexdigest()[:length]


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ──────────────────────────────────────────────────────────────────────
# Main Class
# ──────────────────────────────────────────────────────────────────────


class LogicalAgentAT:  # pylint: disable=too-many-public-methods
    """Motif‑watcher with dyad ecology, self‑healing window and ghost reinforcement."""

    # ------------------------------------------------------------------
    # construction
    # ------------------------------------------------------------------
    def __init__(
        self,
        motifs: Optional[List[str]] = None,
        *,
        contradiction_log_size: int = 50,
        enable_teleport: bool = False,
        verbose: bool = True,
        window_size: int = DEFAULT_WINDOW_SIZE,
        dyad_decay_rate: float = DEFAULT_DYAD_DECAY_RATE,
        enable_auto_triads: bool = True,
        enable_musical_embeddings: bool = False,
    ):
        self.__version__ = __version__

        # Core stores ---------------------------------------------------
        self.entanglement_fields: List[Dict[str, Any]] = []
        self.field_index: Dict[str, List[int]] = defaultdict(list)
        self.field_count: int = 0
        self.motif_embeddings: Dict[str, np.ndarray] = {}

        # Dyad context window ------------------------------------------
        self._dyad_window: deque[int] = deque(maxlen=window_size)
        self._window_size = window_size
        self.dyad_decay_rate: float = float(dyad_decay_rate)
        self.enable_auto_triads = enable_auto_triads
        self.enable_musical_embeddings = enable_musical_embeddings

        # Meta & Ghost stores ------------------------------------------
        self.meta_fields: List[Dict[str, Any]] = []
        self.ghost_motifs: Dict[str, Dict[str, Any]] = {}

        # Logs ----------------------------------------------------------
        self.history: List[str] = []
        self.contradiction_log: deque[str] = deque(maxlen=contradiction_log_size)
        self._contradiction_avg: float = 0.0
        self.generation: int = 0

        # Settings ------------------------------------------------------
        self.enable_teleport = enable_teleport
        self.verbose = verbose

        # Thread‑safety -------------------------------------------------
        self._lock = threading.Lock()

        if motifs:
            self.history.append(f"Watcher initialised with motifs {motifs}")

    # ────────────────────────────────────────────────────────────────
    # Dyad context helpers
    # ────────────────────────────────────────────────────────────────
    def _update_dyad_window(self, motif_count: int) -> None:
        with self._lock:
            self._dyad_window.append(motif_count)

    def get_dyad_context_ratio(self) -> float:
        with self._lock:
            triads = sum(1 for c in self._dyad_window if c >= 3)
            ratio = triads / len(self._dyad_window) if self._dyad_window else 1.0
        DYAD_RATIO_GAUGE.set(ratio)
        return ratio

    # ────────────────────────────────────────────────────────────────
    # Contradiction helpers
    # ────────────────────────────────────────────────────────────────
    def log_contradiction(self, message: str) -> None:
        with self._lock:
            self.contradiction_log.append(message)
            CONTRADICTION_COUNTER.labels(agent="logical_agent").inc()

    # ────────────────────────────────────────────────────────────────
    # Dynamic window helpers
    # ────────────────────────────────────────────────────────────────
    def check_and_adjust_window(self) -> None:
        mu_sat = self._compute_mu_saturation()
        drift = self._detect_field_drift()
        old_size = self._window_size
        if mu_sat > 0.8:
            new_size = int(old_size * 1.5)
        elif drift:
            new_size = int(old_size * 0.75)
        else:
            new_size = old_size
        new_size = min(max(100, new_size), 5000)
        if new_size != old_size:
            self._adjust_window_size(new_size)
            if self.verbose:
                self.history.append(f"WINDOW_RESIZE {old_size}→{new_size} sat={mu_sat:.2f} drift={drift}")

    def _adjust_window_size(self, new_size: int) -> None:
        with self._lock:
            data = list(self._dyad_window)[-new_size:]
            self._dyad_window = deque(data, maxlen=new_size)
            self._window_size = new_size

    # ────────────────────────────────────────────────────────────────
    # Adaptive dyad decay helpers
    # ────────────────────────────────────────────────────────────────
    def adjust_decay_rate(self) -> None:
        contrad_count = len(self.contradiction_log)
        self._contradiction_avg = (
            (1 - CONTRADICTION_EMA_ALPHA) * self._contradiction_avg
            + CONTRADICTION_EMA_ALPHA * contrad_count
        )
        if self._contradiction_avg > 30:
            self.dyad_decay_rate = 0.9995
        elif self._contradiction_avg < 10:
            self.dyad_decay_rate = 0.998
        else:
            # interpolate linearly between the two extremes
            t = (self._contradiction_avg - 10) / 20
            self.dyad_decay_rate = 0.998 + t * (0.9995 - 0.998)

    # ────────────────────────────────────────────────────────────────
    # Saturation / drift detection
    # ────────────────────────────────────────────────────────────────
    def _compute_mu_saturation(self) -> float:
        """Return ratio of duplicate motif pairs inside window."""
        with self._lock:
            counts = defaultdict(int)
            for fid in range(max(0, self.field_count - self._window_size), self.field_count):
                motifs = tuple(sorted(self.entanglement_fields[fid]["motifs"]))
                counts[motifs] += 1
            total = sum(counts.values())
            if total == 0:
                return 0.0
            repeats = sum(c - 1 for c in counts.values() if c > 1)
            return repeats / total

    def _detect_field_drift(self) -> bool:
        with self._lock:
            for field in self.entanglement_fields:
                pv = field.get("persistence_vector")
                if not pv:
                    continue
                if (self.generation - pv["last_surface_echo"]) > 500:
                    return True
        return False

    # ────────────────────────────────────────────────────────────────
    # Ghost reinforcement
    # ────────────────────────────────────────────────────────────────
    def reinforce_ghost_resonance(self, state: np.ndarray) -> None:
        with self._lock:
            for gid, ghost in self.ghost_motifs.items():
                if self._ghost_seen_in_state(gid, state):
                    old = ghost["strength"]
                    ghost["strength"] = min(1.0, old * 1.1)
                    if self.verbose:
                        self.history.append(f"GHOST_RESONANCE {gid} ↑{old:.3f}→{ghost['strength']:.3f}")

    # ────────────────────────────────────────────────────────────────
    # Motif‑Cluster Registration
    # ────────────────────────────────────────────────────────────────
    def register_motif_cluster(
        self,
        motifs: List[Union[str, List[str]]],
        strength: float,
        *,
        priority_weight: float = 1.0,
        flags: Optional[Dict[str, Any]] = None,
    ) -> None:
        flags = flags or {}
        with self._lock:
            if not motifs or len(motifs) < 2:
                self.history.append("Rejected cluster with <2 motifs")
                return
            if self.field_count >= MAX_FIELDS:
                self.history.append("Reached MAX_FIELDS; registration blocked")
                return

            strength = max(0.0, min(float(strength), 1.0))
            parsed = _flatten_motifs(motifs)
            flat_list = parsed["flat_list"]
            subs = parsed["substructures"]

            is_dyad = len(flat_list) == 2
            dyad_exempt = flags.get("dyad_exempt", False)
            ctx = self.get_dyad_context_ratio()

            curvature_bias = 1.0
            if is_dyad and not dyad_exempt:
                strength *= 0.6 + 0.4 * ctx  # soft penalty
                curvature_bias *= 1.5
                if strength > 0.8:
                    curvature_bias *= 2.0
                if self.verbose:
                    self.history.append(
                        f"DYAD_REGISTERED {flat_list} ctx={ctx:.2f} strength→{strength:.3f}"
                    )
            elif is_dyad and dyad_exempt and self.verbose:
                self.history.append(f"DYAD_EXEMPT {flat_list}")

            # Build entry ------------------------------------------------
            entry: Dict[str, Any] = {
                "motifs": flat_list,
                "strength": strength,
                "priority_weight": float(priority_weight),
                "substructures": subs,
                "curvature_bias": curvature_bias,
            }
            if is_dyad:
                entry["dyad_flag"] = True
                if dyad_exempt:
                    entry["dyad_exempt"] = True

            # Ghost context --------------------------------------------
            if is_dyad and self.enable_auto_triads and not dyad_exempt:
                ghost_id = f"_ctx_{_short_hash(str(flat_list))}"
                self.register_ghost_motif(ghost_id, origin="auto_ctx")
                entry["ghost_ctx"] = ghost_id

            # Persistence vector ---------------------------------------
            entry["persistence_vector"] = {
                "original_resonance_index": self.generation,
                "current_lattice_weight": strength,
                "last_surface_echo": self.generation,
            }

            # Store -----------------------------------------------------
            idx = self.field_count
            entry["index"] = idx  # helpful for external agents
            self.entanglement_fields.append(entry)
            self.field_count += 1
            for m in flat_list:
                self.field_index[m].append(idx)

            self._update_dyad_window(len(flat_list))

    # ────────────────────────────────────────────────────────────────
    # Ghost Motif API
    # ────────────────────────────────────────────────────────────────
    def register_ghost_motif(self, motif: str, origin: str, *, strength: float = 0.5):
        with self._lock:
            self.ghost_motifs[motif] = {
                "origin": origin,
                "strength": float(strength),
                "Ω_r": 1.0,
                "ascent_detected": False,
                "witnessed_by": [],
            }

    def promote_ghost_to_field(self, motif: str):
        ghost = self.ghost_motifs.pop(motif, None)
        if ghost:
            self.register_motif_cluster([motif], strength=ghost.get("strength", 0.3))

    # Presence check --------------------------------------------------
    def _ghost_seen_in_state(self, motif_id: str, state: np.ndarray) -> bool:
        emb = self.motif_embeddings.get(motif_id)
        if emb is None:
            return False
        if emb.ndim > 1 and self.enable_musical_embeddings:
            emb = emb.flatten()
            similarity = _cosine(state.flatten(), emb)
        else:
            similarity = float(np.dot(state, emb))
        return similarity > 0.1

    # ────────────────────────────────────────────────────────────────
    # Observe State
    # ────────────────────────────────────────────────────────────────
    def observe_state(self, state: np.ndarray) -> None:
        self.reinforce_ghost_resonance(state)

        with self._lock:
            self.generation += 1
            for fid, field in enumerate(self.entanglement_fields):
                if field.get("dyad_flag") and not field.get("dyad_exempt"):
                    # decay strength -----------------------------------
                    old = field["strength"]
                    field["strength"] *= self.dyad_decay_rate
                    if self.generation % 100 == 0 and self.verbose:
                        self.history.append(
                            f"DYAD_DECAY #{fid} {old:.3f}→{field['strength']:.3f} rate={self.dyad_decay_rate:.6f}"
                        )
                    if field["strength"] < 1e-5:
                        self.log_contradiction("dyad_strength_zero")

                    # auto‑triad promotion -----------------------------
                    gctx = field.get("ghost_ctx")
                    if gctx and self._ghost_seen_in_state(gctx, state):
                        motifs = field["motifs"] + [gctx]
                        self.promote_ghost_to_field(gctx)
                        self.register_motif_cluster(motifs, strength=field["strength"] * 1.1)
                        field["dyad_flag"] = False
                        if self.verbose:
                            self.history.append(f"DYAD_PROMOTED_TO_TRIAD {motifs}")

                # update persistence echo -----------------------------
                pv = field.get("persistence_vector")
                if pv and any(m in self.ghost_motifs for m in field["motifs"]):
                    pv["last_surface_echo"] = self.generation

            # maintain window ratio ------------------------------------
            if self.entanglement_fields:
                self._update_dyad_window(len(self.entanglement_fields[-1]["motifs"]))

        # adaptive processes outside lock ------------------------------
        if self.generation % 50 == 0:
            self.check_and_adjust_window()
        if self.generation % 100 == 0:
            self.adjust_decay_rate()

    # ────────────────────────────────────────────────────────────────
    # Analytics
    # ────────────────────────────────────────────────────────────────
    def export_dyad_metrics(self) -> Dict[str, float]:
        with self._lock:
            total = len(self._dyad_window)
            dyads = sum(1 for c in self._dyad_window if c == 2)
            triads = total - dyads
            return {
                "generation": self.generation,
                "window": total,
                "dyads": dyads,
                "triads": triads,
                "context_ratio": self.get_dyad_context_ratio(),
                "recent_contradictions": len(self.contradiction_log),
                "dyad_decay_rate": self.dyad_decay_rate,
            }

    # alias for compatibility
    export_contradiction_profile = export_dyad_metrics

    # ────────────────────────────────────────────────────────────────
    # Graph rendering helper (unchanged)
    # ────────────────────────────────────────────────────────────────
    def render_entanglement_graph(self) -> nx.Graph:  # type: ignore
        G: nx.Graph = nx.Graph()
        edge_counter = 0
        with self._lock:
            for field in self.entanglement_fields:
                ml = field["motifs"]
                for i in range(len(ml)):
                    for j in range(i + 1, len(ml)):
                        if edge_counter >= MAX_GRAPH_EDGES:
                            self.history.append("Graph edge throttle reached; truncated")
                            return G
                        A, B = ml[i], ml[j]
                        G.add_edge(A, B)
                        edge_counter += 1
        return G

    # ────────────────────────────────────────────────────────────────
    # Serialization helpers
    # ────────────────────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "version": self.__version__,
                "entanglement_fields": self.entanglement_fields,
                "ghost_motifs": self.ghost_motifs,
                "meta_fields": self.meta_fields,
                "_dyad_window": list(self._dyad_window),
                "window_size": self._window_size,
                "dyad_decay_rate": self.dyad_decay_rate,
                "enable_auto_triads": self.enable_auto_triads,
                "enable_musical_embeddings": self.enable_musical_embeddings,
                "_contradiction_avg": self._contradiction_avg,
            }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogicalAgentAT":
        watcher = cls(
            window_size=data.get("window_size", DEFAULT_WINDOW_SIZE),
            dyad_decay_rate=data.get("dyad_decay_rate", DEFAULT_DYAD_DECAY_RATE),
            enable_auto_triads=data.get("enable_auto_triads", True),
            enable_musical_embeddings=data.get("enable_musical_embeddings", False),
            verbose=False,
        )
        watcher.entanglement_fields = data.get("entanglement_fields", [])
        watcher.ghost_motifs = data.get("ghost_motifs", {})
        watcher.meta_fields = data.get("meta_fields", [])
        watcher.field_count = len(watcher.entanglement_fields)
        watcher._dyad_window = deque(
            data.get("_dyad_window", []), maxlen=watcher._window_size
        )
        watcher._contradiction_avg = data.get("_contradiction_avg", 0.0)
        return watcher

    # ────────────────────────────────────────────────────────────────
    # Placeholder stubs for public APIs (unchanged from v2.6)
    # ────────────────────────────────────────────────────────────────
    def emit_alignment_vector(self, fid: int = -1) -> np.ndarray:  # type: ignore
        """Return dummy zero‑vec unless embeddings are wired externally."""
        if fid == -1:
            return np.zeros(1)
        field = self.entanglement_fields[fid]
        vecs = [self.motif_embeddings.get(m) for m in field["motifs"] if m in self.motif_embeddings]
        return np.mean(vecs, axis=0) if vecs else np.zeros(1)
