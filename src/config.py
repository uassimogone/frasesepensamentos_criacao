from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TELEGRAM_BOT_TOKEN = __import__("os").getenv("TEST_TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = __import__("os").getenv("TEST_TELEGRAM_CHAT_ID", "").strip()
STORIES_PER_RUN = int(__import__("os").getenv("STORIES_PER_RUN", "3"))

HISTORY_PATH = BASE_DIR / "data" / "history.json"
DAILY_RUN_STATE_PATH = BASE_DIR / "data" / "daily_runs.json"
OUTPUT_DIR = BASE_DIR / "output"

# O repertório de autores é definido por rótulo em editorial_calendar.py.
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
