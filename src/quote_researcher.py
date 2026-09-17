import random
import re
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from src.editorial_calendar import DayProfile
from src.models import VerifiedQuote


class QuoteResearcher:
    """Coleta somente citações em português de páginas públicas gratuitas do Wikiquote."""

    API_URL = "https://pt.wikiquote.org/w/api.php"

    # Marcadores linguísticos: a citação precisa conter sinais suficientes de português
    # e não pode ter predominância de conectivos de outros idiomas.
    PORTUGUESE_MARKERS = {
        "a", "ao", "aos", "as", "às", "com", "como", "da", "das", "de", "do", "dos",
        "e", "é", "em", "ele", "ela", "eles", "elas", "entre", "essa", "esse", "esta",
        "este", "eu", "foi", "há", "mais", "mas", "não", "nos", "nós", "o", "os", "ou",
        "para", "pela", "pelo", "por", "porque", "que", "quem", "se", "sem", "ser",
        "seu", "sua", "são", "também", "tem", "têm", "todo", "toda", "um", "uma",
        "você", "vocês", "vida", "quando", "muito", "nunca", "sempre", "ainda",
        "aquilo", "aqueles", "aquelas", "durante", "então", "fazer", "pode", "poder",
        "quer", "querer", "deve", "devemos", "próprio", "única", "coisa", "acontece",
        "enquanto", "está", "estão", "outros", "outro", "medo", "liberdade",
    }
    PORTUGUESE_SIGNALS = {
        "não", "você", "vocês", "uma", "umas", "um", "uns", "mais", "para", "com",
        "pela", "pelo", "sua", "seu", "também", "muito", "nunca", "sempre", "ainda",
        "é", "são", "está", "estão", "há", "nós", "aos", "às", "porque", "quando",
        "fazer", "pode", "quer", "deve", "devemos", "próprio", "única", "acontece",
        "enquanto", "liberdade",
    }
    FOREIGN_MARKERS = {
        "the", "and", "of", "to", "in", "is", "that", "with", "for", "from", "are",
        "this", "you", "your", "not", "was", "will", "have", "be",
        "el", "los", "las", "una", "es", "del", "y", "pero", "cuando", "siempre",
        "le", "les", "des", "est", "et", "une", "dans", "pour", "avec",
        "il", "gli", "non", "che", "nel", "della",
    }

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
                        "Citação em português coletada de página pública de curadoria, sem marcação "
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

    @classmethod
    def _is_portuguese(cls, text: str) -> bool:
        words = re.findall(r"[a-záàâãéêíóôõúç]+", text.lower())
        if not words:
            return False

        portuguese_hits = sum(word in cls.PORTUGUESE_MARKERS for word in words)
        portuguese_signals = sum(word in cls.PORTUGUESE_SIGNALS for word in words)
        foreign_hits = sum(word in cls.FOREIGN_MARKERS for word in words)

        # Exige ao menos um marcador característico do português. Isso bloqueia
        # inclusive frases em espanhol que compartilham palavras como "vida" e "que".
        return portuguese_hits >= 2 and portuguese_signals >= 1 and foreign_hits <= portuguese_hits

    @classmethod
    def _is_usable_quote(cls, text: str) -> bool:
        normalized = text.lower()
        if not 25 <= len(text) <= 260 or text.endswith(":") or "http" in text:
            return False
        rejected = ("ver também", "ligações externas", "carece de fontes", "carece de fonte", "citação necessária")
        return cls._is_portuguese(text) and not any(marker in normalized for marker in rejected)
