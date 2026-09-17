import random
import re
from collections import Counter
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from src.editorial_calendar import DayProfile
from src.models import VerifiedQuote


class QuoteResearcher:
    """Pesquisa, filtra e ranqueia citações em português por força editorial."""

    API_URL = "https://pt.wikiquote.org/w/api.php"
    MIN_IMPACT_SCORE = 7
    AUTHOR_LOOKBACK = 28

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
        "tu", "tua", "te", "ti", "és",
    }
    PORTUGUESE_SIGNALS = {
        "não", "você", "vocês", "uma", "umas", "um", "uns", "mais", "para", "com",
        "pela", "pelo", "sua", "seu", "também", "muito", "nunca", "sempre", "ainda",
        "é", "és", "são", "está", "estão", "há", "nós", "aos", "às", "porque", "quando",
        "fazer", "pode", "quer", "deve", "devemos", "próprio", "única", "acontece",
        "enquanto", "liberdade", "tua",
    }
    FOREIGN_MARKERS = {
        "the", "and", "of", "to", "in", "is", "that", "with", "for", "from", "are",
        "this", "you", "your", "not", "was", "will", "have", "be",
        "el", "los", "las", "una", "es", "del", "y", "pero", "cuando", "siempre",
        "le", "les", "des", "est", "et", "une", "dans", "pour", "avec",
        "il", "gli", "non", "che", "nel", "della",
    }

    IMPACT_PATTERNS = (
        "não é", "não basta", "não há", "mas ", "quem ", "quando ", "enquanto ",
        "é preciso", "é melhor", "a vida", "o medo", "a coragem", "a liberdade",
        "a verdade", "o tempo", "o amor", "o mundo", "só ", "nunca ", "sempre ",
        "se você", "se quer", "torna-te", "somos ", "escolher", "mudar",
    )
    IMPACT_TERMS = {
        "coragem", "medo", "liberdade", "verdade", "tempo", "vida", "amor",
        "destino", "escolha", "escolhas", "caráter", "consciência", "silêncio",
        "dor", "força", "mudança", "propósito", "fracasso", "vitória", "sonho",
        "sonhos", "justiça", "dignidade", "esperança", "responsabilidade",
        "disciplina", "ação", "ousadia", "resiliência", "essencial",
    }
    THEME_TERMS = {
        "segunda": {"disciplina", "trabalho", "coragem", "ação", "começar", "começo", "esforço", "persistência"},
        "terca": {"ética", "escolha", "tempo", "verdade", "consciência", "pensamento", "sabedoria", "dúvida"},
        "quarta": {"propósito", "existência", "superação", "resiliência", "dor", "força", "sentido", "adversidade"},
        "quinta": {"liderança", "atitude", "ousadia", "decisão", "coragem", "ação", "risco", "personalidade"},
        "sexta": {"cinema", "história", "humor", "mundo", "sonho", "medo", "poder", "escolha"},
        "sabado": {"amor", "afeto", "vida", "relacionamento", "coração", "felicidade", "saudade", "encontro"},
        "domingo": {"gratidão", "calma", "perspectiva", "paz", "presente", "silêncio", "esperança", "tempo"},
    }

    def research(
        self,
        desired: int,
        recent_items: list[dict],
        profile: DayProfile,
    ) -> list[VerifiedQuote]:
        used_ids = {item.get("content_id") for item in recent_items}
        recent_authors = Counter(
            str(item.get("author", "")).strip().casefold()
            for item in recent_items[-self.AUTHOR_LOOKBACK:]
            if item.get("author")
        )

        # O embaralhamento resolve empates; a ordenação prioriza autores menos usados.
        sources = list(profile.sources)
        random.shuffle(sources)
        sources.sort(key=lambda source: recent_authors[source[0].casefold()])

        selected = []
        for author, page in sources:
            if len(selected) >= desired:
                break

            candidates = self._quotes_from_source(author, page, profile)
            random.shuffle(candidates)
            candidates.sort(
                key=lambda item: self._impact_score(item.quote_pt, profile),
                reverse=True,
            )

            for quote_item in candidates:
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
            text = self._extract_quote_text(item)
            if not self._is_usable_quote(text):
                continue
            if self._impact_score(text, profile) < self.MIN_IMPACT_SCORE:
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
                        "Citação em português, selecionada por relevância e impacto editorial, "
                        "sem marcação de ausência de fonte. Confira o link antes da publicação."
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
    def _extract_quote_text(item) -> str:
        """Extrai a frase principal e ignora listas internas de fonte/referência."""
        parts = []
        for child in item.contents:
            name = getattr(child, "name", None)
            if name in {"ul", "ol", "sup"}:
                continue
            if hasattr(child, "get_text"):
                value = child.get_text(" ", strip=True)
            else:
                value = str(child).strip()
            if value:
                parts.append(value)

        text = " ".join(parts)
        text = re.sub(r"\[\s*\d+\s*\]", "", text)
        return " ".join(text.split())

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
    def _impact_score(cls, text: str, profile: DayProfile) -> int:
        normalized = text.casefold()
        words = re.findall(r"[a-záàâãéêíóôõúç]+", normalized)
        score = 0

        if 55 <= len(text) <= 180:
            score += 5
        elif 35 <= len(text) <= 220:
            score += 3
        else:
            score += 1

        if 8 <= len(words) <= 26:
            score += 4
        elif 5 <= len(words) <= 34:
            score += 2

        score += min(6, 2 * sum(pattern in normalized for pattern in cls.IMPACT_PATTERNS))
        score += min(4, sum(word in cls.IMPACT_TERMS for word in words))
        score += min(6, 2 * sum(word in cls.THEME_TERMS.get(profile.slug, set()) for word in words))

        if "?" in text:
            score += 2
        if ";" in text or "—" in text:
            score += 1
        if re.search(r"\d", text):
            score -= 3
        if any(marker in normalized for marker in ("isbn", "página ", "editora ", "discurso em ", "entrevista a ")):
            score -= 6
        return score

    @classmethod
    def _is_portuguese(cls, text: str) -> bool:
        words = re.findall(r"[a-záàâãéêíóôõúç]+", text.lower())
        if not words:
            return False

        portuguese_hits = sum(word in cls.PORTUGUESE_MARKERS for word in words)
        portuguese_signals = sum(word in cls.PORTUGUESE_SIGNALS for word in words)
        foreign_hits = sum(word in cls.FOREIGN_MARKERS for word in words)
        return portuguese_hits >= 2 and portuguese_signals >= 1 and foreign_hits <= portuguese_hits

    @classmethod
    def _is_usable_quote(cls, text: str) -> bool:
        normalized = text.lower()
        if not 20 <= len(text) <= 240 or text.endswith(":") or "http" in text:
            return False
        rejected = (
            "ver também", "ligações externas", "carece de fontes", "carece de fonte",
            "citação necessária", "sem fontes", "frases atribuídas", "atribuída a",
        )
        return cls._is_portuguese(text) and not any(marker in normalized for marker in rejected)
