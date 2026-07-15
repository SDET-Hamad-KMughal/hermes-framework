"""Evaluate HERMES detections against seeded ground truth."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hermes.evaluation.aggregation import load_raw_records
from hermes.evaluation.ground_truth import (
    evaluate_detection_metrics,
    load_ground_truth,
)


def evaluate_ground_truth(
    *,
    ground_truth_path: Path,
    raw_directory: Path,
    output_path: Path,
) -> dict:
    """Calculate and persist detection metrics."""

    anomalies = load_ground_truth(
        ground_truth_path
    )
    records = load_raw_records(
        raw_directory
    )

    metrics = evaluate_detection_metrics(
        anomalies,
        records,
    )

    result = {
        "ground_truth_anomaly_count": len(anomalies),
        "raw_record_count": len(records),
        "metrics": metrics.to_dict(),
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output_path.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    return result


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--ground-truth",
        default=(
            "evaluation/ground_truth/"
            "hermes_bench.json"
        ),
    )
    parser.add_argument(
        "--raw-dir",
        default="evaluation/raw",
    )
    parser.add_argument(
        "--output",
        default=(
            "evaluation/aggregated/"
            "ground_truth_metrics.json"
        ),
    )

    args = parser.parse_args()

    result = evaluate_ground_truth(
        ground_truth_path=Path(args.ground_truth),
        raw_directory=Path(args.raw_dir),
        output_path=Path(args.output),
    )

    metrics = result["metrics"]

    print("===================================")
    print("HERMES Ground-Truth Evaluation")
    print("===================================")
    print(
        f"Ground-truth anomalies: "
        f"{result['ground_truth_anomaly_count']}"
    )
    print(
        f"Raw records: "
        f"{result['raw_record_count']}"
    )
    print(f"True positives: {metrics['true_positives']}")
    print(f"False positives: {metrics['false_positives']}")
    print(f"False negatives: {metrics['false_negatives']}")
    print(f"True negatives: {metrics['true_negatives']}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1 score: {metrics['f1_score']:.4f}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
