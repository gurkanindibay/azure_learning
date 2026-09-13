"""Evaluation runner executing agentic benchmarks and computing reliability metrics."""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.state import AgentState, Phase
from src.harness.sandbox import ExecutionSandbox
from src.harness.tools import HarnessTools
from src.loop.gates import VerifyGate
from src.loop.loop_controller import LoopController
from src.graph.engine import RefactorGraphEngine
from src.agents.maker import HeuristicMakerAgent, BaseMakerAgent
from src.agents.checker import RuleBasedCheckerAgent


class BenchmarkRunner:
    """Discovers test fixtures, runs the agentic pipeline, and calculates evals metrics."""

    def __init__(self, fixtures_dir: Path, maker_agent: Optional[BaseMakerAgent] = None):
        self.fixtures_dir = fixtures_dir
        self.maker = maker_agent or HeuristicMakerAgent()
        self.checker = RuleBasedCheckerAgent()
        self.sandbox = ExecutionSandbox(timeout_seconds=5)
        self.tools = HarnessTools(self.sandbox)
        self.verify_gate = VerifyGate(self.tools)
        self.controller = LoopController(self.maker, self.checker, self.verify_gate)
        self.engine = RefactorGraphEngine(self.controller)

    def run_all(self) -> Dict[str, Any]:
        fixtures = sorted([d for d in self.fixtures_dir.iterdir() if d.is_dir()])
        total = len(fixtures)
        results: List[Dict[str, Any]] = []

        pass_at_1 = 0
        pass_at_3 = 0
        escalated = 0

        print(f"\n🚀 Running Agentic Refactor Benchmarks across {total} test fixtures...\n")
        print(f"{'FIXTURE ID':<25} | {'STATUS':<10} | {'ITERS':<6} | {'TIME (s)':<8} | {'PASS@1':<6}")
        print("-" * 65)

        for fix in fixtures:
            sol_file = fix / "solution.py"
            test_file = fix / "test_solution.py"

            if not sol_file.exists() or not test_file.exists():
                continue

            orig_code = sol_file.read_text(encoding="utf-8")
            test_code = test_file.read_text(encoding="utf-8")

            state = AgentState(
                task_id=fix.name,
                file_path=str(sol_file),
                test_path=str(test_file),
                original_code=orig_code,
                current_code=orig_code,
                test_code=test_code,
                max_iterations=3,
            )

            start_t = time.time()
            final_state = self.engine.run(state)
            duration = round(time.time() - start_t, 3)

            is_success = final_state.current_phase == Phase.DELIVER
            iters = final_state.iteration
            p1 = is_success and iters <= 1

            if is_success:
                pass_at_3 += 1
                if p1:
                    pass_at_1 += 1
            else:
                escalated += 1

            status_str = "PASSED" if is_success else "ESCALATED"
            p1_str = "YES" if p1 else "NO"
            print(f"{fix.name:<25} | {status_str:<10} | {iters:<6} | {duration:<8.3f} | {p1_str:<6}")

            results.append({
                "fixture": fix.name,
                "status": status_str,
                "iterations": iters,
                "duration_seconds": duration,
                "pass_at_1": p1,
                "trace_steps": len(self.engine.trace_log),
            })

        summary = {
            "total_benchmarks": total,
            "solved": pass_at_3,
            "pass_at_1_count": pass_at_1,
            "pass_at_1_pct": round((pass_at_1 / total) * 100, 1) if total else 0.0,
            "pass_at_3_count": pass_at_3,
            "pass_at_3_pct": round((pass_at_3 / total) * 100, 1) if total else 0.0,
            "escalated_count": escalated,
            "results": results,
        }

        print("-" * 65)
        print(f"📊 SUMMARY: Pass@1: {summary['pass_at_1_pct']}% | Pass@3: {summary['pass_at_3_pct']}% | Solved: {pass_at_3}/{total}\n")
        return summary


if __name__ == "__main__":
    fixtures_path = BASE_DIR / "benchmarks" / "fixtures"
    runner = BenchmarkRunner(fixtures_path)
    runner.run_all()
