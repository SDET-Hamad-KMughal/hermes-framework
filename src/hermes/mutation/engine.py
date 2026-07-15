"""Workflow mutation engine for HERMES."""

from __future__ import annotations

from dataclasses import dataclass

from hermes.mutation.models import MutationType, Workflow
from hermes.mutation.operators import WorkflowMutationOperators


@dataclass(frozen=True, slots=True)
class MutationPlan:
    """Configuration for generating workflow mutations."""

    include_skip: bool = True
    include_duplicate: bool = True
    include_swap: bool = True
    include_reverse: bool = True
    include_logout: bool = True
    max_mutations: int | None = None

    def __post_init__(self) -> None:
        if self.max_mutations is not None and self.max_mutations < 1:
            raise ValueError("max_mutations must be at least 1")


class WorkflowMutationEngine:
    """Generate deterministic context mutations from a workflow."""

    def __init__(
        self,
        plan: MutationPlan | None = None,
    ) -> None:
        self.plan = plan or MutationPlan()

    def generate(self, workflow: Workflow) -> list[Workflow]:
        """Generate all configured workflow mutations."""

        mutations: list[Workflow] = []

        if self.plan.include_skip:
            for index in range(len(workflow.steps)):
                mutations.append(
                    WorkflowMutationOperators.skip_step(
                        workflow,
                        index,
                    )
                )

        if self.plan.include_duplicate:
            for index in range(len(workflow.steps)):
                mutations.append(
                    WorkflowMutationOperators.duplicate_step(
                        workflow,
                        index,
                    )
                )

        if self.plan.include_swap:
            for index in range(max(0, len(workflow.steps) - 1)):
                mutations.append(
                    WorkflowMutationOperators.swap_adjacent(
                        workflow,
                        index,
                    )
                )

        if self.plan.include_reverse and len(workflow.steps) > 1:
            mutations.append(
                WorkflowMutationOperators.reverse_workflow(
                    workflow
                )
            )

        if self.plan.include_logout:
            for index in range(len(workflow.steps) + 1):
                mutations.append(
                    WorkflowMutationOperators.insert_logout(
                        workflow,
                        index,
                    )
                )

        mutations = self._deduplicate(mutations)

        if self.plan.max_mutations is not None:
            mutations = mutations[: self.plan.max_mutations]

        return mutations

    @staticmethod
    def _deduplicate(
        workflows: list[Workflow],
    ) -> list[Workflow]:
        """Remove mutations with identical semantic step sequences."""

        unique: list[Workflow] = []
        seen: set[
            tuple[tuple[str, str, str | None], ...]
        ] = set()

        for workflow in workflows:
            signature = tuple(
                (
                    step.operation_type.value,
                    step.source_state_id,
                    step.target_state_id,
                )
                for step in workflow.steps
            )

            if signature in seen:
                continue

            seen.add(signature)
            unique.append(workflow)

        return unique

    @staticmethod
    def mutation_types(
        workflows: list[Workflow],
    ) -> set[MutationType]:
        """Return the mutation categories present in a result set."""

        discovered: set[MutationType] = set()

        for workflow in workflows:
            value = workflow.metadata.get("mutation_type")

            if value:
                discovered.add(MutationType(value))

        return discovered
