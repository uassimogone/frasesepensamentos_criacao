from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src.models import VerifiedQuote


class StoryRenderer:
    WIDTH = 1080
    HEIGHT = 1920
    SAFE_TOP = 250
    SAFE_BOTTOM = 260
    SIDE_MARGIN = 105

    def __init__(self):
        self.font_regular = self._find_font(
            [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
            ]
        )
        self.font_bold = self._find_font(
            [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            ]
        )

    def _find_font(self, candidates: list[str]) -> str:
        for candidate in candidates:
            if Path(candidate).exists():
                return candidate
        raise FileNotFoundError("Nenhuma fonte compatível foi encontrada.")

    def render(self, quote: VerifiedQuote, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas = Image.new("RGB", (self.WIDTH, self.HEIGHT), (245, 242, 235))
        draw = ImageDraw.Draw(canvas)

        ink = (27, 27, 27)
        muted = (104, 100, 92)
        accent = (132, 36, 45)

        draw.rectangle((0, 0, 22, self.HEIGHT), fill=accent)
        draw.line(
            (self.SIDE_MARGIN, self.SAFE_TOP, self.WIDTH - self.SIDE_MARGIN, self.SAFE_TOP),
            fill=accent,
            width=4,
        )

        label_font = ImageFont.truetype(self.font_bold, 30)
        draw.text(
            (self.SIDE_MARGIN, self.SAFE_TOP + 38),
            "PARA PENSAR",
            font=label_font,
            fill=accent,
        )

        quote_font, lines = self._fit_quote(draw, f"“{quote.quote_pt}”")
        line_height = int(quote_font.size * 1.38)
        block_height = len(lines) * line_height
        top_limit = self.SAFE_TOP + 150
        bottom_limit = self.HEIGHT - self.SAFE_BOTTOM - 180
        y = top_limit + max(0, (bottom_limit - top_limit - block_height) // 2)

        for line in lines:
            width = draw.textlength(line, font=quote_font)
            x = (self.WIDTH - width) / 2
            draw.text((x, y), line, font=quote_font, fill=ink)
            y += line_height

        author_font = ImageFont.truetype(self.font_bold, 38)
        author = quote.author.upper()
        author_width = draw.textlength(author, font=author_font)
        author_y = min(y + 80, self.HEIGHT - self.SAFE_BOTTOM - 90)
        draw.text(((self.WIDTH - author_width) / 2, author_y), author, font=author_font, fill=accent)

        handle_font = ImageFont.truetype(self.font_regular, 28)
        handle = "@uassimogone"
        handle_width = draw.textlength(handle, font=handle_font)
        draw.text(
            ((self.WIDTH - handle_width) / 2, self.HEIGHT - self.SAFE_BOTTOM + 80),
            handle,
            font=handle_font,
            fill=muted,
        )

        canvas.save(output_path, "PNG", optimize=True)
        return output_path

    def _fit_quote(self, draw: ImageDraw.ImageDraw, text: str):
        max_width = self.WIDTH - (2 * self.SIDE_MARGIN)
        max_height = 870
        for size in range(72, 41, -2):
            font = ImageFont.truetype(self.font_regular, size)
            lines = self._wrap_by_pixels(draw, text, font, max_width)
            if len(lines) * int(size * 1.38) <= max_height:
                return font, lines
        font = ImageFont.truetype(self.font_regular, 40)
        return font, self._wrap_by_pixels(draw, text, font, max_width)

    def _wrap_by_pixels(self, draw, text, font, max_width):
        words = text.split()
        lines, current = [], ""
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
