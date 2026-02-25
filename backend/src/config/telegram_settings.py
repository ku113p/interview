"""Telegram bot configuration."""

import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_MODE = os.getenv("TELEGRAM_MODE", "polling")
TELEGRAM_WEBHOOK_HOST = os.getenv("TELEGRAM_WEBHOOK_HOST", "0.0.0.0")
TELEGRAM_WEBHOOK_PORT_STR = os.getenv("TELEGRAM_WEBHOOK_PORT", "8443")
TELEGRAM_WEBHOOK_PATH = os.getenv("TELEGRAM_WEBHOOK_PATH", "/telegram/webhook")
TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL", "")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

TELEGRAM_MAX_MESSAGE_LENGTH = 4096


def get_webhook_port() -> int:
    """Parse and return webhook port."""
    try:
        return int(TELEGRAM_WEBHOOK_PORT_STR)
    except ValueError as e:
        raise RuntimeError(
            f"TELEGRAM_WEBHOOK_PORT must be an integer, got: {TELEGRAM_WEBHOOK_PORT_STR}"
        ) from e


def validate_telegram_config() -> None:
    """Validate Telegram configuration."""
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN not set. Get token from @BotFather on Telegram."
        )
    if TELEGRAM_MODE == "webhook":
        if not TELEGRAM_WEBHOOK_URL:
            raise RuntimeError(
                "TELEGRAM_WEBHOOK_URL required when TELEGRAM_MODE=webhook"
            )
        get_webhook_port()  # Validate port is integer
