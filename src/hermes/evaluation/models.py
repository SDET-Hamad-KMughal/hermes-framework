"""Evaluation-result models for HERMES."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from hermes.comparator.models import BehaviorComparisonResult
from hermes.executor.models import WorkflowExecutionResult


@dataclass(frozen=True, slots=True)
class MutationEvaluation:
    """Evaluation result for one mutated workflow."""

    mutation_workflow_id: str
    execution: WorkflowExecutionResult
    comparison: BehaviorComparisonResult

    def __post_init__(self) -> None:
        if not self.mutation_workflow_id.strip():
            raise ValueError(
                "mutation_workflow_id must not be empty"
            )

    @property
    def anomaly_detected(self) -> bool:
        return self.comparison.status.value == "divergent"

    def to_dict(self) -> dict[str, Any]:
        return {
            "mutation_workflow_id": self.mutation_workflow_id,
            "anomaly_detected": self.anomaly_detected,
            "execution": self.execution.to_dict(),
            "comparison": self.comparison.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """Complete HERMES evaluation result."""

    baseline_execution: WorkflowExecutionResult
    mutations: tuple[MutationEvaluation, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def mutation_count(self) -> int:
        return len(self.mutations)

    @property
    def anomaly_count(self) -> int:
        return sum(
            1
            for mutation in self.mutations
            if mutation.anomaly_detected
        )

    @property
    def equivalent_count(self) -> int:
        return self.mutation_count - self.anomaly_count

    @property
    def anomaly_rate(self) -> float:
        if self.mutation_count == 0:
            return 0.0

        return self.anomaly_count / self.mutation_count

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": {
                "mutation_count": self.mutation_count,
                "anomaly_count": self.anomaly_count,
                "equivalent_count": self.equivalent_count,
                "anomaly_rate": self.anomaly_rate,
            },
            "baseline_execution": (
                self.baseline_execution.to_dict()
            ),
            "mutations": [
                mutation.to_dict()
                for mutation in self.mutations
            ],
            "metadata": dict(self.metadata),
        }
