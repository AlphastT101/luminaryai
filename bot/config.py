import os
from pathlib import Path
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _env_bool(key: str, default: bool = False) -> bool:
    value = os.getenv(key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(key: str, default: int = 0) -> int:
    value = os.getenv(key)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


def _env_color(key: str, default: int) -> int:
    value = os.getenv(key)
    if value is None or value.strip() == "":
        return default
    raw = value.strip().lower().replace("0x", "").replace("#", "")
    try:
        return int(raw, 16)
    except ValueError:
        return default


def _env_optional_int(key: str):
    value = os.getenv(key)
    if value is None or value.strip() == "":
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


DISCORD_TOKEN = _env("DISCORD_TOKEN")
BOT_NAME = _env("BOT_NAME", "LuminaryAI")
BOT_PREFIX = _env("BOT_PREFIX", "ai.")
SHARD_COUNT = _env_int("SHARD_COUNT", 2)

ENABLE_PREFIX_COMMANDS = _env_bool("ENABLE_PREFIX_COMMANDS", True)
ENABLE_SLASH_COMMANDS = _env_bool("ENABLE_SLASH_COMMANDS", True)

MONGODB_URI = _env("MONGODB_URI", "mongodb://localhost:27017/")
POLLINATIONS_TOKEN = _env("POLLINATIONS_TOKEN")

EMBED_COLOR_DEFAULT = _env_color("EMBED_COLOR_DEFAULT", 0x708090)
EMBED_COLOR_ERROR = _env_color("EMBED_COLOR_ERROR", 0xFF0000)
EMBED_COLOR_SUCCESS = _env_color("EMBED_COLOR_SUCCESS", 0x00FF00)
EMBED_COLOR_WARNING = _env_color("EMBED_COLOR_WARNING", 0xFFA500)
EMBED_COLOR_PROCESSING = _env_color("EMBED_COLOR_PROCESSING", 0x99CCFF)
EMBED_COLOR_CONFIRMATION = _env_color("EMBED_COLOR_CONFIRMATION", 0xC8DC6C)

GUILD_LOG_CHANNEL_ID = _env_optional_int("GUILD_LOG_CHANNEL_ID")
ERROR_LOG_CHANNEL_ID = _env_optional_int("ERROR_LOG_CHANNEL_ID")
WELCOME_GUILD_ID = _env_optional_int("WELCOME_GUILD_ID")
WELCOME_CHANNEL_ID = _env_optional_int("WELCOME_CHANNEL_ID")

SUPPORT_SERVER_URL = _env("SUPPORT_SERVER_URL", "")
WEBSITE_URL = _env("WEBSITE_URL", "https://lumixcore.com")
PLAYGROUND_URL = _env("PLAYGROUND_URL", "https://play.lumixcore.com")
BOT_INVITE_URL = _env(
    "BOT_INVITE_URL",
    "&permissions=8&scope=bot",
)
OWNER_NAME = _env("OWNER_NAME", "AlphasT101")
OWNER_URL = _env("OWNER_URL", "https://me.lumixcore.com")

ASSETS_DIR = ROOT_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
FONTS_DIR = ASSETS_DIR / "fonts"
CACHE_DIR = ROOT_DIR / "cache"
AI_IMAGE_PATH = IMAGES_DIR / "thumbnail.png"
FONT_PATH = FONTS_DIR / "arial.ttf"
