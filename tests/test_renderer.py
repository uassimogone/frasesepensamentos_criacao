from PIL import Image

from src.editorial_calendar import get_profile
from src.models import VerifiedQuote
from src.story_renderer import StoryRenderer


def test_renderer_creates_instagram_story(tmp_path):
    quote = VerifiedQuote(
        quote_pt="Não controlamos os acontecimentos, mas podemos escolher nossa resposta.",
        author="Autor Teste",
        source_title="Fonte Teste",
        source_url="https://example.org",
        source_type="livro",
        source_excerpt="Trecho",
    )
    output = tmp_path / "story.png"
    StoryRenderer().render(quote, get_profile("quarta"), output)

    with Image.open(output) as image:
        assert image.size == (1080, 1920)
        assert image.format == "PNG"

def test_renderer_removes_only_wrapping_quotes():
    renderer = StoryRenderer()

    assert renderer._strip_wrapping_quotes('““A vida é agora.””') == "A vida é agora."
    assert renderer._strip_wrapping_quotes('Ela disse “sim” com firmeza.') == 'Ela disse “sim” com firmeza.'
