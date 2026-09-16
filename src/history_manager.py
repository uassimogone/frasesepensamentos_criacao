import json
from datetime import datetime, timezone
from pathlib import Path
from difflib import SequenceMatcher

from src.models import VerifiedQuote, normalize_text


class HistoryManager:
    def __init__(self, path: Path):
        self.path = path

    def read(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def is_duplicate(self, quote: VerifiedQuote, threshold: float = 0.80) -> bool:
        candidate = normalize_text(quote.quote_pt)
        for item in self.read():
            if item.get("content_id") == quote.content_id:
                return True
            previous = normalize_text(item.get("quote_pt", ""))
            same_author = normalize_text(item.get("author", "")) == normalize_text(quote.author)
            similarity = SequenceMatcher(None, candidate, previous).ratio() if previous else 0
            if similarity >= 0.95 or (same_author and similarity >= threshold):
                return True
        return False

    def add(self, quote: VerifiedQuote) -> None:
        records = self.read()
        if any(item.get("content_id") == quote.content_id for item in records):
            return
        payload = quote.to_dict()
        payload["published_to_telegram_at"] = datetime.now(timezone.utc).isoformat()
        records.append(payload)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(records, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
