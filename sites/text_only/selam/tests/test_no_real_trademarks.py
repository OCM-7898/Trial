from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

FORBIDDEN = [
    "Ethiopian Airlines", "ShebaMiles", "Sheba Miles", "Cloud Nine",
    "Skylight", "Ethiopian Skylight", "ET Airlines",
    "ኢትዮጵያ አየር መንገድ", "ሸባማይልስ", "ሸባ ማይልስ", "ክላውድ ናይን", "ስካይላይት",
]

EXEMPT_PATHS = {
    "spec/brand_substitutions.md",
    "tools/brand_substitutions.py",
    "SPEC.md",
    "AGENTS.md",
    "tests/test_no_real_trademarks.py",
}
EXEMPT_DIRS = {".git", ".venv", "dist", "__pycache__", ".pytest_cache", "spec/tasks_source.xlsx"}

SCANNED_SUFFIXES = {".py", ".json", ".html", ".css", ".js", ".md", ".yaml",
                    ".yml", ".txt", ".csv", ".svg"}


def _files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in SCANNED_SUFFIXES:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if any(part in EXEMPT_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if relative in EXEMPT_PATHS:
            continue
        yield relative, path


def test_no_real_trademark_appears_in_any_shipped_file():
    offenders = []
    for relative, path in _files():
        try:
            text = path.read_text("utf-8")
        except UnicodeDecodeError:
            continue
        for mark in FORBIDDEN:
            for match in re.finditer(re.escape(mark), text):
                line = text.count("\n", 0, match.start()) + 1
                offenders.append(f"{relative}:{line} {mark!r}")

    assert not offenders, (
        "real airline trademarks in the tree:\n  " + "\n  ".join(offenders[:20]))


def test_no_real_trademark_is_seeded_into_the_database():
    import sqlite3

    connection = sqlite3.connect(ROOT / "data" / "seed.db")
    tables = [row[0] for row in connection.execute(
        "select name from sqlite_master where type='table'")]

    offenders = []
    for table in tables:
        columns = [row[1] for row in connection.execute(f"pragma table_info({table})")]
        text_columns = [c for c in columns if c.endswith(("_en", "_am")) or
                        c in ("name", "title", "description", "notes", "payload")]
        for column in text_columns:
            for mark in FORBIDDEN:
                hits = connection.execute(
                    f'select count(*) from "{table}" where "{column}" like ?',
                    (f"%{mark}%",)).fetchone()[0]
                if hits:
                    offenders.append(f"{table}.{column}: {hits} row(s) with {mark!r}")

    assert not offenders, "trademarks in the seed data:\n  " + "\n  ".join(offenders)
