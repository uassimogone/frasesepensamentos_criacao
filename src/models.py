from dataclasses import asdict, dataclass
import hashlib
import re
import unicodedata


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^a-zA-Z0-9 ]+", " ", value.lower())
    return re.sub(r"\s+", " ", value).strip()


@dataclass
class VerifiedQuote:
    quote_pt: str
    author: str
    source_title: str
    source_url: str
    source_type: str
    source_excerpt: str
    original_quote: str = ""
    original_language: str = ""
    translated: bool = False
    theme: str = ""
    verification_note: str = ""

    @property
    def content_id(self) -> str:
        basis = f"{normalize_text(self.author)}|{normalize_text(self.quote_pt)}"
        return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["content_id"] = self.content_id
        return payload

    @classmethod
    def from_dict(cls, payload: dict) -> "VerifiedQuote":
        allowed = cls.__dataclass_fields__.keys()
        return cls(**{key: payload.get(key) for key in allowed})
