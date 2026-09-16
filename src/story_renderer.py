from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src.editorial_calendar import DayProfile
from src.models import VerifiedQuote


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

    def render(self, quote: VerifiedQuote, profile: DayProfile, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas = Image.new("RGB", (self.WIDTH, self.HEIGHT), profile.background)
        draw = ImageDraw.Draw(canvas)

        draw.rectangle((0, 0, 22, self.HEIGHT), fill=profile.accent)
        draw.line((self.SIDE_MARGIN, self.SAFE_TOP, self.WIDTH - self.SIDE_MARGIN, self.SAFE_TOP), fill=profile.accent, width=4)

        label_font = ImageFont.truetype(self.fonts["sans_bold"], 30)
        draw.text((self.SIDE_MARGIN, self.SAFE_TOP + 38), profile.label, font=label_font, fill=profile.accent)

        quote_font, lines = self._fit_quote(draw, f"“{quote.quote_pt}”", profile.quote_style)
        line_height = int(quote_font.size * 1.38)
        block_height = len(lines) * line_height
        top_limit = self.SAFE_TOP + 150
        bottom_limit = self.HEIGHT - self.SAFE_BOTTOM - 180
        y = top_limit + max(0, (bottom_limit - top_limit - block_height) // 2)

        for line in lines:
            width = draw.textlength(line, font=quote_font)
            draw.text(((self.WIDTH - width) / 2, y), line, font=quote_font, fill=profile.ink)
            y += line_height

        author_font = ImageFont.truetype(self.fonts["sans_bold"], 38)
        author = quote.author.upper()
        author_width = draw.textlength(author, font=author_font)
        author_y = min(y + 80, self.HEIGHT - self.SAFE_BOTTOM - 90)
        draw.text(((self.WIDTH - author_width) / 2, author_y), author, font=author_font, fill=profile.accent)

        handle_font = ImageFont.truetype(self.fonts["sans_regular"], 28)
        handle = "@uassimogone"
        handle_width = draw.textlength(handle, font=handle_font)
        draw.text(((self.WIDTH - handle_width) / 2, self.HEIGHT - self.SAFE_BOTTOM + 80), handle, font=handle_font, fill=profile.ink)

        canvas.save(output_path, "PNG", optimize=True)
        return output_path

    def _fit_quote(self, draw: ImageDraw.ImageDraw, text: str, style: str):
        max_width, max_height = self.WIDTH - (2 * self.SIDE_MARGIN), 870
        font_name = "serif_regular" if style == "serif" else "sans_regular"
        for size in range(72, 41, -2):
            font = ImageFont.truetype(self.fonts[font_name], size)
            lines = self._wrap_by_pixels(draw, text, font, max_width)
            if len(lines) * int(size * 1.38) <= max_height:
                return font, lines
        font = ImageFont.truetype(self.fonts[font_name], 40)
        return font, self._wrap_by_pixels(draw, text, font, max_width)

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
