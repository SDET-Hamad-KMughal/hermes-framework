"""Hypothesis models for HERMES."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HypothesisCategory(str, Enum):
    """Supported workflow-hypothesis categories."""

    AUTHENTICATION = "authentication"
    ORDERING = "ordering"
    DUPLICATION = "duplication"
    AUTHORIZATION = "authorization"
    STATE_DEPENDENCY = "state_dependency"
    IDEMPOTENCY = "idempotency"


class ExpectedBehavior(str, Enum):
    """Expected outcome of a hypothesis-driven mutation."""

    REJECT = "reject"
    ACCEPT = "accept"
    PRESERVE_STATE = "preserve_state"
    CHANGE_STATE = "change_state"
    REMAIN_EQUIVALENT = "remain_equivalent"
    DIVERGE = "diverge"


@dataclass(frozen=True, slots=True)
class WorkflowHypothesis:
    """Structured hypothesis used to guide workflow mutation."""

    hypothesis_id: str
    title: str
    description: str
    category: HypothesisCategory
    source_workflow_id: str
    mutation_strategy: str
    expected_behavior: ExpectedBehavior
    target_operation: str | None = None
    prerequisite_operation: str | None = None
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip():
            raise ValueError(
                "hypothesis_id must not be empty"
            )

        if not self.title.strip():
            raise ValueError("title must not be empty")

        if not self.description.strip():
            raise ValueError(
                "description must not be empty"
            )

        if not self.source_workflow_id.strip():
            raise ValueError(
                "source_workflow_id must not be empty"
            )

        if not self.mutation_strategy.strip():
            raise ValueError(
                "mutation_strategy must not be empty"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0 and 1"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "source_workflow_id": self.source_workflow_id,
            "mutation_strategy": self.mutation_strategy,
            "expected_behavior": self.expected_behavior.value,
            "target_operation": self.target_operation,
            "prerequisite_operation": (
                self.prerequisite_operation
            ),
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }
