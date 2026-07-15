"""Run all validated HERMES benchmark workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_workflow import (
    execute_workflow,
    load_workflow,
)


WORKFLOW_FILES = (
    "login.json",
    "cart.json",
    "checkout.json",
    "wallet.json",
    "order_history.json",
)


def run_suite(
    workflow_dir: Path,
    output_dir: Path,
    start_url: str,
    headless: bool = True,
) -> dict:
    """Execute every configured benchmark workflow."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = []

    for filename in WORKFLOW_FILES:
        workflow_path = workflow_dir / filename
        workflow = load_workflow(workflow_path)

        execution = execute_workflow(
            workflow=workflow,
            start_url=start_url,
            headless=headless,
        )

        report_path = output_dir / (
            f"{workflow.workflow_id}.json"
        )
        report_path.write_text(
            json.dumps(
                execution.to_dict(),
                indent=2,
            ),
            encoding="utf-8",
        )

        results.append(
            {
                "workflow_id": workflow.workflow_id,
                "workflow_name": workflow.name,
                "success": execution.success,
                "successful_steps": (
                    execution.successful_steps
                ),
                "failed_steps": execution.failed_steps,
                "report": str(report_path),
            }
        )

    summary = {
        "workflow_count": len(results),
        "successful_workflows": sum(
            1 for item in results if item["success"]
        ),
        "failed_workflows": sum(
            1 for item in results if not item["success"]
        ),
        "workflows": results,
    }

    summary_path = output_dir / "suite_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return summary


def main() -> None:
    """Run the complete benchmark workflow suite."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--workflow-dir",
        default="configs/workflows",
    )
    parser.add_argument(
        "--output-dir",
        default="results/benchmark-suite",
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:5000",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
    )

    args = parser.parse_args()

    summary = run_suite(
        workflow_dir=Path(args.workflow_dir),
        output_dir=Path(args.output_dir),
        start_url=args.url,
        headless=not args.headed,
    )

    print("===================================")
    print("HERMES Benchmark Suite Complete")
    print("===================================")
    print(f"Workflows: {summary['workflow_count']}")
    print(
        f"Successful: "
        f"{summary['successful_workflows']}"
    )
    print(
        f"Failed: "
        f"{summary['failed_workflows']}"
    )

    for workflow in summary["workflows"]:
        print(
            f"{workflow['workflow_id']}: "
            f"{'PASS' if workflow['success'] else 'FAIL'} "
            f"({workflow['successful_steps']} passed, "
            f"{workflow['failed_steps']} failed)"
        )


if __name__ == "__main__":
    main()
