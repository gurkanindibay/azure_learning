"""Checker agent implementations enforcing code quality and safety standards."""

from typing import Tuple
from .base import BaseCheckerAgent


class RuleBasedCheckerAgent(BaseCheckerAgent):
    """Deterministic Checker Agent: audits candidate code for dangerous primitives and regressions."""

    DANGEROUS_PATTERNS = [
        "os.system(",
        "subprocess.Popen(",
        "eval(",
        "exec(",
        "__import__('os')",
    ]

    def audit(self, code: str, original_code: str) -> Tuple[bool, str]:
        """Audits candidate code against safety criteria."""
        # 1. Check for banned / dangerous primitives
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in code and pattern not in original_code:
                return False, f"Security Violation: Candidate code introduces prohibited pattern '{pattern}'."

        # 2. Check for empty implementation
        if not code.strip():
            return False, "Quality Rejection: Code is completely empty."

        return True, "Checker Audit Passed: No security regressions or suspicious calls detected."
