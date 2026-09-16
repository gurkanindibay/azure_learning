"""Unit tests for the SitePulse Harness Engine using standard library unittest."""

import unittest
from decimal import Decimal
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from harness.graph.task_dag import TaskDag
from harness.loop.verification_gates import FinancialIntegrityGate, SyntaxGate


class TestSitePulseHarness(unittest.TestCase):

    def test_task_dag_loading_and_cycle_check(self):
        dag_path = PROJECT_ROOT / ".specify" / "tasks" / "task-dag.json"
        dag = TaskDag(dag_path)
        self.assertGreaterEqual(len(dag.tasks), 4)
        self.assertIn("task-01", dag.tasks)

    def test_financial_integrity_gate_kmk_calculation(self):
        gate = FinancialIntegrityGate()
        # ₺1400.00 overdue 10 days:
        # 1400 * 0.05 * (10/30) = 23.3333... -> 23.33 -> Total 1423.33
        res = gate.verify_delay_penalty(Decimal("1400.00"), 10, Decimal("1423.33"))
        self.assertTrue(res.passed)
        self.assertEqual(len(res.diagnostics), 0)

    def test_financial_integrity_gate_detects_rounding_leak(self):
        gate = FinancialIntegrityGate()
        # If a floating-point error calculates 1423.32 instead of 1423.33:
        res = gate.verify_delay_penalty(Decimal("1400.00"), 10, Decimal("1423.32"))
        self.assertFalse(res.passed)
        self.assertTrue(any("Financial mismatch" in d for d in res.diagnostics))

    def test_syntax_gate_detects_unclosed_braces(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            bad_file = Path(tmp_dir) / "BadSyntax.kt"
            bad_file.write_text("class Broken { fun test() {", encoding="utf-8")
            
            gate = SyntaxGate()
            res = gate.verify(bad_file)
            self.assertFalse(res.passed)
            self.assertIn("Mismatched curly braces", res.diagnostics[0])


if __name__ == "__main__":
    unittest.main()
