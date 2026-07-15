"""Rank automatically generated workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hermes.prioritizer import WorkflowScorer
from hermes.workflow_generator.models import GeneratedWorkflow


def load_generated_workflows(directory: Path) -> list[GeneratedWorkflow]:
    """Load generated workflows from a directory."""

    workflows = []

    for file in sorted(directory.glob("workflow_*.json")):
        payload = json.loads(
            file.read_text(encoding="utf-8")
        )

        workflows.append(
            GeneratedWorkflow.from_dict(payload)
        )

    return workflows


def save_ranked(scores, output: Path) -> None:
    """Save ranked workflow scores."""

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        json.dumps(
            [score.to_dict() for score in scores],
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input-dir",
        default="results/generated-workflows",
    )

    parser.add_argument(
        "--output",
        default="results/ranked-workflows/ranked.json",
    )

    parser.add_argument(
        "--maximum-depth",
        type=int,
        default=6,
    )

    parser.add_argument(
        "--total-states",
        type=int,
        required=True,
    )

    args = parser.parse_args()

    workflows = load_generated_workflows(
        Path(args.input_dir)
    )

    scorer = WorkflowScorer()

    ranked = scorer.rank(
        workflows,
        maximum_depth=args.maximum_depth,
        total_state_count=args.total_states,
    )

    save_ranked(
        ranked,
        Path(args.output),
    )

    print(f"Loaded: {len(workflows)} workflows")
    print(f"Ranked: {len(ranked)} workflows")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
