#!/usr/bin/env python3
"""SitePulse Harness CLI: Graph scheduler & Loop verification runner."""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from harness.graph.task_dag import TaskDag
from harness.loop.loop_runner import LoopRunner


def main():
    parser = argparse.ArgumentParser(description="SitePulse Engineering Harness")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Command: status
    subparsers.add_parser("status", help="Show the current Task DAG status")

    # Command: next
    subparsers.add_parser("next", help="Get next runnable tasks in the DAG")

    # Command: verify
    verify_parser = subparsers.add_parser("verify", help="Run verification gates on a task")
    verify_parser.add_argument("--task", required=True, help="Task ID (e.g. task-01)")

    args = parser.parse_args()

    dag_path = PROJECT_ROOT / ".specify" / "tasks" / "task-dag.json"
    if not dag_path.exists():
        print(f"Error: task-dag.json not found at {dag_path}")
        sys.exit(1)

    dag = TaskDag(dag_path)

    if args.command == "status":
        print(dag.render_ascii())

    elif args.command == "next":
        runnable = dag.get_runnable_tasks()
        if not runnable:
            print("No runnable tasks found (all completed or blocked by dependencies).")
        else:
            print(f"Found {len(runnable)} runnable task(s):")
            for t in runnable:
                print(f"  ⚡ {t['id']}: {t['name']} (Spec: {t.get('spec_ref')})")

    elif args.command == "verify":
        task_id = args.task
        if task_id not in dag.tasks:
            print(f"Error: Unknown task {task_id}")
            sys.exit(1)

        task = dag.tasks[task_id]
        print(f"Running verification loop for [{task_id}] {task['name']}...")
        runner = LoopRunner(max_budget=3)
        res = runner.run_task_gates(task, PROJECT_ROOT)

        if res["passed"]:
            print(f"[✔] GATE PASSED! All {res['gates_evaluated']} verification gate(s) satisfied.")
            dag.update_task_status(task_id, "COMPLETED")
            print(f"    Task [{task_id}] status updated to COMPLETED.")
        else:
            print(f"[❌] GATE FAILED with {len(res['diagnostics'])} error(s):")
            for d in res["diagnostics"]:
                print(f"    - {d}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
