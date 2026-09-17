from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DayProfile:
    slug: str
    label: str
    themes: tuple[str, ...]
    sources: tuple[tuple[str, str], ...]
    background: tuple[int, int, int]
    ink: tuple[int, int, int]
    accent: tuple[int, int, int]
    quote_style: str  # serif ou sans


PROFILES = {
    "segunda": DayProfile(
        slug="segunda",
        label="COMEÇANDO",
        themes=("disciplina", "trabalho", "coragem", "ação"),
        sources=(("Sêneca", "Sêneca"), ("Epicteto", "Epicteto"), ("Marco Aurélio", "Marco Aurélio"), ("Nelson Mandela", "Nelson Mandela"), ("Winston Churchill", "Winston Churchill")),
        background=(16, 42, 67), ink=(250, 249, 246), accent=(229, 107, 63), quote_style="sans",
    ),
    "terca": DayProfile(
        slug="terca",
        label="LUCIDEZ",
        themes=("ética", "escolhas", "tempo", "lucidez"),
        sources=(("Aristóteles", "Aristóteles"), ("Cícero", "Cícero"), ("Confúcio", "Confúcio"), ("Michel de Montaigne", "Michel de Montaigne"), ("Hannah Arendt", "Hannah Arendt")),
        background=(243, 239, 230), ink=(30, 77, 58), accent=(191, 138, 61), quote_style="serif",
    ),
    "quarta": DayProfile(
        slug="quarta",
        label="FORÇA",
        themes=("propósito", "existência", "profundidade", "pensamento"),
        sources=(("Friedrich Nietzsche", "Friedrich Nietzsche"), ("Hannah Arendt", "Hannah Arendt"), ("Simone de Beauvoir", "Simone de Beauvoir"), ("Virginia Woolf", "Virginia Woolf"), ("Anaïs Nin", "Anaïs Nin")),
        background=(32, 35, 58), ink=(248, 246, 241), accent=(183, 168, 212), quote_style="serif",
    ),
    "quinta": DayProfile(
        slug="quinta",
        label="ATITUDE",
        themes=("liderança", "atitude", "impacto", "personalidade"),
        sources=(("Eleanor Roosevelt", "Eleanor Roosevelt"), ("Maya Angelou", "Maya Angelou"), ("Nelson Mandela", "Nelson Mandela"), ("Winston Churchill", "Winston Churchill"), ("Albert Einstein", "Albert Einstein")),
        background=(25, 25, 25), ink=(244, 239, 235), accent=(158, 38, 57), quote_style="sans",
    ),
    "sexta": DayProfile(
        slug="sexta",
        label="CULTURA",
        themes=("filmes", "séries", "cultura pop", "humor inteligente"),
        sources=(("Charles Chaplin", "Charles Chaplin"), ("O Poderoso Chefão", "O Poderoso Chefão"), ("Star Wars", "Star Wars"), ("O Senhor dos Anéis", "O Senhor dos Anéis"), ("The Office", "The Office")),
        background=(64, 50, 110), ink=(253, 247, 238), accent=(240, 107, 97), quote_style="sans",
    ),
    "sabado": DayProfile(
        slug="sabado",
        label="VIDA",
        themes=("amor", "relacionamentos", "afeto", "lifestyle"),
        sources=(("Anaïs Nin", "Anaïs Nin"), ("Simone de Beauvoir", "Simone de Beauvoir"), ("Virginia Woolf", "Virginia Woolf"), ("Maya Angelou", "Maya Angelou"), ("Clarice Lispector", "Clarice Lispector")),
        background=(232, 201, 193), ink=(89, 46, 51), accent=(168, 85, 61), quote_style="serif",
    ),
    "domingo": DayProfile(
        slug="domingo",
        label="GRATIDÃO",
        themes=("gratidão", "calma", "perspectiva", "mentalidade"),
        sources=(("Marco Aurélio", "Marco Aurélio"), ("Confúcio", "Confúcio"), ("Nelson Mandela", "Nelson Mandela"), ("Maya Angelou", "Maya Angelou"), ("Khalil Gibran", "Khalil Gibran")),
        background=(248, 246, 239), ink=(52, 81, 64), accent=(215, 183, 122), quote_style="serif",
    ),
}

WEEKDAY_TO_SLUG = ("segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo")


def get_profile(day_override: str = "automatico") -> DayProfile:
    normalized = (day_override or "automatico").strip().lower()
    if normalized != "automatico":
        if normalized not in PROFILES:
            raise ValueError(f"Dia inválido: {day_override}")
        return PROFILES[normalized]
    return PROFILES[WEEKDAY_TO_SLUG[date.today().weekday()]]
