"""Directed application-state graph for HERMES."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hermes.state_graph.state import ApplicationState
from hermes.state_graph.transition import StateTransition


@dataclass(slots=True)
class StateGraph:
    """Store application states and directed transitions."""

    states: dict[str, ApplicationState] = field(default_factory=dict)
    transitions: list[StateTransition] = field(default_factory=list)

    @property
    def state_count(self) -> int:
        """Return the number of unique states."""
        return len(self.states)

    @property
    def transition_count(self) -> int:
        """Return the number of recorded transitions."""
        return len(self.transitions)

    def add_state(self, state: ApplicationState) -> bool:
        """Add a state unless its identifier already exists."""
        if state.state_id in self.states:
            return False

        self.states[state.state_id] = state
        return True

    def get_state(self, state_id: str) -> ApplicationState | None:
        """Return a state by identifier."""
        return self.states.get(state_id)

    def add_transition(self, transition: StateTransition) -> bool:
        """Add a transition when both endpoint states exist."""
        if transition.source_state_id not in self.states:
            raise ValueError("source state must exist before adding transition")

        if transition.target_state_id not in self.states:
            raise ValueError("target state must exist before adding transition")

        if transition in self.transitions:
            return False

        self.transitions.append(transition)
        return True

    def outgoing(self, state_id: str) -> tuple[StateTransition, ...]:
        """Return transitions leaving a state."""
        return tuple(
            transition
            for transition in self.transitions
            if transition.source_state_id == state_id
        )

    def incoming(self, state_id: str) -> tuple[StateTransition, ...]:
        """Return transitions entering a state."""
        return tuple(
            transition
            for transition in self.transitions
            if transition.target_state_id == state_id
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the graph into serializable data."""
        return {
            "states": [state.to_dict() for state in self.states.values()],
            "transitions": [
                transition.to_dict() for transition in self.transitions
            ],
            "statistics": {
                "states": self.state_count,
                "transitions": self.transition_count,
            },
        }
