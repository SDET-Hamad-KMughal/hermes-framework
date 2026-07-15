"""Tests for HERMES evaluation tables."""

import csv

from hermes.evaluation.tables import (
    build_group_rows,
    build_strategy_rows,
    build_workflow_rows,
    write_csv,
)


def test_build_group_rows() -> None:
    summary = {
        "groups": {
            "baseline": {
                "record_count": 2,
                "successful_executions": 2,
                "failed_executions": 0,
                "execution_success_rate": 1.0,
                "duration": {
                    "mean_seconds": 0.25,
                },
            }
        }
    }

    rows = build_group_rows(summary)

    assert len(rows) == 1
    assert rows[0]["group"] == "baseline"
    assert rows[0]["record_count"] == 2
    assert rows[0]["mean_duration_seconds"] == 0.25


def test_build_workflow_rows() -> None:
    records = [
        {
            "group": "baseline",
            "workflow_id": "checkout-flow",
            "total_duration_seconds": 0.2,
        },
        {
            "group": "generic_mutation",
            "source_workflow_id": "checkout-flow",
            "anomaly_detected": True,
            "total_duration_seconds": 0.4,
        },
        {
            "group": "hypothesis_mutation",
            "source_workflow_id": "checkout-flow",
            "anomaly_detected": False,
            "total_duration_seconds": 0.3,
        },
    ]

    rows = build_workflow_rows(records)

    assert len(rows) == 1
    assert rows[0]["workflow_id"] == "checkout-flow"
    assert rows[0]["record_count"] == 3
    assert rows[0]["mutation_record_count"] == 2
    assert rows[0]["anomaly_count"] == 1
    assert rows[0]["anomaly_rate"] == 0.5


def test_build_strategy_rows() -> None:
    records = [
        {
            "group": "generic_mutation",
            "mutation_strategy": "skip_step",
            "execution_success": False,
            "anomaly_detected": True,
            "divergence_score": 0.8,
        },
        {
            "group": "generic_mutation",
            "mutation_strategy": "skip_step",
            "execution_success": True,
            "anomaly_detected": False,
            "divergence_score": 0.2,
        },
    ]

    rows = build_strategy_rows(records)

    assert len(rows) == 1
    assert rows[0]["mutation_strategy"] == "skip_step"
    assert rows[0]["record_count"] == 2
    assert rows[0]["successful_executions"] == 1
    assert rows[0]["execution_success_rate"] == 0.5
    assert rows[0]["anomaly_rate"] == 0.5
    assert rows[0]["mean_divergence_score"] == 0.5


def test_write_csv(tmp_path) -> None:
    output = write_csv(
        [
            {
                "group": "baseline",
                "record_count": 5,
            }
        ],
        tmp_path / "tables" / "summary.csv",
        [
            "group",
            "record_count",
        ],
    )

    assert output.exists()

    with output.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert rows[0]["group"] == "baseline"
    assert rows[0]["record_count"] == "5"
