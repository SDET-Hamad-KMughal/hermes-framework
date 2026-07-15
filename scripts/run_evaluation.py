"""Run an end-to-end HERMES workflow evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hermes.comparator import BehaviorComparator
from hermes.crawler import BrowserManager, CrawlerConfig
from hermes.evaluation import (
    EvaluationPipeline,
    EvaluationReportWriter,
)
from hermes.executor import (
    PlaywrightExecutionContext,
    WorkflowExecutionRunner,
)
from hermes.mutation import (
    MutationPlan,
    Workflow,
    WorkflowStep,
)
from hermes.semantic.models import OperationType


def load_workflow(path: Path) -> Workflow:
    """Load a baseline workflow from JSON."""

    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    steps = tuple(
        WorkflowStep(
            operation_type=OperationType(
                item["operation_type"]
            ),
            label=item["label"],
            source_state_id=item["source_state_id"],
            target_state_id=item.get("target_state_id"),
            selector=item.get("selector"),
            metadata=dict(item.get("metadata", {})),
        )
        for item in payload.get("steps", [])
    )

    return Workflow(
        workflow_id=payload["workflow_id"],
        name=payload["name"],
        steps=steps,
        metadata=dict(payload.get("metadata", {})),
    )


def execute_evaluation(
    workflow: Workflow,
    start_url: str,
    headless: bool = True,
):
    """Execute a complete HERMES evaluation."""

    config = CrawlerConfig(
        start_url=start_url,
        headless=headless,
    )

    browser_manager = BrowserManager(config)

    with browser_manager as manager:
        page = manager.new_page()

        page.goto(
            start_url,
            wait_until="domcontentloaded",
        )

        context = PlaywrightExecutionContext(page)

        pipeline = EvaluationPipeline(
            runner=WorkflowExecutionRunner(),
            comparator=BehaviorComparator(),
            mutation_plan=MutationPlan(max_mutations=3),
        )

        return pipeline.evaluate(
            context,
            workflow,
        )


def main() -> None:
    """Run the complete HERMES evaluation."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--workflow",
        default="results/mutations/baseline_workflow.json",
    )

    parser.add_argument(
        "--url",
        default="http://127.0.0.1:5000",
    )

    parser.add_argument(
        "--output-dir",
        default="results/evaluation",
    )

    parser.add_argument(
        "--headed",
        action="store_true",
    )

    args = parser.parse_args()

    workflow = load_workflow(
        Path(args.workflow)
    )

    result = execute_evaluation(
        workflow=workflow,
        start_url=args.url,
        headless=not args.headed,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = EvaluationReportWriter.save_json(
        result,
        output_dir / "evaluation_report.json",
    )

    csv_path = EvaluationReportWriter.save_csv(
        result,
        output_dir / "evaluation_summary.csv",
    )

    print("===================================")
    print("HERMES Evaluation Complete")
    print("===================================")
    print(f"Mutations: {result.mutation_count}")
    print(f"Anomalies: {result.anomaly_count}")
    print(f"Equivalent: {result.equivalent_count}")
    print(f"Anomaly Rate: {result.anomaly_rate:.2%}")
    print()
    print(f"JSON Report : {json_path}")
    print(f"CSV Report  : {csv_path}")


if __name__ == "__main__":
    main()
