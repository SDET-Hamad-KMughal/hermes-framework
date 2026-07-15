"""Tests for scientific evaluation aggregation."""

import json

import pytest

from hermes.evaluation.aggregation import (
    aggregate_group,
    aggregate_records,
    duration_statistics,
    load_raw_records,
    safe_rate,
    save_aggregation,
)


def baseline_record(
    *,
    success: bool = True,
    duration: float = 0.2,
) -> dict:
    return {
        "group": "baseline",
        "workflow_id": "login-flow",
        "success": success,
        "total_duration_seconds": duration,
    }


def mutation_record(
    *,
    group: str = "generic_mutation",
    success: bool = False,
    anomaly: bool = True,
    status: str = "divergent",
    score: float = 0.8,
    strategy: str = "skip_step",
    duration: float = 0.3,
) -> dict:
    return {
        "group": group,
        "source_workflow_id": "checkout-flow",
        "execution_success": success,
        "anomaly_detected": anomaly,
        "comparison_status": status,
        "divergence_score": score,
        "mutation_strategy": strategy,
        "total_duration_seconds": duration,
    }


def test_safe_rate() -> None:
    assert safe_rate(2, 4) == 0.5
    assert safe_rate(1, 0) == 0.0


def test_duration_statistics() -> None:
    statistics = duration_statistics(
        [
            {"total_duration_seconds": 1.0},
            {"total_duration_seconds": 3.0},
        ]
    )

    assert statistics["total_seconds"] == 4.0
    assert statistics["mean_seconds"] == 2.0
    assert statistics["median_seconds"] == 2.0
    assert statistics["minimum_seconds"] == 1.0
    assert statistics["maximum_seconds"] == 3.0


def test_empty_duration_statistics() -> None:
    statistics = duration_statistics([])

    assert statistics["total_seconds"] == 0.0
    assert statistics["mean_seconds"] == 0.0


def test_aggregate_baseline_group() -> None:
    summary = aggregate_group(
        "baseline",
        [
            baseline_record(success=True),
            baseline_record(success=False),
        ],
    )

    assert summary["record_count"] == 2
    assert summary["successful_executions"] == 1
    assert summary["failed_executions"] == 1
    assert summary["execution_success_rate"] == 0.5


def test_aggregate_mutation_group() -> None:
    summary = aggregate_group(
        "generic_mutation",
        [
            mutation_record(
                success=False,
                anomaly=True,
                status="divergent",
                score=0.8,
            ),
            mutation_record(
                success=True,
                anomaly=False,
                status="equivalent",
                score=0.2,
            ),
        ],
    )

    assert summary["record_count"] == 2
    assert summary["successful_executions"] == 1
    assert summary["anomaly_count"] == 1
    assert summary["anomaly_rate"] == 0.5
    assert summary["divergent_count"] == 1
    assert summary["equivalent_count"] == 1
    assert summary["mean_divergence_score"] == pytest.approx(
        0.5
    )


def test_mutation_strategy_counts() -> None:
    summary = aggregate_group(
        "hypothesis_mutation",
        [
            mutation_record(
                group="hypothesis_mutation",
                strategy="remove_prerequisite",
            ),
            mutation_record(
                group="hypothesis_mutation",
                strategy="remove_prerequisite",
            ),
            mutation_record(
                group="hypothesis_mutation",
                strategy="swap_operations",
            ),
        ],
    )

    assert summary["mutation_strategies"] == {
        "remove_prerequisite": 2,
        "swap_operations": 1,
    }


def test_aggregate_all_records() -> None:
    summary = aggregate_records(
        [
            baseline_record(),
            mutation_record(),
            mutation_record(
                group="hypothesis_mutation",
                anomaly=False,
                status="equivalent",
                score=0.1,
            ),
        ]
    )

    assert summary["total_record_count"] == 3
    assert summary["group_count"] == 3
    assert summary["mutation_record_count"] == 2
    assert summary["total_anomalies"] == 1
    assert summary["overall_mutation_anomaly_rate"] == 0.5


def test_load_raw_records(tmp_path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()

    (raw / "one.json").write_text(
        json.dumps(baseline_record()),
        encoding="utf-8",
    )

    (raw / "two.json").write_text(
        json.dumps(mutation_record()),
        encoding="utf-8",
    )

    records = load_raw_records(raw)

    assert len(records) == 2
    assert all("_source_file" in record for record in records)


def test_missing_raw_directory_is_rejected(
    tmp_path,
) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="raw evaluation directory not found",
    ):
        load_raw_records(tmp_path / "missing")


def test_save_aggregation(tmp_path) -> None:
    output = save_aggregation(
        {"total_record_count": 3},
        tmp_path / "aggregated" / "summary.json",
    )

    assert output.exists()

    payload = json.loads(
        output.read_text(encoding="utf-8")
    )

    assert payload["total_record_count"] == 3
