# LuminaryAI Discord Bot

Discord bot for the LumixCore project. Built with Python.

## Features

- AI chat, image generation, and web search
- Fun commands (wordle, rps, random facts)
- Prefix and/or slash commands (toggleable via `.env`)
- Blacklist system backed by MongoDB

## Project structure

```
backend/
├── main.py                 # Entry point
├── .env.example            # Example environment config
├── .env                    # Your local secrets (not committed)
├── requirements.txt
├── assets/
│   ├── fonts/              # Fonts used by image commands
│   └── images/             # Static images for embeds
├── bot/
│   ├── config.py           # Loads settings from .env
│   ├── cogs/
│   │   ├── prefix/         # Prefix command cogs
│   │   └── slash/          # Slash command cogs
│   ├── events/             # Discord event listeners
│   └── utils/              # Shared helpers (embeds, AI, etc.)
└── cache/                  # Runtime cache (gitignored)
```

## Setup

1. **Clone and install dependencies**

```bash
pip install -r requirements.txt
```

2. **Configure environment**

```bash
cp .env.example .env
```

Edit `.env` and set at least:

| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Bot token from the Discord Developer Portal |
| `POLLINATIONS_TOKEN` | Token for Pollinations image generation |
| `BOT_NAME` | Display name used in embeds |
| `BOT_PREFIX` | Prefix for text commands |
| `ENABLE_PREFIX_COMMANDS` | `true` / `false` |
| `ENABLE_SLASH_COMMANDS` | `true` / `false` |
| `EMBED_COLOR_ERROR` | Hex color for error embeds |
| `EMBED_COLOR_SUCCESS` | Hex color for success embeds |

3. **Run**

```bash
python main.py
```

## Links

- Website: https://lumixcore.com
- Discord: 
