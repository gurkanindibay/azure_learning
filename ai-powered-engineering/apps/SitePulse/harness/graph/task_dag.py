"""Task DAG Engine: Loads, validates, and topologically sorts Spec Kit tasks."""

import json
from pathlib import Path
from typing import Dict, List, Set, Any


class TaskDag:
    def __init__(self, dag_file: Path):
        self.dag_file = dag_file
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self._load()

    def _load(self) -> None:
        with open(self.dag_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for task in data.get("tasks", []):
            task_id = task["id"]
            self.tasks[task_id] = task
            self.dependencies[task_id] = task.get("depends_on", [])

        self._validate_no_cycles()

    def _validate_no_cycles(self) -> None:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self.dependencies.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    raise ValueError(f"Cycle detected in Task DAG involving task: {neighbor}")
            rec_stack.remove(node)

        for task_id in self.tasks:
            if task_id not in visited:
                dfs(task_id)

    def get_runnable_tasks(self) -> List[Dict[str, Any]]:
        """Returns tasks that are PENDING and all of their dependencies are COMPLETED."""
        runnable = []
        for task_id, task in self.tasks.items():
            if task.get("status") == "PENDING":
                deps = self.dependencies.get(task_id, [])
                if all(self.tasks.get(dep, {}).get("status") == "COMPLETED" for dep in deps):
                    runnable.append(task)
        return runnable

    def update_task_status(self, task_id: str, new_status: str) -> None:
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")
        self.tasks[task_id]["status"] = new_status
        # Save back to file
        with open(self.dag_file, "w", encoding="utf-8") as f:
            json.dump({"version": "1.0.0", "project": "SitePulse Mobile (Android)", "tasks": list(self.tasks.values())}, f, indent=2)

    def render_ascii(self) -> str:
        lines = ["=== SitePulse Harness Task DAG ==="]
        status_icons = {
            "COMPLETED": "[✔] VERIFIED",
            "IN_PROGRESS": "[⚡] IN LOOP",
            "PENDING": "[⏳] PENDING",
            "BLOCKED": "[⛔] BLOCKED"
        }
        for task_id, task in self.tasks.items():
            status_text = status_icons.get(task.get("status", "PENDING"), "[?]")
            deps = ", ".join(task.get("depends_on", [])) or "None (Root)"
            lines.append(f"  {task_id} {status_text.ljust(15)} : {task['name']}")
            lines.append(f"       └─ Module: {task.get('module')} | Prereqs: [{deps}]")
        return "\n".join(lines)
