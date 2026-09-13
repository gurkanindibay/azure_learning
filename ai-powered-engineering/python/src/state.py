"""Typed state definitions for the agentic refactoring graph."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Phase(str, Enum):
    """5-Phase agentic loop lifecycle + terminal states."""
    DISCOVER = "DISCOVER"    # Inspect code, run initial baseline tests
    PLAN = "PLAN"            # Formulate hypotheses and fix strategy
    EXECUTE = "EXECUTE"      # Maker generates candidate refactor / patch
    VERIFY = "VERIFY"        # Deterministic verification gate (AST, tests, diff)
    ITERATE = "ITERATE"      # Analyze errors, prune context, update prompt
    DELIVER = "DELIVER"      # Terminal success state: verified working patch
    ESCALATE = "ESCALATE"    # Terminal failure state: budget exhausted or human required


class VerificationResult(BaseModel):
    """Output of the deterministic verification gate."""
    passed: bool
    ast_valid: bool
    diff_valid: bool
    tests_passed: bool
    total_tests: int = 0
    failed_tests: int = 0
    stdout: str = ""
    stderr: str = ""
    error_summary: str = ""


class IterationRecord(BaseModel):
    """Audit log of a single iteration through the feedback loop."""
    iteration: int
    plan: str
    proposed_code: str
    verification: VerificationResult
    diagnostic_feedback: Optional[str] = None


class AgentState(BaseModel):
    """Central state container carried through graph transitions."""
    task_id: str
    file_path: str
    test_path: str
    original_code: str
    current_code: str
    test_code: str

    current_phase: Phase = Phase.DISCOVER
    iteration: int = 0
    max_iterations: int = 3

    history: List[IterationRecord] = Field(default_factory=list)
    latest_verification: Optional[VerificationResult] = None
    latest_plan: str = ""
    latest_diagnostic: str = ""

    # Token and cost tracking (Observability)
    token_usage: Dict[str, int] = Field(default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0})
    is_terminal: bool = False
    delivery_report: Optional[str] = None
