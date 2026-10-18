from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PORTS = {"en": 7770, "am": 7771, "bn": 7772, "hi": 7773, "ur": 7774}
DB_FILES = {"en": "selam_en.db", "am": "selam_am.db", "bn": "selam_bn.db",
            "hi": "selam_hi.db", "ur": "selam_ur.db"}


@dataclass(frozen=True)
class Config:
    language: str
    port: int
    db_path: Path
    generated_dir: Path
    secret_key: str
    session_cookie: str
    seed_db: Path = ROOT / "data" / "seed.db"
    wtf_csrf_enabled: bool = False

    @classmethod
    def for_language(cls, language: str) -> "Config":
        if language not in PORTS:
            raise ValueError(f"unknown language {language!r}")
        return cls(
            language=language,
            port=PORTS[language],
            db_path=ROOT / "data" / DB_FILES[language],
            generated_dir=ROOT / "app" / "static" / "generated" / language,
            secret_key=f"selam-benchmark-fixed-key-{language}",
            session_cookie=f"selam_session_{language}",
        )
