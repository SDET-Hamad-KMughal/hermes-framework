"""Generate executable workflow candidates from semantic operations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hermes.semantic.models import (
    OperationType,
    SemanticOperation,
)
from hermes.workflow_generator import (
    StateAwareWorkflowGenerator,
    WorkflowGenerationConfig,
    WorkflowSelectionConfig,
    WorkflowSelector,
)


def load_operations(path: Path) -> list[SemanticOperation]:
    """Load semantic operations from JSON."""

    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    return [
        SemanticOperation(
            operation_type=OperationType(
                item["operation_type"]
            ),
            label=item["label"],
            source_state_id=item["source_state_id"],
            target_state_id=item.get("target_state_id"),
            selector=item.get("selector"),
            confidence=float(
                item.get("confidence", 0.0)
            ),
            evidence=tuple(
                item.get("evidence", [])
            ),
            metadata=dict(
                item.get("metadata", {})
            ),
        )
        for item in payload
    ]


def generate_workflows(
    operations: list[SemanticOperation],
    *,
    start_state_id: str,
    max_depth: int = 6,
    max_generated: int = 50,
    maximum_selected: int = 10,
) -> list:
    """Generate and rank workflow candidates."""

    generator = StateAwareWorkflowGenerator(
        WorkflowGenerationConfig(
            max_depth=max_depth,
            max_workflows=max_generated,
            minimum_steps=1,
        )
    )

    generated = generator.generate(
        operations,
        start_state_id,
    )

    selector = WorkflowSelector(
        WorkflowSelectionConfig(
            maximum_selected=maximum_selected,
        )
    )

    return selector.select(generated)


def save_workflows(
    workflows: list,
    output_dir: Path,
) -> Path:
    """Save selected workflows and one summary file."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_items = []

    for index, generated in enumerate(
        workflows,
        start=1,
    ):
        filename = f"workflow_{index:02d}.json"
        output = output_dir / filename

        output.write_text(
            json.dumps(
                generated.to_dict(),
                indent=2,
            ),
            encoding="utf-8",
        )

        summary_items.append(
            {
                "filename": filename,
                "workflow_id": (
                    generated.workflow.workflow_id
                ),
                "operation_count": (
                    generated.operation_count
                ),
                "terminal_state_id": (
                    generated.terminal_state_id
                ),
                "state_path": list(
                    generated.state_path
                ),
            }
        )

    summary = {
        "workflow_count": len(summary_items),
        "workflows": summary_items,
    }

    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return summary_path


def main() -> None:
    """Generate and save workflow candidates."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default="results/semantic/operations.json",
    )
    parser.add_argument(
        "--output-dir",
        default="results/generated-workflows",
    )
    parser.add_argument(
        "--start-state-id",
        required=True,
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=6,
    )
    parser.add_argument(
        "--max-generated",
        type=int,
        default=50,
    )
    parser.add_argument(
        "--maximum-selected",
        type=int,
        default=10,
    )

    args = parser.parse_args()

    operations = load_operations(
        Path(args.input)
    )

    workflows = generate_workflows(
        operations,
        start_state_id=args.start_state_id,
        max_depth=args.max_depth,
        max_generated=args.max_generated,
        maximum_selected=args.maximum_selected,
    )

    summary_path = save_workflows(
        workflows,
        Path(args.output_dir),
    )

    print(f"Operations loaded: {len(operations)}")
    print(f"Workflows selected: {len(workflows)}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
