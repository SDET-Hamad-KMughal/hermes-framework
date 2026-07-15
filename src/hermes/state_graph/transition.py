"""State-transition representation for HERMES."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class StateTransition:
    """A transition between two application states."""

    source_state_id: str
    target_state_id: str
    action_type: str
    label: str = ""
    selector: str | None = None
    semantic_target: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the transition."""

        if not self.source_state_id.strip():
            raise ValueError("source_state_id must not be empty")

        if not self.target_state_id.strip():
            raise ValueError("target_state_id must not be empty")

        if not self.action_type.strip():
            raise ValueError("action_type must not be empty")

    def to_dict(self) -> dict[str, Any]:
        """Convert the transition into serializable data."""
        return asdict(self)
