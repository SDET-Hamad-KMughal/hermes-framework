"""Tests for semantic-operation report generation."""

import json

from scripts.discover_semantic_operations import load_state_graph


def test_load_state_graph(tmp_path) -> None:
    graph_path = tmp_path / "state_graph.json"

    graph_path.write_text(
        json.dumps(
            {
                "states": [
                    {
                        "state_id": "home",
                        "url": "http://127.0.0.1:5000/",
                        "title": "Home",
                        "depth": 0,
                        "action_count": 1,
                        "form_count": 0,
                        "metadata": {},
                    },
                    {
                        "state_id": "login",
                        "url": "http://127.0.0.1:5000/login",
                        "title": "Login",
                        "depth": 1,
                        "action_count": 0,
                        "form_count": 1,
                        "metadata": {},
                    },
                ],
                "transitions": [
                    {
                        "source_state_id": "home",
                        "target_state_id": "login",
                        "action_type": "navigate",
                        "label": "Sign In Here",
                        "selector": "a",
                        "semantic_target": "http://127.0.0.1:5000/login",
                        "metadata": {},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    graph = load_state_graph(graph_path)

    assert graph.state_count == 2
    assert graph.transition_count == 1
    assert graph.get_state("login").title == "Login"


def test_load_empty_state_graph(tmp_path) -> None:
    graph_path = tmp_path / "empty_graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "states": [],
                "transitions": [],
            }
        ),
        encoding="utf-8",
    )

    graph = load_state_graph(graph_path)

    assert graph.state_count == 0
    assert graph.transition_count == 0
