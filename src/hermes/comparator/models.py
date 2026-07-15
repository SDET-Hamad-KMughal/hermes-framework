"""Behavior-comparison models for HERMES."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class ComparisonStatus(str, Enum):
    """Overall behavior-comparison outcome."""

    EQUIVALENT = "equivalent"
    DIVERGENT = "divergent"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True, slots=True)
class SignalComparison:
    """Comparison result for one behavioral signal."""

    signal_name: str
    baseline_value: Any
    mutated_value: Any
    equivalent: bool
    weight: float = 1.0
    details: str | None = None

    def __post_init__(self) -> None:
        if not self.signal_name.strip():
            raise ValueError("signal_name must not be empty")

        if self.weight < 0:
            raise ValueError("weight must not be negative")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BehaviorComparisonResult:
    """Complete comparison between baseline and mutated executions."""

    baseline_workflow_id: str
    mutated_workflow_id: str
    status: ComparisonStatus
    signals: tuple[SignalComparison, ...]
    divergence_score: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.baseline_workflow_id.strip():
            raise ValueError(
                "baseline_workflow_id must not be empty"
            )

        if not self.mutated_workflow_id.strip():
            raise ValueError(
                "mutated_workflow_id must not be empty"
            )

        if not 0.0 <= self.divergence_score <= 1.0:
            raise ValueError(
                "divergence_score must be between 0 and 1"
            )

    @property
    def divergent_signals(self) -> int:
        return sum(
            1
            for signal in self.signals
            if not signal.equivalent
        )

    @property
    def equivalent_signals(self) -> int:
        return sum(
            1
            for signal in self.signals
            if signal.equivalent
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_workflow_id": self.baseline_workflow_id,
            "mutated_workflow_id": self.mutated_workflow_id,
            "status": self.status.value,
            "divergence_score": self.divergence_score,
            "divergent_signals": self.divergent_signals,
            "equivalent_signals": self.equivalent_signals,
            "signals": [
                signal.to_dict()
                for signal in self.signals
            ],
            "metadata": dict(self.metadata),
        }
