"""Tests for crawler logging."""

import logging

from hermes.crawler.logging import create_crawler_logger


def test_logger_creates_log_file(tmp_path) -> None:
    log_path = tmp_path / "crawler" / "crawl.log"

    logger = create_crawler_logger(
        log_path,
        name="hermes.test.create",
    )
    logger.info("crawl started")

    for handler in logger.handlers:
        handler.flush()

    assert log_path.exists()
    assert "crawl started" in log_path.read_text(encoding="utf-8")


def test_logger_writes_level_and_message(tmp_path) -> None:
    log_path = tmp_path / "crawl.log"

    logger = create_crawler_logger(
        log_path,
        name="hermes.test.format",
    )
    logger.warning("navigation failed")

    for handler in logger.handlers:
        handler.flush()

    content = log_path.read_text(encoding="utf-8")

    assert "WARNING" in content
    assert "navigation failed" in content


def test_logger_replaces_existing_handlers(tmp_path) -> None:
    log_path = tmp_path / "crawl.log"
    logger_name = "hermes.test.handlers"

    first_logger = create_crawler_logger(log_path, logger_name)
    second_logger = create_crawler_logger(log_path, logger_name)

    assert first_logger is second_logger
    assert len(second_logger.handlers) == 1
    assert isinstance(second_logger.handlers[0], logging.FileHandler)
    assert second_logger.propagate is False
