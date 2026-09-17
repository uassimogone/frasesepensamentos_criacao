from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TELEGRAM_BOT_TOKEN = __import__("os").getenv("TEST_TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = __import__("os").getenv("TEST_TELEGRAM_CHAT_ID", "").strip()
STORIES_PER_RUN = int(__import__("os").getenv("STORIES_PER_RUN", "3"))

HISTORY_PATH = BASE_DIR / "data" / "history.json"
OUTPUT_DIR = BASE_DIR / "output"

# Páginas gratuitas em português. Cada citação precisa trazer referência na página.
WIKIQUOTE_AUTHORS = [
    "Albert Einstein",
    "Anaïs Nin",
    "Aristóteles",
    "Cícero",
    "Confúcio",
    "Eleanor Roosevelt",
    "Epicteto",
    "Friedrich Nietzsche",
    "Hannah Arendt",
    "Marco Aurélio",
    "Maya Angelou",
    "Michel de Montaigne",
    "Nelson Mandela",
    "Sêneca",
    "Simone de Beauvoir",
    "Virginia Woolf",
    "Winston Churchill",
]

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
