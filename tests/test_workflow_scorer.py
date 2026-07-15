"""Tests for HERMES workflow scoring."""

import pytest

from hermes.mutation.models import Workflow, WorkflowStep
from hermes.prioritizer.models import PrioritizationConfig
from hermes.prioritizer.scorer import WorkflowScorer
from hermes.semantic.models import OperationType
from hermes.workflow_generator.models import GeneratedWorkflow


def make_generated(
    workflow_id: str,
    operation_types: tuple[OperationType, ...],
    state_path: tuple[str, ...] | None = None,
) -> GeneratedWorkflow:
    steps = tuple(
        WorkflowStep(
            operation_type=operation_type,
            label=operation_type.value,
            source_state_id=f"state-{index}",
            target_state_id=f"state-{index + 1}",
        )
        for index, operation_type in enumerate(
            operation_types
        )
    )

    if state_path is None:
        state_path = tuple(
            f"state-{index}"
            for index in range(len(steps) + 1)
        )

    workflow = Workflow(
        workflow_id=workflow_id,
        name=workflow_id,
        steps=steps,
    )

    return GeneratedWorkflow(
        workflow=workflow,
        state_path=state_path,
        operation_count=len(steps),
        terminal_state_id=state_path[-1],
    )


def test_score_calculates_components() -> None:
    generated = make_generated(
        "checkout",
        (
            OperationType.LOGIN,
            OperationType.ADD_TO_CART,
            OperationType.CHECKOUT,
        ),
    )

    score = WorkflowScorer().score(
        generated,
        maximum_depth=6,
        total_state_count=6,
    )

    assert score.length_score == pytest.approx(0.5)
    assert score.state_coverage_score == pytest.approx(
        4 / 6
    )
    assert score.operation_diversity_score == 1.0
    assert score.business_operation_score == 1.0
    assert 0.0 <= score.total_score <= 1.0


def test_repeated_operations_reduce_diversity() -> None:
    generated = make_generated(
        "repeated-login",
        (
            OperationType.LOGIN,
            OperationType.LOGIN,
        ),
    )

    score = WorkflowScorer().score(
        generated,
        maximum_depth=4,
        total_state_count=4,
    )

    assert score.operation_diversity_score == 0.5


def test_non_business_operations_reduce_business_score() -> None:
    generated = make_generated(
        "mixed",
        (
            OperationType.LOGIN,
            OperationType.SEARCH,
        ),
    )

    score = WorkflowScorer().score(
        generated,
        maximum_depth=4,
        total_state_count=4,
    )

    assert score.business_operation_score == 0.5


def test_empty_workflow_has_zero_operation_scores() -> None:
    generated = make_generated(
        "empty",
        (),
        state_path=("home",),
    )

    score = WorkflowScorer().score(
        generated,
        maximum_depth=4,
        total_state_count=4,
    )

    assert score.length_score == 0.0
    assert score.operation_diversity_score == 0.0
    assert score.business_operation_score == 0.0


def test_scores_are_capped_at_one() -> None:
    generated = make_generated(
        "large",
        (
            OperationType.LOGIN,
            OperationType.ADD_TO_CART,
            OperationType.CHECKOUT,
        ),
        state_path=(
            "a",
            "b",
            "c",
            "d",
            "e",
        ),
    )

    score = WorkflowScorer().score(
        generated,
        maximum_depth=2,
        total_state_count=2,
    )

    assert score.length_score == 1.0
    assert score.state_coverage_score == 1.0


def test_rank_orders_highest_score_first() -> None:
    workflows = [
        make_generated(
            "login",
            (OperationType.LOGIN,),
        ),
        make_generated(
            "checkout",
            (
                OperationType.LOGIN,
                OperationType.ADD_TO_CART,
                OperationType.CHECKOUT,
            ),
        ),
    ]

    ranked = WorkflowScorer().rank(
        workflows,
        maximum_depth=4,
        total_state_count=5,
    )

    assert (
        ranked[0].generated_workflow.workflow.workflow_id
        == "checkout"
    )
    assert ranked[0].metadata["rank"] == 1
    assert ranked[1].metadata["rank"] == 2


def test_custom_weights_change_score() -> None:
    generated = make_generated(
        "login",
        (OperationType.LOGIN,),
    )

    scorer = WorkflowScorer(
        PrioritizationConfig(
            length_weight=1.0,
            state_coverage_weight=0.0,
            operation_diversity_weight=0.0,
            business_operation_weight=0.0,
        )
    )

    score = scorer.score(
        generated,
        maximum_depth=4,
        total_state_count=10,
    )

    assert score.total_score == pytest.approx(0.25)


@pytest.mark.parametrize(
    ("maximum_depth", "total_state_count", "message"),
    [
        (
            0,
            1,
            "maximum_depth must be at least 1",
        ),
        (
            1,
            0,
            "total_state_count must be at least 1",
        ),
    ],
)
def test_invalid_scoring_context(
    maximum_depth: int,
    total_state_count: int,
    message: str,
) -> None:
    generated = make_generated(
        "login",
        (OperationType.LOGIN,),
    )

    with pytest.raises(ValueError, match=message):
        WorkflowScorer().score(
            generated,
            maximum_depth=maximum_depth,
            total_state_count=total_state_count,
        )
