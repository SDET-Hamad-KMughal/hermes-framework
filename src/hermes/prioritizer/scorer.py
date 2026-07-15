"""Workflow scoring and prioritization for HERMES."""

from __future__ import annotations

from hermes.prioritizer.models import (
    PrioritizationConfig,
    WorkflowScore,
)
from hermes.semantic.models import OperationType
from hermes.workflow_generator.models import GeneratedWorkflow


class WorkflowScorer:
    """Score and rank generated workflows."""

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
        config: PrioritizationConfig | None = None,
    ) -> None:
        self.config = config or PrioritizationConfig()

    def score(
        self,
        workflow: GeneratedWorkflow,
        *,
        maximum_depth: int,
        total_state_count: int,
    ) -> WorkflowScore:
        """Score one generated workflow."""

        if maximum_depth < 1:
            raise ValueError("maximum_depth must be at least 1")

        if total_state_count < 1:
            raise ValueError(
                "total_state_count must be at least 1"
            )

        operation_types = tuple(
            step.operation_type
            for step in workflow.workflow.steps
        )

        length_score = min(
            workflow.operation_count / maximum_depth,
            1.0,
        )

        unique_states = len(set(workflow.state_path))
        state_coverage_score = min(
            unique_states / total_state_count,
            1.0,
        )

        if operation_types:
            operation_diversity_score = (
                len(set(operation_types))
                / len(operation_types)
            )
        else:
            operation_diversity_score = 0.0

        if operation_types:
            business_operation_score = (
                sum(
                    1
                    for operation_type in operation_types
                    if operation_type in self.BUSINESS_OPERATIONS
                )
                / len(operation_types)
            )
        else:
            business_operation_score = 0.0

        total_weight = (
            self.config.length_weight
            + self.config.state_coverage_weight
            + self.config.operation_diversity_weight
            + self.config.business_operation_weight
        )

        weighted_score = (
            length_score * self.config.length_weight
            + state_coverage_score
            * self.config.state_coverage_weight
            + operation_diversity_score
            * self.config.operation_diversity_weight
            + business_operation_score
            * self.config.business_operation_weight
        )

        total_score = weighted_score / total_weight

        return WorkflowScore(
            generated_workflow=workflow,
            total_score=total_score,
            length_score=length_score,
            state_coverage_score=state_coverage_score,
            operation_diversity_score=(
                operation_diversity_score
            ),
            business_operation_score=(
                business_operation_score
            ),
        )

    def rank(
        self,
        workflows: list[GeneratedWorkflow],
        *,
        maximum_depth: int,
        total_state_count: int,
    ) -> list[WorkflowScore]:
        """Score and rank workflows from highest to lowest."""

        scored = [
            self.score(
                workflow,
                maximum_depth=maximum_depth,
                total_state_count=total_state_count,
            )
            for workflow in workflows
        ]

        ranked = sorted(
            scored,
            key=lambda item: (
                item.total_score,
                item.generated_workflow.operation_count,
                item.generated_workflow.workflow.workflow_id,
            ),
            reverse=True,
        )

        return [
            WorkflowScore(
                generated_workflow=item.generated_workflow,
                total_score=item.total_score,
                length_score=item.length_score,
                state_coverage_score=item.state_coverage_score,
                operation_diversity_score=(
                    item.operation_diversity_score
                ),
                business_operation_score=(
                    item.business_operation_score
                ),
                metadata={
                    **item.metadata,
                    "rank": index,
                },
            )
            for index, item in enumerate(
                ranked,
                start=1,
            )
        ]
