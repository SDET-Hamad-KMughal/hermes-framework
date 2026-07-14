"""Browser lifecycle management for the HERMES crawler."""

from __future__ import annotations

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from hermes.crawler.config import CrawlerConfig


class BrowserManager:
    """Manage Playwright browser resources for one crawler session."""

    def __init__(self, config: CrawlerConfig) -> None:
        self.config = config
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    @property
    def is_started(self) -> bool:
        """Return whether the browser session has been started."""
        return self._browser is not None and self._context is not None

    @property
    def context(self) -> BrowserContext | None:
        """Return the active browser context, if available."""
        return self._context

    def start(self) -> BrowserManager:
        """Start Playwright, Chromium, and a browser context."""
        if self.is_started:
            return self

        self._playwright = sync_playwright().start()

        try:
            self._browser = self._playwright.chromium.launch(
                headless=self.config.headless,
            )
            self._context = self._browser.new_context(
                ignore_https_errors=True,
            )
            self._context.set_default_timeout(
                self.config.page_timeout_seconds * 1000
            )
        except Exception:
            self.close()
            raise

        return self

    def new_page(self) -> Page:
        """Create and return a new browser page."""
        if self._context is None:
            raise RuntimeError("BrowserManager must be started before creating a page")

        return self._context.new_page()

    def close(self) -> None:
        """Close all browser resources safely."""
        if self._context is not None:
            self._context.close()
            self._context = None

        if self._browser is not None:
            self._browser.close()
            self._browser = None

        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def __enter__(self) -> BrowserManager:
        """Start the browser when entering a context manager."""
        return self.start()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Close the browser when leaving a context manager."""
        self.close()