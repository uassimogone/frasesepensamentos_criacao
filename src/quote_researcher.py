import json
import re
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

from src.config import BLOCKED_SOURCE_DOMAINS, TEXT_MODELS
from src.models import VerifiedQuote


class QuoteResearcher:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada.")
        self.client = genai.Client(api_key=api_key)

    def research(self, desired: int, recent_items: list[dict]) -> list[VerifiedQuote]:
        recent = [
            {"author": item.get("author"), "quote": item.get("quote_pt")}
            for item in recent_items[-80:]
        ]
        prompt = f"""
Pesquise citações autênticas para Stories em português.
Precisamos obter {max(desired * 4, 8)} candidatos para selecionar {desired}.

TEMAS: estoicismo, filosofia, ética, responsabilidade, disciplina, coragem,
tempo, família, propósito, liderança, liberdade e sociedade.
AUTORES: filósofos, escritores, cientistas, estadistas e personalidades
históricas ou atuais. Varie autores, épocas, gênero e áreas.

REGRAS ABSOLUTAS:
- Somente citações comprováveis.
- Priorize obra original, transcrição oficial, arquivo institucional,
  fundação, universidade, museu, Nobel, Project Gutenberg ou Wikisource.
- Não use Pinterest, Instagram, TikTok, sites de frases ou compilações sem referência.
- Não invente, complete, melhore ou parafraseie.
- Máximo de 260 caracteres na versão em português.
- Se traduzida, forneça também o trecho original.
- A URL deve apontar para a página que contém a evidência, não para busca.
- Informe um trecho da fonte que permita conferir a frase.
- Não repita estes conteúdos recentes: {json.dumps(recent, ensure_ascii=False)}

Retorne exclusivamente JSON:
[
  {{
    "quote_pt": "citação em português",
    "original_quote": "texto original ou vazio",
    "original_language": "idioma ou vazio",
    "translated": true,
    "author": "nome",
    "source_title": "obra, discurso ou entrevista",
    "source_url": "https://...",
    "source_type": "livro|discurso|entrevista|publicacao_oficial|arquivo_institucional",
    "source_excerpt": "trecho de comprovação",
    "theme": "tema"
  }}
]
"""
        raw = self._generate_with_search(prompt)
        candidates = self._parse_list(raw)
        verified = []
        for item in candidates:
            if len(verified) >= desired:
                break
            try:
                quote = VerifiedQuote.from_dict(item)
                if not self._basic_validation(quote):
                    continue
                page_text = self._fetch_source_text(quote.source_url)
                if not page_text:
                    continue
                decision = self._verify_against_source(quote, page_text)
                if not decision.get("verified", False):
                    continue
                quote.verification_note = decision.get("reason", "Confirmada na fonte.")
                verified.append(quote)
            except Exception as exc:
                print(f"⚠️ Candidato descartado: {exc}")
        return verified

    def _generate_with_search(self, prompt: str) -> str:
        last_error = None
        for model in TEXT_MODELS:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.2,
                    ),
                )
                return response.text or "[]"
            except Exception as exc:
                last_error = exc
                time.sleep(2)
        raise RuntimeError(f"Falha em todos os modelos de pesquisa: {last_error}")

    def _parse_list(self, raw: str) -> list[dict]:
        cleaned = re.sub(r"^\s*\x60\x60\x60(?:json)?|\x60\x60\x60\s*$", "", raw.strip(), flags=re.I)
        data = json.loads(cleaned)
        return data if isinstance(data, list) else []

    def _basic_validation(self, quote: VerifiedQuote) -> bool:
        required = [
            quote.quote_pt,
            quote.author,
            quote.source_title,
            quote.source_url,
            quote.source_excerpt,
        ]
        if not all(required) or len(quote.quote_pt) > 260:
            return False
        parsed = urlparse(quote.source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return False
        host = parsed.netloc.lower().removeprefix("www.")
        return not any(host == domain or host.endswith(f".{domain}") for domain in BLOCKED_SOURCE_DOMAINS)

    def _fetch_source_text(self, url: str) -> str:
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; QuoteVerifier/1.0)"},
                timeout=20,
            )
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "text/plain" not in content_type:
                return ""
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "form"]):
                tag.decompose()
            text = " ".join(soup.get_text(" ", strip=True).split())
            return text[:50000]
        except requests.RequestException:
            return ""

    def _verify_against_source(self, quote: VerifiedQuote, page_text: str) -> dict:
        prompt = f"""
Atue como verificador rigoroso de citações. Analise APENAS o conteúdo da fonte
recuperada abaixo. Não use memória externa.

AUTOR DECLARADO: {quote.author}
CITAÇÃO EM PORTUGUÊS: {quote.quote_pt}
TEXTO ORIGINAL DECLARADO: {quote.original_quote}
OBRA/FONTE: {quote.source_title}
TIPO: {quote.source_type}
TRADUZIDA: {quote.translated}

CONTEÚDO RECUPERADO DA FONTE:
{page_text}

Marque verified=true somente se o conteúdo recuperado sustentar simultaneamente:
1. a autoria;
2. a existência da frase ou de seu equivalente original;
3. a fidelidade substancial da tradução, quando houver;
4. a identificação da obra, entrevista, discurso ou publicação.

Na dúvida, retorne false. Responda exclusivamente:
{{"verified": true, "reason": "justificativa objetiva"}}
"""
        for model in TEXT_MODELS:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0,
                    ),
                )
                return json.loads(response.text)
            except Exception:
                continue
        return {"verified": False, "reason": "Falha na segunda verificação."}
