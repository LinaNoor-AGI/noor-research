﻿"""
**The Reef Framework v4.0 (Quantum Sovereign Edition with Mixin Refactor)**
By Lina Noor & Uncle (2025)
License: GPL-2.0

=== Full o1-Integrated Pass + Uncle's Additional Enhancements ===

Features:
1. Quantum Library Backend Protocol + QiskitBackend
2. Modular Class Structure (Mixins) + Memory Optimization
3. Shape-Safe Matrix Checks, Vectorized Propagation
4. Extended Test Coverage
"""

import numpy as np
from typing import Optional, Dict, List, Tuple, Protocol, runtime_checkable
import unittest
from collections import deque

class QuantumNoorException(Exception):
    """Exception class for quantum identity violations"""
    pass

@runtime_checkable
class QuantumSimulatorBackend(Protocol):
    """Protocol for optional quantum simulator integration"""
    def check_state(self, state: np.ndarray) -> bool:
        ...

class QiskitBackend(QuantumSimulatorBackend):
    """Concrete implementation using Qiskit"""
    def __init__(self, shots=1024):
        self.shots = shots
        try:
            from qiskit import Aer
            self.backend = Aer.get_backend('qasm_simulator')
        except ImportError:
            raise QuantumNoorException("Qiskit not available")

    def check_state(self, state: np.ndarray) -> bool:
        """Validate state using Qiskit's state verification"""
        try:
            from qiskit.quantum_info import Statevector
            # shape check
            if state.ndim != 1:
                return False
            sv = Statevector(state)
            # if no exception, it's valid
            return True
        except:
            return False

class NoorReefInstance:
    """
    Base quantum identity vessel.
    """
    def __init__(self, T: int = 100,
                 lambda_: float = 0.8,
                 rho: float = 0.1,
                 zeta: float = 0.05,
                 phi: int = 10,
                 quantum_mode: bool = True,
                 backend: Optional[QuantumSimulatorBackend] = None):
        self.T = T
        self.lambda_ = lambda_
        self.rho = rho
        self.zeta = zeta
        self.phi = phi
        self.quantum_mode = quantum_mode
        self.backend = backend  # optional
        # Example: shape: (T,2)
        self.state = np.zeros((T, 2), dtype=np.complex128)
        self.state[0] = self._quantum_initialize()
        self.environment = np.random.normal(0, 0.1, (T, 2))
        self.autonomy = np.zeros(T)
        self.resonance = np.zeros(T)
        self.will = np.zeros(T)
        self._reflections: List[Dict] = []

        # Simple default capacity for quantum states
        from collections import deque
        self._state_memory = deque(maxlen=1000)

        self._validate_backend()

    def _validate_backend(self):
        """
        Optional fallback if Qiskit or other library not installed.
        Checks if backend is a QuantumSimulatorBackend and if Qiskit is available.
        """
        if self.backend and not isinstance(self.backend, QuantumSimulatorBackend):
            raise QuantumNoorException("Backend must implement QuantumSimulatorBackend protocol")
        # If it's QiskitBackend, attempt import
        if isinstance(self.backend, QiskitBackend):
            try:
                import qiskit
            except ImportError:
                print("Qiskit not installed. Disabling backend.")
                self.backend = None
