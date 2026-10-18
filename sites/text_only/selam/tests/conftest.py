import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

APP_DIR = ROOT / "app"
TEMPLATE_DIR = APP_DIR / "templates"


def python_sources():
    for p in sorted(ROOT.rglob("*.py")):
        if any(part in {".venv", "dist", "__pycache__"} for part in p.parts):
            continue
        yield p


def templates():
    yield from sorted(TEMPLATE_DIR.rglob("*.html"))


def _blank_out(match) -> str:
    return "\n" * match.group(0).count("\n")


def template_code(path) -> str:
    import re

    text = path.read_text("utf-8")
    text = re.sub(r"(?s)\{#.*?#\}", _blank_out, text)
    text = re.sub(r"(?s)<!--.*?-->", _blank_out, text)
    return text
