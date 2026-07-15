"""Tests for the Playwright execution context."""

from unittest.mock import MagicMock

from hermes.executor.playwright_context import (
    PlaywrightExecutionContext,
)


def test_current_url() -> None:
    page = MagicMock()
    page.url = "http://127.0.0.1:5000/products"

    context = PlaywrightExecutionContext(page)

    assert context.current_url == "http://127.0.0.1:5000/products"


def test_goto() -> None:
    page = MagicMock()
    context = PlaywrightExecutionContext(page)

    context.goto("http://127.0.0.1:5000/login")

    page.goto.assert_called_once_with(
        "http://127.0.0.1:5000/login",
        wait_until="domcontentloaded",
    )


def test_click() -> None:
    page = MagicMock()
    locator = MagicMock()
    page.locator.return_value = locator

    context = PlaywrightExecutionContext(page)
    context.click("#checkout")

    page.locator.assert_called_once_with("#checkout")
    locator.first.click.assert_called_once_with()


def test_fill() -> None:
    page = MagicMock()
    locator = MagicMock()
    page.locator.return_value = locator

    context = PlaywrightExecutionContext(page)
    context.fill("#search", "laptop")

    page.locator.assert_called_once_with("#search")
    locator.first.fill.assert_called_once_with("laptop")
