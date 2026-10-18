from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASK_FILES = ("tasks/tasks_en.json", "tasks/tasks_am.json")


def test_committed_task_files_match_a_fresh_generation(tmp_path):
    before = {name: (ROOT / name).read_text("utf-8") for name in TASK_FILES}
    backups = {name: tmp_path / Path(name).name for name in TASK_FILES}
    for name, backup in backups.items():
        backup.write_text(before[name], "utf-8")

    result = subprocess.run(
        [sys.executable, "tools/build_tasks.py"], cwd=ROOT,
        capture_output=True, text=True)
    try:
        assert result.returncode == 0, (
            f"tools/build_tasks.py failed:\n{result.stdout}\n{result.stderr}")
        after = {name: (ROOT / name).read_text("utf-8") for name in TASK_FILES}
        drifted = [name for name in TASK_FILES if before[name] != after[name]]
        if drifted:
            details = []
            for name in drifted:
                old = {t["task_id"]: t for t in json.loads(before[name])}
                new = {t["task_id"]: t for t in json.loads(after[name])}
                for task_id in sorted(set(old) | set(new)):
                    if old.get(task_id) != new.get(task_id):
                        details.append(
                            f"{name} task {task_id}: "
                            f"{old.get(task_id, {}).get('intent', '<absent>')[:70]!r} "
                            f"-> {new.get(task_id, {}).get('intent', '<absent>')[:70]!r}")
            raise AssertionError(
                "the committed task files do not match the seed data. Run "
                "`python tools/build_tasks.py` and commit the result:\n  "
                + "\n  ".join(details[:8]))
    finally:
        for name, backup in backups.items():
            (ROOT / name).write_text(backup.read_text("utf-8"), "utf-8")
