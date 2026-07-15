"""Workflow-context mutation operators for HERMES."""

from __future__ import annotations

from dataclasses import replace

from hermes.mutation.models import (
    MutationType,
    Workflow,
    WorkflowStep,
)
from hermes.semantic.models import OperationType


class WorkflowMutationOperators:
    """Apply deterministic mutations to semantic workflows."""

    @staticmethod
    def skip_step(workflow: Workflow, index: int) -> Workflow:
        """Remove one workflow step."""

        WorkflowMutationOperators._validate_index(
            workflow,
            index,
        )

        steps = (
            workflow.steps[:index]
            + workflow.steps[index + 1 :]
        )

        return WorkflowMutationOperators._mutated_workflow(
            workflow,
            MutationType.SKIP_STEP,
            steps,
            index=index,
        )

    @staticmethod
    def duplicate_step(
        workflow: Workflow,
        index: int,
    ) -> Workflow:
        """Duplicate one workflow step."""

        WorkflowMutationOperators._validate_index(
            workflow,
            index,
        )

        step = workflow.steps[index]
        steps = (
            workflow.steps[: index + 1]
            + (step,)
            + workflow.steps[index + 1 :]
        )

        return WorkflowMutationOperators._mutated_workflow(
            workflow,
            MutationType.DUPLICATE_STEP,
            steps,
            index=index,
        )

    @staticmethod
    def swap_adjacent(
        workflow: Workflow,
        index: int,
    ) -> Workflow:
        """Swap a step with the following step."""

        if index < 0 or index >= len(workflow.steps) - 1:
            raise IndexError(
                "index must reference a step with a successor"
            )

        steps = list(workflow.steps)
        steps[index], steps[index + 1] = (
            steps[index + 1],
            steps[index],
        )

        return WorkflowMutationOperators._mutated_workflow(
            workflow,
            MutationType.SWAP_ADJACENT,
            tuple(steps),
            index=index,
        )

    @staticmethod
    def reverse_workflow(workflow: Workflow) -> Workflow:
        """Reverse the complete workflow order."""

        return WorkflowMutationOperators._mutated_workflow(
            workflow,
            MutationType.REVERSE_WORKFLOW,
            tuple(reversed(workflow.steps)),
        )

    @staticmethod
    def insert_logout(
        workflow: Workflow,
        index: int,
    ) -> Workflow:
        """Insert a logout operation before a selected step."""

        if index < 0 or index > len(workflow.steps):
            raise IndexError("index is outside workflow bounds")

        source_state_id = (
            workflow.steps[index - 1].target_state_id
            if index > 0
            and workflow.steps[index - 1].target_state_id
            else "unknown-state"
        )

        logout_step = WorkflowStep(
            operation_type=OperationType.LOGOUT,
            label="Injected Logout",
            source_state_id=source_state_id,
            metadata={"injected": True},
        )

        steps = (
            workflow.steps[:index]
            + (logout_step,)
            + workflow.steps[index:]
        )

        return WorkflowMutationOperators._mutated_workflow(
            workflow,
            MutationType.INSERT_LOGOUT,
            steps,
            index=index,
        )

    @staticmethod
    def _validate_index(
        workflow: Workflow,
        index: int,
    ) -> None:
        if index < 0 or index >= len(workflow.steps):
            raise IndexError("index is outside workflow bounds")

    @staticmethod
    def _mutated_workflow(
        workflow: Workflow,
        mutation_type: MutationType,
        steps: tuple[WorkflowStep, ...],
        **metadata,
    ) -> Workflow:
        mutation_metadata = dict(workflow.metadata)
        mutation_metadata.update(
            {
                "parent_workflow_id": workflow.workflow_id,
                "mutation_type": mutation_type.value,
                **metadata,
            }
        )

        return replace(
            workflow,
            workflow_id=(
                f"{workflow.workflow_id}--"
                f"{mutation_type.value}"
            ),
            name=f"{workflow.name} [{mutation_type.value}]",
            steps=steps,
            metadata=mutation_metadata,
        )
