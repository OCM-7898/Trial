from __future__ import annotations

import html as htmllib
import json
import re
import sqlite3
import unicodedata
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EN = json.loads((ROOT / "app" / "i18n" / "en.json").read_text("utf-8"))
AM = json.loads((ROOT / "app" / "i18n" / "am.json").read_text("utf-8"))

PLACEHOLDER = re.compile(r"\{([a-z_0-9]+)\}")
NUMBER = re.compile(r"\d+(?:[.,]\d+)?")
TAG = re.compile(r"<[^>]+>")

IDENTICAL_BY_DESIGN = {
    "results.band_morning", "results.band_afternoon", "search.code_placeholder",
}


def _seeded_pairs():
    from app.models import Base

    connection = sqlite3.connect(ROOT / "data" / "seed.db")
    connection.row_factory = sqlite3.Row
    for name, table in sorted(Base.metadata.tables.items()):
        columns = {c.name for c in table.columns}
        fields = sorted({c[:-3] for c in columns if c.endswith("_en")} &
                        {c[:-3] for c in columns if c.endswith("_am")})
        if not fields:
            continue
        key = "id" if "id" in columns else sorted(columns)[0]
        selected = ", ".join(f"{f}_en, {f}_am" for f in fields)
        for row in connection.execute(f"select {key}, {selected} from {table}"):
            for field in fields:
                english, amharic = row[f"{field}_en"], row[f"{field}_am"]
                if english or amharic:
                    yield f"{name}.{row[key]}.{field}", english, amharic


def _geez(text: str) -> bool:
    return any(0x1200 <= ord(c) <= 0x137F for c in text)


def test_catalogues_hold_the_same_keys():
    assert set(EN) == set(AM), {
        "only in en": sorted(set(EN) - set(AM))[:10],
        "only in am": sorted(set(AM) - set(EN))[:10],
    }


def test_placeholders_survive_translation():
    offenders = [
        f"{key}: en={sorted(PLACEHOLDER.findall(EN[key]))} "
        f"am={sorted(PLACEHOLDER.findall(AM[key]))}"
        for key in sorted(EN)
        if Counter(PLACEHOLDER.findall(EN[key])) != Counter(PLACEHOLDER.findall(AM[key]))
    ]
    assert not offenders, offenders


def test_figures_are_copied_not_translated():
    offenders = []
    for key in sorted(EN):
        english, amharic = htmllib.unescape(EN[key]), htmllib.unescape(AM[key])
        if Counter(NUMBER.findall(english)) != Counter(NUMBER.findall(amharic)):
            offenders.append(f"{key}: {english[:60]!r} vs {amharic[:60]!r}")
    for ident, english, amharic in _seeded_pairs():
        if not (english and amharic):
            continue
        e, a = htmllib.unescape(english), htmllib.unescape(amharic)
        if Counter(NUMBER.findall(e)) != Counter(NUMBER.findall(a)):
            offenders.append(f"{ident}: {e[:60]!r} vs {a[:60]!r}")
    assert not offenders, offenders[:10]


def test_seeded_html_has_the_same_shape_in_both_languages():
    offenders = []
    for ident, english, amharic in _seeded_pairs():
        if not (english and amharic):
            continue
        if Counter(TAG.findall(english)) != Counter(TAG.findall(amharic)):
            offenders.append(ident)
    assert not offenders, offenders[:10]


def test_every_translated_string_is_actually_in_amharic():
    offenders = [
        f"{key}: {EN[key][:50]!r}" for key in sorted(EN)
        if EN[key].strip() and key not in IDENTICAL_BY_DESIGN and not _geez(AM[key])
    ]
    offenders += [
        f"{ident}: {english[:50]!r}" for ident, english, amharic in _seeded_pairs()
        if english and english.strip() and amharic and not _geez(amharic)
    ]
    assert not offenders, offenders[:10]


def test_no_stray_latin_words_inside_amharic():
    offenders = []
    for key in sorted(EN):
        stripped = PLACEHOLDER.sub("", AM[key])
        if not _geez(stripped):
            continue
        words = [w for w in re.findall(r"\b[A-Za-z]{3,}\b", stripped)
                 if not re.fullmatch(r"[A-Z]{2,4}", w)]
        if words:
            offenders.append(f"{key}: {words[:5]}")
    for ident, _, amharic in _seeded_pairs():
        if not amharic or not _geez(amharic):
            continue
        plain = htmllib.unescape(TAG.sub(" ", amharic))
        words = [w for w in re.findall(r"\b[A-Za-z]{3,}\b", plain)
                 if not re.fullmatch(r"[A-Z]{2,4}", w)]
        if words:
            offenders.append(f"{ident}: {words[:5]}")
    assert not offenders, offenders[:10]


def test_amharic_uses_the_polite_imperative():
    familiar = re.compile(r"(?<![ሀ-፿])(አድርግ|ሂድ|ተመልከት|ግዛ|ክፈት|ላክ|ሙላ|ጻፍ)(?![ሀ-፿])")
    offenders = [f"{key}: {AM[key][:40]!r}" for key in sorted(AM)
                 if familiar.search(AM[key])]
    offenders += [f"{ident}: {amharic[:40]!r}"
                  for ident, _, amharic in _seeded_pairs()
                  if amharic and familiar.search(amharic)]
    assert not offenders, offenders[:10]


def test_amharic_uses_western_numerals():
    geez_digits = re.compile(r"[፩-፼]")
    offenders = [key for key in sorted(AM) if geez_digits.search(AM[key])]
    offenders += [ident for ident, _, amharic in _seeded_pairs()
                  if amharic and geez_digits.search(amharic)]
    assert not offenders, offenders[:10]


@pytest.mark.parametrize("catalogue,label", [(EN, "en"), (AM, "am")])
def test_strings_are_clean_text(catalogue, label):
    offenders = []
    for key, value in sorted(catalogue.items()):
        if value != unicodedata.normalize("NFC", value):
            offenders.append(f"{key}: not NFC-normalised")
        if value != value.strip():
            offenders.append(f"{key}: surrounding whitespace {value!r}")
        if "  " in value:
            offenders.append(f"{key}: double space")
        if any(unicodedata.category(c) == "Cc" and c not in "\n\t" for c in value):
            offenders.append(f"{key}: control character")
    assert not offenders, f"{label}: {offenders[:10]}"
