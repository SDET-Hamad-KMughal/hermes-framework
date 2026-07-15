"""Tests for HERMES behavior-comparison models."""

import pytest

from hermes.comparator.models import (
    BehaviorComparisonResult,
    ComparisonStatus,
    SignalComparison,
)


def make_signal(equivalent: bool) -> SignalComparison:
    return SignalComparison(
        signal_name="success",
        baseline_value=True,
        mutated_value=equivalent,
        equivalent=equivalent,
    )


def test_create_signal_comparison() -> None:
    signal = make_signal(True)

    assert signal.signal_name == "success"
    assert signal.equivalent is True
    assert signal.weight == 1.0


def test_signal_serialization() -> None:
    signal = make_signal(False)

    data = signal.to_dict()

    assert data["signal_name"] == "success"
    assert data["equivalent"] is False


def test_create_behavior_comparison_result() -> None:
    result = BehaviorComparisonResult(
        baseline_workflow_id="baseline",
        mutated_workflow_id="mutation-1",
        status=ComparisonStatus.DIVERGENT,
        signals=(
            make_signal(True),
            make_signal(False),
        ),
        divergence_score=0.5,
    )

    assert result.divergent_signals == 1
    assert result.equivalent_signals == 1
    assert result.status is ComparisonStatus.DIVERGENT


def test_comparison_result_serialization() -> None:
    result = BehaviorComparisonResult(
        baseline_workflow_id="baseline",
        mutated_workflow_id="mutation-1",
        status=ComparisonStatus.EQUIVALENT,
        signals=(make_signal(True),),
        divergence_score=0.0,
    )

    data = result.to_dict()

    assert data["status"] == "equivalent"
    assert data["divergence_score"] == 0.0
    assert len(data["signals"]) == 1


@pytest.mark.parametrize(
    ("signal_name", "weight", "message"),
    [
        ("", 1.0, "signal_name must not be empty"),
        ("success", -1.0, "weight must not be negative"),
    ],
)
def test_invalid_signal_is_rejected(
    signal_name: str,
    weight: float,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        SignalComparison(
            signal_name=signal_name,
            baseline_value=True,
            mutated_value=False,
            equivalent=False,
            weight=weight,
        )


@pytest.mark.parametrize(
    (
        "baseline_id",
        "mutated_id",
        "score",
        "message",
    ),
    [
        (
            "",
            "mutation",
            0.0,
            "baseline_workflow_id must not be empty",
        ),
        (
            "baseline",
            "",
            0.0,
            "mutated_workflow_id must not be empty",
        ),
        (
            "baseline",
            "mutation",
            -0.1,
            "divergence_score must be between 0 and 1",
        ),
        (
            "baseline",
            "mutation",
            1.1,
            "divergence_score must be between 0 and 1",
        ),
    ],
)
def test_invalid_comparison_result_is_rejected(
    baseline_id: str,
    mutated_id: str,
    score: float,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        BehaviorComparisonResult(
            baseline_workflow_id=baseline_id,
            mutated_workflow_id=mutated_id,
            status=ComparisonStatus.INCONCLUSIVE,
            signals=(),
            divergence_score=score,
        )
