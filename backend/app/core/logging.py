from __future__ import annotations

import logging
import sys
from typing import Any

from .settings import settings


def setup_logging() -> None:
    """
    Minimal production-friendly logging setup.
    - JSON logging can be added later without changing app code.
    """
    root = logging.getLogger()
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    handler.setFormatter(formatter)

    root.addHandler(handler)
    root.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_kv(logger: logging.Logger, msg: str, **kwargs: Any) -> None:
    # Small helper to keep logs structured-ish without introducing more deps.
    if kwargs:
        msg = f"{msg} | " + " ".join(f"{k}={v!r}" for k, v in kwargs.items())
    logger.info(msg)


