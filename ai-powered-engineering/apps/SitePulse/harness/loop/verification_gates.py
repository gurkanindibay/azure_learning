"""Verification Gates for the SitePulse Loop Harness."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
from pathlib import Path


@dataclass
class GateResult:
    name: str
    passed: bool
    diagnostics: List[str]


class SyntaxGate:
    def verify(self, file_path: Path) -> GateResult:
        if not file_path.exists():
            return GateResult(name="SyntaxGate", passed=False, diagnostics=[f"File not found: {file_path}"])
        content = file_path.read_text(encoding="utf-8")
        
        # Check basic syntax / balance brackets
        open_braces = content.count("{")
        close_braces = content.count("}")
        if open_braces != close_braces:
            return GateResult(
                name="SyntaxGate",
                passed=False,
                diagnostics=[f"Mismatched curly braces in {file_path.name}: {open_braces} open vs {close_braces} close"]
            )
        return GateResult(name="SyntaxGate", passed=True, diagnostics=[])


class FinancialIntegrityGate:
    """Enforces KMK Article 20 and strict Decimal arithmetic (zero float precision leaks)."""

    def verify_delay_penalty(self, principal: Decimal, days_overdue: int, calculated_total: Decimal) -> GateResult:
        """
        KMK Rule: 5% monthly delay compensation, pro-rated daily.
        Delay = Principal * 0.05 * (days_overdue / 30)
        """
        monthly_rate = Decimal("0.05")
        days = Decimal(str(days_overdue))
        expected_penalty = (principal * monthly_rate * (days / Decimal("30"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        expected_total = (principal + expected_penalty).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if calculated_total != expected_total:
            return GateResult(
                name="FinancialIntegrityGate",
                passed=False,
                diagnostics=[
                    f"Financial mismatch! Principal: ₺{principal}, Days: {days_overdue}",
                    f"Expected Total: ₺{expected_total} (Penalty: ₺{expected_penalty})",
                    f"Calculated Total: ₺{calculated_total}",
                    f"Difference: ₺{calculated_total - expected_total}"
                ]
            )
        return GateResult(name="FinancialIntegrityGate", passed=True, diagnostics=[])

    def verify_expense_split(self, total_expense: Decimal, shares: List[Decimal]) -> GateResult:
        """Verifies that the sum of all unit shares exactly equals the total expense with 0 kuruş loss."""
        total_shares = sum(shares)
        if total_shares != total_expense:
            return GateResult(
                name="FinancialIntegrityGate",
                passed=False,
                diagnostics=[
                    f"Expense split mismatch! Total Expense: ₺{total_expense}, Sum of shares: ₺{total_shares}",
                    f"Rounding error discrepancy: ₺{total_shares - total_expense}"
                ]
            )
        return GateResult(name="FinancialIntegrityGate", passed=True, diagnostics=[])
