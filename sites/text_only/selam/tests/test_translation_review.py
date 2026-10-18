import csv
import json
import subprocess
import sys

import pytest

from conftest import APP_DIR, ROOT

CSV = ROOT / "spec" / "translation_review.csv"

ENCODING = "utf-8-sig"


def rows():
    with CSV.open(encoding=ENCODING, newline="") as handle:
        return list(csv.DictReader(handle))


def test_every_string_has_a_back_translation():
    missing = [r["key"] for r in rows() if not r["back_translation"].strip()]
    assert not missing, (
        f"{len(missing)} strings have no back-translation, so a reviewer cannot "
        f"check them without reading Ge'ez in full: {missing[:8]}")


def test_every_ui_string_is_covered():
    catalogue = set(json.loads((APP_DIR / "i18n" / "am.json").read_text("utf-8")))
    covered = {r["key"] for r in rows() if r["kind"] == "ui"}
    missing = catalogue - covered
    assert not missing, f"UI strings absent from the review file: {sorted(missing)[:8]}"


def test_seeded_content_is_covered_not_just_the_ui():
    seeded = [r for r in rows() if r["context"].startswith("50 seeded")]
    assert len(seeded) > 400, (
        f"only {len(seeded)} seeded strings are listed; a review of the UI alone "
        f"signs off a fraction of what an agent reads")
    tables = {r["context"] for r in seeded}
    for expected in ("content_pages", "lounges", "contact_offices", "airports"):
        assert any(expected in t for t in tables), f"{expected} is not under review"


def test_rows_are_grouped_for_screen_by_screen_review():
    contexts = [r["context"] for r in rows()]
    assert contexts == sorted(contexts), "rows are not grouped by context"


def test_back_translations_were_rendered_not_copied():
    prose = [r for r in rows() if r["kind"] == "prose" and len(r["english"]) > 60]
    assert prose, "no long prose rows to check"
    identical = [r for r in prose
                 if r["back_translation"].strip() == r["english"].strip()]
    proportion = len(identical) / len(prose)
    assert proportion < 0.30, (
        f"{proportion:.0%} of long prose back-translations are byte-identical to "
        f"the English column ({len(identical)}/{len(prose)}). Some coincidence is "
        f"expected from a faithful translation, but this much suggests the column "
        f"was copied rather than rendered from the Amharic.")


@pytest.mark.slow
def test_regeneration_preserves_review_marks(tmp_path):
    original = CSV.read_text("utf-8")
    try:
        data = rows()
        data[0]["reviewed"] = "y"
        with CSV.open("w", encoding=ENCODING, newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
        marked_key = data[0]["key"]

        result = subprocess.run([sys.executable, "tools/build_translation_review.py"],
                                cwd=ROOT, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr

        after = {r["key"]: r for r in rows()}
        assert after[marked_key]["reviewed"] == "y", \
            "regenerating the file discarded a reviewer's mark"
    finally:
        CSV.write_text(original, "utf-8")


@pytest.mark.slow
def test_changed_amharic_resets_its_review(tmp_path):
    original = CSV.read_text("utf-8")
    try:
        data = rows()
        target = next(r for r in data if r["kind"] == "ui")
        target["reviewed"] = "y"
        target["amharic"] = target["amharic"] + " (edited)"
        with CSV.open("w", encoding=ENCODING, newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)

        subprocess.run([sys.executable, "tools/build_translation_review.py"],
                       cwd=ROOT, capture_output=True, text=True, check=True)

        after = {r["key"]: r for r in rows()}[target["key"]]
        assert after["reviewed"] == "n", \
            "a row whose Amharic changed kept its old review mark"
        assert "changed since review" in after["note"]
    finally:
        CSV.write_text(original, "utf-8")


def test_the_file_carries_a_byte_order_mark():
    assert CSV.read_bytes()[:3] == b"\xef\xbb\xbf", (
        "spec/translation_review.csv has no UTF-8 byte order mark; Excel will "
        "render every Amharic cell as mojibake")


def test_the_file_is_valid_utf8_amharic():
    text = CSV.read_text(ENCODING)
    assert any(0x1200 <= ord(c) <= 0x137F for c in text), "no Ge'ez in the review file"
    suspicious = [row["key"] for row in rows()
                  if "·" in row["amharic"] or "Ã" in row["amharic"]]
    assert not suspicious, f"cells that look like mojibake were written: {suspicious[:5]}"
