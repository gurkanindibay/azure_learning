"""Graph Execution Engine: Orchestrates state transitions, routing, and termination."""

import time
from typing import List, Dict, Any, Optional
from ..state import AgentState, Phase
from ..loop.loop_controller import LoopController
from .nodes import GraphNodes


class RefactorGraphEngine:
    """Explicit state graph engine executing the self-healing workflow."""

    def __init__(self, controller: LoopController):
        self.controller = controller
        self.nodes = GraphNodes(controller)
        self.trace_log: List[Dict[str, Any]] = []

    def _log_step(self, node_name: str, state: AgentState, duration_ms: float):
        self.trace_log.append({
            "step_index": len(self.trace_log) + 1,
            "node": node_name,
            "phase": state.current_phase.value,
            "iteration": state.iteration,
            "is_terminal": state.is_terminal,
            "duration_ms": round(duration_ms, 2),
            "latest_diagnostic": state.latest_diagnostic[:150] if state.latest_diagnostic else "",
        })

    def run(self, state: AgentState) -> AgentState:
        """Executes the graph until a terminal node (DELIVER or ESCALATE) is reached."""
        self.trace_log.clear()

        # 1. Triage Node (Baseline check)
        t0 = time.time()
        state = self.nodes.triage_node(state)
        self._log_step("triage", state, (time.time() - t0) * 1000)

        if state.latest_verification and state.latest_verification.passed:
            # Code is already passing, nothing to fix
            t0 = time.time()
            state.delivery_report = "Initial code already satisfies all tests."
            state = self.nodes.deliver_node(state)
            self._log_step("deliver", state, (time.time() - t0) * 1000)
            return state

        # 2. Iterative Graph Execution
        while not state.is_terminal:
            # Planner
            t0 = time.time()
            state = self.nodes.planner_node(state)
            self._log_step("planner", state, (time.time() - t0) * 1000)

            # Maker
            t0 = time.time()
            state = self.nodes.maker_node(state)
            self._log_step("maker", state, (time.time() - t0) * 1000)

            # Verify Gate
            t0 = time.time()
            state = self.nodes.verify_node(state)
            self._log_step("verify_gate", state, (time.time() - t0) * 1000)

            # Conditional Routing Gate
            if state.latest_verification and state.latest_verification.passed:
                t0 = time.time()
                state.delivery_report = f"Success: Solution verified after {state.iteration} iteration(s)."
                state = self.nodes.deliver_node(state)
                self._log_step("deliver", state, (time.time() - t0) * 1000)
                break

            # Diagnose & Step Iteration
            t0 = time.time()
            state = self.nodes.diagnose_node(state)
            self._log_step("diagnose", state, (time.time() - t0) * 1000)

            if state.is_terminal:
                t0 = time.time()
                state = self.nodes.escalate_node(state)
                self._log_step("escalate", state, (time.time() - t0) * 1000)
                break

        return state
