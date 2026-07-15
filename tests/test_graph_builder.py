"""Tests for building state graphs from crawler results."""

from hermes.crawler.models import Action, CrawlResult, Page
from hermes.state_graph.builder import StateGraphBuilder


def make_result() -> CrawlResult:
    home_url = "http://127.0.0.1:5000/"
    products_url = "http://127.0.0.1:5000/products"

    return CrawlResult(
        start_url=home_url,
        pages=[
            Page(
                url=home_url,
                title="Home",
                depth=0,
                status_code=200,
                actions=[
                    Action(
                        action_type="navigate",
                        label="Products",
                        selector="#products-link",
                        target=products_url,
                    ),
                    Action(
                        action_type="navigate",
                        label="External",
                        selector="#external-link",
                        target="https://example.com/",
                    ),
                ],
            ),
            Page(
                url=products_url,
                title="Products",
                depth=1,
                status_code=200,
            ),
        ],
    )


def test_builder_creates_states() -> None:
    graph = StateGraphBuilder().build(make_result())

    assert graph.state_count == 2

    titles = {state.title for state in graph.states.values()}
    assert titles == {"Home", "Products"}


def test_builder_creates_transition_for_crawled_target() -> None:
    graph = StateGraphBuilder().build(make_result())

    assert graph.transition_count == 1

    transition = graph.transitions[0]

    assert transition.action_type == "navigate"
    assert transition.label == "Products"
    assert transition.selector == "#products-link"
    assert transition.semantic_target == "http://127.0.0.1:5000/products"


def test_builder_ignores_uncrawled_targets() -> None:
    graph = StateGraphBuilder().build(make_result())

    assert all(
        transition.semantic_target != "https://example.com/"
        for transition in graph.transitions
    )


def test_builder_preserves_page_metrics() -> None:
    graph = StateGraphBuilder().build(make_result())

    home = next(
        state for state in graph.states.values() if state.title == "Home"
    )

    assert home.action_count == 2
    assert home.form_count == 0
    assert home.metadata["status_code"] == 200
    assert home.metadata["link_count"] == 0


def test_builder_handles_empty_crawl_result() -> None:
    result = CrawlResult(start_url="http://127.0.0.1:5000/")

    graph = StateGraphBuilder().build(result)

    assert graph.state_count == 0
    assert graph.transition_count == 0
