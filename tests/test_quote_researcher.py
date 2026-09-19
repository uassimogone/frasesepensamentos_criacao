from bs4 import BeautifulSoup

from src.editorial_calendar import get_profile
from src.quote_researcher import QuoteResearcher


def test_accepts_portuguese_quote():
    text = "A liberdade é o direito de dizer às pessoas o que elas não querem ouvir."

    assert QuoteResearcher._is_usable_quote(text)


def test_rejects_english_quote():
    text = "The future belongs to those who believe in the beauty of their dreams."

    assert not QuoteResearcher._is_usable_quote(text)


def test_rejects_spanish_quote():
    text = "La vida es lo que pasa mientras estás ocupado haciendo otros planes."

    assert not QuoteResearcher._is_usable_quote(text)


def test_impactful_quote_scores_higher_than_generic_text():
    profile = get_profile("quarta")
    impactful = "Não é a força, mas a coragem diante do medo, que muda o destino de uma vida."
    generic = "Hoje é um dia comum e podemos fazer muitas coisas ao longo dele."

    assert QuoteResearcher._impact_score(impactful, profile) > QuoteResearcher._impact_score(generic, profile)


def test_extracts_quote_without_nested_source_metadata():
    html = """
    <li>
      Não basta existir; é preciso encontrar um propósito para a vida.
      <sup>[1]</sup>
      <ul><li>Fonte: Livro de exemplo, página 20.</li></ul>
    </li>
    """
    item = BeautifulSoup(html, "html.parser").select_one("li")

    assert QuoteResearcher._extract_quote_text(item) == (
        "Não basta existir; é preciso encontrar um propósito para a vida."
    )


def test_removes_repeated_wrapping_quotes():
    assert QuoteResearcher._clean_quote_text('““A vida é agora.””') == "A vida é agora."


def test_removes_wrapping_quotes_before_loose_period():
    assert QuoteResearcher._clean_quote_text('"Somos aquilo que escolhemos".') == "Somos aquilo que escolhemos"


def test_rejects_editorial_warning_about_altered_content():
    text = '"Se você sabe explicar, então compreendeu." (conteúdo adulterado, veja acima)'
    assert QuoteResearcher._has_attribution_warning(text)
    assert not QuoteResearcher._is_usable_quote(text)


def test_rejects_editorial_warning_about_missing_authorship():
    text = '"A vida não começa amanhã; ela acontece hoje." (em busca da autoria)'
    assert QuoteResearcher._has_attribution_warning(text)
    assert not QuoteResearcher._is_usable_quote(text)
