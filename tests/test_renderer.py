from PIL import Image

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
    StoryRenderer().render(quote, output)

    with Image.open(output) as image:
        assert image.size == (1080, 1920)
        assert image.format == "PNG"
