import hashlib
import re
from pathlib import Path

import requests
from PIL import Image, UnidentifiedImageError

from src.editorial_calendar import DayProfile
from src.models import VerifiedQuote, VisualAsset


class ImageResearcher:
    """Busca imagens abertas no Wikimedia Commons e falha para o minimalista."""

    API_URL = "https://commons.wikimedia.org/w/api.php"
    USER_AGENT = "UassiStoriesBot/2.0 (editorial image research)"
    MIN_WIDTH = 1200
    MIN_HEIGHT = 900
    MAX_BYTES = 12 * 1024 * 1024
    ALLOWED_LICENSE_MARKERS = ("public domain", "cc0", "cc by", "cc-by")
    REJECTED_TITLE_MARKERS = (
        "logo", "signature", "autograph", "coat of arms", "flag", "map", "diagram",
        "icon", "stamp", "coin", "banknote", "poster", "book cover", "svg",
    )

    def find_and_download(
        self,
        quote: VerifiedQuote,
        profile: DayProfile,
        target_dir: Path,
    ) -> VisualAsset | None:
        for query in self._queries(quote, profile):
            for candidate in self._search(query):
                if not self._is_acceptable(candidate):
                    continue
                asset = self._download(candidate, quote.content_id, target_dir)
                if asset:
                    return asset
        return None

    @staticmethod
    def _queries(quote: VerifiedQuote, profile: DayProfile) -> list[str]:
        if quote.author:
            return [
                f'"{quote.author}" portrait painting',
                f'"{quote.author}" portrait',
                f'{profile.themes[0]} allegory painting',
            ]
        return [
            f'{profile.themes[0]} allegory painting',
            f'{profile.themes[-1]} classical painting',
        ]

    def _search(self, query: str) -> list[dict]:
        try:
            response = requests.get(
                self.API_URL,
                params={
                    "action": "query",
                    "format": "json",
                    "generator": "search",
                    "gsrsearch": query,
                    "gsrnamespace": "6",
                    "gsrlimit": "12",
                    "prop": "imageinfo",
                    "iiprop": "url|size|mime|extmetadata",
                    "iiurlwidth": "1600",
                },
                headers={"User-Agent": self.USER_AGENT},
                timeout=20,
            )
            response.raise_for_status()
            pages = response.json().get("query", {}).get("pages", {})
        except (requests.RequestException, ValueError):
            return []

        candidates = []
        for page in pages.values():
            info = (page.get("imageinfo") or [{}])[0]
            metadata = info.get("extmetadata") or {}
            candidates.append(
                {
                    "title": page.get("title", ""),
                    "width": info.get("width", 0),
                    "height": info.get("height", 0),
                    "mime": info.get("mime", ""),
                    "download_url": info.get("thumburl") or info.get("url", ""),
                    "source_url": info.get("descriptionurl", ""),
                    "license": self._metadata_value(metadata, "LicenseShortName"),
                    "creator": self._strip_html(self._metadata_value(metadata, "Artist")),
                }
            )
        return sorted(candidates, key=self._candidate_score, reverse=True)

    @staticmethod
    def _metadata_value(metadata: dict, key: str) -> str:
        value = metadata.get(key, "")
        return value.get("value", "") if isinstance(value, dict) else str(value or "")

    @staticmethod
    def _strip_html(value: str) -> str:
        return re.sub(r"<[^>]+>", "", value or "").strip()

    @classmethod
    def _is_acceptable(cls, item: dict) -> bool:
        title = item.get("title", "").casefold()
        license_name = item.get("license", "").casefold()
        return (
            item.get("width", 0) >= cls.MIN_WIDTH
            and item.get("height", 0) >= cls.MIN_HEIGHT
            and item.get("width", 0) * item.get("height", 0) <= 60_000_000
            and item.get("mime") in {"image/jpeg", "image/png", "image/webp"}
            and bool(item.get("download_url"))
            and bool(item.get("source_url"))
            and any(marker in license_name for marker in cls.ALLOWED_LICENSE_MARKERS)
            and not any(marker in title for marker in cls.REJECTED_TITLE_MARKERS)
        )

    @staticmethod
    def _candidate_score(item: dict) -> float:
        width, height = item.get("width", 0), item.get("height", 0)
        if not width or not height:
            return 0
        ratio = width / height
        vertical_bonus = 4 - min(4, abs(ratio - (9 / 16)) * 4)
        resolution_bonus = min(4, (width * height) / 4_000_000)
        return vertical_bonus + resolution_bonus

    def _download(self, item: dict, content_id: str, target_dir: Path) -> VisualAsset | None:
        target_dir.mkdir(parents=True, exist_ok=True)
        suffix = ".png" if item.get("mime") == "image/png" else ".jpg"
        fingerprint = hashlib.sha256(item["download_url"].encode("utf-8")).hexdigest()[:8]
        target = target_dir / f"{content_id}_{fingerprint}{suffix}"
        try:
            response = requests.get(
                item["download_url"],
                headers={"User-Agent": self.USER_AGENT},
                timeout=30,
            )
            response.raise_for_status()
            if len(response.content) > self.MAX_BYTES:
                return None
            target.write_bytes(response.content)
            with Image.open(target) as image:
                image.verify()
        except (requests.RequestException, OSError, UnidentifiedImageError):
            target.unlink(missing_ok=True)
            return None
        return VisualAsset(
            local_path=target,
            source_url=item["source_url"],
            license_name=item["license"],
            creator=item.get("creator", ""),
            title=item.get("title", ""),
        )
