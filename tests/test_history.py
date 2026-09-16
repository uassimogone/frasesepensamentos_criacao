from pathlib import Path

from src.history_manager import HistoryManager
from src.models import VerifiedQuote


def make_quote(text="A vida é breve."):
    return VerifiedQuote(
        quote_pt=text,
        author="Autor Teste",
        source_title="Obra Teste",
        source_url="https://example.org/source",
        source_type="livro",
        source_excerpt="Trecho de teste",
    )


def test_history_detects_exact_and_similar_duplicates(tmp_path: Path):
    history = HistoryManager(tmp_path / "history.json")
    history.add(make_quote())
    assert history.is_duplicate(make_quote())
    assert history.is_duplicate(make_quote("A vida é muito breve."))


def test_history_keeps_new_quote(tmp_path: Path):
    history = HistoryManager(tmp_path / "history.json")
    history.add(make_quote())
    assert not history.is_duplicate(make_quote("A coragem exige prática diária."))
