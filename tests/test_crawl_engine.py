"""Tests for crawl orchestration."""

from unittest.mock import MagicMock

from hermes.crawler.config import CrawlerConfig
from hermes.crawler.engine import CrawlEngine
from hermes.crawler.models import Link, Page


def make_browser_manager(mock_page: MagicMock) -> MagicMock:
    manager = MagicMock()
    manager.__enter__.return_value = manager
    manager.__exit__.return_value = None
    manager.new_page.return_value = mock_page
    return manager


def test_engine_crawls_internal_links() -> None:
    browser_page = MagicMock()
    browser_manager = make_browser_manager(browser_page)

    config = CrawlerConfig(
        start_url="http://127.0.0.1:5000/",
        max_pages=3,
        max_depth=2,
    )
    engine = CrawlEngine(
        config=config,
        browser_manager=browser_manager,
    )

    engine.extractor.extract = MagicMock(
        side_effect=[
            Page(
                url="http://127.0.0.1:5000/",
                title="Home",
                depth=0,
                links=[
                    Link(
                        text="Products",
                        href="http://127.0.0.1:5000/products",
                        internal=True,
                    ),
                    Link(
                        text="External",
                        href="https://example.com/",
                        internal=False,
                    ),
                ],
            ),
            Page(
                url="http://127.0.0.1:5000/products",
                title="Products",
                depth=1,
            ),
        ]
    )

    result = engine.run()

    assert result.page_count == 2
    assert result.errors == []
    assert result.pages[0].title == "Home"
    assert result.pages[1].title == "Products"
    assert browser_page.goto.call_count == 2

    browser_page.goto.assert_any_call(
        "http://127.0.0.1:5000/",
        wait_until="domcontentloaded",
    )
    browser_page.goto.assert_any_call(
        "http://127.0.0.1:5000/products",
        wait_until="domcontentloaded",
    )


def test_engine_respects_max_pages() -> None:
    browser_page = MagicMock()
    browser_manager = make_browser_manager(browser_page)

    config = CrawlerConfig(
        start_url="http://127.0.0.1:5000/",
        max_pages=1,
        max_depth=3,
    )
    engine = CrawlEngine(
        config=config,
        browser_manager=browser_manager,
    )

    engine.extractor.extract = MagicMock(
        return_value=Page(
            url="http://127.0.0.1:5000/",
            title="Home",
            depth=0,
            links=[
                Link(
                    text="Products",
                    href="http://127.0.0.1:5000/products",
                    internal=True,
                )
            ],
        )
    )

    result = engine.run()

    assert result.page_count == 1
    assert browser_page.goto.call_count == 1


def test_engine_records_navigation_errors() -> None:
    browser_page = MagicMock()
    browser_page.goto.side_effect = RuntimeError("navigation failed")
    browser_manager = make_browser_manager(browser_page)

    config = CrawlerConfig(
        start_url="http://127.0.0.1:5000/",
    )
    engine = CrawlEngine(
        config=config,
        browser_manager=browser_manager,
    )

    result = engine.run()

    assert result.page_count == 0
    assert len(result.errors) == 1
    assert "navigation failed" in result.errors[0]


def test_engine_respects_max_depth() -> None:
    browser_page = MagicMock()
    browser_manager = make_browser_manager(browser_page)

    config = CrawlerConfig(
        start_url="http://127.0.0.1:5000/",
        max_pages=5,
        max_depth=0,
    )
    engine = CrawlEngine(
        config=config,
        browser_manager=browser_manager,
    )

    engine.extractor.extract = MagicMock(
        return_value=Page(
            url="http://127.0.0.1:5000/",
            title="Home",
            depth=0,
            links=[
                Link(
                    text="Products",
                    href="http://127.0.0.1:5000/products",
                    internal=True,
                )
            ],
        )
    )

    result = engine.run()

    assert result.page_count == 1
    assert browser_page.goto.call_count == 1