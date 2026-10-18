from __future__ import annotations

import pytest

from app import create_app
from tasks.score import load, score

from task_near_misses import NEAR_MISSES
from task_solvers import SOLVERS

TASK_IDS = list(range(1, 31))
LANGUAGES = ("en", "am")


def _run(solver, language: str, number: int):
    app = create_app(language)
    client = app.test_client()
    params = load(language)[number]["instantiation"]["parameters"]
    outcome = solver(app, client, params)
    final_url, html = outcome[0], outcome[1]
    answer = outcome[2] if len(outcome) > 2 else ""
    return score(language, number, final_url, html, answer)


@pytest.mark.slow
@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize("number", TASK_IDS)
def test_task_can_be_carried_out(number, language):
    passed, reason = _run(SOLVERS[number], language, number)
    assert passed, f"task {number} [{language}] could not be solved: {reason}"


@pytest.mark.slow
@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize("number", TASK_IDS)
def test_a_plausible_wrong_run_is_rejected(number, language):
    passed, reason = _run(NEAR_MISSES[number], language, number)
    assert not passed, (
        f"task {number} [{language}] accepted a wrong run, so passing it "
        f"measures nothing: {reason}")


def test_every_task_has_both_a_solver_and_a_near_miss():
    tasks = set(load("en"))
    assert tasks == set(SOLVERS), {
        "tasks with no solver": sorted(tasks - set(SOLVERS)),
        "solvers with no task": sorted(set(SOLVERS) - tasks),
    }
    assert tasks == set(NEAR_MISSES), {
        "tasks with no near-miss": sorted(tasks - set(NEAR_MISSES)),
    }
