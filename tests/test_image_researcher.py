from src.editorial_calendar import get_profile
from src.image_researcher import ImageResearcher
from src.models import VerifiedQuote


def test_accepts_large_openly_licensed_image():
    item = {
        "title": "File:Classical portrait.jpg",
        "width": 2400,
        "height": 3000,
        "mime": "image/jpeg",
        "download_url": "https://example.org/image.jpg",
        "source_url": "https://commons.wikimedia.org/wiki/File:Classical_portrait.jpg",
        "license": "Public domain",
    }
    assert ImageResearcher._is_acceptable(item)


def test_rejects_low_resolution_or_unknown_license():
    base = {
        "title": "File:Portrait.jpg",
        "width": 2400,
        "height": 3000,
        "mime": "image/jpeg",
        "download_url": "https://example.org/image.jpg",
        "source_url": "https://commons.wikimedia.org/wiki/File:Portrait.jpg",
        "license": "All rights reserved",
    }
    assert not ImageResearcher._is_acceptable(base)
    assert not ImageResearcher._is_acceptable({**base, "license": "CC BY 4.0", "width": 700})


def test_anonymous_quote_uses_theme_instead_of_author():
    quote = VerifiedQuote(
        quote_pt="Uma frase sem autoria comprovada.",
        author="",
        source_title="Fonte",
        source_url="https://example.org",
        source_type="coleção",
        source_excerpt="Trecho",
    )
    queries = ImageResearcher._queries(quote, get_profile("domingo"))
    assert queries
    assert all('""' not in query for query in queries)
