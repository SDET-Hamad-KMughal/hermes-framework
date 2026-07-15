"""Paper-ready evaluation tables for HERMES."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


def write_csv(
    rows: list[dict[str, Any]],
    output: str | Path,
    fieldnames: list[str],
) -> Path:
    """Write rows to a CSV file."""

    path = Path(output)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)

    return path


def build_group_rows(
    summary: dict[str, Any],
) -> list[dict[str, Any]]:
    """Create one summary row per experiment group."""

    rows: list[dict[str, Any]] = []

    for group_name, metrics in sorted(
        summary.get("groups", {}).items()
    ):
        duration = metrics.get("duration", {})

        rows.append(
            {
                "group": group_name,
                "record_count": metrics.get(
                    "record_count",
                    0,
                ),
                "successful_executions": metrics.get(
                    "successful_executions",
                    0,
                ),
                "failed_executions": metrics.get(
                    "failed_executions",
                    0,
                ),
                "execution_success_rate": metrics.get(
                    "execution_success_rate",
                    0.0,
                ),
                "anomaly_count": metrics.get(
                    "anomaly_count",
                    0,
                ),
                "anomaly_rate": metrics.get(
                    "anomaly_rate",
                    0.0,
                ),
                "mean_divergence_score": metrics.get(
                    "mean_divergence_score",
                    0.0,
                ),
                "mean_duration_seconds": duration.get(
                    "mean_seconds",
                    0.0,
                ),
            }
        )

    return rows


def build_workflow_rows(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Aggregate records by source workflow."""

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for record in records:
        workflow_id = str(
            record.get(
                "source_workflow_id",
                record.get(
                    "workflow_id",
                    "unknown",
                ),
            )
        )
        grouped[workflow_id].append(record)

    rows: list[dict[str, Any]] = []

    for workflow_id, workflow_records in sorted(
        grouped.items()
    ):
        mutation_records = [
            record
            for record in workflow_records
            if record.get("group") != "baseline"
        ]

        anomaly_count = sum(
            1
            for record in mutation_records
            if record.get("anomaly_detected") is True
        )

        durations = [
            float(
                record.get(
                    "total_duration_seconds",
                    0.0,
                )
            )
            for record in workflow_records
        ]

        rows.append(
            {
                "workflow_id": workflow_id,
                "record_count": len(
                    workflow_records
                ),
                "mutation_record_count": len(
                    mutation_records
                ),
                "anomaly_count": anomaly_count,
                "anomaly_rate": (
                    anomaly_count
                    / len(mutation_records)
                    if mutation_records
                    else 0.0
                ),
                "mean_duration_seconds": (
                    mean(durations)
                    if durations
                    else 0.0
                ),
            }
        )

    return rows


def build_strategy_rows(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Aggregate mutation results by strategy and group."""

    grouped: dict[
        tuple[str, str],
        list[dict[str, Any]],
    ] = defaultdict(list)

    for record in records:
        if record.get("group") == "baseline":
            continue

        key = (
            str(record.get("group", "unknown")),
            str(
                record.get(
                    "mutation_strategy",
                    "unknown",
                )
            ),
        )
        grouped[key].append(record)

    rows: list[dict[str, Any]] = []

    for (
        group_name,
        strategy,
    ), strategy_records in sorted(grouped.items()):
        anomaly_count = sum(
            1
            for record in strategy_records
            if record.get("anomaly_detected") is True
        )

        successful = sum(
            1
            for record in strategy_records
            if record.get("execution_success") is True
        )

        divergence_scores = [
            float(record.get("divergence_score", 0.0))
            for record in strategy_records
        ]

        rows.append(
            {
                "group": group_name,
                "mutation_strategy": strategy,
                "record_count": len(
                    strategy_records
                ),
                "successful_executions": successful,
                "execution_success_rate": (
                    successful
                    / len(strategy_records)
                ),
                "anomaly_count": anomaly_count,
                "anomaly_rate": (
                    anomaly_count
                    / len(strategy_records)
                ),
                "mean_divergence_score": (
                    mean(divergence_scores)
                    if divergence_scores
                    else 0.0
                ),
            }
        )

    return rows
