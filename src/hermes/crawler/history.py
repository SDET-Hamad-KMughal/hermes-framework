"""Navigation-history tracking for the HERMES crawler."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class NavigationRecord:
    """One recorded page visit during a crawl."""

    order: int
    url: str
    title: str
    depth: int
    previous_url: str | None
    action: str
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the navigation record to serializable data."""
        return asdict(self)


class NavigationHistory:
    """Store ordered page visits and navigation transitions."""

    def __init__(self) -> None:
        self._records: list[NavigationRecord] = []

    def __len__(self) -> int:
        """Return the number of recorded visits."""
        return len(self._records)

    @property
    def records(self) -> tuple[NavigationRecord, ...]:
        """Return an immutable view of all navigation records."""
        return tuple(self._records)

    @property
    def last_record(self) -> NavigationRecord | None:
        """Return the most recently recorded visit."""
        if not self._records:
            return None

        return self._records[-1]

    def record(
        self,
        url: str,
        title: str,
        depth: int,
        previous_url: str | None = None,
        action: str = "navigate",
    ) -> NavigationRecord:
        """Record one page visit."""

        normalized_url = url.strip()

        if not normalized_url:
            raise ValueError("url must not be empty")

        if depth < 0:
            raise ValueError("depth must not be negative")

        normalized_action = action.strip()

        if not normalized_action:
            raise ValueError("action must not be empty")

        record = NavigationRecord(
            order=len(self._records) + 1,
            url=normalized_url,
            title=title.strip(),
            depth=depth,
            previous_url=(
                previous_url.strip()
                if previous_url and previous_url.strip()
                else None
            ),
            action=normalized_action,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self._records.append(record)
        return record

    def clear(self) -> None:
        """Remove all navigation records."""
        self._records.clear()

    def to_dict(self) -> list[dict[str, Any]]:
        """Return all navigation records as serializable dictionaries."""
        return [record.to_dict() for record in self._records]
