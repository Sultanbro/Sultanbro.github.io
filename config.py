"""Read credentials from the process environment, never from source code."""
import os


def required_setting(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


BOT_TOKEN = required_setting("BOT_TOKEN")
PAYMENTS_TOKEN = required_setting("PAYMENTS_TOKEN")
