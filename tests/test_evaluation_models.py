"""Tests for HERMES evaluation models."""

import pytest

from hermes.comparator.models import (
    BehaviorComparisonResult,
    ComparisonStatus,
)
from hermes.evaluation.models import (
    EvaluationResult,
    MutationEvaluation,
)
from hermes.executor.models import WorkflowExecutionResult


def make_execution(workflow_id: str) -> WorkflowExecutionResult:
    return WorkflowExecutionResult(
        workflow_id=workflow_id,
        workflow_name=workflow_id,
        steps=(),
        started_at="start",
        finished_at="finish",
    )


def make_comparison(
    mutated_id: str,
    status: ComparisonStatus,
) -> BehaviorComparisonResult:
    return BehaviorComparisonResult(
        baseline_workflow_id="baseline",
        mutated_workflow_id=mutated_id,
        status=status,
        signals=(),
        divergence_score=(
            1.0
            if status is ComparisonStatus.DIVERGENT
            else 0.0
        ),
    )


def test_mutation_evaluation_detects_anomaly() -> None:
    mutation = MutationEvaluation(
        mutation_workflow_id="mutation-1",
        execution=make_execution("mutation-1"),
        comparison=make_comparison(
            "mutation-1",
            ComparisonStatus.DIVERGENT,
        ),
    )

    assert mutation.anomaly_detected is True


def test_evaluation_summary() -> None:
    baseline = make_execution("baseline")

    result = EvaluationResult(
        baseline_execution=baseline,
        mutations=(
            MutationEvaluation(
                mutation_workflow_id="mutation-1",
                execution=make_execution("mutation-1"),
                comparison=make_comparison(
                    "mutation-1",
                    ComparisonStatus.DIVERGENT,
                ),
            ),
            MutationEvaluation(
                mutation_workflow_id="mutation-2",
                execution=make_execution("mutation-2"),
                comparison=make_comparison(
                    "mutation-2",
                    ComparisonStatus.EQUIVALENT,
                ),
            ),
        ),
    )

    assert result.mutation_count == 2
    assert result.anomaly_count == 1
    assert result.equivalent_count == 1
    assert result.anomaly_rate == pytest.approx(0.5)


def test_empty_evaluation_has_zero_rate() -> None:
    result = EvaluationResult(
        baseline_execution=make_execution("baseline"),
        mutations=(),
    )

    assert result.mutation_count == 0
    assert result.anomaly_rate == 0.0


def test_evaluation_serialization() -> None:
    result = EvaluationResult(
        baseline_execution=make_execution("baseline"),
        mutations=(),
        metadata={"benchmark": "hermes-bench"},
    )

    data = result.to_dict()

    assert data["summary"]["mutation_count"] == 0
    assert data["metadata"]["benchmark"] == "hermes-bench"


def test_empty_mutation_id_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="mutation_workflow_id must not be empty",
    ):
        MutationEvaluation(
            mutation_workflow_id="",
            execution=make_execution("mutation"),
            comparison=make_comparison(
                "mutation",
                ComparisonStatus.EQUIVALENT,
            ),
        )
