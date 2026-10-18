import argparse
import json
import os
import sys
import time

from agents.base import credentials_line
from agents.local_agent import SYSTEM
from benchmark.env import BrowserEnv
from launch.sites import parse_suite, start, url

SPLIT = "tasks/train_test_split.json"
ROOTS = {"portal": "tasks/text_only/portal", "selam": "tasks/text_only/selam",
         "rail": "tasks/text_only/rail", "ministore": "tasks/visual/ministore",
         "gari": "tasks/visual/gari", "reddit": "tasks/visual/reddit"}


def user_turn(task, obs, err=None):
    head = (f"That action failed: {err}. Choose a different valid action.\n\n" if err else "")
    return (head + f"TASK: {task['intent']}\n\nOBSERVATION:\n{obs.render()}\n\n"
            "Your single action line:")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True, help="suite, e.g. rail, railbn, visualgariam")
    args = ap.parse_args()
    suite = args.lang
    site, lang = parse_suite(suite)
    root = ROOTS[site]

    os.environ.pop("MWA_POPUPS", None)
    start(site, lang)
    time.sleep(1.0)
    base = url(site, lang)

    split = json.load(open(SPLIT))
    train_ids, types = set(split["train"][site]), split["types"][site]
    import glob
    tasks = [t for p in sorted(glob.glob(f"{root}/{lang}/*.json"))
             for t in json.load(open(p, encoding="utf-8")) if t["id"] in train_ids]
    assert len(tasks) == len(train_ids), (suite, len(tasks))

    os.makedirs("grpo/data/steps", exist_ok=True)
    out = open(f"grpo/data/steps/{suite}.jsonl", "w", encoding="utf-8")
    n_steps = n_fail = 0
    for task in tasks:
        system = SYSTEM.replace("{credentials}", credentials_line(task))
        env = BrowserEnv(base)
        obs = env.reset(task.get("start_path", "/"))
        history = []
        solution = list(task["solution"])
        if not solution or not solution[-1].startswith("stop"):
            solution.append("stop")
        for k, act in enumerate(solution):
            user = user_turn(task, obs)
            rec = {"task_id": task["id"], "site": site, "lang": lang, "suite": suite,
                   "step": k, "n_steps": len(solution), "type": types[task["id"]],
                   "messages": [{"role": "system", "content": system}] + history[-8:] +
                               [{"role": "user", "content": user}],
                   "reference": act,
                   "url": obs.url,
                   "links": {str(i): href for i, _, href in obs.links},
                   "forms": {str(i): fields for i, _, _, fields in obs.forms}}
            if act.startswith("stop"):
                rec["answer_checks"] = [e for e in task["eval"] if e["type"] == "answer_match"]
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_steps += 1
            if act.startswith("stop"):
                break
            try:
                obs, _, _ = env.step(act)
            except Exception as e:
                print(f"  !! {task['id']} step {k} {act!r}: {e}", flush=True)
                n_fail += 1
                break
            history += [{"role": "user", "content": user}, {"role": "assistant", "content": act}]
            history = history[-8:]
    out.close()
    print(f"{suite}: {len(tasks)} tasks · {n_steps} steps · {n_fail} replay errors", flush=True)
    os._exit(0)


if __name__ == "__main__":
    main()
