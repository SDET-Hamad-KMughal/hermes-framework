"""Tests for comparator calibration."""

import pytest

from hermes.comparator.calibration import (
    ComparatorCalibration,
    SignalCalibration,
)
from hermes.comparator.models import SignalComparison


def test_apply_default_weights() -> None:
    signals = (
        SignalComparison(
            signal_name="workflow_success",
            baseline_value=True,
            mutated_value=False,
            equivalent=False,
        ),
        SignalComparison(
            signal_name="execution_duration",
            baseline_value=1.0,
            mutated_value=1.5,
            equivalent=False,
        ),
    )

    calibrated = ComparatorCalibration().apply(signals)

    assert calibrated[0].weight == 3.0
    assert calibrated[1].weight == 0.5


def test_unknown_signal_keeps_weight() -> None:
    signal = SignalComparison(
        signal_name="custom_signal",
        baseline_value=1,
        mutated_value=2,
        equivalent=False,
        weight=4.2,
    )

    calibrated = ComparatorCalibration().apply((signal,))

    assert calibrated[0].weight == 4.2


@pytest.mark.parametrize(
    ("name", "weight", "message"),
    [
        ("", 1.0, "signal_name must not be empty"),
        ("signal", -1.0, "weight must not be negative"),
    ],
)
def test_invalid_signal_calibration(
    name: str,
    weight: float,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        SignalCalibration(
            signal_name=name,
            weight=weight,
        )
