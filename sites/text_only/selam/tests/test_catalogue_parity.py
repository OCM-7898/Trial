import json
import re

from conftest import APP_DIR

CODE_LIKE = re.compile(r"^[A-Z0-9 .:,\-/()]+$")


def _catalogue(lang):
    return json.loads((APP_DIR / "i18n" / f"{lang}.json").read_text("utf-8"))


def test_key_sets_match():
    en, am = _catalogue("en"), _catalogue("am")
    only_en = sorted(set(en) - set(am))
    only_am = sorted(set(am) - set(en))
    assert not only_en and not only_am, f"only in en: {only_en}\nonly in am: {only_am}"


def test_no_empty_strings():
    for lang in ("en", "am"):
        empty = sorted(k for k, v in _catalogue(lang).items() if not v.strip())
        assert not empty, f"{lang}.json has empty values: {empty}"


def test_amharic_values_are_not_copied_from_english():
    en, am = _catalogue("en"), _catalogue("am")
    copied = sorted(
        k for k in en
        if en[k] == am.get(k)
        and any(c.isalpha() for c in en[k])
        and not CODE_LIKE.match(en[k])
    )
    assert not copied, f"identical in both languages, so probably untranslated: {copied}"
