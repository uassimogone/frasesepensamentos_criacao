from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

from src.editorial_calendar import DayProfile
from src.models import VerifiedQuote, VisualAsset


class StoryRenderer:
    WIDTH = 1080
    HEIGHT = 1920
    SAFE_TOP = 250
    SAFE_BOTTOM = 260
    SIDE_MARGIN = 105

    def __init__(self):
        self.fonts = {
            "sans_regular": self._find_font(["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]),
            "sans_bold": self._find_font(["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]),
            "serif_regular": self._find_font(["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"]),
            "serif_bold": self._find_font(["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf"]),
        }

    def _find_font(self, candidates: list[str]) -> str:
        for candidate in candidates:
            if Path(candidate).exists():
                return candidate
        raise FileNotFoundError("Nenhuma fonte compatível foi encontrada.")

    def render(
        self,
        quote: VerifiedQuote,
        profile: DayProfile,
        output_path: Path,
        visual: VisualAsset | None = None,
    ) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if visual:
            return self._render_editorial(quote, profile, output_path, visual)
        return self._render_minimal(quote, profile, output_path)

    def _render_minimal(self, quote: VerifiedQuote, profile: DayProfile, output_path: Path) -> Path:
        canvas = Image.new("RGB", (self.WIDTH, self.HEIGHT), profile.background)
        draw = ImageDraw.Draw(canvas)

        draw.rectangle((0, 0, 22, self.HEIGHT), fill=profile.accent)
        draw.line((self.SIDE_MARGIN, self.SAFE_TOP, self.WIDTH - self.SIDE_MARGIN, self.SAFE_TOP), fill=profile.accent, width=4)

        label_font = ImageFont.truetype(self.fonts["sans_bold"], 34)
        draw.text((self.SIDE_MARGIN, self.SAFE_TOP + 38), profile.label, font=label_font, fill=profile.accent)

        quote_text = self._strip_wrapping_quotes(quote.quote_pt)
        quote_font, lines = self._fit_quote(draw, f"“{quote_text}”", profile.quote_style)
        line_height = int(quote_font.size * 1.28)
        block_height = len(lines) * line_height
        top_limit = self.SAFE_TOP + 165
        bottom_limit = self.HEIGHT - self.SAFE_BOTTOM - 200
        y = top_limit + max(0, (bottom_limit - top_limit - block_height) // 2)

        # A citação é o elemento dominante: negrito, tamanho maior e leve contorno
        # para manter presença em qualquer cor de fundo.
        for line in lines:
            width = draw.textlength(line, font=quote_font)
            draw.text(
                ((self.WIDTH - width) / 2, y),
                line,
                font=quote_font,
                fill=profile.ink,
                stroke_width=1,
                stroke_fill=profile.ink,
            )
            y += line_height

        if quote.author:
            author_font = ImageFont.truetype(self.fonts["sans_bold"], 42)
            author = quote.author.upper()
            author_width = draw.textlength(author, font=author_font)
            author_y = min(y + 82, self.HEIGHT - self.SAFE_BOTTOM - 95)
            draw.text(((self.WIDTH - author_width) / 2, author_y), author, font=author_font, fill=profile.accent)

        handle_font = ImageFont.truetype(self.fonts["sans_regular"], 28)
        handle = "@uassimogone"
        handle_width = draw.textlength(handle, font=handle_font)
        draw.text(((self.WIDTH - handle_width) / 2, self.HEIGHT - self.SAFE_BOTTOM + 80), handle, font=handle_font, fill=profile.ink)

        canvas.save(output_path, "PNG", optimize=True)
        return output_path

    def _render_editorial(
        self,
        quote: VerifiedQuote,
        profile: DayProfile,
        output_path: Path,
        visual: VisualAsset,
    ) -> Path:
        with Image.open(visual.local_path) as source:
            canvas = ImageOps.fit(
                source.convert("RGB"),
                (self.WIDTH, self.HEIGHT),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.45),
            )
        canvas = ImageEnhance.Color(canvas).enhance(0.72)
        canvas = ImageEnhance.Contrast(canvas).enhance(1.12)
        canvas = Image.blend(canvas, Image.new("RGB", canvas.size, (20, 14, 9)), 0.30)
        canvas = self._apply_vignette(canvas)
        draw = ImageDraw.Draw(canvas)

        label_color = (214, 169, 88)
        label_font = ImageFont.truetype(self.fonts["sans_bold"], 30)
        draw.text((self.SIDE_MARGIN, self.SAFE_TOP), profile.label, font=label_font, fill=label_color)

        quote_text = self._strip_wrapping_quotes(quote.quote_pt)
        quote_font, lines = self._fit_editorial_quote(draw, f"“{quote_text}”")
        line_height = int(quote_font.size * 1.24)
        block_height = len(lines) * line_height
        top_limit = self.SAFE_TOP + 135
        bottom_limit = self.HEIGHT - self.SAFE_BOTTOM - (190 if quote.author else 100)
        y = top_limit + max(0, (bottom_limit - top_limit - block_height) // 2)

        for line in lines:
            width = draw.textlength(line, font=quote_font)
            draw.text(
                ((self.WIDTH - width) / 2, y),
                line,
                font=quote_font,
                fill=(250, 248, 242),
                stroke_width=5,
                stroke_fill=(12, 10, 8),
            )
            y += line_height

        if quote.author:
            author_font = ImageFont.truetype(self.fonts["serif_bold"], 39)
            author = f"— {quote.author} —"
            author_width = draw.textlength(author, font=author_font)
            author_y = min(y + 62, self.HEIGHT - self.SAFE_BOTTOM - 90)
            draw.text(
                ((self.WIDTH - author_width) / 2, author_y),
                author,
                font=author_font,
                fill=label_color,
                stroke_width=2,
                stroke_fill=(15, 11, 8),
            )

        handle_font = ImageFont.truetype(self.fonts["sans_regular"], 27)
        handle = "@uassimogone"
        handle_width = draw.textlength(handle, font=handle_font)
        draw.text(
            ((self.WIDTH - handle_width) / 2, self.HEIGHT - self.SAFE_BOTTOM + 84),
            handle,
            font=handle_font,
            fill=(238, 234, 225),
            stroke_width=2,
            stroke_fill=(10, 8, 7),
        )
        canvas.save(output_path, "PNG", optimize=True)
        return output_path

    def _fit_editorial_quote(self, draw: ImageDraw.ImageDraw, text: str):
        max_width, max_height = self.WIDTH - (2 * self.SIDE_MARGIN), 850
        for size in range(88, 49, -2):
            font = ImageFont.truetype(self.fonts["serif_bold"], size)
            lines = self._wrap_by_pixels(draw, text, font, max_width)
            if len(lines) * int(size * 1.24) <= max_height:
                return font, lines
        font = ImageFont.truetype(self.fonts["serif_bold"], 48)
        return font, self._wrap_by_pixels(draw, text, font, max_width)

    @staticmethod
    def _apply_vignette(canvas: Image.Image) -> Image.Image:
        mask = Image.new("L", canvas.size, 0)
        pixels = mask.load()
        width, height = canvas.size
        for y in range(height):
            vertical = abs((y / (height - 1)) - 0.5) * 2
            for x in range(width):
                horizontal = abs((x / (width - 1)) - 0.5) * 2
                edge = max(horizontal ** 2, vertical ** 2)
                pixels[x, y] = int(min(150, 150 * edge))
        shade = Image.new("RGB", canvas.size, (0, 0, 0))
        return Image.composite(shade, canvas, mask)

    def _fit_quote(self, draw: ImageDraw.ImageDraw, text: str, style: str):
        max_width, max_height = self.WIDTH - (2 * self.SIDE_MARGIN), 850
        font_name = "serif_bold" if style == "serif" else "sans_bold"
        for size in range(92, 51, -2):
            font = ImageFont.truetype(self.fonts[font_name], size)
            lines = self._wrap_by_pixels(draw, text, font, max_width)
            if len(lines) * int(size * 1.28) <= max_height:
                return font, lines
        font = ImageFont.truetype(self.fonts[font_name], 50)
        return font, self._wrap_by_pixels(draw, text, font, max_width)

    @staticmethod
    def _strip_wrapping_quotes(text: str) -> str:
        """Garante que a arte receba o texto sem aspas externas duplicadas."""
        opening = {'"', "“", "„", "‟", "«", "‹"}
        closing = {'"', "”", "“", "‟", "»", "›"}
        cleaned = text.strip()
        while len(cleaned) >= 2 and cleaned[0] in opening and cleaned[-1] in closing:
            cleaned = cleaned[1:-1].strip()
        return cleaned

    @staticmethod
    def _wrap_by_pixels(draw, text, font, max_width):
        words, lines, current = text.split(), [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if not current or draw.textlength(candidate, font=font) <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines
