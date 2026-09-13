"""Deterministic verification gates to tame stochastic agent generation."""

import re
from typing import Tuple, Optional
from ..state import VerificationResult
from ..harness.tools import HarnessTools
from ..harness.context import ContextManager


class VerifyGate:
    """A hard, non-negotiable verification gate combining AST, diff sanity, and test execution."""

    def __init__(self, tools: Optional[HarnessTools] = None):
        self.tools = tools or HarnessTools()

    def verify(self, original_code: str, candidate_code: str, test_code: str) -> VerificationResult:
        """Executes a multi-stage deterministic check on candidate code."""
        # 1. AST Syntax Gate
        ast_ok, ast_err = self.tools.validate_ast(candidate_code)
        if not ast_ok:
            return VerificationResult(
                passed=False,
                ast_valid=False,
                diff_valid=False,
                tests_passed=False,
                stderr=ast_err or "Syntax error",
                error_summary=f"AST Syntax Check Failed: {ast_err}",
            )

        # 2. Diff Sanity Gate
        diff_ok, diff_msg = self.tools.check_diff_sanity(original_code, candidate_code)
        if not diff_ok:
            return VerificationResult(
                passed=False,
                ast_valid=True,
                diff_valid=False,
                tests_passed=False,
                stderr=diff_msg,
                error_summary=f"Diff Sanity Check Failed: {diff_msg}",
            )

        # 3. Dynamic Test Sandbox Gate
        sandbox_res = self.tools.execute_in_sandbox(candidate_code, test_code)
        stdout = sandbox_res.get("stdout", "")
        stderr = sandbox_res.get("stderr", "")
        tests_passed = sandbox_res.get("passed", False)

        # Parse test metrics if available
        total_tests = 1
        failed_tests = 0 if tests_passed else 1
        
        # Regex search for pytest outcome line e.g. "1 failed, 2 passed in 0.05s"
        match = re.search(r'([0-9]+)\s+failed', stdout)
        if match:
            failed_tests = int(match.group(1))

        error_summary = ""
        if not tests_passed:
            error_summary = ContextManager.extract_failure_signal(stdout, stderr)

        return VerificationResult(
            passed=tests_passed,
            ast_valid=True,
            diff_valid=True,
            tests_passed=tests_passed,
            total_tests=total_tests,
            failed_tests=failed_tests,
            stdout=stdout,
            stderr=stderr,
            error_summary=error_summary,
        )