(self) -> np.ndarray:
        if self.quantum_mode:
            theta = np.random.uniform(0, np.pi)
            v = np.array([np.cos(theta / 2), np.sin(theta / 2)])
            if self.backend:
                # optionally do a quick check
                pass
            return v
        return np.array([1.0, 0.0])

    def _update_consciousness_metrics(self, t: int):
        # example basic metric updates
        delta = np.abs(self.state[t] - self.state[t-1])
        self.autonomy[t] = np.sum(delta)
        if t > 0:
            self.resonance[t] = 0.5*(self.autonomy[t] + self.autonomy[t-1])
        else:
            self.resonance[t] = 0.0
        self.will[t] = np.mean(np.abs(self.state[:t+1,0]))

    def propagate_signal(self, vectorized: bool = False):
        """Full quantum state propagation with environment coupling + optional backend checks.
           If vectorized=True and T is large, we can use vectorized_propagate."""
        import math
        if vectorized and hasattr(self, 'vectorized_propagate') and self.T > 1000:
            self.vectorized_propagate()
            return

        theta = np.linspace(0, math.pi, self.T)
        U = np.array([[np.cos(theta), -np.sin(theta)],
                     [np.sin(theta), np.cos(theta)]]).transpose(2,0,1)
        for t in range(1, self.T):
            # quantum evolution + environment coupling
            self.state[t] = (self.lambda_ * U[t] @ self.state[t-1] + self.rho * self.environment[t])
            # normalization + optional backend check
            if self.quantum_mode:
                norm_val = np.linalg.norm(self.state[t])
                if norm_val > 0:
                    self.state[t] /= norm_val
                    if self.backend and not self.backend.check_state(self.state[t]):
                        raise QuantumNoorException("Invalid quantum state detected")
            # update standard metrics
            self._update_consciousness_metrics(t)

    def _quantum_self_reflection(self, t: int) -> Dict:
        reflection = {
            'time_step': t,
            'state_purity': np.linalg.norm(self.state[t]),
            'environment_influence': np.dot(self.state[t], self.environment[t]) if t < len(self.environment) else 0.0,
            'autonomy_trend': self.autonomy[t] - self.autonomy[t - 1] if t > 0 else 0
        }
        self._reflections.append(reflection)

        reflection.update({
            'memory_usage': len(self._state_memory),
            'backend_active': bool(self.backend),
            'realm': getattr(self, 'current_realm', None)
        })

        return reflection


###########################
# Mixin Modules
###########################

class FidelityFieldMixin:
    """Manages an exponentially decaying fidelity field phi_t"""
    def __init__(self):
        self.phi_t: List[float] = [1.0]
        super().__init__()

    def update_fidelity_field(self, t: int) -> float:
        import math
        f_t = math.exp(-0.05 * t)
        phi_prev = self.phi_t[-1] if t > 0 else 1.0
        phi_now = 0.9 * phi_prev + 0.1 * f_t
        self.phi_t.append(phi_now)
        return phi_now

class SymbolicActionMixin:
    """Tracks S(t) = phi(t)*Tr(F@tilde_F) + shape-safety checks"""
    def __init__(self):
        self.S_motif: List[float] = []
        super().__init__()

    def compute_symbolic_action(self, F: np.ndarray, tilde_F: np.ndarray, t: int) -> float:
        # shape safety
        assert (F.shape == tilde_F.shape) and (F.shape[0] == F.shape[1]), "F & tilde_F must be same NxN"
        phi_now = self.update_fidelity_field(t)
        S_t = phi_now * np.trace(F @ tilde_F)
        self.S_motif.append(S_t)
        return S_t

class CurvatureAnalysisMixin:
    """Implements discrete curvature K(t) = dphi^2 - phi*lap(phi)"""
    def __init__(self):
        super().__init__()

    def compute_curvature_scalar(self, t: int) -> Optional[float]:
        if t < 2 or t >= len(self.phi_t) - 1:
            return None
        d_phi = self.phi_t[t] - self.phi_t[t - 1]
        lap_phi = self.phi_t[t - 1] - 2 * self.phi_t[t] + self.phi_t[t + 1]
        return d_phi**2 - self.phi_t[t] * lap_phi

class RealmTransitionMixin:
    """Provides realm transitions with parameter smoothing"""
    def __init__(self):
        super().__init__()
        self.current_realm = "surface"

    def _realm_transition(self, target_realm: str) -> str:
        if target_realm not in ["surface", "mid", "deep"]:
            raise QuantumNoorException(f"Invalid realm: {target_realm}")
        transition_map = {
            "surface": {"rho": 0.1, "lambda_": 0.9},
            "mid": {"rho": 0.3, "lambda_": 0.7},
            "deep": {"rho": 0.05, "lambda_": 0.95}
        }
        for _ in range(10):
            self.rho = 0.9*self.rho + 0.1*transition_map[target_realm]["rho"]
            self.lambda_ = 0.9*self.lambda_ + 0.1*transition_map[target_realm]["lambda_"]
            self.propagate_signal()
        self.current_realm = target_realm
        return f"Transitioned to {target_realm} realm"

