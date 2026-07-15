"""Generate workflow-context mutation reports for HERMES."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hermes.mutation import (
    MutationPlan,
    Workflow,
    WorkflowMutationEngine,
    WorkflowStep,
)
from hermes.semantic.models import OperationType


def load_workflow(path: Path) -> Workflow:
    """Load a baseline semantic workflow from JSON."""

    payload = json.loads(path.read_text(encoding="utf-8"))

    steps = tuple(
        WorkflowStep(
            operation_type=OperationType(item["operation_type"]),
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


def generate_report(
    workflow: Workflow,
    plan: MutationPlan | None = None,
) -> dict:
    """Generate a serializable mutation report."""

    engine = WorkflowMutationEngine(plan)
    mutations = engine.generate(workflow)

    mutation_counts: dict[str, int] = {}

    for item in mutations:
        mutation_type = item.metadata.get(
            "mutation_type",
            "unknown",
        )
        mutation_counts[mutation_type] = (
            mutation_counts.get(mutation_type, 0) + 1
        )

    return {
        "baseline": workflow.to_dict(),
        "summary": {
            "baseline_steps": len(workflow),
            "generated_mutations": len(mutations),
            "mutation_types": mutation_counts,
        },
        "mutations": [
            mutation.to_dict()
            for mutation in mutations
        ],
    }


def main() -> None:
    """Generate and save a mutation report."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="results/mutations/baseline_workflow.json",
    )
    parser.add_argument(
        "--output",
        default="results/mutations/mutation_report.json",
    )
    parser.add_argument(
        "--max-mutations",
        type=int,
        default=None,
    )
    args = parser.parse_args()

    workflow = load_workflow(Path(args.input))
    plan = MutationPlan(
        max_mutations=args.max_mutations,
    )
    report = generate_report(
        workflow,
        plan,
    )

    output = Path(args.output)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(
        f"Baseline steps: "
        f"{report['summary']['baseline_steps']}"
    )
    print(
        f"Generated mutations: "
        f"{report['summary']['generated_mutations']}"
    )
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
