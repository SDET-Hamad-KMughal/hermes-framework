"""Tests for HERMES application states."""

import pytest

from hermes.state_graph.state import ApplicationState


def test_create_application_state() -> None:
    state = ApplicationState.create(
        url="http://127.0.0.1:5000/products",
        title="Products",
        depth=1,
        action_count=4,
        form_count=1,
    )

    assert len(state.state_id) == 16
    assert state.url == "http://127.0.0.1:5000/products"
    assert state.title == "Products"
    assert state.depth == 1
    assert state.action_count == 4
    assert state.form_count == 1


def test_state_identifier_is_deterministic() -> None:
    first = ApplicationState.create(
        url="http://127.0.0.1:5000/cart",
        title="Cart",
        depth=1,
    )
    second = ApplicationState.create(
        url="http://127.0.0.1:5000/cart",
        title="Cart",
        depth=3,
    )

    assert first.state_id == second.state_id


def test_state_serialization() -> None:
    state = ApplicationState.create(
        url="http://127.0.0.1:5000/login",
        title="Login",
        depth=0,
        metadata={"authenticated": False},
    )

    data = state.to_dict()

    assert data["title"] == "Login"
    assert data["metadata"]["authenticated"] is False


def test_empty_url_is_rejected() -> None:
    with pytest.raises(ValueError, match="url must not be empty"):
        ApplicationState.create("", "Page", 0)
