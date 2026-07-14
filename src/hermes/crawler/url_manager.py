"""URL normalization and filtering for the HERMES crawler."""

from __future__ import annotations

from urllib.parse import urldefrag, urljoin, urlparse, urlunparse


class URLManager:
    """Normalize URLs and determine whether they are crawlable."""

    IGNORED_SCHEMES = {
        "javascript",
        "mailto",
        "tel",
        "data",
    }

    def __init__(
        self,
        start_url: str,
        allow_external_links: bool = False,
    ) -> None:
        self.start_url = self.normalize(start_url)
        self.allow_external_links = allow_external_links

        parsed_start = urlparse(self.start_url)
        self._start_netloc = parsed_start.netloc.lower()

    def normalize(
        self,
        url: str,
        base_url: str | None = None,
    ) -> str:
        """Resolve and normalize a URL."""

        cleaned_url = url.strip()

        if not cleaned_url:
            return ""

        parsed_input = urlparse(cleaned_url)

        if parsed_input.scheme.lower() in self.IGNORED_SCHEMES:
            return ""

        if base_url is not None:
            cleaned_url = urljoin(base_url, cleaned_url)

        cleaned_url, _fragment = urldefrag(cleaned_url)

        parsed = urlparse(cleaned_url)

        if parsed.scheme.lower() not in {"http", "https"}:
            return ""

        normalized_path = parsed.path or "/"

        normalized = parsed._replace(
            scheme=parsed.scheme.lower(),
            netloc=parsed.netloc.lower(),
            path=normalized_path,
            fragment="",
        )

        return urlunparse(normalized)

    def is_internal(self, url: str) -> bool:
        """Return whether a URL belongs to the starting application."""

        normalized_url = self.normalize(url)

        if not normalized_url:
            return False

        return urlparse(normalized_url).netloc.lower() == self._start_netloc

    def is_crawlable(
        self,
        url: str,
        base_url: str | None = None,
    ) -> bool:
        """Return whether a URL may be added to the crawl queue."""

        normalized_url = self.normalize(url, base_url)

        if not normalized_url:
            return False

        if self.allow_external_links:
            return True

        return self.is_internal(normalized_url)