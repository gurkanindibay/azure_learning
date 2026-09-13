"""5-Phase Self-Healing Loop Controller."""

from typing import Optional
from ..state import AgentState, Phase, IterationRecord, VerificationResult
from .gates import VerifyGate
from ..agents.base import BaseMakerAgent, BaseCheckerAgent
from ..agents.checker import RuleBasedCheckerAgent


class LoopController:
    """Controls the 5-phase iterative feedback loop."""

    def __init__(
        self,
        maker: BaseMakerAgent,
        checker: Optional[BaseCheckerAgent] = None,
        verify_gate: Optional[VerifyGate] = None,
    ):
        self.maker = maker
        self.checker = checker or RuleBasedCheckerAgent()
        self.verify_gate = verify_gate or VerifyGate()

    def step_discover(self, state: AgentState) -> AgentState:
        """Phase 1: Discover baseline state by running tests on initial code."""
        state.current_phase = Phase.DISCOVER
        initial_verif = self.verify_gate.verify(
            original_code=state.original_code,
            candidate_code=state.current_code,
            test_code=state.test_code,
        )
        state.latest_verification = initial_verif
        state.latest_diagnostic = initial_verif.error_summary or initial_verif.stderr
        return state

    def step_plan(self, state: AgentState) -> AgentState:
        """Phase 2: Formulate hypothesis and refactor strategy."""
        state.current_phase = Phase.PLAN
        plan = self.maker.generate_plan(state)
        state.latest_plan = plan
        return state

    def step_execute(self, state: AgentState) -> AgentState:
        """Phase 3: Execute candidate refactoring patch."""
        state.current_phase = Phase.EXECUTE
        new_code = self.maker.generate_patch(state)
        state.current_code = new_code
        return state

    def step_verify(self, state: AgentState) -> AgentState:
        """Phase 4: Run candidate code through deterministic verify gate and checker audit."""
        state.current_phase = Phase.VERIFY
        verif_result = self.verify_gate.verify(
            original_code=state.original_code,
            candidate_code=state.current_code,
            test_code=state.test_code,
        )
        
        # If unit tests & syntax passed, run checker audit
        if verif_result.passed:
            checker_ok, checker_msg = self.checker.audit(state.current_code, state.original_code)
            if not checker_ok:
                verif_result.passed = False
                verif_result.error_summary = checker_msg

        state.latest_verification = verif_result
        state.latest_diagnostic = verif_result.error_summary or verif_result.stderr

        # Record iteration history
        record = IterationRecord(
            iteration=state.iteration,
            plan=state.latest_plan,
            proposed_code=state.current_code,
            verification=verif_result,
            diagnostic_feedback=state.latest_diagnostic,
        )
        state.history.append(record)
        return state

    def step_iterate(self, state: AgentState) -> AgentState:
        """Phase 5: Evaluate loop continuation or transition to terminal states."""
        state.current_phase = Phase.ITERATE
        state.iteration += 1

        if state.latest_verification and state.latest_verification.passed:
            state.current_phase = Phase.DELIVER
            state.is_terminal = True
            state.delivery_report = f"Success: Solution verified after {state.iteration} iteration(s)."
        elif state.iteration >= state.max_iterations:
            state.current_phase = Phase.ESCALATE
            state.is_terminal = True
            state.delivery_report = (
                f"Escalation: Max retry budget ({state.max_iterations}) exhausted without passing tests.\n"
                f"Last error: {state.latest_diagnostic}"
            )
        else:
            # Continue to next iteration loop
            state.current_phase = Phase.PLAN

        return state
