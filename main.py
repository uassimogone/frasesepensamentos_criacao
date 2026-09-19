import argparse
import sys

from src.config import DAILY_RUN_STATE_PATH, HISTORY_PATH, OUTPUT_DIR, STORIES_PER_RUN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from src.daily_run import DailyRunGuard
from src.editorial_calendar import get_profile
from src.history_manager import HistoryManager
from src.quote_researcher import QuoteResearcher
from src.story_renderer import StoryRenderer
from src.special_quotes import POWER_PROFILE, power_and_corruption_quotes
from src.telegram_bot import TelegramBot


def run(total: int, day_override: str, run_mode: str = "workflow_dispatch", special: str = "nenhum") -> int:
    guard = DailyRunGuard(DAILY_RUN_STATE_PATH)
    if run_mode == "schedule" and guard.already_completed():
        print("⏭️ A entrega automática de hoje já foi concluída; esta janela redundante será ignorada.")
        return 0

    is_special = special == "poder_corrupcao"
    profile = POWER_PROFILE if is_special else get_profile(day_override)
    print(f"▶️ {profile.label}: gerando {total} Stories com fontes públicas.")
    history = HistoryManager(HISTORY_PATH)
    renderer = StoryRenderer()
    telegram = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    candidates = (
        power_and_corruption_quotes()[:total]
        if is_special
        else QuoteResearcher().research(total, history.read(), profile)
    )

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
    if run_mode == "schedule" and sent > 0:
        guard.mark_completed(sent)
    return 0 if sent > 0 else 2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=STORIES_PER_RUN)
    parser.add_argument("--day", default="automatico", choices=["automatico", "segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"])
    parser.add_argument("--run-mode", default="workflow_dispatch", choices=["schedule", "workflow_dispatch", "push"])
    parser.add_argument("--special", default="nenhum", choices=["nenhum", "poder_corrupcao"])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not 1 <= args.count <= 5:
        print("A quantidade deve estar entre 1 e 5.", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(run(args.count, args.day, args.run_mode, args.special))
