from PIL import Image

from src.editorial_calendar import get_profile
from src.models import VerifiedQuote, VisualAsset
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


def test_renderer_creates_editorial_story_with_image(tmp_path):
    background = tmp_path / "background.jpg"
    Image.new("RGB", (1400, 1800), (120, 80, 40)).save(background)
    quote = VerifiedQuote(
        quote_pt="Onde está o medo, ali também está a tarefa.",
        author="Autor Teste",
        source_title="Fonte",
        source_url="https://example.org",
        source_type="livro",
        source_excerpt="Trecho",
    )
    visual = VisualAsset(background, "https://commons.wikimedia.org", "Public domain")
    output = tmp_path / "editorial.png"

    StoryRenderer().render(quote, get_profile("quarta"), output, visual)

    with Image.open(output) as image:
        assert image.size == (1080, 1920)


def test_renderer_accepts_quote_without_author(tmp_path):
    quote = VerifiedQuote(
        quote_pt="A prudência escuta antes de responder.",
        author="",
        source_title="Fonte",
        source_url="https://example.org",
        source_type="coleção",
        source_excerpt="Trecho",
    )
    output = tmp_path / "anonymous.png"
    StoryRenderer().render(quote, get_profile("terca"), output)
    assert output.exists()
