"""Export HERMES state graphs."""

from __future__ import annotations

import json
from pathlib import Path

from hermes.state_graph.graph import StateGraph


class StateGraphExporter:
    """Export a state graph to JSON or DOT."""

    @staticmethod
    def save_json(graph: StateGraph, path: str | Path) -> Path:
        """Save the graph as formatted JSON."""

        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)

        output.write_text(
            json.dumps(graph.to_dict(), indent=2),
            encoding="utf-8",
        )

        return output

    @staticmethod
    def save_dot(graph: StateGraph, path: str | Path) -> Path:
        """Save the graph as Graphviz DOT."""

        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "digraph HERMES {",
            "    rankdir=LR;",
        ]

        for state in graph.states.values():
            label = StateGraphExporter._escape(
                f"{state.title}\\n{state.url}"
            )
            lines.append(
                f'    "{state.state_id}" [label="{label}"];'
            )

        for transition in graph.transitions:
            label = StateGraphExporter._escape(
                transition.label or transition.action_type
            )
            lines.append(
                f'    "{transition.source_state_id}" -> "{transition.target_state_id}" '
                f'[label="{label}"];'
            )

        lines.append("}")

        output.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )

        return output

    @staticmethod
    def _escape(value: str) -> str:
        """Escape Graphviz label text."""

        return (
            value.replace("\\", "\\\\")
                 .replace('"', '\\"')
        )
