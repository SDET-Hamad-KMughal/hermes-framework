"""Aggregate HERMES scientific evaluation records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hermes.evaluation.aggregation import (
    aggregate_records,
    load_raw_records,
    save_aggregation,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--raw-dir",
        default="evaluation/raw",
    )
    parser.add_argument(
        "--output",
        default=(
            "evaluation/aggregated/"
            "evaluation_metrics.json"
        ),
    )

    args = parser.parse_args()

    records = load_raw_records(
        Path(args.raw_dir)
    )

    summary = aggregate_records(records)

    output = save_aggregation(
        summary,
        Path(args.output),
    )

    print("===================================")
    print("HERMES Evaluation Aggregation Complete")
    print("===================================")
    print(
        f"Raw records: "
        f"{summary['total_record_count']}"
    )
    print(
        f"Mutation records: "
        f"{summary['mutation_record_count']}"
    )
    print(
        f"Detected anomalies: "
        f"{summary['total_anomalies']}"
    )
    print(
        f"Overall mutation anomaly rate: "
        f"{summary['overall_mutation_anomaly_rate']:.2%}"
    )
    print(f"Output: {output}")

    print()
    print(
        json.dumps(
            summary["groups"],
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
