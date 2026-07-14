"""Session-state management for the HERMES crawler."""

from __future__ import annotations

from typing import Any

from hermes.crawler.browser import BrowserManager


class SessionManager:
    """Manage cookies and authentication state for a browser session."""

    def __init__(self, browser_manager: BrowserManager) -> None:
        self.browser_manager = browser_manager
        self._authenticated = False

    @property
    def is_authenticated(self) -> bool:
        """Return whether the current session is authenticated."""
        return self._authenticated

    def mark_authenticated(self) -> None:
        """Mark the current browser session as authenticated."""
        self._authenticated = True

    def mark_unauthenticated(self) -> None:
        """Mark the current browser session as unauthenticated."""
        self._authenticated = False

    def get_cookies(self) -> list[dict[str, Any]]:
        """Return cookies from the active browser context."""
        context = self.browser_manager.context

        if context is None:
            raise RuntimeError(
                "BrowserManager must be started before reading cookies"
            )

        return context.cookies()

    def set_cookies(self, cookies: list[dict[str, Any]]) -> None:
        """Add cookies to the active browser context."""
        context = self.browser_manager.context

        if context is None:
            raise RuntimeError(
                "BrowserManager must be started before setting cookies"
            )

        context.add_cookies(cookies)

    def clear(self) -> None:
        """Clear cookies and reset authentication state."""
        context = self.browser_manager.context

        if context is None:
            raise RuntimeError(
                "BrowserManager must be started before clearing session"
            )

        context.clear_cookies()
        self._authenticated = False
