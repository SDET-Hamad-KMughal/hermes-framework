"""Ground-truth anomaly models for HERMES."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class GroundTruthAnomaly:
    """Seeded business-logic anomaly."""

    anomaly_id: str
    workflow_id: str
    mutation_strategy: str
    expected_behavior: str
    description: str
    oracle: str
    severity: str = "medium"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in (
            "anomaly_id",
            "workflow_id",
            "mutation_strategy",
            "expected_behavior",
            "description",
            "oracle",
        ):
            value = getattr(self, field_name)
            if not str(value).strip():
                raise ValueError(
                    f"{field_name} must not be empty"
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "anomaly_id": self.anomaly_id,
            "workflow_id": self.workflow_id,
            "mutation_strategy": self.mutation_strategy,
            "expected_behavior": self.expected_behavior,
            "description": self.description,
            "oracle": self.oracle,
            "severity": self.severity,
            "metadata": dict(self.metadata),
        }
