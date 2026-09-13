"""Abstract base contracts for Maker and Checker agents."""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
from ..state import AgentState


class BaseMakerAgent(ABC):
    """The generative role: responsible for proposing candidate code / patches."""

    @abstractmethod
    def generate_plan(self, state: AgentState) -> str:
        """Formulates an analytical plan based on failing tests/errors."""
        pass

    @abstractmethod
    def generate_patch(self, state: AgentState) -> str:
        """Generates candidate Python source code."""
        pass


class BaseCheckerAgent(ABC):
    """The analytical/audit role: evaluates candidate code beyond unit test passes."""

    @abstractmethod
    def audit(self, code: str, original_code: str) -> Tuple[bool, str]:
        """Audits code quality, security regressions, or unwanted behavioral shifts."""
        pass
