from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

STANDALONE_HTML = sorted(
    p for p in ROOT.glob("spec/*.html")
) + sorted(ROOT.glob("*.html"))

CSV_FILES = sorted(ROOT.glob("spec/*.csv"))


def _has_geez(text: str) -> bool:
    return any(0x1200 <= ord(ch) <= 0x137F for ch in text)


@pytest.mark.parametrize("path", STANDALONE_HTML,
                         ids=lambda p: p.relative_to(ROOT).as_posix())
def test_standalone_html_declares_utf8(path):
    head = path.read_text("utf-8")[:2048]
    assert re.search(r'<meta\s+charset=["\']?utf-8', head, re.I), (
        f"{path.relative_to(ROOT)} has no charset declaration; a browser opening "
        f"it from disk will guess the local codepage and render Ge'ez as mojibake")


@pytest.mark.parametrize("path", CSV_FILES,
                         ids=lambda p: p.relative_to(ROOT).as_posix())
def test_csv_with_geez_carries_a_byte_order_mark(path):
    raw = path.read_bytes()
    if not _has_geez(raw.decode("utf-8-sig", errors="replace")):
        pytest.skip("no Ge'ez in this file, so the mark is not required")
    assert raw[:3] == b"\xef\xbb\xbf", (
        f"{path.relative_to(ROOT)} contains Ge'ez but has no UTF-8 byte order "
        f"mark; Excel will render every Amharic cell as mojibake")


def test_the_sites_own_pages_declare_it_too():
    base = (ROOT / "app" / "templates" / "base.html").read_text("utf-8")
    assert re.search(r'<meta\s+charset=["\']?utf-8', base, re.I), \
        "base.html lost its charset declaration"
