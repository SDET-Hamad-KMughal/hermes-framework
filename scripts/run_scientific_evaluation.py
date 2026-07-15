"""Run the complete HERMES scientific evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hermes.evaluation import ExperimentRunner


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        default="evaluation/configs/experiment.json",
    )

    args = parser.parse_args()

    runner = ExperimentRunner(
        Path(args.config)
    )

    summary = runner.run()

    print("===================================")
    print("HERMES Scientific Evaluation Complete")
    print("===================================")
    print(
        f"Baseline records: "
        f"{summary['baseline_record_count']}"
    )
    print(
        f"Generic mutation records: "
        f"{summary['generic_mutation_record_count']}"
    )
    print(
        f"Hypothesis mutation records: "
        f"{summary['hypothesis_mutation_record_count']}"
    )
    print(
        f"Total records: "
        f"{summary['total_record_count']}"
    )
    print(
        f"Summary: "
        f"{summary['summary_path']}"
    )

    print()
    print(
        json.dumps(
            {
                "experiment_id": summary["experiment_id"],
                "benchmark": summary["benchmark"],
                "total_record_count": (
                    summary["total_record_count"]
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
