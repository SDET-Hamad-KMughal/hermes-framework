"""Build a HERMES state graph from a crawl report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hermes.crawler.models import (
    Action,
    CrawlResult,
    Form,
    FormField,
    Link,
    Page,
)
from hermes.state_graph import StateGraphBuilder, StateGraphExporter


def load_crawl_result(path: Path) -> CrawlResult:
    """Load a crawler JSON report into HERMES models."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    pages: list[Page] = []

    for page_data in payload.get("pages", []):
        links = [
            Link(
                text=item["text"],
                href=item["href"],
                internal=item["internal"],
            )
            for item in page_data.get("links", [])
        ]

        actions = [
            Action(
                action_type=item["action_type"],
                label=item["label"],
                selector=item["selector"],
                target=item.get("target"),
            )
            for item in page_data.get("actions", [])
        ]

        pages.append(
            Page(
                url=page_data["url"],
                title=page_data["title"],
                depth=page_data["depth"],
                status_code=page_data.get("status_code"),
                links=links,
                actions=actions,
            )
        )

        forms = [
            Form(
                action=item["action"],
                method=item["method"],
                fields=[
                    FormField(
                        name=field["name"],
                        field_type=field["field_type"],
                        value=field.get("value"),
                        required=field.get("required", False),
                    )
                    for field in item.get("fields", [])
                ],
            )
            for item in page_data.get("forms", [])
        ]

        pages[-1].forms.extend(forms)

    return CrawlResult(
        start_url=payload.get("start_url", ""),
        pages=pages,
        errors=list(payload.get("errors", [])),
    )


def main() -> None:
    """Build and export a state graph."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="results/crawler/crawl_report.json",
    )
    parser.add_argument(
        "--json-output",
        default="results/state_graph/state_graph.json",
    )
    parser.add_argument(
        "--dot-output",
        default="results/state_graph/state_graph.dot",
    )
    args = parser.parse_args()

    crawl_result = load_crawl_result(Path(args.input))
    graph = StateGraphBuilder().build(crawl_result)

    StateGraphExporter.save_json(graph, args.json_output)
    StateGraphExporter.save_dot(graph, args.dot_output)

    print(f"States: {graph.state_count}")
    print(f"Transitions: {graph.transition_count}")
    print(f"JSON: {args.json_output}")
    print(f"DOT: {args.dot_output}")




def main() -> None:
    """Build and export a state graph."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default="results/crawler/crawl_report.json",
    )

    parser.add_argument(
        "--json-output",
        default="results/state_graph/state_graph.json",
    )

    parser.add_argument(
        "--dot-output",
        default="results/state_graph/state_graph.dot",
    )

    args = parser.parse_args()

    crawl_result = load_crawl_result(Path(args.input))
    graph = StateGraphBuilder().build(crawl_result)

    StateGraphExporter.save_json(
        graph,
        args.json_output,
    )

    StateGraphExporter.save_dot(
        graph,
        args.dot_output,
    )

    print(f"States: {graph.state_count}")
    print(f"Transitions: {graph.transition_count}")
    print(f"JSON: {args.json_output}")
    print(f"DOT: {args.dot_output}")


if __name__ == "__main__":
    main()
