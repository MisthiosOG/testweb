# TrashGC

Telegram bot for Sky: Children of the Light automation — farm, quests, Eden, wings, map unlocks, and more. Refactored from trashgc-main-bot with modular `sky_functions` and textdb auth bypass.

## Requirements

- Python 3.9+ (3.12 recommended)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

## Quick start

```bash
# 1. Clone and enter the project
git clone https://github.com/iPowfuVM/TrashGC.git
cd TrashGC

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and set MAIN_TOKEN to your bot token

# 5. Run the bot
python main.py
```

Open your bot in Telegram and send `/start`.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MAIN_TOKEN` | Yes | Main bot token (also accepts `BOT_TOKEN_MAIN`) |
| `BOT_TOKEN_LOG` | No | Optional second bot for admin/log messages |

Never commit `.env`. Copy from `.env.example` and fill in your own values locally.

## Project layout

```
main.py              # Telegram handlers
bot_context.py       # Shared bot references
users/               # User session and login flow
functions/           # Auth, sessions, Sky API requests, version scrapers
sky_functions/       # Game features (farm, quests, eden, wings, …)
resources/           # Game JSON data (levels, quests, wings, …)
```

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Begin login flow (Live or Beta server) |
| `/cancel` | Reset infinite loops (infeden / infseasonal) |
| `/help` | Feature list |
| `/lua` | Forward Lua helper file |
| `/lib` | Forward Lib helper file |
| `/sauto` | Hidden quick-run from Lua code |
| `/create-account` | Create and bind a new Sky account |

## Deploy (Heroku-style)

`Procfile` and `runtime.txt` are included. Set `MAIN_TOKEN` in your host's environment variables — not in the repo.

```bash
git push heroku main
```

## Auth

Access is gated by a textdb bypass list. Contact the bot owner (`iPowfuVM`) to be added.

## License

Use at your own risk. Ask the bot owner before using on accounts you do not own.
