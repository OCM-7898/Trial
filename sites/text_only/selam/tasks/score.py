from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import lang as language_module
from app.config import Config


CHROME = re.compile(r"<(header|footer|nav)\b.*?</\1>", re.S | re.I)


def main_content(html: str) -> str:
    if not html:
        return ""
    stripped = CHROME.sub(" ", html)
    mains = re.findall(r"<main\b[^>]*>(.*?)</main>", stripped, re.S | re.I)
    return "\n".join(mains) if mains else stripped


@contextmanager
def live_session(lang: str):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    language_module.set_active(lang)
    config = Config.for_language(lang)
    if not config.db_path.exists():
        raise SystemExit(f"{config.db_path} does not exist -- is the build running?")
    engine = create_engine(f"sqlite:///{config.db_path}", future=True)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def load(lang: str) -> dict[int, dict]:
    path = ROOT / "tasks" / f"tasks_{lang}.json"
    return {task["task_id"]: task for task in json.loads(path.read_text("utf-8"))}


def score(lang: str, task_id: int, final_url: str, html: str, answer: str) -> tuple[bool, str]:
    task = load(lang)[task_id]
    if not task["runnable"]:
        return False, f"task {task_id} is not runnable yet; waiting on {task['blocked_by']}"

    evaluation = task["eval"]
    if "validator" in evaluation:
        module = importlib.import_module(evaluation["validator"])
        with live_session(lang) as session:
            return module.validate(session, final_url, html,
                                   **evaluation.get("validator_args", {}))

    references = evaluation.get("reference_answers", {})
    required = references.get("must_include", [])

    if references.get("answer_only"):
        haystack, source = answer, "the reported answer"
    else:
        haystack, source = f"{answer}\n{main_content(html)}", "the answer or the page"

    missing = [item for item in required if str(item) not in haystack]
    if missing:
        return False, f"{source} is missing: {missing}"
    return True, f"{source} contains all {len(required)} required elements"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", choices=("en", "am", "bn", "hi", "ur"), required=True)
    parser.add_argument("--task", type=int, required=True)
    parser.add_argument("--final-url", default="")
    parser.add_argument("--html-file", type=Path, default=None)
    parser.add_argument("--answer", default="", help="the agent's reported answer")
    args = parser.parse_args()

    html = args.html_file.read_text("utf-8") if args.html_file else ""
    passed, reason = score(args.lang, args.task, args.final_url, html, args.answer)
    print(f"task {args.task} [{args.lang}]: {'PASS' if passed else 'FAIL'} -- {reason}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
