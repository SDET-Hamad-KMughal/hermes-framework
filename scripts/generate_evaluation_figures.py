"""Generate paper-ready HERMES evaluation figures."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read CSV rows."""

    with path.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        return list(csv.DictReader(handle))


def generate_group_anomaly_figure(
    rows: list[dict[str, str]],
    output: Path,
) -> None:
    """Plot anomaly rate by experiment group."""

    groups = [row["group"] for row in rows]
    rates = [
        float(row["anomaly_rate"]) * 100
        for row in rows
    ]

    plt.figure(figsize=(7, 4))
    plt.bar(groups, rates)
    plt.ylabel("Anomaly Rate (%)")
    plt.xlabel("Experiment Group")
    plt.title("Anomaly Rate by Experiment Group")
    plt.tight_layout()
    plt.savefig(output, dpi=300)
    plt.close()


def generate_workflow_anomaly_figure(
    rows: list[dict[str, str]],
    output: Path,
) -> None:
    """Plot anomaly rate by workflow."""

    workflows = [
        row["workflow_id"]
        for row in rows
    ]
    rates = [
        float(row["anomaly_rate"]) * 100
        for row in rows
    ]

    plt.figure(figsize=(9, 5))
    plt.bar(workflows, rates)
    plt.ylabel("Anomaly Rate (%)")
    plt.xlabel("Workflow")
    plt.title("Anomaly Rate by Benchmark Workflow")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output, dpi=300)
    plt.close()


def generate_strategy_divergence_figure(
    rows: list[dict[str, str]],
    output: Path,
) -> None:
    """Plot mean divergence by mutation strategy."""

    labels = [
        f"{row['group']}:{row['mutation_strategy']}"
        for row in rows
    ]
    scores = [
        float(row["mean_divergence_score"])
        for row in rows
    ]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, scores)
    plt.ylabel("Mean Divergence Score")
    plt.xlabel("Mutation Strategy")
    plt.title("Behavioral Divergence by Mutation Strategy")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(output, dpi=300)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input-dir",
        default="evaluation/tables",
    )
    parser.add_argument(
        "--output-dir",
        default="evaluation/figures",
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    group_rows = read_csv(
        input_dir / "group_summary.csv"
    )
    workflow_rows = read_csv(
        input_dir / "workflow_summary.csv"
    )
    strategy_rows = read_csv(
        input_dir
        / "mutation_strategy_summary.csv"
    )

    generate_group_anomaly_figure(
        group_rows,
        output_dir / "group_anomaly_rate.png",
    )
    generate_workflow_anomaly_figure(
        workflow_rows,
        output_dir / "workflow_anomaly_rate.png",
    )
    generate_strategy_divergence_figure(
        strategy_rows,
        output_dir / "strategy_divergence.png",
    )

    print(
        f"Generated: "
        f"{output_dir / 'group_anomaly_rate.png'}"
    )
    print(
        f"Generated: "
        f"{output_dir / 'workflow_anomaly_rate.png'}"
    )
    print(
        f"Generated: "
        f"{output_dir / 'strategy_divergence.png'}"
    )


if __name__ == "__main__":
    main()
