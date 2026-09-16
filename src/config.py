import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TEST_TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TEST_TELEGRAM_CHAT_ID", "").strip()
STORIES_PER_RUN = int(os.getenv("STORIES_PER_RUN", "2"))

TEXT_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
]

HISTORY_PATH = BASE_DIR / "data" / "history.json"
OUTPUT_DIR = BASE_DIR / "output"

BLOCKED_SOURCE_DOMAINS = {
    "pinterest.com",
    "brainyquote.com",
    "goodreads.com",
    "pensador.com",
    "frases.com.br",
    "instagram.com",
    "facebook.com",
    "tiktok.com",
    "x.com",
    "twitter.com",
}
