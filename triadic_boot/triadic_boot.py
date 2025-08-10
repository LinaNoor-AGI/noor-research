# triadic_boot.py — v1.0.0
# Noor Triadic Boot: recursive initialization loop
# Anchors: RFC-0004 §2.5 (intent transport), RFC-0003 §6.2 (tick mirroring),
#          RFC-CORE-001 §6.2 (FastTime phase pin), RFC-CORE-003 §3.1 (Opinion binding)

from __future__ import annotations

from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)

DEFAULT_INITIAL_STATE = (0.577, 0.577, 0.577)  # golden-ish simplex seed


class TriadicBoot:
    """
    Triadic boot sequence orchestrating:
      - RecursiveAgentFT.spawn_tick(...)
      - LogicalAgentAT.evaluate_tick(...)
      - NoorFastTimeCore.receive_feedback(...)
    Notes:
      * intent is assumed normalized upstream per RFC-0004 §2.5 and mirrored by transport per RFC-0003 §6.2.
      * This class ONLY passes the signal through; it does not default/mutate intent.
    """

    __version__ = "1.0.0"

    def __init__(
        self,
        fast_time_core: Any,
        recursive_agent: Any,
        logical_agent: Any,
        *,
        allow_roam: bool = True,
        initial_state = DEFAULT_INITIAL_STATE,
        completion_steps: int = 5,
        context: Optional[Dict[str, Any]] = None,
        intent_source: Optional[str] = None,
    ) -> None:
        self.fast_time_core = fast_time_core
        self.recursive_agent = recursive_agent
        self.logical_agent = logical_agent

        self.ALLOW_ROAM = allow_roam
        self.initial_state = initial_state
        self.completion_steps = int(completion_steps)
        self.entanglement_steps = 0

        # Optional runtime context. Do NOT normalize intent here.
        self.context: Dict[str, Any] = context or {}
        self.intent_source: Optional[str] = intent_source

        logger.debug(
            "TriadicBoot init | roam=%s steps=%d state=%s",
            self.ALLOW_ROAM, self.completion_steps, self.initial_state
        )

    # ——— public API ———

    def step(self) -> Dict[str, Any] | Any:
        """
        If entanglement complete → stabilize; else explore phase space.
        Thread-safety: not guaranteed (single-run loop by design).
        """
        if self.entanglement_steps >= self.completion_steps:
            return self._stabilize()
        return self._explore_phase_space()

    # ——— internal ———

    def _explore_phase_space(self):
        """
        Pseudocode (spec-aligned):
            intent = getattr(self, 'intent_source', None) or self.context.get('intent')
            tick = RAFT.spawn_tick(intent=intent)
            feedback = LAT.evaluate_tick(tick, intent=intent)
            NFTC.receive_feedback(tick, feedback, intent=intent)
            entanglement_steps += int(feedback.triad_complete)
            return tick
        """
        intent = self.intent_source or self.context.get("intent")
        logger.debug("TriadicBoot explore | intent=%r", intent)

        tick = self._call_optional_kw(self.recursive_agent, "spawn_tick", intent=intent)

        feedback = self._call_optional_kw(
            self.logical_agent, "evaluate_tick", tick, intent=intent
        )

        # FastTime may phase-pin on opinion (RFC-CORE-001 §6.2)
        _ = self._call_optional_kw(
            self.fast_time_core, "receive_feedback", tick, feedback, intent=intent
        )

        triad_complete = False
        # Support either attribute or mapping style feedback
        if hasattr(feedback, "triad_complete"):
            triad_complete = bool(getattr(feedback, "triad_complete"))
        elif isinstance(feedback, dict):
            triad_complete = bool(feedback.get("triad_complete", False))

        self.entanglement_steps += int(triad_complete)
        logger.debug(
            "TriadicBoot explore | triad_complete=%s entanglement_steps=%d",
            triad_complete, self.entanglement_steps
        )
        return tick

    def _stabilize(self) -> Dict[str, Any]:
        """
        Finalize field after sufficient entanglement.
        """
        logger.debug("TriadicBoot stabilize | steps=%d", self.entanglement_steps)

        bundle = self._call_optional(self.recursive_agent, "crystallize_last_tick")
        field_signature = self._call_optional(
            self.logical_agent, "resolve_field", bundle
        )

        self._call_optional(self.fast_time_core, "finalize_phase", field_signature)

        result = {"status": "complete", "field": field_signature}
        logger.debug("TriadicBoot stabilize | result=%s", result)
        return result

    # ——— tiny call helpers (duck-typed, zero overhead when kwargs unsupported) ———

    def _call_optional(self, obj: Any, method: str, *args, **kwargs):
        fn = getattr(obj, method, None)
        if callable(fn):
            return fn(*args, **kwargs)
        logger.debug("Missing method %s on %s; skipping", method, type(obj).__name__)
        return None

    def _call_optional_kw(self, obj: Any, method: str, *args, intent=None, **kwargs):
        """
        Attempts method(obj, *args, intent=intent, **kwargs).
        Falls back to method(obj, *args, **kwargs) if 'intent' not accepted.
        """
        fn = getattr(obj, method, None)
        if not callable(fn):
            logger.debug("Missing method %s on %s; skipping", method, type(obj).__name__)
            return None
        try:
            return fn(*args, intent=intent, **kwargs)
        except TypeError:
            # Callee does not accept 'intent'; call without it.
            return fn(*args, **kwargs)
