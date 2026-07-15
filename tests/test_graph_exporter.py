"""Tests for HERMES state-graph export."""

import json

from hermes.state_graph.exporter import StateGraphExporter
from hermes.state_graph.graph import StateGraph
from hermes.state_graph.state import ApplicationState
from hermes.state_graph.transition import StateTransition


def make_graph() -> StateGraph:
    graph = StateGraph()

    home = ApplicationState.create(
        "http://127.0.0.1:5000/",
        "Home",
        0,
    )
    products = ApplicationState.create(
        "http://127.0.0.1:5000/products",
        "Products",
        1,
    )

    graph.add_state(home)
    graph.add_state(products)

    graph.add_transition(
        StateTransition(
            source_state_id=home.state_id,
            target_state_id=products.state_id,
            action_type="navigate",
            label="Products",
        )
    )

    return graph


def test_save_json(tmp_path) -> None:
    output = tmp_path / "graph" / "state_graph.json"

    result = StateGraphExporter.save_json(
        make_graph(),
        output,
    )

    assert result == output
    assert output.exists()

    data = json.loads(
        output.read_text(encoding="utf-8")
    )

    assert data["statistics"]["states"] == 2
    assert data["statistics"]["transitions"] == 1


def test_save_dot(tmp_path) -> None:
    output = tmp_path / "graph" / "state_graph.dot"

    result = StateGraphExporter.save_dot(
        make_graph(),
        output,
    )

    assert result == output
    assert output.exists()

    content = output.read_text(encoding="utf-8")

    assert "digraph HERMES" in content
    assert "Home" in content
    assert "Products" in content
    assert "->" in content


def test_exporter_creates_parent_directories(
    tmp_path,
) -> None:
    json_path = tmp_path / "a" / "b" / "graph.json"
    dot_path = tmp_path / "c" / "d" / "graph.dot"

    StateGraphExporter.save_json(
        StateGraph(),
        json_path,
    )
    StateGraphExporter.save_dot(
        StateGraph(),
        dot_path,
    )

    assert json_path.exists()
    assert dot_path.exists()
