"""Execution-result models for HERMES."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from hermes.semantic.models import OperationType


@dataclass(frozen=True, slots=True)
class ExecutionStepResult:
    """Result of executing one workflow step."""

    step_index: int
    operation_type: OperationType
    label: str
    success: bool
    url_before: str | None = None
    url_after: str | None = None
    duration_seconds: float = 0.0
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.step_index < 0:
            raise ValueError("step_index must not be negative")

        if self.duration_seconds < 0:
            raise ValueError(
                "duration_seconds must not be negative"
            )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["operation_type"] = self.operation_type.value
        return data


@dataclass(frozen=True, slots=True)
class WorkflowExecutionResult:
    """Complete execution trace for one workflow."""

    workflow_id: str
    workflow_name: str
    steps: tuple[ExecutionStepResult, ...]
    started_at: str
    finished_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.workflow_id.strip():
            raise ValueError("workflow_id must not be empty")

        if not self.workflow_name.strip():
            raise ValueError("workflow_name must not be empty")

    @property
    def success(self) -> bool:
        return all(step.success for step in self.steps)

    @property
    def successful_steps(self) -> int:
        return sum(1 for step in self.steps if step.success)

    @property
    def failed_steps(self) -> int:
        return sum(1 for step in self.steps if not step.success)

    @property
    def total_duration_seconds(self) -> float:
        return sum(step.duration_seconds for step in self.steps)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "success": self.success,
            "successful_steps": self.successful_steps,
            "failed_steps": self.failed_steps,
            "total_duration_seconds": self.total_duration_seconds,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": dict(self.metadata),
        }
