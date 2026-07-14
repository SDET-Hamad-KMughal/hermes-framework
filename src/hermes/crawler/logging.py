"""Logging utilities for the HERMES crawler."""

from __future__ import annotations

import logging
from pathlib import Path


def create_crawler_logger(
    log_path: str | Path,
    name: str = "hermes.crawler",
) -> logging.Logger:
    """Create a crawler logger that writes to a file."""

    output_path = Path(log_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    handler = logging.FileHandler(
        output_path,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
    )

    logger.addHandler(handler)
    return logger
