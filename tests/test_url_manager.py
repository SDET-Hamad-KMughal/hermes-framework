"""Tests for crawler URL normalization and filtering."""

import pytest

from hermes.crawler.url_manager import URLManager


@pytest.fixture
def manager() -> URLManager:
    return URLManager(
        start_url="http://127.0.0.1:5000/",
        allow_external_links=False,
    )


def test_normalize_absolute_url(manager: URLManager) -> None:
    result = manager.normalize(
        "HTTP://127.0.0.1:5000/products#catalog"
    )

    assert result == "http://127.0.0.1:5000/products"


def test_normalize_relative_url(manager: URLManager) -> None:
    result = manager.normalize(
        "../cart",
        base_url="http://127.0.0.1:5000/products/1",
    )

    assert result == "http://127.0.0.1:5000/cart"


def test_normalize_empty_path(manager: URLManager) -> None:
    result = manager.normalize("http://127.0.0.1:5000")

    assert result == "http://127.0.0.1:5000/"


@pytest.mark.parametrize(
    "url",
    [
        "",
        "   ",
        "javascript:void(0)",
        "mailto:test@example.com",
        "tel:+123456789",
        "data:text/plain,hello",
    ],
)
def test_ignored_urls_return_empty_string(
    manager: URLManager,
    url: str,
) -> None:
    assert manager.normalize(url) == ""


def test_internal_url_detection(manager: URLManager) -> None:
    assert manager.is_internal(
        "http://127.0.0.1:5000/checkout"
    ) is True


def test_external_url_detection(manager: URLManager) -> None:
    assert manager.is_internal(
        "https://example.com/"
    ) is False


def test_external_url_is_not_crawlable_by_default(
    manager: URLManager,
) -> None:
    assert manager.is_crawlable(
        "https://example.com/"
    ) is False


def test_external_url_can_be_allowed() -> None:
    manager = URLManager(
        start_url="http://127.0.0.1:5000/",
        allow_external_links=True,
    )

    assert manager.is_crawlable(
        "https://example.com/"
    ) is True


def test_relative_internal_url_is_crawlable(
    manager: URLManager,
) -> None:
    assert manager.is_crawlable(
        "/checkout",
        base_url="http://127.0.0.1:5000/cart",
    ) is True