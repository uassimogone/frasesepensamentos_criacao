import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


class DailyRunGuard:
    """Impede que as janelas redundantes publiquem mais de uma vez por dia."""

    TIMEZONE = ZoneInfo("America/Sao_Paulo")

    def __init__(self, path: Path):
        self.path = path

    def today(self) -> str:
        return datetime.now(self.TIMEZONE).date().isoformat()

    def already_completed(self) -> bool:
        if not self.path.exists():
            return False
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        return payload.get("last_successful_scheduled_date") == self.today()

    def mark_completed(self, sent: int) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "last_successful_scheduled_date": self.today(),
            "stories_sent": sent,
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
