# magaz

## Runtime configuration

This repository contains a Python Telegram bot and its web frontend.
Supply `BOT_TOKEN` and `PAYMENTS_TOKEN` as environment variables before starting
`main.py`. `.env.example` lists the required names; Python does not automatically
load that file. Use your process manager or export the variables in your shell.
The application stops with a configuration error when either value is missing.
Never put bot or payment credentials into frontend assets.
