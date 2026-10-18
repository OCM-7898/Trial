import re

from conftest import ROOT, python_sources

FORBIDDEN = re.compile(r"\b(?:datetime\.now|datetime\.utcnow|date\.today|time\.time)\s*\(")
ALLOWED = {"app/clock.py"}


def test_no_live_clock_outside_clock_module():
    offenders = []
    for path in python_sources():
        rel = path.relative_to(ROOT).as_posix()
        if rel in ALLOWED or rel.startswith("tests/"):
            continue
        for lineno, line in enumerate(path.read_text("utf-8").splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            if FORBIDDEN.search(line):
                offenders.append(f"{rel}:{lineno}: {line.strip()}")
    assert not offenders, "live clock used outside app/clock.py:\n" + "\n".join(offenders)
