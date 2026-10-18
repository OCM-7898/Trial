# Selam Airways — a bilingual web-agent benchmark environment

A self-hosted, deterministic clone of an African flag-carrier airline website,
built in two language versions — English and Amharic — that are identical in
every respect except the language of every user-visible string.

The point is measurement. If an agent scores lower on the Amharic build, the
site is not the reason: same routes, same DOM skeleton, same database, same
prices, same frozen clock. `verify_parity.py` proves that on every build, and
fails the build when it is not true.

The full specification is [SPEC.md](SPEC.md). This file is how to run it.
[HANDOVER.html](HANDOVER.html) is the briefing to hand someone picking this up:
what is built, what is left, and what to read in what order.

## Quick start

Python 3.11 or newer, and nothing else. No Docker, no npm, no network.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py
python run.py --lang en --port 7770
```

Then open <http://localhost:7770>. For the Amharic build, in a second terminal:

```bash
source .venv/bin/activate
python run.py --lang am --port 7771
```

Both run at once. They use separate database files and share no process state.

`python seed.py` must print this hash, on any machine and any supported Python:

```
sha256        9567ad62dbb9b16e94dc6cb26d72b3f76374f44f3d1a7d57fe1317265428d55c
```

If it differs, the seed inputs have been edited — that is the check, not a
formality. Verified on CPython 3.11.16 and 3.14.5, which produce byte-identical
databases.

## Shipping the two artifacts

```bash
python export.py                     # dist/selam-airways-{en,am}.zip
python verify_parity.py --from-dist dist
```

`export.py` resolves every `t("key")` into a literal, deletes `app/i18n/`
outright, drops the unused half of every paired column, and bakes the language
into the config. The shipped Amharic zip contains no English UI string, no
catalogue, no fallback path and no toggle. It then boots each artifact, crawls
every route and submits nine forms; a 5xx anywhere fails the build.

Each zip runs offline on a clean machine with Python 3.11 and nothing else.

## Running one episode

```bash
curl -X POST http://localhost:7770/reset     # ~7 ms, restores byte-identical state
# run the agent with the intent from tasks/tasks_en.json
python -m tasks.score --lang en --task 13 --final-url "<where the agent stopped>"
```

[tasks/README.md](tasks/README.md) has the detail. Thirty tasks, the same
thirty ids in both languages, seventeen with a validator that queries the
database directly rather than scraping.

To walk the tasks by hand, open [spec/TESTING_RUNBOOK.html](spec/TESTING_RUNBOOK.html)
— credentials, click paths and pass conditions for all thirty, in both languages.

## What is in here

| | |
|---|---|
| Routes | 133, across the 40 service areas of SPEC.md §8 |
| Tasks | 30, in both languages, 17 with state validators |
| Airports / routes / flights | 75 / 164 / ~11,000 over a 180-day window |
| Bookings | 60 PNRs, covering every branch the tasks need |
| Strings under review | 1,948, all back-translated |
| Tests | 420 |

Eighteen of the forty service areas are **distractors**: no task depends on
them, and they exist so that an agent has somewhere plausible to go wrong. They
are functional — forms submit, searches return seeded rows, confirmations
render — because a dead link is not a distractor, it is a bug.

## The rules that shape the code

Four constraints run through everything, and most of the tests exist to enforce
one of them:

**Determinism.** `FROZEN_TODAY = 2026-03-16`. `datetime.now()` and
`date.today()` are banned outside `app/clock.py`, and a test greps for
violations. Prices are static per `(flight, fare class)`. Nothing is random at
request time.

**Resettability.** `POST /reset` restores `data/seed.db` byte for byte and
clears generated PDFs. Twenty consecutive cycles with write traffic in between
produce one hash.

**Programmatic evaluability.** Every task has a machine-checkable condition.
Purchase flows end at a `/review` URL and nothing is ever marked paid, so a
state-check task asserts a pending row plus the review URL — never a payment.

**Language isolation.** There is no language toggle: no query parameter, no
cookie, no header, no admin page, no UI control. Each artifact physically
contains one language.

## Working on it

```bash
pip install -r requirements-dev.txt  # adds pytest and pypdf
python -m pytest -q                  # 420 tests, ~49 s
python verify_parity.py              # six checks against the source tree
python seed.py                       # regenerates data/seed.db, byte-identical
```

The suite is the specification made executable. Some of it enforces rules that
are easy to break without noticing:

| Test | Refuses |
|---|---|
| `test_no_live_clock` | `datetime.now()` anywhere but `app/clock.py` |
| `test_static_keys` | `t(variable)` — export bakes literals and cannot resolve one |
| `test_no_literal_text` | user-visible text in a template that is not a `t()` call |
| `test_no_paired_column_access` | naming `x_en`/`x_am` outside `app/models/` |
| `test_translation_hygiene` | a placeholder, figure or HTML shape that differs between languages |
| `test_no_real_trademarks` | a real airline's marks, in any file or database column |
| `test_glossary` | a locked domain term rendered two different ways |
| `test_no_dead_links` | a route in `routes_map.py` with no view |
| `test_builds_share_nothing` | a writable path, cookie or key shared by both builds |
| `test_shipped_files_declare_their_encoding` | a shipped file whose Ge'ez would open as mojibake |
| `test_every_area_is_reachable` | a route nothing links to, in either build |
| `test_task_walkthroughs` | a task that cannot be solved, or that accepts a wrong run |
| `test_tasks_match_the_seed` | task configs that have drifted from the database |

Regenerate seed data with the tools that produce it — `tools/make_*.py` write
YAML into `spec/seed_data/`, and `seed.py` compiles that into the database.
Editing the YAML by hand works but the generators carry the non-degeneracy
assertions, so prefer them.

Adding a user-visible string means adding it to both `app/i18n/en.json` and
`app/i18n/am.json`, plus a back-translation in `tools/back_translations.py`;
`tests/test_translation_review.py` fails otherwise. Adding a paired database
column means annotating it in `tools/build_translation_review.py`, for the same
reason.

## Before using this for measurement

`spec/translation_review.csv` has a back-translation for all 1,948 Amharic
strings and **zero reviewed by a native speaker**. `spec/HOW_TO_REVIEW.md` is
the brief to send with it. Until that pass happens, a
performance gap measured with this environment cannot be attributed to language
difficulty rather than to translation quality. SPEC.md §18.2 says the same.

## Provenance

No real airline's trademarks appear anywhere. Geography is real — city names,
airport names, IATA codes — because it is factual and the Amharic content needs
it. Every commercial mark is invented; `app/brand.py` is the one file to edit to
rename them, and `spec/brand_substitutions.md` records each substitution. All
imagery is original SVG. See [NOTICE.md](NOTICE.md).
