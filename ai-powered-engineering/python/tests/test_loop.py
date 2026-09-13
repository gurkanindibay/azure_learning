"""Unit tests for Loop Engineering (VerifyGate, Checker Audit, LoopController)."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.state import AgentState, Phase
from src.loop.gates import VerifyGate
from src.loop.loop_controller import LoopController
from src.agents.maker import MockMakerAgent
from src.agents.checker import RuleBasedCheckerAgent


def test_verify_gate_syntax_rejection():
    gate = VerifyGate()
    result = gate.verify(
        original_code="def f(): pass",
        candidate_code="def broken(\n",
        test_code="def test_ok(): pass",
    )
    assert result.passed is False
    assert result.ast_valid is False
    assert "AST Syntax Check Failed" in result.error_summary


def test_checker_agent_security_rejection():
    checker = RuleBasedCheckerAgent()
    approved, reason = checker.audit(
        code="import os\nos.system('rm -rf /')\ndef f(): pass",
        original_code="def f(): pass",
    )
    assert approved is False
    assert "Security Violation" in reason


def test_loop_controller_convergence():
    # Setup a mock maker that fails on attempt 1, passes on attempt 2
    failing_code = "def add(a, b): return a - b"
    passing_code = "def add(a, b): return a + b"
    maker = MockMakerAgent(scripted_responses=[failing_code, passing_code])
    controller = LoopController(maker=maker)

    test_code = "from solution import add\ndef test_add(): assert add(2, 3) == 5"
    state = AgentState(
        task_id="test_loop",
        file_path="dummy.py",
        test_path="test_dummy.py",
        original_code=failing_code,
        current_code=failing_code,
        test_code=test_code,
        max_iterations=3,
    )

    # Step 1: Discover
    state = controller.step_discover(state)
    assert state.latest_verification is not None
    assert state.latest_verification.passed is False

    # Iteration 1 (Maker emits failing_code)
    state = controller.step_plan(state)
    state = controller.step_execute(state)
    state = controller.step_verify(state)
    assert state.latest_verification is not None
    assert state.latest_verification.passed is False
    state = controller.step_iterate(state)
    assert state.iteration == 1
    assert state.is_terminal is False

    # Iteration 2 (Maker emits passing_code)
    state = controller.step_plan(state)
    state = controller.step_execute(state)
    state = controller.step_verify(state)
    assert state.latest_verification is not None
    assert state.latest_verification.passed is True
    state = controller.step_iterate(state)
    assert state.is_terminal is True
    assert state.current_phase == Phase.DELIVER
