"""Tests for crawler configuration and data models."""

import pytest

from hermes.crawler import (
    Action,
    CrawlerConfig,
    CrawlResult,
    Form,
    FormField,
    Link,
    Page,
)


def test_crawler_config_defaults() -> None:
    config = CrawlerConfig(start_url="http://127.0.0.1:5000")

    assert config.max_pages == 50
    assert config.max_depth == 5
    assert config.headless is True
    assert config.allow_external_links is False


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("start_url", ""),
        ("max_pages", 0),
        ("max_depth", -1),
        ("page_timeout_seconds", 0),
    ],
)
def test_invalid_crawler_configuration(
    field_name: str,
    value: object,
) -> None:
    arguments = {"start_url": "http://127.0.0.1:5000"}
    arguments[field_name] = value

    with pytest.raises(ValueError):
        CrawlerConfig(**arguments)


def test_crawl_result_metrics_and_serialization() -> None:
    page = Page(
        url="http://127.0.0.1:5000/login",
        title="Login",
        depth=0,
        status_code=200,
        links=[
            Link(
                text="Home",
                href="http://127.0.0.1:5000/",
                internal=True,
            )
        ],
        forms=[
            Form(
                action="/login",
                method="POST",
                fields=(
                    FormField(
                        name="email",
                        field_type="email",
                        required=True,
                    ),
                ),
            )
        ],
        actions=[
            Action(
                action_type="submit",
                label="Login",
                selector="button[type='submit']",
            )
        ],
    )

    result = CrawlResult(
        start_url="http://127.0.0.1:5000",
        pages=[page],
    )

    assert result.page_count == 1
    assert result.link_count == 1
    assert result.form_count == 1
    assert result.action_count == 1
    assert result.to_dict()["pages"][0]["title"] == "Login"