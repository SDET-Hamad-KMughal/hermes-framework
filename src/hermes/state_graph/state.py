"""Application-state representation for HERMES."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ApplicationState:
    """A normalized observable state of a web application."""

    state_id: str
    url: str
    title: str
    depth: int
    action_count: int = 0
    form_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        url: str,
        title: str,
        depth: int,
        action_count: int = 0,
        form_count: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> "ApplicationState":
        """Create a state with a deterministic identifier."""

        normalized_url = url.strip()
        normalized_title = title.strip()

        if not normalized_url:
            raise ValueError("url must not be empty")
        if depth < 0:
            raise ValueError("depth must not be negative")
        if action_count < 0:
            raise ValueError("action_count must not be negative")
        if form_count < 0:
            raise ValueError("form_count must not be negative")

        identity = f"{normalized_url}|{normalized_title}"
        state_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]

        return cls(
            state_id=state_id,
            url=normalized_url,
            title=normalized_title,
            depth=depth,
            action_count=action_count,
            form_count=form_count,
            metadata=dict(metadata or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the state into serializable data."""
        return asdict(self)
