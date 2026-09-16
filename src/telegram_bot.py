from html import escape
from pathlib import Path

import requests

from src.models import VerifiedQuote


class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        if not token or not chat_id:
            raise ValueError("Credenciais do bot de testes do Telegram não configuradas.")
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_story(self, image_path: Path, quote: VerifiedQuote, position: int, total: int):
        with image_path.open("rb") as image:
            response = requests.post(
                f"{self.base_url}/sendPhoto",
                data={"chat_id": self.chat_id},
                files={"photo": image},
                timeout=40,
            )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok"):
            raise RuntimeError(f"Telegram rejeitou a imagem: {payload}")

        translated = "Sim" if quote.translated else "Não"
        original = (
            f"\n<b>Texto original:</b> {escape(quote.original_quote)}"
            if quote.original_quote
            else ""
        )
        message = (
            f"<b>STORY DE TESTE {position}/{total}</b>\n\n"
            f"<b>Citação:</b> {escape(quote.quote_pt)}\n"
            f"<b>Autor:</b> {escape(quote.author)}\n"
            f"<b>Fonte:</b> {escape(quote.source_title)}\n"
            f"<b>Tipo:</b> {escape(quote.source_type)}\n"
            f"<b>Tradução:</b> {translated}{original}\n"
            f"<b>Verificação:</b> {escape(quote.verification_note)}\n"
            f"<b>ID:</b> <code>{quote.content_id}</code>\n\n"
            f'<a href="{escape(quote.source_url, quote=True)}">Abrir fonte de verificação</a>'
        )
        self.send_message(message)

    def send_message(self, text: str):
        response = requests.post(
            f"{self.base_url}/sendMessage",
            json={
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok"):
            raise RuntimeError(f"Telegram rejeitou a mensagem: {payload}")
