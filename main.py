import argparse
import sys

from src.config import DAILY_RUN_STATE_PATH, HISTORY_PATH, OUTPUT_DIR, STORIES_PER_RUN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from src.daily_run import DailyRunGuard
from src.editorial_calendar import get_profile
from src.history_manager import HistoryManager
from src.image_researcher import ImageResearcher
from src.quote_researcher import QuoteResearcher
from src.story_renderer import StoryRenderer
from src.special_quotes import (\n    LUCIDEZ_REVISADA_PROFILE,\n    POWER_PROFILE,\n    power_and_corruption_quotes,\n    revised_lucidity_quotes,\n)
from src.telegram_bot import TelegramBot


def run(total: int, day_override: str, run_mode: str = "workflow_dispatch", special: str = "nenhum") -> int:
    guard = DailyRunGuard(DAILY_RUN_STATE_PATH)
    is_special = special in {"poder_corrupcao", "lucidez_revisada"}
    guarded_run = run_mode in {"schedule", "push"} and not is_special
    if guarded_run and guard.already_completed():
        print("⏭️ A entrega automática de hoje já foi concluída; esta janela redundante será ignorada.")
        return 0

    profile = (\n        POWER_PROFILE if special == "poder_corrupcao"\n        else LUCIDEZ_REVISADA_PROFILE if special == "lucidez_revisada"\n        else get_profile(day_override)\n    )
    print(f"▶️ {profile.label}: gerando {total} Stories com fontes públicas.")
    history = HistoryManager(HISTORY_PATH)
    renderer = StoryRenderer()
    image_researcher = ImageResearcher()
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
        visual = image_researcher.find_and_download(quote, profile, OUTPUT_DIR / "assets")
        renderer.render(quote, profile, output, visual)
        telegram.send_story(output, quote, sent + 1, total, visual)
        history.add(quote)
        sent += 1

    if sent < total:
        telegram.send_message(f"⚠️ {profile.label}: {sent}/{total} Stories enviados. Não havia outros conteúdos inéditos adequados.")
    print(f"🏁 {profile.label}: {sent} Story(s) enviado(s).")
    if guarded_run and sent > 0:
        guard.mark_completed(sent)
    return 0 if sent > 0 else 2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=STORIES_PER_RUN)
    parser.add_argument("--day", default="automatico", choices=["automatico", "segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"])
    parser.add_argument("--run-mode", default="workflow_dispatch", choices=["schedule", "workflow_dispatch", "push"])
    parser.add_argument("--special", default="nenhum", choices=["nenhum", "poder_corrupcao", "lucidez_revisada"])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not 1 <= args.count <= 5:
        print("A quantidade deve estar entre 1 e 5.", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(run(args.count, args.day, args.run_mode, args.special))
