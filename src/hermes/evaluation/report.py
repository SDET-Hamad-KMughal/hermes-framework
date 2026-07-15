"""Evaluation report generation for HERMES."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from hermes.evaluation.models import EvaluationResult


class EvaluationReportWriter:
    """Save HERMES evaluation results as JSON and CSV."""

    @staticmethod
    def save_json(
        result: EvaluationResult,
        path: str | Path,
    ) -> Path:
        output = Path(path)
        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_text(
            json.dumps(
                result.to_dict(),
                indent=2,
            ),
            encoding="utf-8",
        )

        return output

    @staticmethod
    def save_csv(
        result: EvaluationResult,
        path: str | Path,
    ) -> Path:
        output = Path(path)
        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "mutation_workflow_id",
                    "execution_success",
                    "failed_steps",
                    "comparison_status",
                    "divergence_score",
                    "anomaly_detected",
                ],
            )

            writer.writeheader()

            for mutation in result.mutations:
                writer.writerow(
                    {
                        "mutation_workflow_id": (
                            mutation.mutation_workflow_id
                        ),
                        "execution_success": (
                            mutation.execution.success
                        ),
                        "failed_steps": (
                            mutation.execution.failed_steps
                        ),
                        "comparison_status": (
                            mutation.comparison.status.value
                        ),
                        "divergence_score": (
                            mutation.comparison.divergence_score
                        ),
                        "anomaly_detected": (
                            mutation.anomaly_detected
                        ),
                    }
                )

        return output
