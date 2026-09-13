"""Command Line Interface for running PatchMaster Agent."""

import sys
import argparse
from pathlib import Path

# Add package root to sys.path
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE_ROOT))

from src.state import AgentState, Phase
from src.harness.sandbox import ExecutionSandbox
from src.harness.tools import HarnessTools
from src.loop.gates import VerifyGate
from src.loop.loop_controller import LoopController
from src.graph.engine import RefactorGraphEngine
from src.agents.maker import HeuristicMakerAgent, LLMMakerAgent
from src.agents.checker import RuleBasedCheckerAgent
from benchmarks.runner import BenchmarkRunner


def main():
    parser = argparse.ArgumentParser(description="PatchMaster: Self-Healing Agentic Refactoring Bot")
    parser.add_argument("--benchmark", action="store_true", help="Run the benchmark eval suite")
    parser.add_argument("--target", type=str, help="Path to Python source file to refactor")
    parser.add_argument("--test", type=str, help="Path to Pytest test file")
    parser.add_argument("--llm", action="store_true", help="Use live LLM (requires OPENAI_API_KEY or GEMINI_API_KEY)")
    parser.add_argument("--max-iter", type=int, default=3, help="Max retry iterations before escalation (default: 3)")

    args = parser.parse_args()

    if args.benchmark:
        fixtures_dir = PACKAGE_ROOT / "benchmarks" / "fixtures"
        runner = BenchmarkRunner(fixtures_dir)
        runner.run_all()
        return

    if not args.target or not args.test:
        parser.print_help()
        print("\nExample usage:")
        print("  python3 src/cli.py --benchmark")
        print("  python3 src/cli.py --target path/to/solution.py --test path/to/test_solution.py")
        sys.exit(1)

    target_path = Path(args.target)
    test_path = Path(args.test)

    if not target_path.exists() or not test_path.exists():
        print(f"Error: Target or test file not found ({args.target}, {args.test})")
        sys.exit(1)

    orig_code = target_path.read_text(encoding="utf-8")
    test_code = test_path.read_text(encoding="utf-8")

    maker = LLMMakerAgent() if args.llm else HeuristicMakerAgent()
    checker = RuleBasedCheckerAgent()
    sandbox = ExecutionSandbox(timeout_seconds=5)
    tools = HarnessTools(sandbox)
    verify_gate = VerifyGate(tools)
    controller = LoopController(maker, checker, verify_gate)
    engine = RefactorGraphEngine(controller)

    state = AgentState(
        task_id=target_path.stem,
        file_path=str(target_path),
        test_path=str(test_path),
        original_code=orig_code,
        current_code=orig_code,
        test_code=test_code,
        max_iterations=args.max_iter,
    )

    print(f"\n[PatchMaster] Starting refactor task for: {target_path.name}")
    print(f"[PatchMaster] Maker: {maker.__class__.__name__} | Max Iterations: {args.max_iter}\n")

    final_state = engine.run(state)

    print("\n" + "=" * 50)
    print(f"Final Status: {final_state.current_phase.value}")
    print(f"Iterations:   {final_state.iteration}/{final_state.max_iterations}")
    print(f"Report:       {final_state.delivery_report}")
    print("=" * 50)

    print("\nExecution Graph Trace:")
    for step in engine.trace_log:
        print(f"  Step {step['step_index']}: Node={step['node']:<12} Phase={step['phase']:<10} Duration={step['duration_ms']}ms")

    if final_state.current_phase == Phase.DELIVER:
        print("\nProposed Verified Solution:")
        print("-" * 40)
        print(final_state.current_code)
        print("-" * 40)


if __name__ == "__main__":
    main()
