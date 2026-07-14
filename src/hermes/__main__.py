"""Command-line interface for HERMES."""

from __future__ import annotations

import argparse
from pathlib import Path

from hermes import __version__
from hermes.crawler import CrawlEngine, CrawlReport, CrawlerConfig


def build_parser() -> argparse.ArgumentParser:
    """Create the HERMES command-line parser."""

    parser = argparse.ArgumentParser(
        prog="hermes",
        description=(
            "HERMES: Hypothesis-driven Exploration through Reasoning "
            "for Modeling and Executing Semantic Workflows."
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"HERMES {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    crawl_parser = subparsers.add_parser(
        "crawl",
        help="Crawl a stateful web application.",
    )
    crawl_parser.add_argument(
        "--url",
        required=True,
        help="Starting URL for the crawl.",
    )
    crawl_parser.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="Maximum number of pages to crawl.",
    )
    crawl_parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum crawl depth.",
    )
    crawl_parser.add_argument(
        "--headed",
        action="store_true",
        help="Run Chromium with a visible browser window.",
    )
    crawl_parser.add_argument(
        "--allow-external-links",
        action="store_true",
        help="Allow crawling external domains.",
    )
    crawl_parser.add_argument(
        "--output",
        default="results/crawler/crawl_report.json",
        help="Path for the generated JSON report.",
    )

    return parser


def run_crawl(args: argparse.Namespace) -> int:
    """Execute the crawl command."""

    config = CrawlerConfig(
        start_url=args.url,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        headless=not args.headed,
        allow_external_links=args.allow_external_links,
    )

    result = CrawlEngine(config).run()
    report = CrawlReport(result)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report.save_json(output_path)

    statistics = report.statistics

    print(f"Crawl completed: {output_path}")
    print(f"Pages: {statistics.pages}")
    print(f"Links: {statistics.links}")
    print(f"Forms: {statistics.forms}")
    print(f"Actions: {statistics.actions}")
    print(f"Errors: {statistics.errors}")

    return 0 if statistics.errors == 0 else 1


def main() -> None:
    """Run the HERMES command-line interface."""

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "crawl":
        raise SystemExit(run_crawl(args))

    parser.print_help()


if __name__ == "__main__":
    main()
