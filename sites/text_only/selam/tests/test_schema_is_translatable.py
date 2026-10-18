import pytest

from app.models import Base

PAIRED_SUFFIXES = ("_en", "_am")


def paired_columns() -> dict[str, set[str]]:
    out = {}
    for name, table in Base.metadata.tables.items():
        columns = {c.name for c in table.columns}
        fields = {c[:-3] for c in columns if c.endswith("_en")} & \
                 {c[:-3] for c in columns if c.endswith("_am")}
        if fields:
            out[name] = {f"{f}{s}" for f in fields for s in PAIRED_SUFFIXES}
    return out


def test_no_unique_constraint_covers_a_translated_column():
    offenders = []
    paired = paired_columns()
    for name, table in Base.metadata.tables.items():
        translated = paired.get(name, set())
        if not translated:
            continue
        for constraint in table.constraints:
            columns = {c.name for c in getattr(constraint, "columns", [])}
            overlap = columns & translated
            if overlap:
                offenders.append(f"{name}.{getattr(constraint, 'name', '?')}: {sorted(overlap)}")
    assert not offenders, (
        "constraints over translated columns cannot survive export and would differ "
        "between builds:\n  " + "\n  ".join(offenders))


def test_no_index_covers_a_translated_column_it_cannot_keep():
    offenders = []
    paired = paired_columns()
    for name, table in Base.metadata.tables.items():
        translated = paired.get(name, set())
        for index in table.indexes:
            columns = {c.name for c in index.columns}
            if len(columns & translated) > 1:
                offenders.append(f"{name}.{index.name}: {sorted(columns & translated)}")
    assert not offenders, "indexes spanning both languages: " + str(offenders)


def test_no_module_names_a_paired_column_directly():
    import re

    from conftest import ROOT

    pattern = re.compile(r"\b[A-Z][A-Za-z]*\.[a-z_]+_(?:en|am)\b")
    offenders = []
    for path in sorted((ROOT / "app").rglob("*.py")):
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith("app/models/"):
            continue
        for number, line in enumerate(path.read_text("utf-8").splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            if pattern.search(line):
                offenders.append(f"{relative}:{number}: {line.strip()}")
    assert not offenders, (
        "use translated_column(Model, 'field') instead:\n  " + "\n  ".join(offenders))
