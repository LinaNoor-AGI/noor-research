"""
recursive_agent_ft.py (v3.7.0)
------------------------------------------------------------
Symbolic flow agent with **entangled Gremlin curvature**, musical harmony,
adaptive thresholds, FieldAnchor poetry, ghost decay, latency‑aware depth
rebound, and full Prometheus observability.

Gremlin is now a per‑field continuous weight, not a global mode.
"""

from __future__ import annotations

__version__ = "3.7.0"

import math
import time
import hashlib
from collections import defaultdict, deque
from typing import List, Optional, Dict, Any

import numpy as np

# ─────────────────────────────────────────────────────────────────────
# Prometheus stubs / metrics
# ─────────────────────────────────────────────────────────────────────
try:
    from prometheus_client import Histogram, Gauge, Counter

    STEP_LATENCY_HIST = Histogram(
        "recursive_agent_step_latency_seconds", "entangled_step latency",
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5)
    )
    DEPTH_GAUGE = Gauge("recursive_agent_recursion_depth", "Current max_depth")
    DRIFT_COUNTER = Counter("recursive_agent_drift_total", "FieldAnchor / fallback recoveries")
    LATENCY_SPIKE_COUNTER = Counter("recursive_agent_latency_spikes_total", "Steps >0.1s")
    GREMLIN_MEAN_GAUGE = Gauge("recursive_agent_gremlin_mean", "Mean gremlin weight per cycle")
    GREMLIN_MAX_GAUGE = Gauge("recursive_agent_gremlin_max", "Max gremlin weight per cycle")
    GREMLIN_STD_GAUGE = Gauge("recursive_agent_gremlin_std", "Std dev of gremlin weights per cycle")
except Exception:
    class _Stub:
        def __getattr__(self, _): return lambda *a, **k: None
    STEP_LATENCY_HIST = DEPTH_GAUGE = DRIFT_COUNTER = LATENCY_SPIKE_COUNTER = _Stub()
    GREMLIN_MEAN_GAUGE = GREMLIN_MAX_GAUGE = GREMLIN_STD_GAUGE = _Stub()

from noor_fasttime_core import NoorFastTimeCore, QuantumNoorException
from logical_agent_at import LogicalAgentAT

# ─────────────────────────────────────────────────────────────────────
# Entangled Gremlin Helpers
# ─────────────────────────────────────────────────────────────────────

GREMLIN_NOISE_SCALE: float = 0.02        # σ for perturbation noise
DEFAULT_GREMLIN_DECAY_RATE: float = 0.98  # per‑step exponential decay


def apply_gremlin_perturbation(state: np.ndarray, gremlin_weight: float) -> np.ndarray:
    if gremlin_weight <= 0.01:
        return state
    sigma = GREMLIN_NOISE_SCALE * gremlin_weight
    noise = np.random.normal(0.0, sigma, size=state.shape)
    return state + noise


def dynamic_depth_jitter(path_fields: List[Dict[str, Any]]) -> int:
    if not path_fields:
        return 0
    g_arr = np.array([f.get("gremlin_weight", 0.0) for f in path_fields], dtype=float)
    avg_g = float(np.mean(g_arr))
    w = [max(avg_g/2.0, 0.0), 1.0, max(avg_g/2.0, 0.0)]
    return np.random.choice([-1, 0, 1], p=np.array(w)/sum(w))


def decay_gremlin_weights(fields: List[Dict[str, Any]], decay_rate: float = DEFAULT_GREMLIN_DECAY_RATE):
    for field in fields:
        gw = field.get("gremlin_weight")
        if gw is not None:
            field["gremlin_weight"] = gw * decay_rate


def export_gremlin_stats(fields: List[Dict[str, Any]]) -> Dict[str, float]:
    g_arr = np.array([f.get("gremlin_weight", 0.0) for f in fields], dtype=float)
    if g_arr.size == 0:
        return {"mean":0.0, "max":0.0, "std":0.0}
    return {"mean":float(g_arr.mean()), "max":float(g_arr.max()), "std":float(g_arr.std())}

# ─────────────────────────────────────────────────────────────────────
# harmony & helper utilities
# ─────────────────────────────────────────────────────────────────────

def _short_hash(s: str, length: int = 6) -> str:
    return hashlib.sha1(s.encode("utf-8", "replace")).hexdigest()[:length]


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a.flatten(), b.flatten()
    dot = float(np.dot(a, b))
    denom = (np.linalg.norm(a)*np.linalg.norm(b))+1e-12
    return dot/denom

_MAJOR_THIRD=0.5; _MINOR_THIRD=0.7071; _PERF_FIFTH=0.8660; _HARM_TOL=0.04

