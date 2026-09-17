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
