"""Evaluation pipeline for HERMES."""

from __future__ import annotations

from hermes.comparator import BehaviorComparator
from hermes.evaluation.models import (
    EvaluationResult,
    MutationEvaluation,
)
from hermes.executor import WorkflowExecutionRunner
from hermes.mutation import (
    MutationPlan,
    Workflow,
    WorkflowMutationEngine,
)


class EvaluationPipeline:
    """Execute baseline and mutated workflows."""

    def __init__(
        self,
        runner: WorkflowExecutionRunner,
        comparator: BehaviorComparator,
        mutation_plan: MutationPlan | None = None,
    ) -> None:

        self.runner = runner
        self.comparator = comparator
        self.mutation_engine = WorkflowMutationEngine(
            mutation_plan
        )

    def evaluate(
        self,
        context,
        workflow: Workflow,
    ) -> EvaluationResult:

        baseline_execution = self.runner.execute(
            context,
            workflow,
        )

        mutation_results = []

        for mutation in self.mutation_engine.generate(
            workflow
        ):

            execution = self.runner.execute(
                context,
                mutation,
            )

            comparison = self.comparator.compare(
                baseline_execution,
                execution,
            )

            mutation_results.append(
                MutationEvaluation(
                    mutation_workflow_id=mutation.workflow_id,
                    execution=execution,
                    comparison=comparison,
                )
            )

        return EvaluationResult(
            baseline_execution=baseline_execution,
            mutations=tuple(mutation_results),
        )
