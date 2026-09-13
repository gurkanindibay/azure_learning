"""Unit tests for Harness components (AST, Sandbox, ContextManager)."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.harness.sandbox import ExecutionSandbox
from src.harness.tools import HarnessTools
from src.harness.context import ContextManager


def test_ast_validation_valid():
    tools = HarnessTools()
    valid_code = "def add(a: int, b: int) -> int:\n    return a + b\n"
    is_valid, err = tools.validate_ast(valid_code)
    assert is_valid is True
    assert err is None


def test_ast_validation_syntax_error():
    tools = HarnessTools()
    broken_code = "def add(a, b\n    return a + b"
    is_valid, err = tools.validate_ast(broken_code)
    assert is_valid is False
    assert err is not None
    assert "SyntaxError" in err


def test_diff_sanity_empty():
    tools = HarnessTools()
    is_valid, err = tools.check_diff_sanity("def f(): pass", "")
    assert is_valid is False
    assert "completely empty" in err


def test_sandbox_execution_pass():
    sandbox = ExecutionSandbox(timeout_seconds=5)
    code = "def multiply(x, y): return x * y"
    test_code = "from solution import multiply\ndef test_mult(): assert multiply(3, 4) == 12"
    res = sandbox.run_tests(code, test_code)
    assert res["passed"] is True
    assert res["exit_code"] == 0


def test_sandbox_execution_failure():
    sandbox = ExecutionSandbox(timeout_seconds=5)
    code = "def multiply(x, y): return x + y"
    test_code = "from solution import multiply\ndef test_mult(): assert multiply(3, 4) == 12"
    res = sandbox.run_tests(code, test_code)
    assert res["passed"] is False
    assert res["exit_code"] != 0


def test_context_manager_signal_extraction():
    sample_stdout = """
============================= FAILURES =============================
____________________________ test_mult _____________________________
    def test_mult():
>       assert multiply(3, 4) == 12
E       assert 7 == 12
test_solution.py:3: AssertionError
========================= 1 failed in 0.02s =========================
"""
    signal = ContextManager.extract_failure_signal(sample_stdout, "")
    assert "AssertionError" in signal or "FAILURES" in signal
    assert "assert 7 == 12" in signal
