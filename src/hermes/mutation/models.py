"""Workflow-mutation models for HERMES."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from hermes.semantic.models import OperationType


class MutationType(str, Enum):
    """Supported workflow-context mutation categories."""

    SKIP_STEP = "skip_step"
    DUPLICATE_STEP = "duplicate_step"
    SWAP_ADJACENT = "swap_adjacent"
    REVERSE_WORKFLOW = "reverse_workflow"
    INSERT_LOGOUT = "insert_logout"
    SWITCH_IDENTITY = "switch_identity"


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    """One semantic operation inside a workflow."""

    operation_type: OperationType
    label: str
    source_state_id: str
    target_state_id: str | None = None
    selector: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source_state_id.strip():
            raise ValueError("source_state_id must not be empty")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["operation_type"] = self.operation_type.value
        return data


@dataclass(frozen=True, slots=True)
class Workflow:
    """An ordered semantic workflow."""

    workflow_id: str
    name: str
    steps: tuple[WorkflowStep, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.workflow_id.strip():
            raise ValueError("workflow_id must not be empty")

        if not self.name.strip():
            raise ValueError("name must not be empty")

    def __len__(self) -> int:
        return len(self.steps)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": dict(self.metadata),
        }
