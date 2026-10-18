import json
import re
import subprocess
import sys
import zipfile

import pytest

from conftest import ROOT

DIST = ROOT / "dist"
GEEZ = re.compile(r"[ሀ-፿]")

SKIP = ("fonts/", ".db", ".woff2", ".ttf")

MARKERS = {
    "en": ["Selam Airways", "Manage booking", "Highland Class", "Selam Miles"],
    "am": ["ሰላም አየር መንገድ", "የቦታ ማስያዣን ማስተዳደር", "ሃይላንድ ክላስ", "ሰላም ማይልስ"],
}

CONTENT_SKIP = ("tasks/tasks_",)


@pytest.fixture(scope="module")
def artifacts():
    result = subprocess.run([sys.executable, "export.py"], cwd=ROOT,
                            capture_output=True, text=True)
    assert result.returncode == 0, f"export.py failed:\n{result.stdout}\n{result.stderr}"
    return {lang: DIST / f"selam-airways-{lang}.zip" for lang in ("en", "am")}


def _members(archive):
    with zipfile.ZipFile(archive) as zf:
        return {name: zf.read(name) for name in zf.namelist()}


@pytest.mark.slow
def test_both_artifacts_are_produced(artifacts):
    for lang, path in artifacts.items():
        assert path.exists(), f"{path.name} was not built"
        assert path.stat().st_size > 1_000_000, f"{path.name} looks truncated"


@pytest.mark.slow
def test_no_translation_machinery_survives(artifacts):
    for lang, path in artifacts.items():
        names = set(_members(path))
        forbidden = [n for n in names
                     if n.rsplit("/", 1)[-1] in ("en.json", "am.json", "glossary.json")
                     or "/i18n/" in n]
        assert not forbidden, f"{lang}: translation machinery shipped -- {forbidden}"


@pytest.mark.slow
def test_neither_artifact_contains_the_other_language(artifacts):
    for lang, path in artifacts.items():
        other = "am" if lang == "en" else "en"
        leaks = []
        for name, blob in _members(path).items():
            if any(skip in name for skip in SKIP + CONTENT_SKIP):
                continue
            try:
                text = blob.decode("utf-8")
            except UnicodeDecodeError:
                continue
            for marker in MARKERS[other]:
                if marker in text:
                    leaks.append(f"{name}: {marker!r}")
        assert not leaks, f"{lang} artifact contains {other} content: {leaks[:5]}"


@pytest.mark.slow
def test_task_intents_are_in_the_build_language(artifacts):
    geez = re.compile(r"[ሀ-፿]")
    for lang, path in artifacts.items():
        tasks = json.loads(_members(path)[f"tasks/tasks_{lang}.json"].decode("utf-8"))
        assert len(tasks) == 30
        for task in tasks:
            has_geez = bool(geez.search(task["intent"]))
            if lang == "am":
                assert has_geez, f"task {task['task_id']}: Amharic intent has no Ge'ez"
            else:
                assert not has_geez, f"task {task['task_id']}: English intent has Ge'ez"


@pytest.mark.slow
def test_only_this_builds_task_file_ships(artifacts):
    for lang, path in artifacts.items():
        other = "am" if lang == "en" else "en"
        names = set(_members(path))
        assert f"tasks/tasks_{lang}.json" in names, f"{lang}: its own task file is missing"
        assert f"tasks/tasks_{other}.json" not in names, \
            f"{lang} artifact ships the {other} task file"


@pytest.mark.slow
def test_english_artifact_has_no_geez_at_all(artifacts):
    leaks = []
    for name, blob in _members(artifacts["en"]).items():
        if any(skip in name for skip in SKIP + CONTENT_SKIP):
            continue
        try:
            text = blob.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if GEEZ.search(text):
            leaks.append(name)
    assert not leaks, f"Ge'ez codepoints in the English artifact: {leaks}"


@pytest.mark.slow
def test_no_unbaked_translation_calls_remain(artifacts):
    sys.path.insert(0, str(ROOT / "tools"))
    from bake import remaining_calls

    for lang, path in artifacts.items():
        offenders = []
        for name, blob in _members(path).items():
            if not name.endswith((".py", ".html")):
                continue
            found = remaining_calls(blob.decode("utf-8"), name.endswith(".py"))
            if found:
                offenders.append(f"{name}: {found[:2]}")
        assert not offenders, f"{lang}: unbaked t() calls -- {offenders}"


@pytest.mark.slow
def test_artifacts_declare_no_language_choice(artifacts):
    for lang, path in artifacts.items():
        members = _members(path)
        run_py = members["run.py"].decode("utf-8")
        assert "--lang" not in run_py, f"{lang}: run.py still offers --lang"
        config = members["app/config.py"].decode("utf-8")
        assert "PORTS" not in config and "DB_FILES" not in config, \
            f"{lang}: config.py still maps languages to ports"
        assert f'LANGUAGE = "{lang}"' in config


@pytest.mark.slow
def test_exported_build_boots_and_serves(tmp_path, artifacts):
    for lang, archive in artifacts.items():
        target = tmp_path / lang
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(target)

        script = (
            "import sys; sys.path.insert(0, '.');"
            "from app import create_app;"
            "c = create_app().test_client();"
            "import json;"
            "print(json.dumps({u: c.get(u).status_code for u in "
            "['/', '/manage', '/lounges', '/miles/join', '/help', '/book/search']}))"
        )
        result = subprocess.run([sys.executable, "-c", script], cwd=target,
                                capture_output=True, text=True)
        assert result.returncode == 0, f"{lang} artifact failed to boot:\n{result.stderr[-1200:]}"
        statuses = json.loads(result.stdout.strip().splitlines()[-1])
        bad = {u: s for u, s in statuses.items() if s != 200}
        assert not bad, f"{lang} artifact served errors: {bad}"


@pytest.mark.slow
def test_parity_passes_against_the_artifacts():
    result = subprocess.run(
        [sys.executable, "verify_parity.py", "--from-dist", "dist"],
        cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "All six checks pass" in result.stdout
