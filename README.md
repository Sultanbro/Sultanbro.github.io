> Sanitized source snapshot for code review. Runtime credentials, operational exports, and personal test data are excluded. External integrations require your own configuration. This legacy project needs dependency and deployment review before production use. Existing license and attribution notices remain applicable. See [SECURITY.md](SECURITY.md).

# magaz

## Runtime configuration

This repository contains a Python Telegram bot and its web frontend.
Supply `BOT_TOKEN` and `PAYMENTS_TOKEN` as environment variables before starting
`main.py`. `.env.example` lists the required names; Python does not automatically
load that file. Use your process manager or export the variables in your shell.
The application stops with a configuration error when either value is missing.
Never put bot or payment credentials into frontend assets.
