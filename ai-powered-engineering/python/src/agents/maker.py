"""Maker implementations: Mock, Heuristic, and Live LLM agents."""

import os
import re
from typing import List, Optional
from .base import BaseMakerAgent
from ..state import AgentState
from ..harness.context import ContextManager


class MockMakerAgent(BaseMakerAgent):
    """Deterministic mock agent used for testing loops, graphs, and failure handling."""

    def __init__(self, scripted_responses: Optional[List[str]] = None):
        self.scripted_responses = scripted_responses or []
        self.call_count = 0

    def generate_plan(self, state: AgentState) -> str:
        return f"Plan for iteration {state.iteration + 1}: Analyze verification failure and apply targeted adjustment."

    def generate_patch(self, state: AgentState) -> str:
        idx = min(self.call_count, len(self.scripted_responses) - 1)
        self.call_count += 1
        if self.scripted_responses:
            return self.scripted_responses[idx]
        return state.current_code


class HeuristicMakerAgent(BaseMakerAgent):
    """Heuristic agent that reads pytest error summaries and applies smart transformations.
    
    Demonstrates how self-correction works in practice without requiring an external API key.
    """

    def generate_plan(self, state: AgentState) -> str:
        diag = state.latest_diagnostic or ""
        if "IndexError" in diag or "off-by-one" in diag.lower():
            return "Identified boundary condition error: Adjust indexing range or slice bounds."
        elif "NoneType" in diag or "AttributeError" in diag:
            return "Identified null pointer / None dereference: Add guard check for None input."
        elif "KeyError" in diag:
            return "Identified missing key: Add default dict lookup or .get() fallback."
        return "Generic refactor: inspect logic and apply corrective patch."

    def generate_patch(self, state: AgentState) -> str:
        code = state.current_code
        diag = state.latest_diagnostic or ""

        # Simulated stochastic behavior: on iteration 0, produce a naive attempt that still fails
        # on iteration >= 1, produce the targeted fix from the failure feedback
        if "case_01" in state.task_id or "deltas" in code:
            if state.iteration == 0:
                # Naive fix: drops '+ 1', but still fails at items[i + 1]
                return code.replace("range(len(items) + 1)", "range(len(items))")
            else:
                # Iteration 1+: feedback received IndexError, corrects to range(len(items) - 1)
                code = re.sub(r'range\(len\((\w+)\)(\s*\+\s*1)?\)', r'range(len(\1) - 1)', code)
                return code
        
        if "NoneType" in diag or "'NoneType' object has no attribute" in diag:
            # Insert None guard if not present
            if "if " not in code or "is None" not in code:
                lines = code.splitlines()
                for i, line in enumerate(lines):
                    if line.strip().startswith("def "):
                        indent = "    "
                        guard = f"{indent}if text is None or not text:\n{indent}    return ''"
                        lines.insert(i + 1, guard)
                        code = "\n".join(lines)
                        break

        if "dictionary changed size during iteration" in diag or "dict_mutation" in state.task_id:
            code = code.replace("for k, v in data.items():", "for k, v in list(data.items()):")
            code = code.replace("for key in my_dict:", "for key in list(my_dict.keys()):")

        if "logic_flaw" in state.task_id or "discount" in code.lower():
            code = code.replace("price * discount", "price * (1 - discount)")
            code = code.replace("amount + (amount * rate)", "amount * (1 + rate)")

        return code


class LLMMakerAgent(BaseMakerAgent):
    """Live LLM agent utilizing OpenAI or Google GenAI if environment credentials exist."""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name

    def generate_plan(self, state: AgentState) -> str:
        prompt = f"Given code that failed with:\n{state.latest_diagnostic}\nPropose a concise 2-sentence fix plan."
        return self._call_llm(prompt)

    def generate_patch(self, state: AgentState) -> str:
        prompt = ContextManager.format_iteration_prompt(
            original_code=state.original_code,
            current_code=state.current_code,
            test_code=state.test_code,
            history=state.history,
            diagnostic_hint=state.latest_diagnostic,
        )
        raw_output = self._call_llm(prompt)
        # Strip markdown code blocks if wrapped
        match = re.search(r'```(?:python)?\s*(.*?)\s*```', raw_output, re.DOTALL)
        if match:
            return match.group(1)
        return raw_output.strip()

    def _call_llm(self, prompt: str) -> str:
        # Graceful fallback if no API key is set
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "# Error: No LLM API key configured. Switch to HeuristicMakerAgent or set OPENAI_API_KEY."
        
        # Standard urllib call or openai client if installed
        try:
            from openai import OpenAI  # type: ignore
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            return f"# LLM API invocation failed: {str(e)}"
