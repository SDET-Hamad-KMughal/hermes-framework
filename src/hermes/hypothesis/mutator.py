"""Hypothesis-driven workflow mutation for HERMES."""

from __future__ import annotations

from dataclasses import replace

from hermes.hypothesis.models import WorkflowHypothesis
from hermes.mutation.models import Workflow
from hermes.semantic.models import OperationType


class HypothesisMutator:
    """Convert structured hypotheses into workflow mutations."""

    def mutate(
        self,
        workflow: Workflow,
        hypothesis: WorkflowHypothesis,
    ) -> Workflow:
        """Apply the mutation strategy described by a hypothesis."""

        strategy = hypothesis.mutation_strategy

        if strategy == "remove_prerequisite":
            return self._remove_prerequisite(
                workflow,
                hypothesis,
            )

        if strategy == "duplicate_operation":
            return self._duplicate_operation(
                workflow,
                hypothesis,
            )

        if strategy == "swap_operations":
            return self._swap_operations(
                workflow,
                hypothesis,
            )

        raise ValueError(
            f"unsupported hypothesis mutation strategy: {strategy}"
        )

    @staticmethod
    def _operation_value(
        operation_type: OperationType,
    ) -> str:
        return operation_type.value

    def _remove_prerequisite(
        self,
        workflow: Workflow,
        hypothesis: WorkflowHypothesis,
    ) -> Workflow:
        prerequisite = hypothesis.prerequisite_operation

        if not prerequisite:
            raise ValueError(
                "remove_prerequisite requires prerequisite_operation"
            )

        steps = list(workflow.steps)

        index = next(
            (
                position
                for position, step in enumerate(steps)
                if self._operation_value(step.operation_type)
                == prerequisite
            ),
            None,
        )

        if index is None:
            raise ValueError(
                f"prerequisite operation not found: {prerequisite}"
            )

        del steps[index]

        return self._build_mutated_workflow(
            workflow,
            hypothesis,
            tuple(steps),
        )

    def _duplicate_operation(
        self,
        workflow: Workflow,
        hypothesis: WorkflowHypothesis,
    ) -> Workflow:
        target = hypothesis.target_operation

        if not target:
            raise ValueError(
                "duplicate_operation requires target_operation"
            )

        steps = list(workflow.steps)

        index = next(
            (
                position
                for position, step in enumerate(steps)
                if self._operation_value(step.operation_type)
                == target
            ),
            None,
        )

        if index is None:
            raise ValueError(
                f"target operation not found: {target}"
            )

        steps.insert(
            index + 1,
            replace(
                steps[index],
                metadata={
                    **steps[index].metadata,
                    "hypothesis_duplicate": True,
                },
            ),
        )

        return self._build_mutated_workflow(
            workflow,
            hypothesis,
            tuple(steps),
        )

    def _swap_operations(
        self,
        workflow: Workflow,
        hypothesis: WorkflowHypothesis,
    ) -> Workflow:
        target = hypothesis.target_operation
        prerequisite = hypothesis.prerequisite_operation

        if not target or not prerequisite:
            raise ValueError(
                "swap_operations requires target and prerequisite"
            )

        steps = list(workflow.steps)

        target_index = next(
            (
                index
                for index, step in enumerate(steps)
                if self._operation_value(step.operation_type)
                == target
            ),
            None,
        )

        prerequisite_index = next(
            (
                index
                for index, step in enumerate(steps)
                if self._operation_value(step.operation_type)
                == prerequisite
            ),
            None,
        )

        if target_index is None:
            raise ValueError(
                f"target operation not found: {target}"
            )

        if prerequisite_index is None:
            raise ValueError(
                f"prerequisite operation not found: {prerequisite}"
            )

        steps[target_index], steps[prerequisite_index] = (
            steps[prerequisite_index],
            steps[target_index],
        )

        return self._build_mutated_workflow(
            workflow,
            hypothesis,
            tuple(steps),
        )

    @staticmethod
    def _build_mutated_workflow(
        workflow: Workflow,
        hypothesis: WorkflowHypothesis,
        steps: tuple,
    ) -> Workflow:
        return Workflow(
            workflow_id=(
                f"{workflow.workflow_id}--"
                f"{hypothesis.hypothesis_id.lower()}"
            ),
            name=(
                f"{workflow.name} — "
                f"{hypothesis.title}"
            ),
            steps=steps,
            metadata={
                **workflow.metadata,
                "hypothesis_id": hypothesis.hypothesis_id,
                "hypothesis_title": hypothesis.title,
                "mutation_strategy": (
                    hypothesis.mutation_strategy
                ),
                "expected_behavior": (
                    hypothesis.expected_behavior.value
                ),
            },
        )
