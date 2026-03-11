"""
config — Loads application settings from YAML and environment variables.
"""

import os
from pathlib import Path
from urllib.parse import quote_plus

import yaml
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

# Resolve the path to settings.yaml relative to this file
_CONFIG_PATH = Path(__file__).resolve().parent / "settings.yaml"


def load_settings() -> dict:
    """Read settings.yaml and return as dict."""
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Singleton-like access to settings
SETTINGS = load_settings()

# Shortcuts for frequently used values
TELEGRAM_BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY: str = os.environ["OPENAI_API_KEY"]

AI_MODEL: str = SETTINGS["ai"]["model"]
AI_REASONING: bool = SETTINGS["ai"]["reasoning"]
AI_LANGUAGE: str = SETTINGS["ai"]["language"]
AI_INSTRUCTIONS: str = SETTINGS["ai"]["instructions"]
AI_MAX_TOKENS: int = SETTINGS["ai"]["max_tokens"]
AI_TEMPERATURE: float = SETTINGS["ai"]["temperature"]
AI_TIMEOUT: int = SETTINGS["ai"]["timeout"]
AI_MAX_RETRIES: int = SETTINGS["ai"]["max_retries"]

MIN_AGE: int = SETTINGS["telegram"]["min_age"]
MAX_CONTEXT_MESSAGES: int = SETTINGS["conversation"]["max_context_messages"]

POSTGRES_DATABASE: str = os.getenv("POSTGRES_DB", SETTINGS["postgres"]["database"])
POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", SETTINGS["postgres"]["host"])
POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", SETTINGS["postgres"]["port"]))
POSTGRES_USER: str = os.getenv("POSTGRES_USER", SETTINGS["postgres"]["user"])
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", SETTINGS["postgres"]["password"])

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"postgresql://{quote_plus(POSTGRES_USER)}:{quote_plus(POSTGRES_PASSWORD)}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}",
)
