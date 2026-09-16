import argparse
import sys

from src.config import HISTORY_PATH, OUTPUT_DIR, STORIES_PER_RUN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from src.editorial_calendar import get_profile
from src.history_manager import HistoryManager
from src.quote_researcher import QuoteResearcher
from src.story_renderer import StoryRenderer
from src.telegram_bot import TelegramBot


def run(total: int, day_override: str) -> int:
    profile = get_profile(day_override)
    print(f"▶️ {profile.label}: gerando {total} Stories com fontes públicas.")
    history = HistoryManager(HISTORY_PATH)
    renderer = StoryRenderer()
    telegram = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    candidates = QuoteResearcher().research(total, history.read(), profile)

    sent = 0
    for quote in candidates:
        if history.is_duplicate(quote):
            continue
        output = OUTPUT_DIR / f"{profile.slug}_{sent + 1}_{quote.content_id}.png"
        renderer.render(quote, profile, output)
        telegram.send_story(output, quote, sent + 1, total)
        history.add(quote)
        sent += 1

    if sent < total:
        telegram.send_message(f"⚠️ {profile.label}: {sent}/{total} Stories enviados. Não havia outros conteúdos inéditos adequados.")
    print(f"🏁 {profile.label}: {sent} Story(s) enviado(s).")
    return 0 if sent > 0 else 2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=STORIES_PER_RUN)
    parser.add_argument("--day", default="automatico", choices=["automatico", "segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not 1 <= args.count <= 5:
        print("A quantidade deve estar entre 1 e 5.", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(run(args.count, args.day))
