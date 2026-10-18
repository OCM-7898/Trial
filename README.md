# LoWAgent

LoWAgent is a benchmark for web agents in low-resource languages. It contains **six
self-hosted websites in five languages** (English, Bengali, Hindi, Urdu and Amharic).
The language versions of a website share the same pages, data and tasks; only the
language changes, so differences in agent performance can be attributed to language.

| Website | Type | Text tasks | Visual tasks |
|---|---|---|---|
| Ministore | e-commerce store | 75 per language | 50 per language |
| Redora | discussion forum | 75 per language | 50 per language |
| GariBazaar | used-car marketplace | 75 per language | 50 per language |
| Haritia Portal | government services | 75 per language | – |
| RailSetu | rail reservations | 75 per language | – |
| Selam Airways | airline | 75 per language | – |

In total there are 2,250 text tasks and 750 visual tasks. The benchmark also includes
an **interface-disruption** setting and a fixed **train/test split** for post-training.

## Contents

- [Installation](#installation)
- [Checking the installation](#checking-the-installation)
- [Running models](#running-models)
- [Task types](#task-types)
- [GRPO training](#grpo-training)
- [Repository layout](#repository-layout)
- [Data and licenses](#data-and-licenses)

## Installation

Python 3.11 or newer is required.

```bash
pip install -r requirements.txt

# copy the product, car and forum images into the websites (run once)
python assets/abo/sync_images.py
python assets/gari_cars/sync_images.py
python sites/visual/sync_reddit_images.py
```

Additional requirements depend on what you run:

| To run | Install |
|---|---|
| Open-weight models | `vllm` |
| Gemini / OpenAI / Anthropic models | `google-genai` / `openai` / `anthropic`, and set `GEMINI_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` |
| Visual tasks | headless Chrome (`chrome-headless-shell` or Chrome/Chromium on `PATH`, or `MWA_CHROME=/path/to/chrome`), and fonts for Bengali, Devanagari, Urdu and Ethiopic (e.g. Noto Sans Bengali / Devanagari / Ethiopic, Noto Nastaliq Urdu) |
| GRPO training | `verl` (tested with 0.10), `vllm`, `peft`, `transformers`, and GPUs |

## Checking the installation

Every task has a reference solution. Replaying it must score 100%:

```bash
python -m benchmark.run_benchmark --agent scripted --lang railbn --autostart
python -m benchmark.screenshot.run_screenshot_benchmark --agent scripted --site gari --lang ur --autostart
```

Text tasks are grouped into **suites**, one per website and language. A suite name is
the website prefix plus the language code (none for English):

| Website | Suite names |
|---|---|
| Haritia Portal | `portal`, `portalbn`, `portalhi`, `portalur`, `portalam` |
| Selam Airways | `selam`, `selambn`, ... |
| RailSetu | `rail`, `railbn`, ... |
| Ministore | `visual`, `visualbn`, ... |
| GariBazaar | `visualgari`, `visualgaribn`, ... |
| Redora | `visualreddit`, `visualredditbn`, ... |

`--autostart` starts the website for the run. To start a website yourself, run
`python -m launch.sites <site> <lang>`, e.g. `python -m launch.sites rail bn`
(sites: `portal`, `selam`, `rail`, `ministore`, `gari`, `reddit`).

## Running models

Run the scripts from the repository root. Each script runs all websites and languages
unless you narrow it down with `SITES` and `LANGS`.

```bash
# open-weight model, served with vLLM on this machine
MODEL=meta-llama/Llama-3.1-8B-Instruct scripts/run_local.sh

# API models
AGENT=gemini MWA_THINK_BUDGET=0 scripts/run_api.sh
AGENT=openai MWA_OPENAI_MODEL=gpt-5.6-luna MWA_REASONING_EFFORT=none scripts/run_api.sh

# with interface disruptions
MODEL=meta-llama/Llama-3.1-8B-Instruct POPUPS=1 scripts/run_local.sh

# visual tasks
MODEL=google/gemma-3-27b-it scripts/run_visual.sh
AGENT=gemini MWA_THINK_BUDGET=0 scripts/run_visual.sh

# a quick trial: the first 3 tasks of each suite
MODEL=meta-llama/Llama-3.1-8B-Instruct LIMIT=3 SITES=rail LANGS="en bn" scripts/run_local.sh
```

### Options

All options are environment variables.

| Option | Scripts | Meaning |
|---|---|---|
| `MODEL` | `run_local`, `run_visual` | Hugging Face model id or local path (served with vLLM) |
| `AGENT` | `run_api`, `run_visual` | `gemini`, `openai` or `llm` (Anthropic); `run_visual` also accepts `local` (default) |
| `SITES` | all run scripts | websites to run, e.g. `"gari reddit"` |
| `LANGS` | all run scripts | languages to run, e.g. `"en am"` |
| `LIMIT` | all run scripts | run only the first N tasks per suite (logs go to `trial/`) |
| `POPUPS=1` | `run_local`, `run_api` | enable interface disruptions |
| `TAG` | all run scripts | name of the results folder (default: the model name) |
| `LANES` | `run_api` | websites run in parallel (default 6; lower it if rate-limited) |
| `TP`, `PORT`, `MAX_LEN`, `GPU_UTIL`, `VLLM_ARGS` | `run_local`, `run_visual` | vLLM tensor-parallel GPUs (1), port (8000), context length (131072), GPU memory share (0.90), extra arguments |
| `STRICT=1` | `run_local` | parse only the first line of the reply (ablation) |
| `MWA_GEMINI_MODEL`, `MWA_OPENAI_MODEL`, `MWA_ANTHROPIC_MODEL` | API runs | model id |
| `MWA_THINK_BUDGET`, `MWA_REASONING_EFFORT` | API runs | thinking budget (Gemini; mapped to effort levels for OpenAI) / OpenAI reasoning effort |
| `MWA_MAX_TOKENS` | all agents | output tokens per step (default 4096) |

### Results

Logs are written to `results/<model>/<site>/<lang>.log` (visual tasks:
`results/screenshot/<model>/<site>/<lang>.log`). Each log has one `[PASS]` or `[FAIL]`
line per task with the actions taken, followed by a `Score:` line and, for API models,
the token usage. Runs with interface disruptions also write `<lang>.popups.jsonl`,
recording how each disruption was handled.

### Fixed settings

Every model sees the same system prompt, the last four observation-action turns as
history, page text truncated to 4,000 characters, and at most 4,096 output tokens per
step. Each task has its own step limit (30 or 40). Do not run two runs against the same
website on one machine at the same time: each website uses fixed ports.

## Task types

- **Text tasks** (all six websites): information lookups, multi-step transactions
  (checkouts, bookings, posts and form submissions), and traps whose correct answer is
  `N/A`. Task N is the same task in every language. Tasks are scored on the outcome:
  the database state after the episode or the final answer.
- **Visual tasks** (Ministore, Redora, GariBazaar): the task gives a reference photo,
  and the agent must find the pictured item on the website before answering a question
  about it or acting on it. Each step, the agent sees the text page together with a
  screenshot of the full page, in which every link and form carries the same number as
  in the text. The actions are the same as for text tasks.
- **Interface disruptions** (`POPUPS=1`): the websites show a full-page cookie notice
  on arrival, then an app-install advertisement on the next page. Accepting the offer
  ends the task as a failure; each task gets two extra steps.

The agent's actions are `goto <path>`, `click <link>`, `fill <form> name=value; ...`
and `stop <answer>`.

## GRPO training

```bash
# 1. training data: replay the train tasks (15 per website, all languages)
scripts/build_grpo_data.sh

# 2. train with verl + LoRA
MODEL=/path/to/Llama-3.1-8B-Instruct scripts/train_grpo.sh

# 3. merge the LoRA adapter into a servable model (here: epoch 3)
CKPT=checkpoints/llama-3.1-8b-instruct_grpo/global_step_87 \
BASE=/path/to/Llama-3.1-8B-Instruct OUT=models/llama8b_grpo scripts/export_grpo.sh

# 4. evaluate
MODEL=models/llama8b_grpo scripts/run_local.sh
```

Each training example is one step of a reference solution: the agent's prompt at that
step and the reference action. The reward (`grpo/reward.py`) is 1 if a sampled action
has the same effect as the reference action (same page, same form values, or an answer
the evaluator accepts) and 0 otherwise. `train_grpo.sh` uses the settings from the paper
(LoRA rank 32, learning rate 1e-5, 64 states and 8 samples per update, 5 epochs). It
accepts `NAME`, `OUT_ROOT`, `NGPU`, `EPOCHS`, `BATCH`, `GROUP`, `LR`, `LORA_RANK`,
`MAX_PROMPT`, `SAVE_FREQ` and `EXTRA` (more verl overrides).

The split is in `tasks/train_test_split.json`. Evaluation runs all 75 tasks per website;
report the 60 test tasks (each log line includes the task id), for the base model as well.

## Repository layout

```
agents/      agents: scripted, local (vLLM), API, and screenshot agents (vision/)
assets/      product, car and forum images, copied into the websites by the sync scripts
benchmark/   text browser, evaluator, runner, interface disruptions, screenshot/ (visual tasks)
grpo/        GRPO training data, verl data format and reward
launch/      sites.py: starts any website in any language
scripts/     run, training and export scripts
sites/       the six websites
tasks/       text tasks per website and language, image/ (visual tasks), train_test_split.json
```

## Data and licenses

Product images come from the [Amazon Berkeley Objects](https://amazon-berkeley-objects.s3.amazonaws.com/index.html)
dataset (CC BY 4.0; see `assets/abo/LICENSE-CC-BY-4.0.txt`, with per-image attribution
in `sites/visual/ATTRIBUTIONS.csv` and `assets/trap_photos/ATTRIBUTIONS.csv`). Car
images come from a dataset of car photographs collected for this work. All other
website content (listings, posts, schedules and records) is generated and fictional.
