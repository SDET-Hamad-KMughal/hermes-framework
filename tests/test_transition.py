"""Tests for HERMES state transitions."""

import pytest

from hermes.state_graph.transition import StateTransition


def test_create_transition() -> None:
    transition = StateTransition(
        source_state_id="state-1",
        target_state_id="state-2",
        action_type="navigate",
        label="Products",
        selector="#products-link",
        semantic_target="open_products",
    )

    assert transition.source_state_id == "state-1"
    assert transition.target_state_id == "state-2"
    assert transition.action_type == "navigate"
    assert transition.label == "Products"


def test_transition_serialization() -> None:
    transition = StateTransition(
        source_state_id="state-1",
        target_state_id="state-2",
        action_type="click",
        metadata={"depth": 1},
    )

    data = transition.to_dict()

    assert data["action_type"] == "click"
    assert data["metadata"]["depth"] == 1


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {
                "source_state_id": "",
                "target_state_id": "state-2",
                "action_type": "navigate",
            },
            "source_state_id must not be empty",
        ),
        (
            {
                "source_state_id": "state-1",
                "target_state_id": "",
                "action_type": "navigate",
            },
            "target_state_id must not be empty",
        ),
        (
            {
                "source_state_id": "state-1",
                "target_state_id": "state-2",
                "action_type": "",
            },
            "action_type must not be empty",
        ),
    ],
)
def test_invalid_transition_is_rejected(kwargs, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        StateTransition(**kwargs)
