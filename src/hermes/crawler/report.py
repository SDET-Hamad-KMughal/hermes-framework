"""Crawl-report generation for HERMES."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from hermes.crawler.history import NavigationHistory
from hermes.crawler.models import CrawlResult


@dataclass(frozen=True, slots=True)
class CrawlStatistics:
    """Summary statistics for one crawl execution."""

    pages: int
    links: int
    forms: int
    actions: int
    errors: int

    def to_dict(self) -> dict[str, int]:
        """Return serializable statistics."""
        return asdict(self)


class CrawlReport:
    """Create and save a structured crawl report."""

    def __init__(
        self,
        result: CrawlResult,
        history: NavigationHistory | None = None,
    ) -> None:
        self.result = result
        self.history = history or NavigationHistory()

    @property
    def statistics(self) -> CrawlStatistics:
        """Compute crawl statistics."""

        return CrawlStatistics(
            pages=len(self.result.pages),
            links=sum(len(page.links) for page in self.result.pages),
            forms=sum(len(page.forms) for page in self.result.pages),
            actions=sum(len(page.actions) for page in self.result.pages),
            errors=len(self.result.errors),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert report into a serializable dictionary."""

        return {
            "statistics": self.statistics.to_dict(),
            "history": self.history.to_dict(),
            "pages": [page.to_dict() for page in self.result.pages],
            "errors": list(self.result.errors),
        }

    def save_json(self, path: str | Path) -> None:
        """Save report as JSON."""

        output = Path(path)
        output.write_text(
            json.dumps(self.to_dict(), indent=2),
            encoding="utf-8",
        )
