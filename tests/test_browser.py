"""Tests for the HERMES browser manager."""

from unittest.mock import MagicMock, patch

import pytest

from hermes.crawler import BrowserManager, CrawlerConfig


def test_browser_manager_initial_state() -> None:
    config = CrawlerConfig(start_url="http://127.0.0.1:5000")
    manager = BrowserManager(config)

    assert manager.is_started is False


def test_new_page_requires_started_browser() -> None:
    config = CrawlerConfig(start_url="http://127.0.0.1:5000")
    manager = BrowserManager(config)

    with pytest.raises(
        RuntimeError,
        match="BrowserManager must be started before creating a page",
    ):
        manager.new_page()


@patch("hermes.crawler.browser.sync_playwright")
def test_start_new_page_and_close(mock_sync_playwright: MagicMock) -> None:
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    config = CrawlerConfig(
        start_url="http://127.0.0.1:5000",
        headless=True,
        page_timeout_seconds=15,
    )
    manager = BrowserManager(config)

    returned_manager = manager.start()
    returned_page = manager.new_page()

    assert returned_manager is manager
    assert manager.is_started is True
    assert returned_page is mock_page

    mock_playwright.chromium.launch.assert_called_once_with(headless=True)
    mock_browser.new_context.assert_called_once_with(
        ignore_https_errors=True,
    )
    mock_context.set_default_timeout.assert_called_once_with(15000)
    mock_context.new_page.assert_called_once_with()

    manager.close()

    mock_context.close.assert_called_once_with()
    mock_browser.close.assert_called_once_with()
    mock_playwright.stop.assert_called_once_with()
    assert manager.is_started is False


@patch("hermes.crawler.browser.sync_playwright")
def test_context_manager_closes_resources(
    mock_sync_playwright: MagicMock,
) -> None:
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()

    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context

    config = CrawlerConfig(start_url="http://127.0.0.1:5000")

    with BrowserManager(config) as manager:
        assert manager.is_started is True

    mock_context.close.assert_called_once_with()
    mock_browser.close.assert_called_once_with()
    mock_playwright.stop.assert_called_once_with()