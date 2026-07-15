"""Tests for the HERMES state graph."""

import pytest

from hermes.state_graph.graph import StateGraph
from hermes.state_graph.state import ApplicationState
from hermes.state_graph.transition import StateTransition


def make_state(path: str, title: str) -> ApplicationState:
    return ApplicationState.create(
        url=f"http://127.0.0.1:5000{path}",
        title=title,
        depth=0,
    )


def test_graph_starts_empty() -> None:
    graph = StateGraph()

    assert graph.state_count == 0
    assert graph.transition_count == 0


def test_add_and_get_state() -> None:
    graph = StateGraph()
    state = make_state("/", "Home")

    assert graph.add_state(state) is True
    assert graph.add_state(state) is False
    assert graph.get_state(state.state_id) is state
    assert graph.state_count == 1


def test_add_transition() -> None:
    graph = StateGraph()
    home = make_state("/", "Home")
    products = make_state("/products", "Products")
    graph.add_state(home)
    graph.add_state(products)

    transition = StateTransition(
        source_state_id=home.state_id,
        target_state_id=products.state_id,
        action_type="navigate",
        label="Products",
    )

    assert graph.add_transition(transition) is True
    assert graph.add_transition(transition) is False
    assert graph.transition_count == 1


def test_transition_requires_existing_states() -> None:
    graph = StateGraph()
    transition = StateTransition(
        source_state_id="missing-source",
        target_state_id="missing-target",
        action_type="navigate",
    )

    with pytest.raises(
        ValueError,
        match="source state must exist before adding transition",
    ):
        graph.add_transition(transition)


def test_incoming_and_outgoing_transitions() -> None:
    graph = StateGraph()
    home = make_state("/", "Home")
    products = make_state("/products", "Products")
    graph.add_state(home)
    graph.add_state(products)

    transition = StateTransition(
        source_state_id=home.state_id,
        target_state_id=products.state_id,
        action_type="navigate",
    )
    graph.add_transition(transition)

    assert graph.outgoing(home.state_id) == (transition,)
    assert graph.incoming(products.state_id) == (transition,)
    assert graph.outgoing(products.state_id) == ()


def test_graph_serialization() -> None:
    graph = StateGraph()
    home = make_state("/", "Home")
    graph.add_state(home)

    data = graph.to_dict()

    assert data["statistics"]["states"] == 1
    assert data["statistics"]["transitions"] == 0
    assert data["states"][0]["title"] == "Home"
