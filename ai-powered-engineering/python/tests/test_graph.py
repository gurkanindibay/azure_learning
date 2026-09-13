"""Unit tests for Graph Engineering (RefactorGraphEngine transitions and termination)."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.state import AgentState, Phase
from src.loop.loop_controller import LoopController
from src.graph.engine import RefactorGraphEngine
from src.agents.maker import MockMakerAgent


def test_graph_fast_delivery_when_already_passing():
    code = "def greet(): return 'hello'"
    test_code = "from solution import greet\ndef test_g(): assert greet() == 'hello'"

    maker = MockMakerAgent()
    controller = LoopController(maker=maker)
    engine = RefactorGraphEngine(controller)

    state = AgentState(
        task_id="fast_pass",
        file_path="dummy.py",
        test_path="test_dummy.py",
        original_code=code,
        current_code=code,
        test_code=test_code,
    )

    final_state = engine.run(state)
    assert final_state.current_phase == Phase.DELIVER
    assert final_state.iteration == 0
    # Trace should only contain triage and deliver
    nodes_visited = [s["node"] for s in engine.trace_log]
    assert nodes_visited == ["triage", "deliver"]


def test_graph_escalation_on_budget_exhaustion():
    # Mock maker that constantly emits failing code
    failing_code = "def broken(): return False"
    test_code = "from solution import broken\ndef test_b(): assert broken() is True"

    maker = MockMakerAgent(scripted_responses=[failing_code, failing_code, failing_code])
    controller = LoopController(maker=maker)
    engine = RefactorGraphEngine(controller)

    state = AgentState(
        task_id="exhaust_budget",
        file_path="dummy.py",
        test_path="test_dummy.py",
        original_code=failing_code,
        current_code=failing_code,
        test_code=test_code,
        max_iterations=2,
    )

    final_state = engine.run(state)
    assert final_state.current_phase == Phase.ESCALATE
    assert final_state.iteration == 2
    assert final_state.delivery_report is not None
    assert "Escalation" in final_state.delivery_report
