"""Tests for crawler session-state management."""

from unittest.mock import MagicMock

import pytest

from hermes.crawler.session import SessionManager


def make_browser_manager(context=None) -> MagicMock:
    manager = MagicMock()
    manager.context = context
    return manager


def test_session_starts_unauthenticated() -> None:
    manager = make_browser_manager(MagicMock())
    session = SessionManager(manager)

    assert session.is_authenticated is False


def test_authentication_state_can_change() -> None:
    manager = make_browser_manager(MagicMock())
    session = SessionManager(manager)

    session.mark_authenticated()
    assert session.is_authenticated is True

    session.mark_unauthenticated()
    assert session.is_authenticated is False


def test_get_cookies() -> None:
    context = MagicMock()
    context.cookies.return_value = [
        {
            "name": "session",
            "value": "abc123",
            "domain": "127.0.0.1",
            "path": "/",
        }
    ]

    session = SessionManager(make_browser_manager(context))

    cookies = session.get_cookies()

    assert cookies[0]["name"] == "session"
    context.cookies.assert_called_once_with()


def test_set_cookies() -> None:
    context = MagicMock()
    session = SessionManager(make_browser_manager(context))

    cookies = [
        {
            "name": "session",
            "value": "abc123",
            "domain": "127.0.0.1",
            "path": "/",
        }
    ]

    session.set_cookies(cookies)

    context.add_cookies.assert_called_once_with(cookies)


def test_clear_session() -> None:
    context = MagicMock()
    session = SessionManager(make_browser_manager(context))
    session.mark_authenticated()

    session.clear()

    context.clear_cookies.assert_called_once_with()
    assert session.is_authenticated is False


@pytest.mark.parametrize(
    "operation",
    [
        "get",
        "set",
        "clear",
    ],
)
def test_active_context_is_required(operation: str) -> None:
    session = SessionManager(make_browser_manager(None))

    with pytest.raises(
        RuntimeError,
        match="BrowserManager must be started",
    ):
        if operation == "get":
            session.get_cookies()
        elif operation == "set":
            session.set_cookies([])
        else:
            session.clear()
