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
        sources=(
            ("Sêneca", "Sêneca"),
            ("Epicteto", "Epicteto"),
            ("Marco Aurélio", "Marco Aurélio"),
            ("Viktor Frankl", "Viktor Frankl"),
            ("Friedrich Nietzsche", "Friedrich Nietzsche"),
            ("Ayrton Senna", "Ayrton Senna"),
            ("Muhammad Ali", "Muhammad Ali"),
            ("Bruce Lee", "Bruce Lee"),
            ("Abraham Lincoln", "Abraham Lincoln"),
            ("José Saramago", "José Saramago"),
        ),
        background=(16, 42, 67), ink=(250, 249, 246), accent=(229, 107, 63), quote_style="sans",
    ),
    "terca": DayProfile(
        slug="terca",
        label="LUCIDEZ",
        themes=("ética", "escolhas", "tempo", "lucidez"),
        sources=(
            ("Machado de Assis", "Machado de Assis"),
            ("Fernando Pessoa", "Fernando Pessoa"),
            ("José Saramago", "José Saramago"),
            ("Hannah Arendt", "Hannah Arendt"),
            ("Simone Weil", "Simone Weil"),
            ("Michel Foucault", "Michel Foucault"),
            ("Carl Jung", "Carl Gustav Jung"),
            ("Arthur Schopenhauer", "Arthur Schopenhauer"),
            ("Michel de Montaigne", "Michel de Montaigne"),
            ("Cícero", "Cícero"),
            ("Aristóteles", "Aristóteles"),
        ),
        background=(243, 239, 230), ink=(30, 77, 58), accent=(191, 138, 61), quote_style="serif",
    ),
    "quarta": DayProfile(
        slug="quarta",
        label="FORÇA",
        themes=("propósito", "existência", "superação", "resiliência"),
        sources=(
            ("Viktor Frankl", "Viktor Frankl"),
            ("Friedrich Nietzsche", "Friedrich Nietzsche"),
            ("Fiódor Dostoiévski", "Fiódor Dostoiévski"),
            ("Albert Camus", "Albert Camus"),
            ("Guimarães Rosa", "João Guimarães Rosa"),
            ("Clarice Lispector", "Clarice Lispector"),
            ("Frida Kahlo", "Frida Kahlo"),
            ("Martin Luther King Jr.", "Martin Luther King, Jr."),
            ("Malala Yousafzai", "Malala Yousafzai"),
            ("Maya Angelou", "Maya Angelou"),
        ),
        background=(32, 35, 58), ink=(248, 246, 241), accent=(183, 168, 212), quote_style="serif",
    ),
    "quinta": DayProfile(
        slug="quinta",
        label="ATITUDE",
        themes=("liderança", "atitude", "ousadia", "personalidade"),
        sources=(
            ("Ayrton Senna", "Ayrton Senna"),
            ("Bruce Lee", "Bruce Lee"),
            ("Steve Jobs", "Steve Jobs"),
            ("Muhammad Ali", "Muhammad Ali"),
            ("Michael Jordan", "Michael Jordan"),
            ("Kobe Bryant", "Kobe Bryant"),
            ("Frida Kahlo", "Frida Kahlo"),
            ("Malala Yousafzai", "Malala Yousafzai"),
            ("Martin Luther King Jr.", "Martin Luther King, Jr."),
            ("Oscar Wilde", "Oscar Wilde"),
        ),
        background=(25, 25, 25), ink=(244, 239, 235), accent=(158, 38, 57), quote_style="sans",
    ),
    "sexta": DayProfile(
        slug="sexta",
        label="CULTURA",
        themes=("cinema", "séries", "cultura pop", "humor inteligente"),
        sources=(
            ("Rocky", "Rocky"),
            ("Matrix", "Matrix"),
            ("Clube da Luta", "Clube da Luta"),
            ("Batman: O Cavaleiro das Trevas", "Batman: O Cavaleiro das Trevas"),
            ("Interestelar", "Interestelar"),
            ("O Poderoso Chefão", "O Poderoso Chefão"),
            ("Star Wars", "Star Wars"),
            ("O Senhor dos Anéis", "O Senhor dos Anéis"),
            ("The Office", "The Office"),
            ("Charles Chaplin", "Charles Chaplin"),
            ("Oscar Wilde", "Oscar Wilde"),
        ),
        background=(64, 50, 110), ink=(253, 247, 238), accent=(240, 107, 97), quote_style="sans",
    ),
    "sabado": DayProfile(
        slug="sabado",
        label="VIDA",
        themes=("amor", "relacionamentos", "afeto", "vida"),
        sources=(
            ("Clarice Lispector", "Clarice Lispector"),
            ("Machado de Assis", "Machado de Assis"),
            ("Fernando Pessoa", "Fernando Pessoa"),
            ("Carlos Drummond de Andrade", "Carlos Drummond de Andrade"),
            ("Vinicius de Moraes", "Vinicius de Moraes"),
            ("Mario Quintana", "Mario Quintana"),
            ("Khalil Gibran", "Khalil Gibran"),
            ("Pablo Neruda", "Pablo Neruda"),
            ("Oscar Wilde", "Oscar Wilde"),
            ("Virginia Woolf", "Virginia Woolf"),
            ("Simone de Beauvoir", "Simone de Beauvoir"),
        ),
        background=(232, 201, 193), ink=(89, 46, 51), accent=(168, 85, 61), quote_style="serif",
    ),
    "domingo": DayProfile(
        slug="domingo",
        label="GRATIDÃO",
        themes=("gratidão", "calma", "perspectiva", "mentalidade"),
        sources=(
            ("Rubem Alves", "Rubem Alves"),
            ("Dalai Lama", "Dalai Lama"),
            ("Thich Nhat Hanh", "Thich Nhat Hanh"),
            ("Khalil Gibran", "Khalil Gibran"),
            ("Rumi", "Rumi"),
            ("Mario Quintana", "Mario Quintana"),
            ("Guimarães Rosa", "João Guimarães Rosa"),
            ("Fernando Pessoa", "Fernando Pessoa"),
            ("Marco Aurélio", "Marco Aurélio"),
            ("Sêneca", "Sêneca"),
            ("Confúcio", "Confúcio"),
        ),
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
