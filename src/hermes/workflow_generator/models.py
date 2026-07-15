"""Automatic workflow-generation models for HERMES."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hermes.mutation.models import Workflow


@dataclass(frozen=True, slots=True)
class WorkflowGenerationConfig:
    """Configuration for state-aware workflow generation."""

    max_depth: int = 6
    max_workflows: int = 50
    include_unknown_operations: bool = False
    allow_repeated_states: bool = False
    minimum_steps: int = 1

    def __post_init__(self) -> None:
        if self.max_depth < 1:
            raise ValueError("max_depth must be at least 1")

        if self.max_workflows < 1:
            raise ValueError("max_workflows must be at least 1")

        if self.minimum_steps < 1:
            raise ValueError("minimum_steps must be at least 1")

        if self.minimum_steps > self.max_depth:
            raise ValueError(
                "minimum_steps must not exceed max_depth"
            )


@dataclass(frozen=True, slots=True)
class GeneratedWorkflow:
    """A generated workflow with path-level provenance."""

    workflow: Workflow
    state_path: tuple[str, ...]
    operation_count: int
    terminal_state_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.state_path:
            raise ValueError("state_path must not be empty")

        if self.operation_count < 0:
            raise ValueError(
                "operation_count must not be negative"
            )

        if not self.terminal_state_id.strip():
            raise ValueError(
                "terminal_state_id must not be empty"
            )

    @classmethod
    def from_dict(
        cls,
        payload: dict[str, Any],
    ) -> "GeneratedWorkflow":
        """Reconstruct a generated workflow from serialized data."""

        from hermes.mutation.models import Workflow, WorkflowStep
        from hermes.semantic.models import OperationType

        workflow_data = payload["workflow"]

        steps = tuple(
            WorkflowStep(
                operation_type=OperationType(
                    item["operation_type"]
                ),
                label=item["label"],
                source_state_id=item["source_state_id"],
                target_state_id=item.get("target_state_id"),
                selector=item.get("selector"),
                metadata=dict(item.get("metadata", {})),
            )
            for item in workflow_data.get("steps", [])
        )

        workflow = Workflow(
            workflow_id=workflow_data["workflow_id"],
            name=workflow_data["name"],
            steps=steps,
            metadata=dict(
                workflow_data.get("metadata", {})
            ),
        )

        return cls(
            workflow=workflow,
            state_path=tuple(payload["state_path"]),
            operation_count=int(payload["operation_count"]),
            terminal_state_id=payload["terminal_state_id"],
            metadata=dict(payload.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow.to_dict(),
            "state_path": list(self.state_path),
            "operation_count": self.operation_count,
            "terminal_state_id": self.terminal_state_id,
            "metadata": dict(self.metadata),
        }
