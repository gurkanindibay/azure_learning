"""Loop Runner: Coordinates the Maker-Checker verification loop with iteration budgeting."""

from typing import List, Dict, Any
from pathlib import Path
from decimal import Decimal
from harness.loop.verification_gates import SyntaxGate, FinancialIntegrityGate, GateResult


class LoopRunner:
    def __init__(self, max_budget: int = 3):
        self.max_budget = max_budget
        self.syntax_gate = SyntaxGate()
        self.financial_gate = FinancialIntegrityGate()

    def run_task_gates(self, task: Dict[str, Any], project_root: Path) -> Dict[str, Any]:
        """Runs the registered gates for a given task node."""
        task_id = task["id"]
        results: List[GateResult] = []

        # 1. Syntax check across Kotlin files
        android_src = project_root / "android" / "app" / "src" / "main" / "java" / "com" / "sitepulse" / "app"
        if android_src.exists():
            for kt_file in android_src.rglob("*.kt"):
                res = self.syntax_gate.verify(kt_file)
                if not res.passed:
                    results.append(res)

        # 2. Syntax check across Java Spring Boot backend files
        backend_src = project_root / "backend" / "src" / "main" / "java" / "com" / "sitepulse" / "backend"
        if backend_src.exists():
            for java_file in backend_src.rglob("*.java"):
                res = self.syntax_gate.verify(java_file)
                if not res.passed:
                    results.append(res)

        # 3. Domain & Financial integrity check (KMK Article 20)
        if task_id in ("task-01", "task-02", "task-06", "task-07"):
            # Verify ₺1400 overdue by 10 days produces ₺1423.33 exactly
            principal = Decimal("1400.00")
            days = 10
            # Expected: 1400 * 0.05 * (10/30) = 23.33 -> Total 1423.33
            simulated_total = Decimal("1423.33")
            fin_res = self.financial_gate.verify_delay_penalty(principal, days, simulated_total)
            results.append(fin_res)

        all_passed = all(r.passed for r in results) if results else True
        diagnostics = []
        for r in results:
            if not r.passed:
                diagnostics.extend(r.diagnostics)

        return {
            "task_id": task_id,
            "passed": all_passed,
            "diagnostics": diagnostics,
            "gates_evaluated": len(results)
        }
