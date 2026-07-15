"""State-aware workflow generation for HERMES."""

from __future__ import annotations

from collections import defaultdict

from hermes.mutation.models import Workflow, WorkflowStep
from hermes.semantic.models import OperationType, SemanticOperation
from hermes.workflow_generator.models import (
    GeneratedWorkflow,
    WorkflowGenerationConfig,
)


class StateAwareWorkflowGenerator:
    """Generate connected semantic workflows from discovered operations."""

    def __init__(
        self,
        config: WorkflowGenerationConfig | None = None,
    ) -> None:
        self.config = config or WorkflowGenerationConfig()

    def generate(
        self,
        operations: list[SemanticOperation],
        start_state_id: str,
    ) -> list[GeneratedWorkflow]:
        """Generate connected workflows beginning at one state."""

        adjacency: dict[str, list[SemanticOperation]] = defaultdict(list)

        for operation in operations:
            if (
                operation.operation_type is OperationType.UNKNOWN
                and not self.config.include_unknown_operations
            ):
                continue

            adjacency[operation.source_state_id].append(operation)

        generated: list[GeneratedWorkflow] = []

        self._walk(
            adjacency=adjacency,
            current_state_id=start_state_id,
            state_path=(start_state_id,),
            operation_path=(),
            generated=generated,
        )

        return generated[: self.config.max_workflows]

    def _walk(
        self,
        *,
        adjacency: dict[str, list[SemanticOperation]],
        current_state_id: str,
        state_path: tuple[str, ...],
        operation_path: tuple[SemanticOperation, ...],
        generated: list[GeneratedWorkflow],
    ) -> None:
        if len(generated) >= self.config.max_workflows:
            return

        if (
            len(operation_path) >= self.config.minimum_steps
            and operation_path
        ):
            generated.append(
                self._build_generated_workflow(
                    operation_path,
                    state_path,
                )
            )

            if len(generated) >= self.config.max_workflows:
                return

        if len(operation_path) >= self.config.max_depth:
            return

        for operation in adjacency.get(current_state_id, []):
            target_state_id = (
                operation.target_state_id
                or current_state_id
            )

            if (
                not self.config.allow_repeated_states
                and target_state_id in state_path
            ):
                continue

            self._walk(
                adjacency=adjacency,
                current_state_id=target_state_id,
                state_path=state_path + (target_state_id,),
                operation_path=operation_path + (operation,),
                generated=generated,
            )

    @staticmethod
    def _build_generated_workflow(
        operations: tuple[SemanticOperation, ...],
        state_path: tuple[str, ...],
    ) -> GeneratedWorkflow:
        workflow_steps = tuple(
            WorkflowStep(
                operation_type=operation.operation_type,
                label=operation.label,
                source_state_id=operation.source_state_id,
                target_state_id=operation.target_state_id,
                selector=operation.selector,
                metadata=dict(operation.metadata),
            )
            for operation in operations
        )

        signature = "-".join(
            operation.operation_type.value
            for operation in operations
        )

        workflow = Workflow(
            workflow_id=f"generated-{signature}",
            name=f"Generated {signature}",
            steps=workflow_steps,
            metadata={
                "generated": True,
                "source": "state_graph",
            },
        )

        return GeneratedWorkflow(
            workflow=workflow,
            state_path=state_path,
            operation_count=len(operations),
            terminal_state_id=state_path[-1],
            metadata={
                "operation_types": [
                    operation.operation_type.value
                    for operation in operations
                ],
            },
        )
