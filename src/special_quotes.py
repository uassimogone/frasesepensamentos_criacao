from src.editorial_calendar import DayProfile
from src.models import VerifiedQuote


POWER_PROFILE = DayProfile(
    slug="poder",
    label="PODER",
    themes=("poder", "corrupção", "limites", "justiça"),
    sources=(),
    background=(20, 21, 24),
    ink=(247, 243, 235),
    accent=(180, 42, 48),
    quote_style="serif",
)


def power_and_corruption_quotes() -> list[VerifiedQuote]:
    return [
        VerifiedQuote(
            quote_pt="O poder tende a corromper, e o poder absoluto corrompe absolutamente.",
            author="Lord Acton",
            source_title="Carta a Mandell Creighton, 5 de abril de 1887",
            source_url="https://en.wikisource.org/wiki/Letter_to_Bishop_Mandell_Creighton,_April_5,_1887",
            source_type="correspondência histórica",
            source_excerpt="Power tends to corrupt, and absolute power corrupts absolutely.",
            original_quote="Power tends to corrupt, and absolute power corrupts absolutely.",
            original_language="inglês",
            translated=True,
            theme="poder e corrupção",
            verification_note="Tradução direta do trecho da carta de Lord Acton a Mandell Creighton.",
        ),
        VerifiedQuote(
            quote_pt="Todo homem que tem poder é levado a abusar dele; vai até encontrar limites.",
            author="Montesquieu",
            source_title="Do Espírito das Leis, Livro XI, capítulo IV",
            source_url="https://www.gutenberg.org/files/27573/27573-h/27573-h.htm",
            source_type="obra em domínio público",
            source_excerpt="C’est une expérience éternelle, que tout homme qui a du pouvoir est porté à en abuser.",
            original_quote="Tout homme qui a du pouvoir est porté à en abuser; il va jusqu’à ce qu’il trouve des limites.",
            original_language="francês",
            translated=True,
            theme="abuso de poder e limites institucionais",
            verification_note="Tradução do Livro XI, capítulo IV, de Do Espírito das Leis.",
        ),
        VerifiedQuote(
            quote_pt=(
                "De tanto ver triunfar as nulidades, de tanto ver prosperar a desonra, "
                "de tanto ver crescer a injustiça, de tanto ver agigantarem-se os poderes "
                "nas mãos dos maus, o homem chega a desanimar da virtude, a rir-se da honra, "
                "a ter vergonha de ser honesto."
            ),
            author="Rui Barbosa",
            source_title="Oração aos Moços",
            source_url="https://www2.senado.leg.br/bdsf/handle/id/573952",
            source_type="obra histórica em acervo público",
            source_excerpt="Trecho de Oração aos Moços, discurso aos formandos da Faculdade de Direito de São Paulo.",
            original_language="português",
            translated=False,
            theme="desonra, injustiça e abuso de poder",
            verification_note="Trecho atribuído à obra Oração aos Moços, de Rui Barbosa, em acervo do Senado Federal.",
        ),
    ]
