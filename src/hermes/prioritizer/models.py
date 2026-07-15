"""Workflow-prioritization models for HERMES."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hermes.workflow_generator.models import GeneratedWorkflow


@dataclass(frozen=True, slots=True)
class PrioritizationConfig:
    """Weights used to rank generated workflows."""

    length_weight: float = 0.20
    state_coverage_weight: float = 0.25
    operation_diversity_weight: float = 0.30
    business_operation_weight: float = 0.25

    def __post_init__(self) -> None:
        weights = (
            self.length_weight,
            self.state_coverage_weight,
            self.operation_diversity_weight,
            self.business_operation_weight,
        )

        if any(weight < 0 for weight in weights):
            raise ValueError(
                "prioritization weights must not be negative"
            )

        if sum(weights) <= 0:
            raise ValueError(
                "at least one prioritization weight must be positive"
            )


@dataclass(frozen=True, slots=True)
class WorkflowScore:
    """Scored workflow with component-level evidence."""

    generated_workflow: GeneratedWorkflow
    total_score: float
    length_score: float
    state_coverage_score: float
    operation_diversity_score: float
    business_operation_score: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        values = (
            self.total_score,
            self.length_score,
            self.state_coverage_score,
            self.operation_diversity_score,
            self.business_operation_score,
        )

        if any(not 0.0 <= value <= 1.0 for value in values):
            raise ValueError(
                "workflow scores must be between 0 and 1"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.generated_workflow.to_dict(),
            "total_score": self.total_score,
            "length_score": self.length_score,
            "state_coverage_score": self.state_coverage_score,
            "operation_diversity_score": (
                self.operation_diversity_score
            ),
            "business_operation_score": (
                self.business_operation_score
            ),
            "metadata": dict(self.metadata),
        }
