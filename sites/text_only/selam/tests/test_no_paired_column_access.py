from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"

EXEMPT_DIRS = ("models",)

SUFFIXES = ("_en", "_am")


def _sources():
    for path in sorted(APP.rglob("*.py")):
        if any(part in EXEMPT_DIRS for part in path.relative_to(APP).parts[:-1]):
            continue
        yield path


def _paired_fields() -> set[str]:
    from app.models import Base

    fields = set()
    for table in Base.metadata.tables.values():
        columns = {c.name for c in table.columns}
        fields |= ({c[:-3] for c in columns if c.endswith("_en")} &
                   {c[:-3] for c in columns if c.endswith("_am")})
    return fields


def _offences(path: Path, fields: set[str]) -> list[str]:
    tree = ast.parse(path.read_text("utf-8"))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            name = node.attr
        elif isinstance(node, ast.keyword) and node.arg:
            name = node.arg
        else:
            continue
        if name.endswith(SUFFIXES) and name[:-3] in fields:
            found.append(f"{path.relative_to(ROOT).as_posix()}:{node.lineno} {name}")
    return found


def test_no_language_half_is_named_outside_the_models_package():
    fields = _paired_fields()
    assert fields, "no paired columns found; the scan would pass vacuously"
    offences = [o for path in _sources() for o in _offences(path, fields)]
    assert not offences, (
        "these names a language half directly and will raise in one artifact:\n  "
        + "\n  ".join(offences)
    )
