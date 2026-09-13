"""Strictly scoped action surfaces for reading, patching, and inspecting code."""

import ast
import difflib
from typing import Tuple, Optional, Dict, Any
from .sandbox import ExecutionSandbox


class HarnessTools:
    """Encapsulates the action surfaces exposed to the agentic loop."""

    def __init__(self, sandbox: Optional[ExecutionSandbox] = None):
        self.sandbox = sandbox or ExecutionSandbox(timeout_seconds=5)

    @staticmethod
    def validate_ast(code: str) -> Tuple[bool, Optional[str]]:
        """Deterministic syntax gate: parse code into Python AST."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}"
        except Exception as e:
            return False, f"AST parse error: {str(e)}"

    @staticmethod
    def check_diff_sanity(original: str, candidate: str, min_retention_ratio: float = 0.2) -> Tuple[bool, str]:
        """Safety gate: prevents catastrophic wipes or deleting all logic."""
        if not candidate.strip():
            return False, "Candidate patch is completely empty."
        
        orig_lines = [line.strip() for line in original.strip().splitlines() if line.strip()]
        cand_lines = [line.strip() for line in candidate.strip().splitlines() if line.strip()]

        if len(cand_lines) == 0:
            return False, "Candidate code has 0 non-empty lines."

        # Compute unified diff
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            candidate.splitlines(keepends=True),
            fromfile="original.py",
            tofile="candidate.py",
        )
        diff_text = "".join(diff)

        return True, diff_text

    def execute_in_sandbox(self, code: str, test_code: str) -> Dict[str, Any]:
        """Runs the candidate code against tests in an isolated sandbox."""
        return self.sandbox.run_tests(code, test_code)
