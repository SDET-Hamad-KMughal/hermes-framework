import pytest
from hermes.crawler.history import NavigationHistory


def test_records_preserve_visit_order() -> None:
    history = NavigationHistory()

    history.record(
        url="http://127.0.0.1:5000/",
        title="Home",
        depth=0,
    )

    history.record(
        url="http://127.0.0.1:5000/products",
        title="Products",
        depth=1,
        previous_url="http://127.0.0.1:5000/",
    )

    assert history.records[0].order == 1
    assert history.records[1].order == 2


def test_history_serialization() -> None:
    history = NavigationHistory()

    history.record(
        url="http://127.0.0.1:5000/cart",
        title="Cart",
        depth=2,
        previous_url="http://127.0.0.1:5000/products",
        action="click",
    )

    serialized = history.to_dict()

    assert serialized[0]["url"] == "http://127.0.0.1:5000/cart"
    assert serialized[0]["action"] == "click"
    assert serialized[0]["order"] == 1


def test_clear_history() -> None:
    history = NavigationHistory()

    history.record(
        url="http://127.0.0.1:5000/",
        title="Home",
        depth=0,
    )

    history.clear()

    assert len(history) == 0
    assert history.last_record is None


def test_last_record_returns_latest_visit() -> None:
    history = NavigationHistory()

    history.record(
        url="http://127.0.0.1:5000/",
        title="Home",
        depth=0,
    )
    history.record(
        url="http://127.0.0.1:5000/cart",
        title="Cart",
        depth=1,
        previous_url="http://127.0.0.1:5000/",
    )

    assert history.last_record is not None
    assert history.last_record.url == "http://127.0.0.1:5000/cart"


def test_empty_history_serialization() -> None:
    history = NavigationHistory()

    assert history.to_dict() == []


def test_empty_url_is_rejected() -> None:
    history = NavigationHistory()

    with pytest.raises(ValueError, match="url must not be empty"):
        history.record(
            url="",
            title="Page",
            depth=0,
        )


def test_whitespace_url_is_rejected() -> None:
    history = NavigationHistory()

    with pytest.raises(ValueError, match="url must not be empty"):
        history.record(
            url="   ",
            title="Page",
            depth=0,
        )


def test_negative_depth_is_rejected() -> None:
    history = NavigationHistory()

    with pytest.raises(ValueError, match="depth must not be negative"):
        history.record(
            url="http://127.0.0.1:5000/",
            title="Page",
            depth=-1,
        )


def test_empty_action_is_rejected() -> None:
    history = NavigationHistory()

    with pytest.raises(ValueError, match="action must not be empty"):
        history.record(
            url="http://127.0.0.1:5000/",
            title="Page",
            depth=0,
            action="",
        )

