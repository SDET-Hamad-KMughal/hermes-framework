"""Tests for HERMES behavior comparison."""

import pytest

from hermes.comparator.comparator import (
    BehaviorComparator,
    ComparatorConfig,
)
from hermes.comparator.models import ComparisonStatus
from hermes.executor.models import (
    ExecutionStepResult,
    WorkflowExecutionResult,
)
from hermes.semantic.models import OperationType


def make_execution(
    workflow_id: str,
    *,
    successes: tuple[bool, ...] = (True,),
    final_url: str = "http://test/success",
    durations: tuple[float, ...] | None = None,
) -> WorkflowExecutionResult:
    if durations is None:
        durations = tuple(0.1 for _ in successes)

    steps = tuple(
        ExecutionStepResult(
            step_index=index,
            operation_type=OperationType.CHECKOUT,
            label="Checkout",
            success=success,
            url_before="http://test/cart",
            url_after=final_url,
            duration_seconds=durations[index],
            error=None if success else "step failed",
        )
        for index, success in enumerate(successes)
    )

    return WorkflowExecutionResult(
        workflow_id=workflow_id,
        workflow_name=workflow_id,
        steps=steps,
        started_at="start",
        finished_at="finish",
    )


def test_equivalent_executions() -> None:
    baseline = make_execution("baseline")
    mutated = make_execution("mutation")

    result = BehaviorComparator().compare(
        baseline,
        mutated,
    )

    assert result.status is ComparisonStatus.EQUIVALENT
    assert result.divergence_score == 0.0
    assert result.divergent_signals == 0


def test_success_difference_is_detected() -> None:
    baseline = make_execution(
        "baseline",
        successes=(True,),
    )
    mutated = make_execution(
        "mutation",
        successes=(False,),
    )

    result = BehaviorComparator().compare(
        baseline,
        mutated,
    )

    assert result.status is ComparisonStatus.DIVERGENT
    assert result.divergence_score > 0.0

    success_signal = next(
        signal
        for signal in result.signals
        if signal.signal_name == "workflow_success"
    )

    assert success_signal.equivalent is False


def test_final_url_difference_is_detected() -> None:
    baseline = make_execution(
        "baseline",
        final_url="http://test/success",
    )
    mutated = make_execution(
        "mutation",
        final_url="http://test/error",
    )

    result = BehaviorComparator().compare(
        baseline,
        mutated,
    )

    final_url_signal = next(
        signal
        for signal in result.signals
        if signal.signal_name == "final_url"
    )

    assert final_url_signal.equivalent is False


def test_step_outcome_difference_is_detected() -> None:
    baseline = make_execution(
        "baseline",
        successes=(True, True),
    )
    mutated = make_execution(
        "mutation",
        successes=(True, False),
    )

    result = BehaviorComparator().compare(
        baseline,
        mutated,
    )

    outcome_signal = next(
        signal
        for signal in result.signals
        if signal.signal_name == "step_outcomes"
    )

    assert outcome_signal.equivalent is False


def test_duration_within_tolerance_is_equivalent() -> None:
    comparator = BehaviorComparator(
        ComparatorConfig(
            duration_tolerance_seconds=0.5,
        )
    )

    baseline = make_execution(
        "baseline",
        durations=(1.0,),
    )
    mutated = make_execution(
        "mutation",
        durations=(1.4,),
    )

    result = comparator.compare(
        baseline,
        mutated,
    )

    duration_signal = next(
        signal
        for signal in result.signals
        if signal.signal_name == "execution_duration"
    )

    assert duration_signal.equivalent is True


def test_duration_outside_tolerance_is_divergent() -> None:
    comparator = BehaviorComparator(
        ComparatorConfig(
            duration_tolerance_seconds=0.2,
        )
    )

    baseline = make_execution(
        "baseline",
        durations=(1.0,),
    )
    mutated = make_execution(
        "mutation",
        durations=(2.0,),
    )

    result = comparator.compare(
        baseline,
        mutated,
    )

    duration_signal = next(
        signal
        for signal in result.signals
        if signal.signal_name == "execution_duration"
    )

    assert duration_signal.equivalent is False


def test_empty_execution_results_are_comparable() -> None:
    baseline = make_execution(
        "baseline",
        successes=(),
        durations=(),
    )
    mutated = make_execution(
        "mutation",
        successes=(),
        durations=(),
    )

    result = BehaviorComparator().compare(
        baseline,
        mutated,
    )

    assert result.status is ComparisonStatus.EQUIVALENT
    assert result.divergence_score == 0.0


@pytest.mark.parametrize(
    ("threshold", "tolerance", "message"),
    [
        (
            -0.1,
            1.0,
            "divergence_threshold must be between 0 and 1",
        ),
        (
            1.1,
            1.0,
            "divergence_threshold must be between 0 and 1",
        ),
        (
            0.3,
            -0.1,
            "duration_tolerance_seconds must not be negative",
        ),
    ],
)
def test_invalid_comparator_configuration(
    threshold: float,
    tolerance: float,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        ComparatorConfig(
            divergence_threshold=threshold,
            duration_tolerance_seconds=tolerance,
        )
