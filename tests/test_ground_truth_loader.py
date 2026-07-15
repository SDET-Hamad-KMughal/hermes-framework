"""Tests for ground-truth loader."""

import json

import pytest

from hermes.evaluation.ground_truth.loader import (
    load_ground_truth,
)


def sample_payload():
    return {
        "benchmark": "hermes-bench",
        "anomalies": [
            {
                "anomaly_id": "GT001",
                "workflow_id": "checkout",
                "mutation_strategy": "remove_login",
                "expected_behavior": "reject",
                "description": "Checkout without login.",
                "oracle": "checkout denied",
                "severity": "high",
                "metadata": {},
            }
        ],
    }


def test_load_ground_truth(tmp_path):
    file = tmp_path / "ground.json"

    file.write_text(
        json.dumps(sample_payload()),
        encoding="utf-8",
    )

    anomalies = load_ground_truth(file)

    assert len(anomalies) == 1
    assert anomalies[0].anomaly_id == "GT001"
    assert anomalies[0].severity == "high"


def test_missing_file(tmp_path):
    with pytest.raises(
        FileNotFoundError,
        match="ground-truth file not found",
    ):
        load_ground_truth(
            tmp_path / "missing.json"
        )


def test_empty_anomalies(tmp_path):
    file = tmp_path / "ground.json"

    file.write_text(
        json.dumps(
            {
                "benchmark": "hermes",
                "anomalies": [],
            }
        ),
        encoding="utf-8",
    )

    anomalies = load_ground_truth(file)

    assert anomalies == []
