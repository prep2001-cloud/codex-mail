"""Logging utilities for the invoice automation system."""
from __future__ import annotations

import logging
from typing import Any, Mapping, Optional

_LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format=_LOG_FORMAT)


def log_event(logger: logging.Logger, message: str, *, extra: Optional[Mapping[str, Any]] = None) -> None:
    if extra:
        logger.info("%s | extra=%s", message, extra)
    else:
        logger.info(message)
