"""Playwright execution context for HERMES."""

from __future__ import annotations

from playwright.sync_api import Page


class PlaywrightExecutionContext:
    """Adapt a Playwright page to the HERMES execution interface."""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def current_url(self) -> str:
        """Return the currently loaded URL."""

        return self.page.url

    def goto(self, url: str) -> None:
        """Navigate to a URL."""

        self.page.goto(
            url,
            wait_until="domcontentloaded",
        )

    def click(self, selector: str) -> None:
        """Click an element."""

        self.page.locator(selector).first.click()

    def fill(self, selector: str, value: str) -> None:
        """Fill a form field."""

        self.page.locator(selector).first.fill(value)
