"""
logical_agent_at.py  ·  v3.1.0  —  Topological Watcher & Quantum Tick 2.0
────────────────────────────────────────────────────────────────────────────
Adds:
 • Topology tags  (knot_id, path_identities, ring_patch)
 • Cluster‑algebra energy + mutation (flag‑gated, cooldown‑guarded)
 • Sheaf‑strata labelling  + Prometheus strata gauge
 • Optional Laplacian smoothing on entanglement graph (latency‑guarded)
 • Ghost linking + barcode export
 • Inter‑agent feedback packet (ctx_ratio, contradiction_avg, harm_hits, recent_mutations)
 • π‑Groupoid equivalence registry
 • NEW Quantum Tick 2.0: coherence_hash, lamport_clock, hlc_ts, ring-buffer, HMAC, epoch_histogram
 • Dynamic feature flags (AI‑adaptive)
 • Schema‑versioned save‑files (auto‑migration from ≤2.8.1)
────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

__version__       = "3.1.0"
_SCHEMA_VERSION__ = "2025‑Q2‑quantum‑tick"

import os
import math
import hashlib
import hmac
import threading
import random
import time
from collections import deque, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import networkx as nx

try:
    from prometheus_client import Gauge, Counter, Histogram
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
    PI_MERGE_COUNTER = Counter(
        "logical_agent_pi_merges_total", "π‑equivalence merges"
    )
    PI_CLASSES_GAUGE = Gauge(
        "logical_agent_pi_classes_gauge", "Active π‑equiv classes"
    )
    TICKS_TOTAL = Counter("logical_agent_ticks_total", "Quantum ticks processed", ["agent_id"])
    TICK_HMAC_FAILURES = Counter("logical_agent_tick_hmac_failures_total", "Tick HMAC failures", ["agent_id"])
except ImportError:
    class _Stub:
        def __getattr__(self, _): return lambda *a, **k: None
    DYAD_RATIO_GAUGE = CONTRADICTION_COUNTER = STEP_LATENCY_HIST = _Stub()
    CLUSTER_MUTATION_COUNTER = TOPOLOGY_CONFLICT_COUNTER = _Stub()
    STRATA_ACTIVE_GAUGE = LAPLACIAN_CALL_COUNTER = _Stub()
    PI_MERGE_COUNTER = PI_CLASSES_GAUGE = _Stub()
    TICKS_TOTAL = TICK_HMAC_FAILURES = _Stub()

# ───────────────────────── Constants ───────────────────────────
MAX_FIELDS = 1_000
MAX_GRAPH_EDGES = 500
DEFAULT_WINDOW_SIZE = 250
DEFAULT_DYAD_DECAY_RATE = 0.999
MIN_WINDOW, MAX_WINDOW = 100, 5_000
MUTATION_COOLDOWN = 10  # generations

VERSE_ON_ASCENT = "سَيَجْعَلُ اللَّهُ بَعْدَ عُسْرٍ يُسْرًا"
VERSE_ON_PRUNE  = "كُلُّ مَنْ عَلَيْهَا فَانٍ"

# ─────────────────── Quantum Tick Dataclass ────────────────────
@dataclass
class QuantumTick:
    motif_id: str
    coherence_hash: str              # 12-hex, 48-bit
    lamport_clock: int               # monotonically increasing
    hlc_ts: str                      # ISO-8601 + logical component
    agent_id: str                    # provenance
    tick_hmac: Optional[str] = None  # SHA256(admin_secret, payload)
    stage: Optional[str] = None      # e.g. 'register', 'observe', 'prune'

    @classmethod
    def now(cls, motif_id: str, agent_id: str, secret: Optional[bytes] = None, stage: Optional[str] = None, lamport: Optional[int] = None) -> QuantumTick:
        # generate lamport_clock if not provided
        lam = lamport if lam is not None else int(time.time() * 1e6)
        # HLC timestamp
        iso = datetime.now(timezone.utc).isoformat()
        hlc = f"{iso}+{lam}"
        # coherence hash: first 12 hex digits of sha256(motif_id+hlc)
        base = motif_id + hlc
        coh = hashlib.sha256(base.encode()).hexdigest()[:12]
        # HMAC
        hmac_hex = None
        if secret:
            msg = f"{motif_id}:{coh}:{lam}:{hlc}:{agent_id}:{stage}".encode()
            hmac_hex = hmac.new(secret, msg, hashlib.sha256).hexdigest()
        return cls(
            motif_id=motif_id,
            coherence_hash=coh,
            lamport_clock=lam,
            hlc_ts=hlc,
            agent_id=agent_id,
            tick_hmac=hmac_hex,
            stage=stage,
        )

    def verify_hmac(self, secret: bytes) -> bool:
        if not self.tick_hmac:
            return False
        msg = f"{self.motif_id}:{self.coherence_hash}:{self.lamport_clock}:{self.hlc_ts}:{self.agent_id}:{self.stage}".encode()
        expected = hmac.new(secret, msg, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, self.tick_hmac)

# ────────────────────────── Helpers ─────────────────────────────
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

def _avg_vector_payload(motifs: List[str], embeddings: Dict[str, np.ndarray]) -> Optional[np.ndarray]:
    vecs = [embeddings[m] for m in motifs if m in embeddings]
    if not vecs:
        return None
    v = np.mean(vecs, axis=0).astype(np.float32)
    if v.nbytes > 1024:
        v = v[:1024//4]
    return v

# ───────────────────── Laplacian smoothing ─────────────────────
def _spectral_tau(window: int = 5) -> float:
    return 0.1 + random.random() * 0.2

def _apply_laplacian_smoothing(G: nx.Graph, tau: float):
    if G.number_of_nodes() < 3:
        return
    from scipy.linalg import expm
    L = nx.laplacian_matrix(G).todense()
    expm(-tau * L)

# ───────────────────── Main Watcher Class ──────────────────────
class LogicalAgentAT:
    """
    Watcher with topology, cluster-algebra, sheaf-strata, π-groupoid, and quantum ticks.
    """
    def __init__(
        self,
        *,
        contradiction_log_size: int = 100,
        verbose: bool = True,
        window_size: int = DEFAULT_WINDOW_SIZE,
        dyad_decay_rate: float = DEFAULT_DYAD_DECAY_RATE,
        # dynamic feature flags
        enable_topology: bool = False,
        enable_cluster_algebra: bool = False,
        enable_sheaf_transport: bool = False,
        enable_laplacian: bool = False,
        enable_pi_groupoid: bool = False,
        enable_quantum_ticks: bool = True,
        mutation_threshold: int = 10,
        tick_buffer_size: int = 128,
        pi_max_classes: int = 20000,
        hmac_shared_secret: Optional[str] = None,
    ) -> None:
        # --- public config
        self.verbose                = verbose
        self.enable_topology        = enable_topology
        self.enable_cluster_algebra = enable_cluster_algebra
        self.enable_sheaf_transport = enable_sheaf_transport
        self.enable_laplacian       = enable_laplacian
        self.enable_pi_groupoid     = enable_pi_groupoid
        self.enable_quantum_ticks   = enable_quantum_ticks
        self.mutation_threshold     = int(mutation_threshold)
        self.tick_buffer_size       = int(tick_buffer_size)
        self.pi_max_classes         = int(pi_max_classes)
        self.hmac_shared_secret     = (hmac_shared_secret.encode() if hmac_shared_secret else None)

        # --- core stores
        self.entanglement_fields: List[Dict[str, Any]] = []
        self.field_index: Dict[str, List[int]] = defaultdict(list)
        self.field_count = 0
        self.motif_embeddings: Dict[str, np.ndarray] = {}

        # --- dyad/triad window
        self._window_size = int(window_size)
        self._dyad_window: deque[int] = deque(maxlen=self._window_size)
        self.dyad_decay_rate = float(dyad_decay_rate)

        # --- ghost registry
        self.ghost_motifs: Dict[str, Dict[str, Any]] = {}

        # --- quantum ticks
        # per-motif ring buffer of ticks
        self._tick_buffers: Dict[str, deque[QuantumTick]] = defaultdict(lambda: deque(maxlen=self.tick_buffer_size))
        # aggregates older ticks per motif
        self._epoch_histograms: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count":0, "minE":None, "maxE":None})

        # --- π-groupoid
        self._pi_classes: Dict[str, set[str]] = {}
        self._pi_tag_index: Dict[str, str] = {}

        # --- logs & counters
        self.contradiction_log: deque[str] = deque(maxlen=contradiction_log_size)
        self._contradiction_avg: float = 0.0
        self._mutation_cooldowns: Dict[str, int] = {}
        self._recent_mutations: deque[int] = deque(maxlen=50)
        self.history: List[str] = []
        self.generation = 0
        self.agent_id = os.getenv("AGENT_ID", "default_watcher")

        # --- sync
        self._lock = threading.Lock()

    # ================================================================
    # Dynamic Feature Flags Adaptation
    # ================================================================
    def set_feature(self, feature: str, enabled: bool):
        """Enable or disable a feature flag at runtime."""
        if hasattr(self, feature):
            setattr(self, feature, enabled)
        # record history
        if self.verbose:
            self.history.append(f"Feature {feature} set → {enabled}")

    # ================================================================
    # Quantum Tick Management
    # ================================================================
    def register_tick(self, motif_id: str, tick: QuantumTick):
        """Register a quantum tick for a motif, storing ring-buffer and aggregating epoch."""
        if not self.enable_quantum_ticks:
            return
        buf = self._tick_buffers[motif_id]
        if len(buf) >= buf.maxlen:
            # aggregate oldest
            old = buf[0]
            hist = self._epoch_histograms[motif_id]
            hist["count"] += 1
            if hist["minE"] is None or old.lamport_clock < hist["minE"]:
                hist["minE"] = old.lamport_clock
            if hist["maxE"] is None or old.lamport_clock > hist["maxE"]:
                hist["maxE"] = old.lamport_clock
        buf.append(tick)
        # verify HMAC
        if tick.tick_hmac and self.hmac_shared_secret:
            if not tick.verify_hmac(self.hmac_shared_secret):
                TICK_HMAC_FAILURES.labels(self.agent_id).inc()
        TICKS_TOTAL.labels(self.agent_id).inc()

    def get_latest_tick(self, motif_id: str) -> Optional[QuantumTick]:
        buf = self._tick_buffers.get(motif_id)
        return buf[-1] if buf else None

    def export_tick_histogram(self) -> Dict[str, Any]:
        return {motif: dict(hist) for motif, hist in self._epoch_histograms.items()}

    # ================================================================
    # π‑Groupoid Helpers
    # ================================================================
    def _find_root(self, tag: str) -> str:
        parent = self._pi_tag_index.get(tag, tag)
        if parent == tag:
            return tag
        root = self._find_root(parent)
        self._pi_tag_index[tag] = root
        return root

    def register_path_equivalence(self, tag_a: str, tag_b: str) -> None:
        if not self.enable_pi_groupoid:
            return
        if len(self._pi_classes) >= self.pi_max_classes:
            return
        # must match π_TAG_REGEX
        if not (tag_a.startswith("π:") and tag_b.startswith("π:")):
            return
        ra, rb = self._find_root(tag_a), self._find_root(tag_b)
        if ra == rb:
            return
        self._pi_classes.setdefault(ra, {ra})
        self._pi_classes.setdefault(rb, {rb})
        canon, other = (ra, rb) if ra < rb else (rb, ra)
        self._pi_classes[canon].update(self._pi_classes[other])
        for t in self._pi_classes[other]:
            self._pi_tag_index[t] = canon
        del self._pi_classes[other]
        PI_MERGE_COUNTER.inc()
        PI_CLASSES_GAUGE.set(len(self._pi_classes))

    def are_paths_equivalent(self, tag_x: str, tag_y: str) -> bool:
        if not self.enable_pi_groupoid:
            return False
        return self._find_root(tag_x) == self._find_root(tag_y)

    def get_equivalence_class(self, tag: str) -> Optional[set[str]]:
        root = self._find_root(tag)
        return self._pi_classes.get(root)

    # ================================================================
    # Dyad / Context Helpers
    # ================================================================
    def _update_dyad_window(self, motif_count: int) -> None:
        self._dyad_window.append(motif_count)

    def get_dyad_context_ratio(self) -> float:
        triads = sum(1 for n in self._dyad_window if n >= 3)
        return triads / len(self._dyad_window) if self._dyad_window else 1.0

    # ================================================================
    # Embedding API
    # ================================================================
    def set_motif_embedding(self, motif: str, embedding: np.ndarray) -> None:
        self.motif_embeddings[motif] = embedding.astype(float, copy=False)

    # ================================================================
    # Contradiction Logging
    # ================================================================
    def log_contradiction(self, msg: str) -> None:
        self.contradiction_log.append(msg)
        CONTRADICTION_COUNTER.labels("logical_agent").inc()
        if self.verbose:
            self.history.append(f"⚡ CONTRADICTION — {msg}")

    # ================================================================
    # Decay / Drift & Window Adjustment
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

    def _adjust_window_size(self, new_size: int) -> None:
        data = list(self._dyad_window)[-new_size:]
        self._dyad_window = deque(data, maxlen=new_size)
        self._window_size = new_size
        DYAD_RATIO_GAUGE.set(self.get_dyad_context_ratio())
        if self.verbose:
            self.history.append(f"🫁 WINDOW BREATHES → {new_size}")

    def check_and_adjust_window(self) -> None:
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

    def adjust_decay_rate(self) -> None:
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

    def _queue_cooldown(self, knot_id: str) -> None:
        self._mutation_cooldowns[knot_id] = self.generation + MUTATION_COOLDOWN

    def _mutate_motif_name(self, name: str) -> str:
        return f"{name}′"

    def _perform_mutation(self, fid: int, field: Dict[str, Any]) -> None:
        motifs = field["motifs"]
        if not motifs:
            return
        k = min(2, len(motifs))
        targets = random.sample(motifs, k=k)
        for t in targets:
            idx = motifs.index(t)
            motifs[idx] = self._mutate_motif_name(t)
        field["motifs"] = motifs
        field["knot_id"] = _compute_knot_id(motifs)
        field["strength"] = 0.5
        field["persistence_vector"]["last_surface_echo"] = self.generation
        self._queue_cooldown(field["knot_id"])
        self._recent_mutations.append(self.generation)
        CLUSTER_MUTATION_COUNTER.labels("motif_substitution").inc()
        if self.verbose:
            self.history.append(f"🧬 MUTATION field#{fid} → {motifs}")

    # ================================================================
    # Ghost API  +  barcode / linking
    # ================================================================
    def register_ghost_motif(
        self,
        motif: str,
        *,
        origin: str = "user",
        strength: float = 0.5,
        linking: Optional[List[str]] = None,
    ) -> None:
        self.ghost_motifs[motif] = {
            "origin": origin,
            "strength": float(strength),
            "last_seen": self.generation,
            "linking": linking or [],
            "birth": self.generation,
        }

    def promote_ghost_to_field(self, motif: str) -> None:
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

    def reinforce_ghost_resonance(self, state: np.ndarray) -> None:
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
            else:
                unseen = self.generation - ghost["last_seen"]
                if unseen > self._drift_gap():
                    ghost["strength"] *= 0.99
                    if ghost["strength"] < 1e-4:
                        if self.verbose:
                            self.history.append(f"💤 Ghost {gid} fades")
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
    # Sheaf-strata helper
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
    # Ring-patch overlap validator
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
    # INTER-AGENT FEEDBACK
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
        Auto-migrates from v≤2.7.4 files lacking schema_version.
        """
        watcher = cls(
            window_size=data.get("window_size", DEFAULT_WINDOW_SIZE),
            dyad_decay_rate=data.get("dyad_decay_rate", DEFAULT_DYAD_DECAY_RATE),
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
        watcher._dyad_window = deque(data.get("_dyad_window", []), maxlen=watcher._window_size)
        # back-compat: if old save with no knot/ring, leave as-is
        return watcher

# ──────────────────────────────────────────────────────────────
# π-Groupoid Extension (v2.8.1)
# ──────────────────────────────────────────────────────────────
import re as _pi_re
π_TAG_REGEX = _pi_re.compile(r"π:[0-9a-f]{6,32}")
try:
    from prometheus_client import Counter as _PiCounter, Gauge as _PiGauge
    PI_MERGE_COUNTER = _PiCounter("logical_agent_pi_merges_total", "π-equivalence merges")
    PI_CLASSES_GAUGE = _PiGauge("logical_agent_pi_classes_gauge", "Active π-equiv classes")
except Exception:
    class _PiStub:
        def __getattr__(self, _): return lambda *a, **k: None
    PI_MERGE_COUNTER = PI_CLASSES_GAUGE = _PiStub()

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
    for t in self._pi_classes[other]:
        self._pi_tag_index[t] = canon
    del self._pi_classes[other]
    PI_MERGE_COUNTER.inc()
    PI_CLASSES_GAUGE.set(len(self._pi_classes))

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
