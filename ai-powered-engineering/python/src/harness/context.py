"""Context management & anti-rot compaction to preserve signal over iterations."""

import re
from typing import List
from ..state import IterationRecord


class ContextManager:
    """Combats context rot by distilling test outputs and compacting history."""

    @staticmethod
    def extract_failure_signal(stdout: str, stderr: str) -> str:
        """Extracts the precise traceback and assertion error from pytest output."""
        combined = (stdout or "") + "\n" + (stderr or "")
        
        # Look for AssertionError or Traceback sections
        lines = combined.splitlines()
        extracted = []
        capture = False

        for line in lines:
            if "FAILURES" in line or "Traceback" in line or "AssertionError" in line or "FAILED" in line:
                capture = True
            if capture:
                # Strip out ANSI escape codes if present
                clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                extracted.append(clean_line)
        
        if not extracted:
            # Fallback to last 15 lines if no regex match
            extracted = [re.sub(r'\x1b\[[0-9;]*m', '', l) for l in lines[-15:]]

        return "\n".join(extracted[:25])  # Cap at 25 concise lines

    @classmethod
    def format_iteration_prompt(
        cls,
        original_code: str,
        current_code: str,
        test_code: str,
        history: List[IterationRecord],
        diagnostic_hint: str = "",
    ) -> str:
        """Constructs a compact, high-signal prompt for the Maker agent."""
        history_summary = []
        for rec in history:
            err_snip = rec.verification.error_summary or (rec.verification.stderr[:100] if rec.verification.stderr else "Failed tests")
            history_summary.append(f"- Attempt #{rec.iteration}: {err_snip}")

        summary_text = "\n".join(history_summary) if history_summary else "No prior attempts."

        prompt = f"""### TASK: Fix the following code to make all tests pass.

### CURRENT SOURCE CODE:
```python
{current_code}
```

### TEST SUITE:
```python
{test_code}
```

### PRIOR ATTEMPTS & FAILURES:
{summary_text}

### LATEST VERIFICATION FEEDBACK:
{diagnostic_hint}

### INSTRUCTIONS:
- Return ONLY the updated, self-contained Python code.
- Do NOT alter test expectations; fix the logic in the source code.
- Ensure zero syntax errors and complete edge-case handling.
"""
        return prompt