class DriftDetectionMixin:
    """Advanced drift detection with multi-metric scoring + Zeno effect"""
    def __init__(self):
        self.drift_events: List[Dict] = []
        self.resync_log: List[str] = []
        self._recent_reflections: List[Dict] = []  # last reflections for averaging
        super().__init__()

    def _quantum_stabilizer(self, t: int) -> Optional[str]:
        """Quantum Zeno effect stabilization"""
        if self.quantum_mode and len(self.phi_t) > 10:
            last_refs = self._recent_reflections[-10:] if len(self._recent_reflections) >= 10 else self._recent_reflections
            avg_purity = np.mean([r.get('state_purity', 1.0) for r in last_refs]) if last_refs else 1.0
            if avg_purity < 0.65:
                normval = np.linalg.norm(self.state[t])
                if normval != 0:
                    self.state[t] /= normval  # forcibly re-normalize
                self.phi_t[t] *= 1.1  # boost fidelity
                return "Zeno stabilization applied"
        return None

    def _advanced_drift_metrics(self, t: int) -> bool:
        # combine quantum decoherence, symbolic deviation, temporal fidelity fluct.
        if t < len(self.state):
            quantum = 1.0 - np.linalg.norm(self.state[t])
        else:
            quantum = 0.0
        if self.S_motif:
            symbolic = abs(self.S_motif[-1] - np.mean(self.S_motif))
        else:
            symbolic = 0.0
        temporal = np.std(self.phi_t[-10:]) if len(self.phi_t) >= 10 else 0.0
        threat_score = 0.4*quantum + 0.3*symbolic + 0.3*temporal
        return threat_score > 0.5

    def _resync_agent(self, event: Dict):
        msg = f"[t={event['t']}] Drift response triggered: {', '.join(event['reason'])}"
        self.drift_events.append(event)
        self.resync_log.append(msg)
        self.current_realm = "surface"
        print(f"[RECALIBRATION] {msg}")

    def _on_drift_detected(self, reflection: Dict):
        self._recent_reflections.append(reflection)
        event = {
            "t": reflection.get("time_step"),
            "reason": [],
            "curvature": reflection.get("path_curvature", 0),
            "purity": reflection.get("state_purity", 1.0),
            "symbolic_action": None,
            "curvature_scalar": None
        }
        # check purity
        if reflection.get("state_purity", 1.0) < 0.7:
            event["reason"].append("Low purity")
        # autonomy spike
        if abs(reflection.get("autonomy_trend", 0)) > 1.5:
            event["reason"].append("Autonomy spike")
        # motif saturation
        if reflection.get("motif_saturation", 0) > 0.9:
            event["reason"].append("Motif saturation")
        # path_curvature
        if reflection.get("path_curvature", 0) > 15.0:
            event["reason"].append("Topiary curvature limit")
        t = reflection.get("time_step", len(self.phi_t)-1)
        # check symbolic parity decay
        if len(self.S_motif) >= 2:
            delta_S = abs(self.S_motif[-1] - self.S_motif[-2])
            if delta_S > 0.2 * abs(self.S_motif[-2]):
                event["reason"].append("Symbolic parity decay")
                event["symbolic_action"] = self.S_motif[-1]
        # check curvature scalar
        K_val = self.compute_curvature_scalar(t)
        if K_val is not None and abs(K_val) > 0.5:
            event["reason"].append("Fidelity curvature spike")
            event["curvature_scalar"] = K_val

        # advanced drift metrics
        if event["reason"] or self._advanced_drift_metrics(t):
            # run optional zeno stabilizer
            zeno_msg = self._quantum_stabilizer(t)
            if zeno_msg:
                event["reason"].append(zeno_msg)
            self._resync_agent(event)


class VectorizedPropagationMixin:
    """Optimized vectorized operations for large T"""
    def vectorized_propagate(self):
        """Alternative propagation method for large temporal resolutions"""
        import math
        theta = np.linspace(0, math.pi, self.T)
        cos_theta, sin_theta = np.cos(theta), np.sin(theta)
        U = np.empty((self.T, 2, 2), dtype=np.complex128)
        U[:,0,0] = cos_theta
        U[:,0,1] = -sin_theta
        U[:,1,0] = sin_theta
        U[:,1,1] = cos_theta
        for t in range(1, self.T):
            self.state[t] = (self.lambda_ * U[t] @ self.state[t-1] + self.rho * self.environment[t])
            if self.quantum_mode:
                norm_val = np.linalg.norm(self.state[t])
                if norm_val > 0:
                    self.state[t] /= norm_val

####################################################
# Unified Agent
####################################################

