"""Workflow ranking and selection for HERMES."""

from __future__ import annotations

from dataclasses import dataclass

from hermes.semantic.models import OperationType
from hermes.workflow_generator.models import GeneratedWorkflow


@dataclass(frozen=True, slots=True)
class WorkflowSelectionConfig:
    """Configuration for ranking generated workflows."""

    maximum_selected: int = 10
    prefer_longer_workflows: bool = True
    require_business_operation: bool = True

    def __post_init__(self) -> None:
        if self.maximum_selected < 1:
            raise ValueError(
                "maximum_selected must be at least 1"
            )


class WorkflowSelector:
    """Rank and select useful generated workflows."""

    BUSINESS_OPERATIONS = {
        OperationType.LOGIN,
        OperationType.REGISTER,
        OperationType.ADD_TO_CART,
        OperationType.REMOVE_FROM_CART,
        OperationType.CHECKOUT,
        OperationType.PAYMENT,
        OperationType.TOP_UP_WALLET,
        OperationType.VIEW_ORDERS,
    }

    def __init__(
        self,
        config: WorkflowSelectionConfig | None = None,
    ) -> None:
        self.config = config or WorkflowSelectionConfig()

    def select(
        self,
        workflows: list[GeneratedWorkflow],
    ) -> list[GeneratedWorkflow]:
        """Return ranked, filtered workflows."""

        candidates = [
            workflow
            for workflow in workflows
            if self._is_eligible(workflow)
        ]

        ranked = sorted(
            candidates,
            key=self._score,
            reverse=True,
        )

        return ranked[: self.config.maximum_selected]

    def _is_eligible(
        self,
        workflow: GeneratedWorkflow,
    ) -> bool:
        if not self.config.require_business_operation:
            return True

        return any(
            step.operation_type in self.BUSINESS_OPERATIONS
            for step in workflow.workflow.steps
        )

    def _score(
        self,
        workflow: GeneratedWorkflow,
    ) -> tuple[int, int, int]:
        business_count = sum(
            1
            for step in workflow.workflow.steps
            if step.operation_type in self.BUSINESS_OPERATIONS
        )

        unique_operations = len(
            {
                step.operation_type
                for step in workflow.workflow.steps
            }
        )

        length_score = (
            workflow.operation_count
            if self.config.prefer_longer_workflows
            else -workflow.operation_count
        )

        return (
            business_count,
            unique_operations,
            length_score,
        )
