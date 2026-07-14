"""Crawl orchestration for the HERMES crawler."""

from __future__ import annotations

from hermes.crawler.browser import BrowserManager
from hermes.crawler.config import CrawlerConfig
from hermes.crawler.dom_extractor import DOMExtractor
from hermes.crawler.models import CrawlResult
from hermes.crawler.queue import CrawlQueue
from hermes.crawler.url_manager import URLManager


class CrawlEngine:
    """Coordinate browser navigation, extraction, and URL discovery."""

    def __init__(
        self,
        config: CrawlerConfig,
        browser_manager: BrowserManager | None = None,
    ) -> None:
        self.config = config
        self.url_manager = URLManager(
            start_url=config.start_url,
            allow_external_links=config.allow_external_links,
        )
        self.extractor = DOMExtractor(self.url_manager)
        self.browser_manager = browser_manager or BrowserManager(config)

    def run(self) -> CrawlResult:
        """Execute one complete crawl session."""

        result = CrawlResult(start_url=self.url_manager.start_url)
        queue = CrawlQueue(max_depth=self.config.max_depth)
        queue.add(self.url_manager.start_url, depth=0)

        with self.browser_manager as manager:
            page = manager.new_page()

            while (
                not queue.is_empty
                and result.page_count < self.config.max_pages
            ):
                target = queue.pop()

                if queue.has_visited(target.url):
                    continue

                try:
                    page.goto(
                        target.url,
                        wait_until="domcontentloaded",
                    )

                    crawled_page = self.extractor.extract(
                        page,
                        depth=target.depth,
                    )

                    result.pages.append(crawled_page)
                    queue.mark_visited(target.url)

                    self._queue_links(
                        queue=queue,
                        current_depth=target.depth,
                        links=crawled_page.links,
                    )
                except Exception as exc:
                    queue.mark_visited(target.url)
                    result.errors.append(
                        f"{target.url}: {type(exc).__name__}: {exc}"
                    )

        return result


    def _queue_links(
        self,
        queue: CrawlQueue,
        current_depth: int,
        links,
    ) -> None:
        """Add crawlable links discovered on the current page."""

        next_depth = current_depth + 1

        for link in links:
            if not self.url_manager.is_crawlable(link.href):
                continue

            queue.add(
                url=link.href,
                depth=next_depth,
            )
