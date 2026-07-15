"""Scientific evaluation result aggregation for HERMES."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any


def load_raw_records(
    raw_directory: str | Path,
) -> list[dict[str, Any]]:
    """Load all raw scientific-evaluation records."""

    directory = Path(raw_directory)

    if not directory.exists():
        raise FileNotFoundError(
            f"raw evaluation directory not found: {directory}"
        )

    records: list[dict[str, Any]] = []

    for path in sorted(directory.glob("*.json")):
        payload = json.loads(
            path.read_text(encoding="utf-8")
        )

        if isinstance(payload, dict):
            payload["_source_file"] = str(path)
            records.append(payload)

    return records


def safe_rate(
    numerator: int,
    denominator: int,
) -> float:
    """Return a zero-safe ratio."""

    if denominator == 0:
        return 0.0

    return numerator / denominator


def duration_statistics(
    records: list[dict[str, Any]],
) -> dict[str, float]:
    """Calculate duration statistics for records."""

    durations = [
        float(record.get("total_duration_seconds", 0.0))
        for record in records
        if record.get("total_duration_seconds") is not None
    ]

    if not durations:
        return {
            "total_seconds": 0.0,
            "mean_seconds": 0.0,
            "median_seconds": 0.0,
            "minimum_seconds": 0.0,
            "maximum_seconds": 0.0,
        }

    return {
        "total_seconds": sum(durations),
        "mean_seconds": mean(durations),
        "median_seconds": median(durations),
        "minimum_seconds": min(durations),
        "maximum_seconds": max(durations),
    }


def aggregate_group(
    group_name: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Aggregate metrics for one experiment group."""

    record_count = len(records)

    if group_name == "baseline":
        successful = sum(
            1
            for record in records
            if record.get("success") is True
        )

        failed = record_count - successful

        return {
            "group": group_name,
            "record_count": record_count,
            "successful_executions": successful,
            "failed_executions": failed,
            "execution_success_rate": safe_rate(
                successful,
                record_count,
            ),
            "duration": duration_statistics(records),
        }

    successful = sum(
        1
        for record in records
        if record.get("execution_success") is True
    )

    failed = record_count - successful

    anomaly_count = sum(
        1
        for record in records
        if record.get("anomaly_detected") is True
    )

    equivalent_count = sum(
        1
        for record in records
        if record.get("comparison_status") == "equivalent"
    )

    divergent_count = sum(
        1
        for record in records
        if record.get("comparison_status") == "divergent"
    )

    divergence_scores = [
        float(record.get("divergence_score", 0.0))
        for record in records
        if record.get("divergence_score") is not None
    ]

    mutation_strategies = Counter(
        str(record.get("mutation_strategy", "unknown"))
        for record in records
    )

    return {
        "group": group_name,
        "record_count": record_count,
        "successful_executions": successful,
        "failed_executions": failed,
        "execution_success_rate": safe_rate(
            successful,
            record_count,
        ),
        "anomaly_count": anomaly_count,
        "anomaly_rate": safe_rate(
            anomaly_count,
            record_count,
        ),
        "equivalent_count": equivalent_count,
        "divergent_count": divergent_count,
        "mean_divergence_score": (
            mean(divergence_scores)
            if divergence_scores
            else 0.0
        ),
        "median_divergence_score": (
            median(divergence_scores)
            if divergence_scores
            else 0.0
        ),
        "mutation_strategies": dict(
            sorted(mutation_strategies.items())
        ),
        "duration": duration_statistics(records),
    }


def aggregate_records(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Aggregate all scientific-evaluation records."""

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for record in records:
        group_name = str(
            record.get("group", "unknown")
        )
        grouped[group_name].append(record)

    group_summaries = {
        group_name: aggregate_group(
            group_name,
            group_records,
        )
        for group_name, group_records in sorted(
            grouped.items()
        )
    }

    mutation_records = [
        record
        for record in records
        if record.get("group") in {
            "generic_mutation",
            "hypothesis_mutation",
        }
    ]

    total_anomalies = sum(
        1
        for record in mutation_records
        if record.get("anomaly_detected") is True
    )

    workflow_counts = Counter(
        str(
            record.get(
                "source_workflow_id",
                record.get("workflow_id", "unknown"),
            )
        )
        for record in records
    )

    return {
        "total_record_count": len(records),
        "group_count": len(group_summaries),
        "mutation_record_count": len(mutation_records),
        "total_anomalies": total_anomalies,
        "overall_mutation_anomaly_rate": safe_rate(
            total_anomalies,
            len(mutation_records),
        ),
        "workflow_record_counts": dict(
            sorted(workflow_counts.items())
        ),
        "groups": group_summaries,
    }


def save_aggregation(
    summary: dict[str, Any],
    output: str | Path,
) -> Path:
    """Save an aggregated scientific-evaluation summary."""

    path = Path(output)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return path
