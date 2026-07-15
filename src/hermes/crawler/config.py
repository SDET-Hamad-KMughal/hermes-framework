"""Configuration models for the HERMES crawler."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CrawlerConfig:
    """Runtime configuration for a crawler session."""

    start_url: str
    max_pages: int = 50
    max_depth: int = 5
    page_timeout_seconds: int = 15
    max_retries: int = 2
    retry_backoff_seconds: float = 0.5
    headless: bool = True
    allow_external_links: bool = False

    def __post_init__(self) -> None:
        if not self.start_url.strip():
            raise ValueError("start_url must not be empty")

        if self.max_pages < 1:
            raise ValueError("max_pages must be at least 1")

        if self.max_depth < 0:
            raise ValueError("max_depth must not be negative")

        if self.page_timeout_seconds < 1:
            raise ValueError("page_timeout_seconds must be at least 1")