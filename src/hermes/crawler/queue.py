"""FIFO crawl queue with depth and duplicate control."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CrawlTarget:
    """A URL scheduled for crawling at a specific depth."""

    url: str
    depth: int


class CrawlQueue:
    """Manage queued and visited crawl targets."""

    def __init__(self, max_depth: int) -> None:
        if max_depth < 0:
            raise ValueError("max_depth must not be negative")

        self.max_depth = max_depth
        self._queue: deque[CrawlTarget] = deque()
        self._queued_urls: set[str] = set()
        self._visited_urls: set[str] = set()

    def __len__(self) -> int:
        """Return the number of waiting crawl targets."""
        return len(self._queue)

    @property
    def is_empty(self) -> bool:
        """Return whether no crawl targets remain."""
        return not self._queue

    @property
    def visited_count(self) -> int:
        """Return the number of visited URLs."""
        return len(self._visited_urls)

    def add(self, url: str, depth: int) -> bool:
        """Add a URL if it is valid, in range, and not already known."""
        normalized_url = url.strip()

        if not normalized_url:
            return False

        if depth < 0 or depth > self.max_depth:
            return False

        if normalized_url in self._queued_urls:
            return False

        if normalized_url in self._visited_urls:
            return False

        self._queue.append(CrawlTarget(url=normalized_url, depth=depth))
        self._queued_urls.add(normalized_url)
        return True

    def pop(self) -> CrawlTarget:
        """Return and remove the next crawl target."""
        if self.is_empty:
            raise IndexError("Cannot pop from an empty crawl queue")

        target = self._queue.popleft()
        self._queued_urls.remove(target.url)
        return target

    def mark_visited(self, url: str) -> None:
        """Record a URL as visited and remove it from queued tracking."""
        normalized_url = url.strip()

        if not normalized_url:
            raise ValueError("visited URL must not be empty")

        self._queued_urls.discard(normalized_url)
        self._visited_urls.add(normalized_url)

    def has_visited(self, url: str) -> bool:
        """Return whether a URL has already been visited."""
        return url.strip() in self._visited_urls

    def is_queued(self, url: str) -> bool:
        """Return whether a URL is currently waiting in the queue."""
        return url.strip() in self._queued_urls
