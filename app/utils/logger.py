"""Centralized logging configuration."""

import logging
import sys
from typing import Optional


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure application-wide logging.

    Args:
        log_level: Logging level string (DEBUG, INFO, WARNING, ERROR).

    Returns:
        Configured root logger instance.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | "
        "request_id=%(request_id)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root_logger = logging.getLogger("dental_ai_agent")
    root_logger.setLevel(numeric_level)

    if not root_logger.handlers:
        root_logger.addHandler(handler)

    root_logger.propagate = False
    return root_logger


class RequestIdFilter(logging.Filter):
    """Inject request_id into log records for traceability."""

    def __init__(self, request_id: str = "-") -> None:
        super().__init__()
        self.request_id = request_id

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = getattr(record, "request_id", self.request_id)
        return True


def get_logger(name: str, request_id: Optional[str] = None) -> logging.Logger:
    """
    Return a child logger with optional request ID context.

    Args:
        name: Logger name, typically module name.
        request_id: Optional request correlation ID.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(f"dental_ai_agent.{name}")
    if request_id:
        logger.addFilter(RequestIdFilter(request_id))
    return logger
