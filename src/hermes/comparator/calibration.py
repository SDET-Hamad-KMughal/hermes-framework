"""Behavior comparator calibration utilities."""

from __future__ import annotations

from dataclasses import dataclass

from hermes.comparator.models import SignalComparison


@dataclass(frozen=True, slots=True)
class SignalCalibration:
    """Weighting for one comparison signal."""

    signal_name: str
    weight: float

    def __post_init__(self) -> None:
        if not self.signal_name.strip():
            raise ValueError("signal_name must not be empty")

        if self.weight < 0:
            raise ValueError("weight must not be negative")


class ComparatorCalibration:
    """Apply calibrated weights to comparison signals."""

    DEFAULT_WEIGHTS = {
        "workflow_success": 3.0,
        "failed_steps": 2.0,
        "final_url": 2.5,
        "step_outcomes": 1.5,
        "execution_duration": 0.5,
    }

    def apply(
        self,
        signals: tuple[SignalComparison, ...],
    ) -> tuple[SignalComparison, ...]:

        calibrated = []

        for signal in signals:
            calibrated.append(
                SignalComparison(
                    signal_name=signal.signal_name,
                    baseline_value=signal.baseline_value,
                    mutated_value=signal.mutated_value,
                    equivalent=signal.equivalent,
                    weight=self.DEFAULT_WEIGHTS.get(
                        signal.signal_name,
                        signal.weight,
                    ),
                    details=signal.details,
                )
            )

        return tuple(calibrated)
