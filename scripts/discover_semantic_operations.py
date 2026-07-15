"""Discover semantic operations from a HERMES state graph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hermes.semantic import SemanticOperationDiscovery
from hermes.state_graph.graph import StateGraph
from hermes.state_graph.state import ApplicationState
from hermes.state_graph.transition import StateTransition


def load_state_graph(path: Path) -> StateGraph:
    """Load a state graph from exported JSON."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    graph = StateGraph()

    for item in payload.get("states", []):
        graph.add_state(
            ApplicationState(
                state_id=item["state_id"],
                url=item["url"],
                title=item["title"],
                depth=item["depth"],
                action_count=item.get("action_count", 0),
                form_count=item.get("form_count", 0),
                metadata=dict(item.get("metadata", {})),
            )
        )

    for item in payload.get("transitions", []):
        graph.add_transition(
            StateTransition(
                source_state_id=item["source_state_id"],
                target_state_id=item["target_state_id"],
                action_type=item["action_type"],
                label=item.get("label", ""),
                selector=item.get("selector"),
                semantic_target=item.get("semantic_target"),
                metadata=dict(item.get("metadata", {})),
            )
        )

    return graph


def main() -> None:
    """Discover and export semantic operations."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="results/state_graph/state_graph.json",
    )
    parser.add_argument(
        "--output",
        default="results/semantic/operations.json",
    )
    args = parser.parse_args()

    graph = load_state_graph(Path(args.input))
    operations = SemanticOperationDiscovery().discover(graph)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            [operation.to_dict() for operation in operations],
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Operations: {len(operations)}")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
