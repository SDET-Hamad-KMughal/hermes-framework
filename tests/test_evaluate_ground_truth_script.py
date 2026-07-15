"""Tests for the ground-truth evaluation script."""

import json

from scripts.evaluate_ground_truth import (
    evaluate_ground_truth,
)


def test_evaluate_ground_truth(tmp_path) -> None:
    ground_truth_path = tmp_path / "ground_truth.json"
    raw_directory = tmp_path / "raw"
    output_path = tmp_path / "output" / "metrics.json"

    raw_directory.mkdir()

    ground_truth_path.write_text(
        json.dumps(
            {
                "benchmark": "hermes-bench",
                "anomalies": [
                    {
                        "anomaly_id": "GT001",
                        "workflow_id": "checkout-flow",
                        "mutation_strategy": (
                            "remove_prerequisite"
                        ),
                        "expected_behavior": "reject",
                        "description": (
                            "Checkout without login."
                        ),
                        "oracle": "unexpected acceptance",
                        "severity": "high",
                        "metadata": {},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    (raw_directory / "record.json").write_text(
        json.dumps(
            {
                "group": "hypothesis_mutation",
                "source_workflow_id": "checkout-flow",
                "mutation_strategy": (
                    "remove_prerequisite"
                ),
                "anomaly_detected": True,
            }
        ),
        encoding="utf-8",
    )

    result = evaluate_ground_truth(
        ground_truth_path=ground_truth_path,
        raw_directory=raw_directory,
        output_path=output_path,
    )

    assert output_path.exists()
    assert result["ground_truth_anomaly_count"] == 1
    assert result["raw_record_count"] == 1
    assert result["metrics"]["true_positives"] == 1
    assert result["metrics"]["precision"] == 1.0
    assert result["metrics"]["recall"] == 1.0


def test_empty_ground_truth_is_supported(
    tmp_path,
) -> None:
    ground_truth_path = tmp_path / "ground_truth.json"
    raw_directory = tmp_path / "raw"
    output_path = tmp_path / "metrics.json"

    raw_directory.mkdir()

    ground_truth_path.write_text(
        json.dumps(
            {
                "benchmark": "hermes-bench",
                "anomalies": [],
            }
        ),
        encoding="utf-8",
    )

    result = evaluate_ground_truth(
        ground_truth_path=ground_truth_path,
        raw_directory=raw_directory,
        output_path=output_path,
    )

    assert result["ground_truth_anomaly_count"] == 0
    assert result["metrics"]["precision"] == 0.0
    assert result["metrics"]["recall"] == 0.0
