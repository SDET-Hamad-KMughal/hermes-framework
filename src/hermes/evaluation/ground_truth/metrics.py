"""Ground-truth detection metrics for HERMES."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hermes.evaluation.ground_truth.models import (
    GroundTruthAnomaly,
)


@dataclass(frozen=True, slots=True)
class DetectionMetrics:
    """Precision, recall, and F1 for anomaly detection."""

    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int

    @property
    def precision(self) -> float:
        denominator = (
            self.true_positives
            + self.false_positives
        )

        if denominator == 0:
            return 0.0

        return self.true_positives / denominator

    @property
    def recall(self) -> float:
        denominator = (
            self.true_positives
            + self.false_negatives
        )

        if denominator == 0:
            return 0.0

        return self.true_positives / denominator

    @property
    def f1_score(self) -> float:
        denominator = self.precision + self.recall

        if denominator == 0:
            return 0.0

        return (
            2
            * self.precision
            * self.recall
            / denominator
        )

    @property
    def accuracy(self) -> float:
        total = (
            self.true_positives
            + self.false_positives
            + self.false_negatives
            + self.true_negatives
        )

        if total == 0:
            return 0.0

        return (
            self.true_positives
            + self.true_negatives
        ) / total

    def to_dict(self) -> dict[str, Any]:
        return {
            "true_positives": self.true_positives,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            "true_negatives": self.true_negatives,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "accuracy": self.accuracy,
        }


def anomaly_key(
    workflow_id: str,
    mutation_strategy: str,
) -> tuple[str, str]:
    """Return the matching key for one anomaly."""

    return (
        workflow_id.strip(),
        mutation_strategy.strip(),
    )


def evaluate_detection_metrics(
    ground_truth: list[GroundTruthAnomaly],
    records: list[dict[str, Any]],
) -> DetectionMetrics:
    """Compare detected anomalies with known ground truth."""

    known_anomalies = {
        anomaly_key(
            anomaly.workflow_id,
            anomaly.mutation_strategy,
        )
        for anomaly in ground_truth
    }

    evaluated_keys: set[tuple[str, str]] = set()
    detected_keys: set[tuple[str, str]] = set()

    for record in records:
        if record.get("group") == "baseline":
            continue

        workflow_id = str(
            record.get(
                "source_workflow_id",
                record.get("workflow_id", ""),
            )
        )

        mutation_strategy = str(
            record.get(
                "mutation_strategy",
                "",
            )
        )

        if not workflow_id or not mutation_strategy:
            continue

        key = anomaly_key(
            workflow_id,
            mutation_strategy,
        )

        evaluated_keys.add(key)

        if record.get("anomaly_detected") is True:
            detected_keys.add(key)

    true_positives = len(
        detected_keys & known_anomalies
    )

    false_positives = len(
        detected_keys - known_anomalies
    )

    false_negatives = len(
        known_anomalies - detected_keys
    )

    true_negatives = len(
        (
            evaluated_keys
            - known_anomalies
        )
        - detected_keys
    )

    return DetectionMetrics(
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        true_negatives=true_negatives,
    )