def _is_harmonic_triad(vecs: List[np.ndarray]) -> bool:
    vs=[v for v in vecs if np.linalg.norm(v)>1e-9][:3]
    if len(vs)<3: return False
    sims=[_cos(vs[i],vs[j]) for i in range(3) for j in range(i+1,3)]
    return any(abs(s-t)<_HARM_TOL for s in sims for t in (_MAJOR_THIRD,_MINOR_THIRD,_PERF_FIFTH))

# ─────────────────────────────────────────────────────────────────────
class RecursiveAgentFT:
    """Symbolic flow agent with entangled Gremlin curvature and harmony sensing."""

    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]]|None=None,
        *,
        environment: Optional[np.ndarray]=None,
        state_dim: int=2,
        name: str="RecursiveAgentFT_v3.7.0",
        max_depth: int=2,
        enable_synergy_normalization: bool=True,
        enable_internal_time_decay: bool=True,
        gate0_dyad_penalty: float=0.95,
        meta_promote_threshold: int=3,
        ghost_promote_threshold: int=5,
        verbose: bool=True,
        enable_harmony: bool=True,
    ) -> None:
        if not 1<=max_depth<=5:
            raise ValueError("max_depth must be between 1 and 5")
        self.version=__version__
        self.name=name
        self.state_dim=state_dim
        self.environment=environment
        self.max_depth=max_depth
        self.enable_synergy_normalization=enable_synergy_normalization
        self.enable_internal_time_decay=enable_internal_time_decay
        self.gate0_dyad_penalty=gate0_dyad_penalty
        self.meta_promote_threshold=meta_promote_threshold
        self.ghost_promote_threshold=ghost_promote_threshold
        self.verbose=verbose
        self.enable_harmony=enable_harmony

        self.core=NoorFastTimeCore(initial_state=initial_state)
        self.watchers=watchers or []
        self.time_step=0
        self.synergy_memory: Dict[str,float]={}
        self.traversal_memory: List[Dict[str,Any]]=[]
        self._harm_hit_window: deque[int]=deque(maxlen=100)
        self._last_latency_spike: Optional[int]=None
        self._saved_depth: Optional[int]=None
        self._enforce_agent_boundary()

    def entangled_step(self) -> None:
        start=time.perf_counter()

        # gather context
        fields=[f for w in self.watchers for f in w.entanglement_fields]
        watcher_ctx=[w.get_dyad_context_ratio() for w in self.watchers]
        ctx_ratio=max(0.1, np.mean(watcher_ctx) if watcher_ctx else 1.0)

        # dynamic thresholds
        if self.time_step%25==0:
            # thresholds unchanged here; future: scale by gremlin stats
            pass

        richness_sigma=np.std(list(self.synergy_memory.values()) or [0.0])
        self.max_depth= max(2, min(5, self.max_depth))

        self.core.update_context_ratio(ctx_ratio)

        # choose next state
        if not fields:
            chosen_state,synergy,path=self._fallback_step(),0.0,[]
        else:
            all_paths=self.generate_field_paths(fields,self.max_depth)
            best=-np.inf;chosen_state=None;path=[]
            for p in all_paths:
                cand=self._build_state_with_gremlin(p)
                score=self._score_candidate(cand,p,watcher_ctx,ctx_ratio)
                if score>best:
                    best,chosen_state,path=score,cand,p
            synergy=best; path=path
            self.core.futures=[self._build_state_with_gremlin(p) for p in all_paths]

        # dyad penalty
        dyad_penalty=self._compute_dyad_penalty(path,watcher_ctx,ctx_ratio)
        if self.core.gate_overlay==0:
            dyad_penalty=(dyad_penalty+self.gate0_dyad_penalty)/2.0
        synergy=min(synergy*dyad_penalty,10.0)

        # core step & observe
        self.core.step(chosen_state)
        self.time_step+=1
        for w in self.watchers:
            w.observe_state(chosen_state)
            decay_gremlin_weights(w.entanglement_fields)

        # harmonic drought
        if path and _is_harmonic_triad([self._field_vector(f) for f in path]):
            self._harm_hit_window.append(1)
        else:
            self._harm_hit_window.append(0)
        if len(self._harm_hit_window)==self._harm_hit_window.maxlen and sum(self._harm_hit_window)==0 and self.verbose:
            event="|🎻 harmony_drought"
        else:
            event=None

        sig=self.path_signature(path)
        self.synergy_memory[sig]=self.synergy_memory.get(sig,0.0)+math.tanh(synergy)

        # record metrics
        stats=export_gremlin_stats(fields)
        GREMLIN_MEAN_GAUGE.set(stats["mean"]);
        GREMLIN_MAX_GAUGE.set(stats["max"]);
        GREMLIN_STD_GAUGE.set(stats["std"]);

        # depth jitter for next cycle
        jitter=dynamic_depth_jitter(path)
        if jitter!=0:
            nd=self.max_depth+jitter
            self.max_depth=max(2,min(5,nd))
        DEPTH_GAUGE.set(self.max_depth)

        # finalize step record
        step_rec={"time_step":self.time_step,"synergy":synergy,
                  "dyad_penalty":dyad_penalty,"chosen_path":[f.get("index",-1) for f in path],
                  "event":event}
        # latency
        latency=time.perf_counter()-start
        STEP_LATENCY_HIST.observe(latency)
        if latency>0.1:
            LATENCY_SPIKE_COUNTER.inc()
            if self._saved_depth is None:
                self._saved_depth=self.max_depth
            self.max_depth=max(2,self.max_depth-1)
            self._last_latency_spike=self.time_step
            DEPTH_GAUGE.set(self.max_depth)
            step_rec["alert"]="⚠️ latency_spike"
        self.traversal_memory.append(step_rec)

    # ------------------------------------------------------------------
    # State builders & scorers
    # ------------------------------------------------------------------
    def _build_state_with_gremlin(self, fields: List[Dict[str,Any]]) -> np.ndarray:
        state=self.core.current_state.copy()
        for field in fields:
            weight=field.get("strength",1.0)
            gremlin=field.get("gremlin_weight",0.0)
            vec=self._field_vector(field)
            if np.linalg.norm(vec)<1e-10:
                vec=np.random.normal(0,0.01,self.state_dim); vec/=np.linalg.norm(vec)+1e-10
            state+=vec*weight
            state=apply_gremlin_perturbation(state,gremlin)
            if self.environment is not None:
                state+=self.environment*0.01*(1.0+gremlin)
        # harmony
        if _is_harmonic_triad([self._field_vector(f) for f in fields]):
            state*=1.10
            gid=f"harmonic_{_short_hash(self.path_signature(fields))}"
            for w in self.watchers:
                if gid not in w.ghost_motifs:
                    w.register_ghost_motif(gid,origin="harmonic_resonance",strength=0.1)
        return state

    def _score_candidate(self, cand: np.ndarray, fields: List[Dict[str,Any]], watcher_ctx: List[float], default_ctx: float) -> float:
        score=float(np.linalg.norm(cand))+1.0
        sig=self.path_signature(fields)
        if self.enable_synergy_normalization:
            score+=math.tanh(self.synergy_memory.get(sig,0.0))
        if self.enable_internal_time_decay:
            decay=sum(f.get("internal_time",0.0) for f in fields)
            score*=math.exp(-decay)
        penalty=self._compute_dyad_penalty(fields, watcher_ctx, default_ctx)
        score*=penalty
        score*=np.mean([self._clamp_priority(f.get("priority_weight",1.0)) for f in fields])
        return score

    def _fallback_step(self)->np.ndarray:
        fallback=np.random.normal(0,0.05,self.state_dim)
        return fallback/(np.linalg.norm(fallback)+1e-10)

    def _compute_dyad_penalty(self, fields:List[Dict[str,Any]], watcher_ctx:List[float], default_ctx:float) -> float:
        dyad=sum(1 for f in fields if f.get("dyad_flag"))
        total=len(fields)
        if not total: return 1.0
        ratio=dyad/total
        ctx=np.mean(watcher_ctx) if watcher_ctx else default_ctx
        pen=1.0-ratio*(0.5+0.5*(1-ctx))
        return max(0.5,pen)

    def _field_vector(self, field: Dict[str,Any]) -> np.ndarray:
        motifs=field.get("motifs",[])
        if not motifs: return np.zeros(self.state_dim)
        vecs=[np.random.normal(0,0.01,self.state_dim) for _ in motifs]
        return sum(vecs)/len(vecs)

    def path_signature(self, fields:List[Dict[str,Any]])->str:
        ids=[str(f.get("index",id(f))) for f in fields]
        return _short_hash("|".join(ids))

    def _clamp_priority(self,p:float)->float:
        return max(0.5,min(1.5,p))

    def _enforce_agent_boundary(self):
        if self.state_dim<1 or self.state_dim>512:
            raise QuantumNoorException("Invalid state dimension.")

    def cache_field_anchor(self)->None:
        if hasattr(self.core,"save_field_anchor"):
            self.core.save_field_anchor()

    def restore_field_anchor(self)->bool:
        if hasattr(self.core,"restore_from_anchor"):
            self.core.restore_from_anchor(); return True
        return False

# End of RecursiveAgentFT v3.7.0
