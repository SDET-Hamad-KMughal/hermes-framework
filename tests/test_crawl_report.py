"""Tests for crawl-report generation."""

import json

from hermes.crawler.history import NavigationHistory
from hermes.crawler.models import Action, CrawlResult, Form, Link, Page
from hermes.crawler.report import CrawlReport, CrawlStatistics


def make_result() -> CrawlResult:
    return CrawlResult(
        start_url="http://127.0.0.1:5000/",
        pages=[
            Page(
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
                forms=[
                    Form(
                        action="http://127.0.0.1:5000/login",
                        method="POST",
                    )
                ],
                actions=[
                    Action(
                        action_type="navigate",
                        label="Products",
                        selector="#products-link",
                        target="http://127.0.0.1:5000/products",
                    )
                ],
            )
        ],
        errors=["sample error"],
    )


def test_report_statistics() -> None:
    report = CrawlReport(make_result())

    statistics = report.statistics

    assert isinstance(statistics, CrawlStatistics)
    assert statistics.pages == 1
    assert statistics.links == 1
    assert statistics.forms == 1
    assert statistics.actions == 1
    assert statistics.errors == 1


def test_report_serialization() -> None:
    history = NavigationHistory()
    history.record(
        url="http://127.0.0.1:5000/",
        title="Home",
        depth=0,
        action="start",
    )

    report = CrawlReport(make_result(), history)
    data = report.to_dict()

    assert data["statistics"]["pages"] == 1
    assert data["statistics"]["errors"] == 1
    assert data["pages"][0]["title"] == "Home"
    assert data["history"][0]["action"] == "start"
    assert data["errors"] == ["sample error"]


def test_save_json(tmp_path) -> None:
    output = tmp_path / "crawl_report.json"
    report = CrawlReport(make_result())

    report.save_json(output)

    assert output.exists()

    saved = json.loads(output.read_text(encoding="utf-8"))

    assert saved["statistics"]["pages"] == 1
    assert saved["pages"][0]["url"] == "http://127.0.0.1:5000/"
