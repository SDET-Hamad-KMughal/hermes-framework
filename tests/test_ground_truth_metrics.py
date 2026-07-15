"""Tests for HERMES ground-truth detection metrics."""

import pytest

from hermes.evaluation.ground_truth.metrics import (
    DetectionMetrics,
    anomaly_key,
    evaluate_detection_metrics,
)
from hermes.evaluation.ground_truth.models import (
    GroundTruthAnomaly,
)


def make_anomaly(
    workflow_id: str,
    strategy: str,
) -> GroundTruthAnomaly:
    return GroundTruthAnomaly(
        anomaly_id=f"{workflow_id}-{strategy}",
        workflow_id=workflow_id,
        mutation_strategy=strategy,
        expected_behavior="reject",
        description="Seeded anomaly.",
        oracle="unexpected acceptance",
    )


def test_detection_metric_properties() -> None:
    metrics = DetectionMetrics(
        true_positives=8,
        false_positives=2,
        false_negatives=2,
        true_negatives=8,
    )

    assert metrics.precision == pytest.approx(0.8)
    assert metrics.recall == pytest.approx(0.8)
    assert metrics.f1_score == pytest.approx(0.8)
    assert metrics.accuracy == pytest.approx(0.8)


def test_zero_safe_metrics() -> None:
    metrics = DetectionMetrics(
        true_positives=0,
        false_positives=0,
        false_negatives=0,
        true_negatives=0,
    )

    assert metrics.precision == 0.0
    assert metrics.recall == 0.0
    assert metrics.f1_score == 0.0
    assert metrics.accuracy == 0.0


def test_metrics_serialization() -> None:
    data = DetectionMetrics(
        true_positives=1,
        false_positives=2,
        false_negatives=3,
        true_negatives=4,
    ).to_dict()

    assert data["true_positives"] == 1
    assert "precision" in data
    assert "f1_score" in data


def test_anomaly_key() -> None:
    assert anomaly_key(
        " checkout ",
        " skip_step ",
    ) == (
        "checkout",
        "skip_step",
    )


def test_evaluate_detection_metrics() -> None:
    ground_truth = [
        make_anomaly(
            "checkout-flow",
            "remove_prerequisite",
        ),
        make_anomaly(
            "wallet-flow",
            "duplicate_operation",
        ),
    ]

    records = [
        {
            "group": "hypothesis_mutation",
            "source_workflow_id": "checkout-flow",
            "mutation_strategy": "remove_prerequisite",
            "anomaly_detected": True,
        },
        {
            "group": "hypothesis_mutation",
            "source_workflow_id": "wallet-flow",
            "mutation_strategy": "duplicate_operation",
            "anomaly_detected": False,
        },
        {
            "group": "generic_mutation",
            "source_workflow_id": "login-flow",
            "mutation_strategy": "skip_step",
            "anomaly_detected": True,
        },
        {
            "group": "generic_mutation",
            "source_workflow_id": "cart-flow",
            "mutation_strategy": "duplicate_step",
            "anomaly_detected": False,
        },
    ]

    metrics = evaluate_detection_metrics(
        ground_truth,
        records,
    )

    assert metrics.true_positives == 1
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 1
    assert metrics.true_negatives == 1
    assert metrics.precision == pytest.approx(0.5)
    assert metrics.recall == pytest.approx(0.5)
    assert metrics.f1_score == pytest.approx(0.5)


def test_baseline_records_are_ignored() -> None:
    metrics = evaluate_detection_metrics(
        [],
        [
            {
                "group": "baseline",
                "workflow_id": "login-flow",
                "mutation_strategy": "skip_step",
                "anomaly_detected": True,
            }
        ],
    )

    assert metrics.to_dict() == {
        "true_positives": 0,
        "false_positives": 0,
        "false_negatives": 0,
        "true_negatives": 0,
        "precision": 0.0,
        "recall": 0.0,
        "f1_score": 0.0,
        "accuracy": 0.0,
    }
