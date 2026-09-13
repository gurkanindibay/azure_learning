"""Node functions for the refactoring state graph."""

from typing import Dict, Any
from ..state import AgentState, Phase
from ..loop.loop_controller import LoopController


class GraphNodes:
    """Encapsulates discrete node executions within the graph."""

    def __init__(self, controller: LoopController):
        self.controller = controller

    def triage_node(self, state: AgentState) -> AgentState:
        """Node 1: Evaluates initial baseline test status."""
        return self.controller.step_discover(state)

    def planner_node(self, state: AgentState) -> AgentState:
        """Node 2: Generates hypothesis and fix plan."""
        return self.controller.step_plan(state)

    def maker_node(self, state: AgentState) -> AgentState:
        """Node 3: Synthesizes candidate code patch."""
        return self.controller.step_execute(state)

    def verify_node(self, state: AgentState) -> AgentState:
        """Node 4: Deterministic verification gate."""
        return self.controller.step_verify(state)

    def diagnose_node(self, state: AgentState) -> AgentState:
        """Node 5: Distills errors, updates iteration count, prunes context."""
        return self.controller.step_iterate(state)

    def deliver_node(self, state: AgentState) -> AgentState:
        """Terminal Node: Successful delivery."""
        state.current_phase = Phase.DELIVER
        state.is_terminal = True
        return state

    def escalate_node(self, state: AgentState) -> AgentState:
        """Terminal Node: Escalation to human engineer."""
        state.current_phase = Phase.ESCALATE
        state.is_terminal = True
        return state
