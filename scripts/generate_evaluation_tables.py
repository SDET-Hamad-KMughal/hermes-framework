"""Generate paper-ready HERMES evaluation tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hermes.evaluation.aggregation import load_raw_records
from hermes.evaluation.tables import (
    build_group_rows,
    build_strategy_rows,
    build_workflow_rows,
    write_csv,
)


def generate_tables(
    *,
    raw_directory: Path,
    aggregated_summary: Path,
    output_directory: Path,
) -> dict[str, Path]:
    """Generate all scientific-evaluation CSV tables."""

    records = load_raw_records(raw_directory)

    summary = json.loads(
        aggregated_summary.read_text(
            encoding="utf-8"
        )
    )

    group_rows = build_group_rows(summary)
    workflow_rows = build_workflow_rows(records)
    strategy_rows = build_strategy_rows(records)

    group_path = write_csv(
        group_rows,
        output_directory / "group_summary.csv",
        [
            "group",
            "record_count",
            "successful_executions",
            "failed_executions",
            "execution_success_rate",
            "anomaly_count",
            "anomaly_rate",
            "mean_divergence_score",
            "mean_duration_seconds",
        ],
    )

    workflow_path = write_csv(
        workflow_rows,
        output_directory / "workflow_summary.csv",
        [
            "workflow_id",
            "record_count",
            "mutation_record_count",
            "anomaly_count",
            "anomaly_rate",
            "mean_duration_seconds",
        ],
    )

    strategy_path = write_csv(
        strategy_rows,
        output_directory / "mutation_strategy_summary.csv",
        [
            "group",
            "mutation_strategy",
            "record_count",
            "successful_executions",
            "execution_success_rate",
            "anomaly_count",
            "anomaly_rate",
            "mean_divergence_score",
        ],
    )

    return {
        "group_summary": group_path,
        "workflow_summary": workflow_path,
        "mutation_strategy_summary": strategy_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--raw-dir",
        default="evaluation/raw",
    )
    parser.add_argument(
        "--summary",
        default=(
            "evaluation/aggregated/"
            "evaluation_metrics.json"
        ),
    )
    parser.add_argument(
        "--output-dir",
        default="evaluation/tables",
    )

    args = parser.parse_args()

    outputs = generate_tables(
        raw_directory=Path(args.raw_dir),
        aggregated_summary=Path(args.summary),
        output_directory=Path(args.output_dir),
    )

    print("===================================")
    print("HERMES Evaluation Tables Generated")
    print("===================================")

    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
