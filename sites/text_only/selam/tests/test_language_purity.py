import html as html_module
import re

import pytest

from app import create_app

GEEZ = re.compile(r"[ሀ-፿]")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")

from app.i18n import latin_tokens

WHITELIST = latin_tokens.ALLOWED

IDENTIFIER = re.compile(latin_tokens.IDENTIFIER_PATTERN)

def _letter_codes() -> set[str]:
    import sqlite3

    from conftest import ROOT

    codes: set[str] = set()
    with sqlite3.connect(ROOT / "data" / "seed.db") as conn:
        for sql in (
            "select iata from airports", "select icao from airports",
            "select code from fare_classes", "select code from aircraft_types",
            "select pnr from bookings",
            "select distinct country_code from airports",
        ):
            codes.update(row[0] for row in conn.execute(sql) if row[0])
    return {c for c in codes if c.isalpha()}


LETTER_CODES = _letter_codes()


EMAIL = re.compile(latin_tokens.EMAIL_PATTERN)
URL_PATH = re.compile(latin_tokens.URL_PATH_PATTERN)


def _is_allowed(word: str, context: str) -> bool:
    if word in WHITELIST or word in LETTER_CODES:
        return True
    if any(word in address for address in EMAIL.findall(context)):
        return True
    if any(word in url for url in URL_PATH.findall(context)):
        return True
    for token in re.findall(r"[A-Za-z0-9-]+", context):
        if word in token and IDENTIFIER.match(token):
            return True
    return False

ROUTES = [
    "/",
    "/book/search",
    "/book/results?origin=ADD&destination=NBO&depart=2026-04-12&return=2026-04-19&adults=1",
    "/book/results?origin=NBO&destination=LHR&depart=2026-04-12",
    "/book/results?origin=LOS&destination=DXB&depart=2026-04-14",
]


VISIBLE_ATTRS = ("placeholder", "alt", "title", "aria-label")
_ATTR = re.compile(
    r"\b(?:" + "|".join(VISIBLE_ATTRS) + r")\s*=\s*(\"[^\"]*\"|\'[^\']*\')",
    re.IGNORECASE,
)


def _visible_text(html: str) -> str:
    html = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)
    html = re.sub(r"(?s)<!--.*?-->", " ", html)
    attr_text = " ".join(m.group(1)[1:-1] for m in _ATTR.finditer(html))
    body = re.sub(r"(?s)<[^>]+>", " ", html)
    text = html_module.unescape(body + " " + attr_text)
    return re.sub(r"\s+", " ", text)


@pytest.mark.parametrize("route", ROUTES)
def test_english_build_has_no_geez(route):
    client = create_app("en").test_client()
    text = _visible_text(client.get(route).get_data(as_text=True))
    found = GEEZ.findall(text)
    assert not found, f"Ge'ez codepoints in the English build at {route}: {set(found)}"


@pytest.mark.parametrize("route", ROUTES)
def test_amharic_build_has_no_stray_latin(route):
    client = create_app("am").test_client()
    text = _visible_text(client.get(route).get_data(as_text=True))
    stray = {w for w in LATIN_WORD.findall(text) if not _is_allowed(w, text)}
    assert not stray, f"untranslated Latin text in the Amharic build at {route}: {sorted(stray)}"
