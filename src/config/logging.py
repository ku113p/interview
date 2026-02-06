import logging
import logging.config
import re
import sys
from typing import Iterable

from pythonjsonlogger.json import JsonFormatter as jsonlogger_JsonFormatter

REDACT_PATTERNS: Iterable[re.Pattern[str]] = (re.compile(r"sk-or-v1-[A-Za-z0-9]+"),)


def _redact(text: str) -> str:
    """Redact sensitive information from log messages.

    Args:
        text: Text to redact

    Returns:
        str: Text with sensitive patterns replaced
    """
    redacted = text
    for pattern in REDACT_PATTERNS:
        redacted = pattern.sub("***REDACTED***", redacted)
    return redacted


class RedactingJsonFormatter(jsonlogger_JsonFormatter):
    """JSON formatter that redacts sensitive information from logs."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        return _redact(message)


def configure_logging(level: int = logging.INFO, use_json: bool = True) -> None:
    """Configure application logging with optional JSON formatting and redaction.

    Args:
        level: Logging level (default: logging.INFO)
        use_json: Whether to use JSON formatting (default: True)
    """
    formatter_name = "json" if use_json else "standard"
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "src.config.logging.RedactingJsonFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": formatter_name,
                "stream": sys.stderr,
            },
        },
        "root": {
            "level": level,
            "handlers": ["console"],
        },
    }

    logging.config.dictConfig(config)
