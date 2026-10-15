"""Read credentials from the process environment, never from source code."""
import os


def required_setting(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


BOT_TOKEN = required_setting("BOT_TOKEN")
PAYMENTS_TOKEN = required_setting("PAYMENTS_TOKEN")

from urllib.parse import urlparse

WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://sultanbro.github.io/").strip()
if urlparse(WEBAPP_URL).scheme != "https" or not urlparse(WEBAPP_URL).netloc:
    raise RuntimeError("WEBAPP_URL must be an HTTPS URL")
ORDERS_DB = os.environ.get("ORDERS_DB", "data/orders.sqlite3")
