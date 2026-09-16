import random
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from src.editorial_calendar import DayProfile
from src.models import VerifiedQuote


class QuoteResearcher:
    """Coleta citações de páginas públicas gratuitas do Wikiquote em português."""

    API_URL = "https://pt.wikiquote.org/w/api.php"

    def research(
        self,
        desired: int,
        recent_items: list[dict],
        profile: DayProfile,
    ) -> list[VerifiedQuote]:
        used_ids = {item.get("content_id") for item in recent_items}
        sources = list(profile.sources)
        random.shuffle(sources)

        selected = []
        for author, page in sources:
            if len(selected) >= desired:
                break
            for quote_item in self._quotes_from_source(author, page, profile):
                if quote_item.content_id in used_ids:
                    continue
                if any(item.content_id == quote_item.content_id for item in selected):
                    continue
                selected.append(quote_item)
                break
        return selected

    def _quotes_from_source(
        self,
        author: str,
        page: str,
        profile: DayProfile,
    ) -> list[VerifiedQuote]:
        html = self._fetch_page(page)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        candidates = []
        for item in soup.select("li"):
            text = " ".join(item.get_text(" ", strip=True).split())
            if not self._is_usable_quote(text):
                continue

            candidates.append(
                VerifiedQuote(
                    quote_pt=self._strip_wrapping_quotes(text.strip(" -–—")),
                    author=author,
                    source_title=f"Wikiquote em português — {page}",
                    source_url=f"https://pt.wikiquote.org/wiki/{quote(page.replace(' ', '_'))}",
                    source_type="página pública de curadoria",
                    source_excerpt="Citação disponível na página pública de origem.",
                    original_language="português",
                    translated=False,
                    theme=", ".join(profile.themes),
                    verification_note=(
                        "Citação coletada de página pública de curadoria, sem marcação "
                        "de ausência de fonte. Confira o link antes da publicação definitiva."
                    ),
                )
            )
        return candidates

    def _fetch_page(self, page: str) -> str:
        try:
            response = requests.get(
                self.API_URL,
                params={"action": "parse", "page": page, "prop": "text", "format": "json", "redirects": "1"},
                headers={"User-Agent": "UassiStoriesBot/1.0 (content curation)"},
                timeout=20,
            )
            response.raise_for_status()
            return response.json().get("parse", {}).get("text", {}).get("*", "")
        except (requests.RequestException, ValueError):
            return ""

    @staticmethod
    def _strip_wrapping_quotes(text: str) -> str:
        """Remove pares de aspas externas; preserva aspas usadas dentro da frase."""
        opening = {'"', "“", "„", "‟", "«", "‹"}
        closing = {'"', "”", "“", "‟", "»", "›"}
        cleaned = text.strip()
        while len(cleaned) >= 2 and cleaned[0] in opening and cleaned[-1] in closing:
            cleaned = cleaned[1:-1].strip()
        return cleaned

    @staticmethod
    def _is_usable_quote(text: str) -> bool:
        normalized = text.lower()
        if not 25 <= len(text) <= 260 or text.endswith(":") or "http" in text:
            return False
        rejected = ("ver também", "ligações externas", "carece de fontes", "carece de fonte", "citação necessária")
        return not any(marker in normalized for marker in rejected)
