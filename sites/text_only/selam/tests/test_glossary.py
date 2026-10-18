import json
import re

import pytest

from conftest import APP_DIR

GLOSSARY = json.loads((APP_DIR / "i18n" / "glossary.json").read_text("utf-8"))
EN = json.loads((APP_DIR / "i18n" / "en.json").read_text("utf-8"))
AM = json.loads((APP_DIR / "i18n" / "am.json").read_text("utf-8"))

PREFIXES = ("የ", "በ", "ከ", "ለ", "ወደ", "እንደ")

BRAND_PHRASES = ("Selam Miles", "Selam Airways", "Highland Class", "Highland Lounge",
                 "Selam Sky Lounge", "Selam Economy", "Economy Flex", "SkyLink")


ETHIOPIC_START = 0x1200
ETHIOPIC_END = 0x137F


def consonants(word: str) -> str:
    return "".join(
        chr(0x1200 + ((ord(ch) - ETHIOPIC_START) // 8) * 8)
        for ch in word
        if ETHIOPIC_START <= ord(ch) <= ETHIOPIC_END
    )


def longest_common_run(a: str, b: str) -> str:
    best = ""
    for start in range(len(a)):
        for end in range(start + 1, len(a) + 1):
            piece = a[start:end]
            if piece in b and len(piece) > len(best):
                best = piece
    return best


def shares_root(primary: str, candidate: str) -> bool:
    a, b = consonants(primary), consonants(candidate)
    if not a or not b:
        return False
    needed = 1 if min(len(a), len(b)) <= 2 else 2
    return len(longest_common_run(a, b)) >= needed


def strip_prefix(word: str) -> str:
    for prefix in PREFIXES:
        if word.startswith(prefix) and len(word) > len(prefix) + 1:
            return word[len(prefix):]
    return word


def amharic_contains(term: str, text: str) -> bool:
    if term in text:
        return True
    tokens = [strip_prefix(t) for t in re.split(r"[\s፣።፤]+", text) if t]
    for word in term.split():
        stem = strip_prefix(word)[:-1]
        if not stem or not any(t.startswith(stem) for t in tokens):
            return False
    return True


def english_uses(term: str, english: str) -> bool:
    text = english
    for phrase in BRAND_PHRASES:
        text = text.replace(phrase, " ")
    text = re.sub(r"\{[^}]*\}", " ", text)
    return bool(re.search(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE))


@pytest.mark.parametrize("term", sorted(GLOSSARY))
def test_term_renders_consistently(term):
    entry = GLOSSARY[term]
    accepted = entry.get("forms") or [entry["am"]]
    exempt = entry.get("exempt", {})
    offenders = []
    for key, english in sorted(EN.items()):
        if not english_uses(term, english):
            continue
        if key in exempt:
            continue
        amharic = AM.get(key, "")
        if not any(amharic_contains(form, amharic) for form in accepted):
            offenders.append(f"{key}: en={english!r} am={amharic!r}")
    assert not offenders, (
        f"'{term}' must render as one of {accepted}; these do not:\n  "
        + "\n  ".join(offenders[:6]))


def test_accepted_forms_share_a_root():
    for term, entry in GLOSSARY.items():
        forms = entry.get("forms") or [entry["am"]]
        if len(forms) < 2:
            continue
        primary = strip_prefix(forms[0].split()[0])
        for form in forms[1:]:
            candidate = strip_prefix(form.split()[0])
            assert shares_root(primary, candidate), (
                f"'{term}': {form!r} (skeleton {consonants(candidate)}) is not built on "
                f"the same root as {forms[0]!r} (skeleton {consonants(primary)}); "
                f"a synonym here would defeat the glossary")


def test_glossary_covers_the_terms_claude_md_requires():
    required = {
        "round-trip", "booking reference", "reservation", "boarding pass",
        "online check-in", "checked baggage", "cabin baggage", "aisle seat",
        "extra legroom", "stopover", "lounge", "travel insurance", "refund",
        "cabin class", "itinerary", "flight status", "fare difference", "passenger",
    }
    missing = required - set(GLOSSARY)
    assert not missing, f"glossary is missing required terms: {sorted(missing)}"


def test_spreadsheet_terms_are_marked_as_vetted():
    vetted = [t for t, e in GLOSSARY.items() if e["source"] == "spreadsheet"]
    assert len(vetted) >= 18, f"only {len(vetted)} terms trace to the spreadsheet"
    for term, entry in GLOSSARY.items():
        assert entry["source"] in ("spreadsheet", "generated", "claimed"), term


def test_every_exemption_states_a_reason():
    for term, entry in GLOSSARY.items():
        for key, reason in entry.get("exempt", {}).items():
            assert reason.strip(), f"{term}/{key} is exempt with no reason given"
            assert key in EN, f"{term} exempts {key!r}, which is not a real key"


def test_exemptions_stay_rare():
    total = sum(len(e.get("exempt", {})) for e in GLOSSARY.values())
    assert total <= len(GLOSSARY) // 4, (
        f"{total} exemptions across {len(GLOSSARY)} terms is too many to still "
        f"call this a locked vocabulary")