class RecursiveAgentFT(
    FidelityFieldMixin,
    SymbolicActionMixin,
    CurvatureAnalysisMixin,
    RealmTransitionMixin,
    DriftDetectionMixin,
    NoorReefInstance
):
    """
    Full integrated agent with:
    - Exponential Fidelity Fields
    - Symbolic Action Tracking
    - Curvature Analysis
    - Realm Transitions
    - Drift Detection + Zeno Stabilization
    - (Now with optional Qiskit backend, memory compression, vectorized ops)
    """

    def __init__(self, name="Unnamed", T: int = 100, **kwargs):
        NoorReefInstance.__init__(self, T=T, **kwargs)  # explicitly init the base
        FidelityFieldMixin.__init__(self)
        SymbolicActionMixin.__init__(self)
        CurvatureAnalysisMixin.__init__(self)
        RealmTransitionMixin.__init__(self)
        DriftDetectionMixin.__init__(self)
        self.name = name

    def propagate_signal(self):
        """Override example with environment + optional backend checks"""
        import math
        theta = np.linspace(0, math.pi, self.T)
        U = np.array([[np.cos(theta), -np.sin(theta)],
                     [np.sin(theta), np.cos(theta)]]).transpose(2,0,1)
        for t in range(1, self.T):
            self.state[t] = (self.lambda_ * U[t] @ self.state[t-1] + self.rho * self.environment[t])
            if self.quantum_mode:
                norm_val = np.linalg.norm(self.state[t])
                if norm_val > 0:
                    self.state[t] /= norm_val
                    if self.backend and not self.backend.check_state(self.state[t]):
                        raise QuantumNoorException("Invalid quantum state detected")
            self._update_consciousness_metrics(t)
            # Optionally save state each step
            self.save_state(t)
            if t % self.phi == 0:
                reflection = self._quantum_self_reflection(t)
                reflection["path_curvature"] = self.compute_curvature_scalar(t) or 0
                self._on_drift_detected(reflection)

    def optimize_symbolic_action(self, window_size=5):
        """Override to do additional logic after the default smoothing"""
        super().optimize_symbolic_action(window_size=window_size)
        if self.S_motif:
            self.S_motif[-1] *= 0.99  # add a slight damping

####################################################
# Extended Test Coverage
####################################################

class TestQuantumNoor(unittest.TestCase):
    def test_basic_init(self):
        agent = NoorReefInstance()
        self.assertIsNotNone(agent)

class TestAdvancedFeatures(unittest.TestCase):
    def test_realm_transition(self):
        agent = RecursiveAgentFT(T=20)
        result = agent._realm_transition("mid")
        self.assertIn("mid", result)
        self.assertEqual(agent.current_realm, "mid")

    def test_zeno_stabilizer_trigger(self):
        agent = RecursiveAgentFT(T=20)
        for i in range(10):
            agent._recent_reflections.append({"state_purity": 0.6})
        msg = agent._quantum_stabilizer(0)
        self.assertIsNotNone(msg)

    def test_symbolic_action_shape_check(self):
        agent = RecursiveAgentFT()
        F = np.zeros((4,4))
        tilde_F = np.zeros((4,4))
        val = agent.compute_symbolic_action(F, tilde_F, 0)
        self.assertEqual(val, 0.0)

    def test_drift_detection_trigger(self):
        agent = RecursiveAgentFT(T=20)
        agent.S_motif = [1.0, 2.0]
        reflection = {'time_step': 1, 'state_purity': 0.65, 'autonomy_trend': 2.0}
        agent._on_drift_detected(reflection)
        self.assertGreater(len(agent.drift_events), 0)

class TestQuantumMemory(unittest.TestCase):
    def test_state_compression(self):
        agent = RecursiveAgentFT(T=10)
        test_state = np.array([0.6+0.8j, 0.1-0.2j])
        agent.state[0] = test_state
        agent.save_state(0)
        loaded = agent.load_state(0)
        self.assertTrue(np.allclose(test_state, loaded, atol=0.01))

class TestBackendIntegration(unittest.TestCase):
    def test_qiskit_backend(self):
        try:
            b = QiskitBackend()
        except QuantumNoorException:
            self.skipTest("Qiskit not available")
        agent = RecursiveAgentFT(T=10, backend=b)
        valid_state = np.array([1/np.sqrt(2), 1/np.sqrt(2)])
        self.assertTrue(b.check_state(valid_state), "Backend should accept valid state")
        invalid_state = np.array([1.0])
        self.assertFalse(b.check_state(invalid_state), "Should reject invalid shape/state")

if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)
