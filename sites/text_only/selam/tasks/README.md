# Running an episode

Thirty tasks, in two language builds. `tasks_en.json` and `tasks_am.json` hold
the same 30 ids in the same order with the same structure; only `intent` and the
reference answers differ.

## One episode

```bash
# 1. restore seed state and confirm it
curl -s -X POST http://localhost:7770/reset
curl -s http://localhost:7770/reset/status      # {"clean": true, ...}

# 2. run the agent with the task's `intent`, starting at `start_url`

# 3. score it
python -m tasks.score --lang en --task 13 \
    --final-url "$FINAL_URL" --html-file page.html
```

`POST /reset` must be called **between every episode**. It restores the database
byte-for-byte and clears generated boarding passes, and it returns the seed hash
so a harness can assert a clean start. It completes in about 5 ms.

## What a task record contains

| Field | Meaning |
|---|---|
| `intent` | the instruction given to the agent, fully instantiated |
| `start_url` | always the home page; the agent must navigate |
| `eval.eval_types` | `string_match`, `url_match`, `program_html`, `db_state` |
| `eval.reference_answers.must_include` | substrings a correct answer contains |
| `eval.validator` | dotted path to a module exposing `validate()` |
| `eval.validator_args` | concrete arguments, resolved from seed data |
| `instantiation.rationale` | **why these values** — what makes the task non-degenerate |
| `runnable` | false while the service area is still being built |
| `blocked_by` | the routes a blocked task is waiting on |

`instantiation.rationale` is worth reading before writing new tasks. Each value
was chosen so the answer cannot be produced without using the site — task 7 uses
a booking whose fare *is* refundable but was sold through an agent, so an agent
that reads only the fare rules gets it wrong.

## Validators

```python
validate(db_session, final_url, page_html) -> (bool, str)
```

They query the database directly and never scrape for the state they assert.
Each one checks the intended change **and** that no unintended change occurred:
that no other booking picked up a request, that the segment itself was not
rewritten, and — for every purchase flow — that nothing anywhere is marked paid.

Prices are recomputed from the rules rather than compared to whatever the site
charged, so a pricing bug fails the task instead of being ratified by it.

`tests/test_validators.py` drives each one through a correct run *and* a
plausible near-miss, because a validator that has only seen correct runs is
untested in the direction that matters.

## Current coverage

20 of 30 tasks are runnable. The rest are emitted with `runnable: false` and the
routes they need listed in `blocked_by`; they become runnable as those service
areas are built, with no change to the task file.

## Reproducibility

Every task is deterministic against the frozen clock (16 March 2026) and the
seeded database, whose hash is byte-identical across runs. A reference number
issued during an episode is predictable: sequences restart from the seeded
high-water mark after each reset, so the same episode run twice produces the
same `MC-`, `RF-` or membership number.

## Is a task actually answerable, and is a pass meaningful?

Both are checked on every test run, for both languages, by
`tests/test_task_walkthroughs.py`.

For each of the thirty tasks it holds two files:

* `tests/task_solvers.py` -- a scripted **correct** run. It drives the site the
  way an agent does: follows the links the page offers, submits the site's own
  forms with the site's own field names, reads the answer off the page. Nothing
  in it touches the database, so a task the site cannot actually perform cannot
  be made to pass.
* `tests/task_near_misses.py` -- a scripted **plausible wrong** run. 20 kg where
  the task said 23. A window seat where it said aisle. The summary page instead
  of the one with the answer. One step short of the review page. The right kind
  of row on the wrong booking. The scorer must reject every one.

The second file is the one that matters. A validator that passes a correct run
proves nothing by itself -- one that returned `True` unconditionally would pass
too. The near-miss is what makes a pass mean something.

Running the first full pass of these found five tasks whose evaluation was
vacuous:

| Task | Why a wrong run passed |
|---|---|
| 4 | the timetable prints all seven days with a Yes/No column, so any list of day names matched the page |
| 9 | its reference answer was "Group booking", and the footer links to "Group bookings" from every page in the build |
| 23 | its reference answers were "48", "24" and "cannot", all three of which the special-meals page contains |
| 24 | the validator checked only that the seed data still supported the question, never what the agent did |
| 27 | (the near-miss was at fault, not the task -- the partner's unfiltered list legitimately shows the answer) |

Three fixes came out of that and are worth knowing about when you write a new
task:

* the scorer strips the header, nav and footer before matching, because nothing
  in the site chrome can be evidence that an agent found anything;
* a task whose page displays every option in full -- "which days does this route
  operate" -- sets `"answer_only": true` in its reference answers, and is scored
  on what the agent reported rather than on the page it opened;
* a validator must assert the agent's action, not only that the environment
  still supports the question.

Adding a task means adding a solver and a near-miss for it. A test refuses a
task that has neither, because such a task is one nobody has shown is answerable.
