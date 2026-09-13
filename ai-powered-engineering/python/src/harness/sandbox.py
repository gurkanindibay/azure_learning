"""Isolated execution sandbox for executing tests without side effects."""

import os
import sys
import tempfile
import subprocess
from typing import Tuple, Dict, Any
from pathlib import Path


class ExecutionSandbox:
    """Provides an isolated filesystem and subprocess boundary for executing code."""

    def __init__(self, timeout_seconds: int = 5):
        self.timeout_seconds = timeout_seconds

    def run_tests(self, code: str, test_code: str, module_name: str = "solution") -> Dict[str, Any]:
        """Runs the provided code against test_code inside an isolated directory.
        
        Returns a dict with:
            passed (bool)
            exit_code (int)
            stdout (str)
            stderr (str)
            duration_ms (float)
        """
        with tempfile.TemporaryDirectory(prefix="patchmaster_sandbox_") as temp_dir:
            temp_path = Path(temp_dir)
            source_file = temp_path / f"{module_name}.py"
            test_file = temp_path / f"test_{module_name}.py"

            source_file.write_text(code, encoding="utf-8")
            test_file.write_text(test_code, encoding="utf-8")

            # Execute pytest via current python interpreter
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                str(test_file),
                "-q",
                "--tb=short",
                "--no-header",
            ]

            try:
                result = subprocess.run(
                    cmd,
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                )
                return {
                    "passed": result.returncode == 0,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            except subprocess.TimeoutExpired:
                return {
                    "passed": False,
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": f"Execution timed out after {self.timeout_seconds} seconds (possible infinite loop).",
                }
            except Exception as e:
                return {
                    "passed": False,
                    "exit_code": -2,
                    "stdout": "",
                    "stderr": f"Sandbox execution error: {str(e)}",
                }
