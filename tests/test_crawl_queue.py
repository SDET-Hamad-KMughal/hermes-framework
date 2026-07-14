"""Tests for the HERMES crawl queue."""

import pytest

from hermes.crawler.queue import CrawlQueue, CrawlTarget


def test_queue_starts_empty() -> None:
    queue = CrawlQueue(max_depth=3)

    assert len(queue) == 0
    assert queue.is_empty is True
    assert queue.visited_count == 0


def test_invalid_max_depth() -> None:
    with pytest.raises(
        ValueError,
        match="max_depth must not be negative",
    ):
        CrawlQueue(max_depth=-1)


def test_add_and_pop_target() -> None:
    queue = CrawlQueue(max_depth=3)

    assert queue.add(
        "http://127.0.0.1:5000/",
        depth=0,
    ) is True

    target = queue.pop()

    assert target == CrawlTarget(
        url="http://127.0.0.1:5000/",
        depth=0,
    )
    assert queue.is_empty is True


def test_queue_uses_fifo_order() -> None:
    queue = CrawlQueue(max_depth=3)

    queue.add("http://127.0.0.1:5000/first", depth=0)
    queue.add("http://127.0.0.1:5000/second", depth=1)

    assert queue.pop().url == "http://127.0.0.1:5000/first"
    assert queue.pop().url == "http://127.0.0.1:5000/second"


def test_duplicate_queued_url_is_rejected() -> None:
    queue = CrawlQueue(max_depth=3)

    assert queue.add(
        "http://127.0.0.1:5000/cart",
        depth=1,
    ) is True

    assert queue.add(
        "http://127.0.0.1:5000/cart",
        depth=2,
    ) is False


def test_visited_url_is_rejected() -> None:
    queue = CrawlQueue(max_depth=3)

    queue.add("http://127.0.0.1:5000/cart", depth=1)
    target = queue.pop()
    queue.mark_visited(target.url)

    assert queue.has_visited(target.url) is True
    assert queue.visited_count == 1
    assert queue.add(target.url, depth=2) is False


@pytest.mark.parametrize(
    ("url", "depth"),
    [
        ("", 0),
        ("   ", 0),
        ("http://127.0.0.1:5000/", -1),
        ("http://127.0.0.1:5000/", 4),
    ],
)
def test_invalid_targets_are_rejected(
    url: str,
    depth: int,
) -> None:
    queue = CrawlQueue(max_depth=3)

    assert queue.add(url, depth) is False


def test_pop_from_empty_queue_fails() -> None:
    queue = CrawlQueue(max_depth=3)

    with pytest.raises(
        IndexError,
        match="Cannot pop from an empty crawl queue",
    ):
        queue.pop()


def test_empty_visited_url_fails() -> None:
    queue = CrawlQueue(max_depth=3)

    with pytest.raises(
        ValueError,
        match="visited URL must not be empty",
    ):
        queue.mark_visited("")
