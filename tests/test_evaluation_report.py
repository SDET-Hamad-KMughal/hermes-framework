"""Tests for HERMES evaluation report generation."""

import csv
import json

from hermes.comparator.models import (
    BehaviorComparisonResult,
    ComparisonStatus,
)
from hermes.evaluation.models import (
    EvaluationResult,
    MutationEvaluation,
)
from hermes.evaluation.report import EvaluationReportWriter
from hermes.executor.models import WorkflowExecutionResult


def make_execution(
    workflow_id: str,
) -> WorkflowExecutionResult:
    return WorkflowExecutionResult(
        workflow_id=workflow_id,
        workflow_name=workflow_id,
        steps=(),
        started_at="start",
        finished_at="finish",
    )


def make_result() -> EvaluationResult:
    baseline = make_execution("baseline")
    mutation_execution = make_execution("mutation-1")

    comparison = BehaviorComparisonResult(
        baseline_workflow_id="baseline",
        mutated_workflow_id="mutation-1",
        status=ComparisonStatus.DIVERGENT,
        signals=(),
        divergence_score=1.0,
    )

    return EvaluationResult(
        baseline_execution=baseline,
        mutations=(
            MutationEvaluation(
                mutation_workflow_id="mutation-1",
                execution=mutation_execution,
                comparison=comparison,
            ),
        ),
    )


def test_save_json(tmp_path) -> None:
    output = tmp_path / "evaluation" / "report.json"

    result = EvaluationReportWriter.save_json(
        make_result(),
        output,
    )

    assert result == output
    assert output.exists()

    data = json.loads(
        output.read_text(encoding="utf-8")
    )

    assert data["summary"]["mutation_count"] == 1
    assert data["summary"]["anomaly_count"] == 1


def test_save_csv(tmp_path) -> None:
    output = tmp_path / "evaluation" / "summary.csv"

    result = EvaluationReportWriter.save_csv(
        make_result(),
        output,
    )

    assert result == output
    assert output.exists()

    with output.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert rows[0]["mutation_workflow_id"] == "mutation-1"
    assert rows[0]["comparison_status"] == "divergent"
    assert rows[0]["anomaly_detected"] == "True"


def test_report_writer_creates_directories(
    tmp_path,
) -> None:
    json_path = tmp_path / "a" / "b" / "report.json"
    csv_path = tmp_path / "c" / "d" / "summary.csv"

    EvaluationReportWriter.save_json(
        make_result(),
        json_path,
    )
    EvaluationReportWriter.save_csv(
        make_result(),
        csv_path,
    )

    assert json_path.exists()
    assert csv_path.exists()
