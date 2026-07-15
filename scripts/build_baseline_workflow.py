"""Build a baseline workflow from semantic discovery output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hermes.mutation import Workflow, WorkflowStep
from hermes.semantic.models import OperationType


def load_operations(path: Path):
    """Load semantic operations."""

    return json.loads(
        path.read_text(encoding="utf-8")
    )


def build_workflow(operations):
    """Build baseline workflow."""

    steps = []

    for operation in operations:
        steps.append(
            WorkflowStep(
                operation_type=OperationType(
                    operation["operation_type"]
                ),
                label=operation["label"],
                source_state_id=operation["source_state_id"],
                target_state_id=operation.get(
                    "target_state_id"
                ),
                selector=operation.get("selector"),
                metadata=dict(
                    operation.get("metadata", {})
                ),
            )
        )

    return Workflow(
        workflow_id="baseline-workflow",
        name="Automatically Generated Workflow",
        steps=tuple(steps),
        metadata={
            "generated_by": "HERMES",
        },
    )


def main() -> None:
    """Build and save the baseline workflow."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default="results/semantic/operations.json",
    )

    parser.add_argument(
        "--output",
        default="results/mutations/baseline_workflow.json",
    )

    args = parser.parse_args()

    operations = load_operations(
        Path(args.input)
    )

    workflow = build_workflow(
        operations
    )

    output = Path(args.output)



def main() -> None:
    """Build and save the baseline workflow."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default="results/semantic/operations.json",
    )

    parser.add_argument(
        "--output",
        default="results/mutations/baseline_workflow.json",
    )

    args = parser.parse_args()

    operations = load_operations(
        Path(args.input)
    )

    workflow = build_workflow(
        operations
    )

    output = Path(args.output)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        json.dumps(
            workflow.to_dict(),
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Operations loaded: {len(operations)}")
    print(f"Workflow steps: {len(workflow)}")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
