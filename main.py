import argparse
import sys

from src.config import (
    HISTORY_PATH,
    OUTPUT_DIR,
    STORIES_PER_RUN,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)
from src.history_manager import HistoryManager
from src.quote_researcher import QuoteResearcher
from src.story_renderer import StoryRenderer
from src.telegram_bot import TelegramBot


def run(total: int) -> int:
    print(f"▶️ Iniciando geração de {total} Stories com fontes públicas.")
    history = HistoryManager(HISTORY_PATH)
    researcher = QuoteResearcher()
    renderer = StoryRenderer()
    telegram = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

    candidates = researcher.research(desired=total, recent_items=history.read())
    sent = 0

    for quote in candidates:
        if history.is_duplicate(quote):
            print(f"⏭️ Duplicata descartada: {quote.author}")
            continue

        output = OUTPUT_DIR / f"story_{sent + 1}_{quote.content_id}.png"
        renderer.render(quote, output)
        telegram.send_story(output, quote, sent + 1, total)
        history.add(quote)
        sent += 1
        print(f"✅ Story enviado: {quote.author} ({quote.content_id})")

    if sent < total:
        warning = (
            f"⚠️ Execução concluída com {sent}/{total} Stories. "
            "Não havia outras citações inéditas com referência adequada nas fontes consultadas."
        )
        print(warning)
        telegram.send_message(warning)

    print(f"🏁 Execução finalizada: {sent} Story(s) enviado(s).")
    return 0 if sent > 0 else 2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=STORIES_PER_RUN)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not 1 <= args.count <= 5:
        print("A quantidade deve estar entre 1 e 5.", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(run(args.count))
