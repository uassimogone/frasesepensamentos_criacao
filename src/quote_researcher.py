import random
import re
from datetime import date
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from src.config import WIKIQUOTE_AUTHORS
from src.models import VerifiedQuote


class QuoteResearcher:
    """Coleta citações de páginas públicas do Wikiquote em português.

    O Wikiquote é a fonte gratuita de curadoria e rastreabilidade. A automação
    descarta itens explicitamente marcados pela própria página como sem fonte.
    """

    API_URL = "https://pt.wikiquote.org/w/api.php"

    def research(self, desired: int, recent_items: list[dict]) -> list[VerifiedQuote]:
        used_ids = {item.get("content_id") for item in recent_items}
        authors = list(WIKIQUOTE_AUTHORS)
        random.Random(date.today().isoformat()).shuffle(authors)

        selected = []
        for author in authors:
            if len(selected) >= desired:
                break
            for quote_item in self._quotes_from_author(author):
                if quote_item.content_id in used_ids:
                    continue
                if any(item.content_id == quote_item.content_id for item in selected):
                    continue
                selected.append(quote_item)
                break  # diversidade: no máximo uma citação por autor a cada execução
        return selected

    def _quotes_from_author(self, author: str) -> list[VerifiedQuote]:
        html = self._fetch_page(author)
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
                    quote_pt=text.strip(" -–—"),
                    author=author,
                    source_title=f"Wikiquote em português — {author}",
                    source_url=f"https://pt.wikiquote.org/wiki/{quote(author.replace(' ', '_'))}",
                    source_type="página pública de curadoria",
                    source_excerpt="Citação disponível na página pública do autor.",
                    original_quote="",
                    original_language="português",
                    translated=False,
                    theme="pensamento",
                    verification_note=(
                        "Citação coletada de página pública de curadoria, sem marcação "
                        "de ausência de fonte. Confira o link antes da publicação definitiva."
                    ),
                )
            )
        return candidates

    def _fetch_page(self, author: str) -> str:
        try:
            response = requests.get(
                self.API_URL,
                params={
                    "action": "parse",
                    "page": author,
                    "prop": "text",
                    "format": "json",
                    "redirects": "1",
                },
                headers={"User-Agent": "UassiStoriesBot/1.0 (content curation)"},
                timeout=20,
            )
            response.raise_for_status()
            return response.json().get("parse", {}).get("text", {}).get("*", "")
        except (requests.RequestException, ValueError):
            return ""

    @staticmethod
    def _is_usable_quote(text: str) -> bool:
        normalized = text.lower()
        if not 25 <= len(text) <= 260:
            return False
        if text.endswith(":") or text.count("http") > 0:
            return False
        rejected = [
            "ver também",
            "ligações externas",
            "carece de fontes",
            "carece de fonte",
            "citação necessária",
        ]
        return not any(marker in normalized for marker in rejected)
