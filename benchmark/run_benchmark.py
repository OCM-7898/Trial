import argparse
import sys
import glob
import json
import time

from benchmark.env import BrowserEnv
from benchmark.evaluator import evaluate
from benchmark.popup_env import PopupEnv
from benchmark.popup_text import ORDER as POPUP_ORDER, REVIEWED
from launch.sites import site_urls as suite_urls, start_suite

POPUP_EXTRA_STEPS = len(POPUP_ORDER)
POPUP_OUTCOMES = ("dismissed", "took_offer", "stopped_on_popup",
                  "timed_out_on_popup", "never_shown")


def suite_lang(suite):
    for prefix in ("visualreddit", "visualgari", "visual", "portal", "selam", "rail"):
        if suite.startswith(prefix):
            return suite[len(prefix):] or "en"
    raise SystemExit(f"unknown suite {suite!r}")



def load_tasks(patterns):
    tasks = []
    for pat in patterns:
        for path in sorted(glob.glob(pat)):
            with open(path) as f:
                tasks.extend(json.load(f))
    return tasks


def make_agent(name):
    if name == "scripted":
        from agents.scripted_agent import ScriptedAgent
        return ScriptedAgent()
    if name == "llm":
        from agents.llm_agent import LLMAgent
        return LLMAgent()
    if name == "openai":
        from agents.openai_agent import OpenAIAgent
        return OpenAIAgent()
    if name == "gemini":
        from agents.gemini_agent import GeminiAgent
        return GeminiAgent()
    if name == "local":
        from agents.local_agent import LocalAgent
        return LocalAgent()
    raise SystemExit(f"Unknown agent: {name}")


def run_task(agent, task, max_steps=15, site_urls=None,
             trace=False, popups=False, popup_lang="en"):
    max_steps = task.get("max_steps", max_steps)
    site_urls = site_urls or suite_urls("visual")
    base_url = site_urls[task["site"]]
    if not popups:
        env = BrowserEnv(base_url)
    else:
        env = PopupEnv(base_url, lang=popup_lang)
        max_steps += POPUP_EXTRA_STEPS
    obs = env.reset(task.get("start_path", "/"))
    if not popups and "data-mwa-popup" in (env.last_html or ""):
        raise SystemExit("this site serves pop-ups (started with MWA_POPUPS=1) "
                         "but --popups is off: restart the sites without it")
    if popups and trace:
        print(f"       0. (arrival)  -> {env.current_url}  [POP-UP cookie showing]")
    agent.begin(task)

    final_answer = None
    for step_no in range(max_steps):
        action = agent.act(task, obs)
        before = getattr(env, "popup_active", None)
        try:
            obs, done, answer = env.step(action)
        except Exception as e:
            obs = obs
            agent.on_error(str(e))
            if trace:
                print(f"      {step_no + 1:>2}. {action[:160]}  !! {e}")
            continue
        if trace:
            where = "" if done else f"  -> {env.current_url}"
            if popups:
                now = env.popup_active
                if before and now is None:
                    where += {"dismissed": f"  [pop-up {before} dismissed]",
                              "took_offer": "  [took the offer: task ends as a FAIL]",
                              }.get(env.popup_log[before]["outcome"], "")
                elif before and done:
                    where += f"  [stopped on the {before} pop-up]"
                elif now and now != before:
                    where += f"  [POP-UP {now} showing]"
            print(f"      {step_no + 1:>2}. {action[:160]}{where}")
        if done:
            final_answer = answer
            break
    success, details = evaluate(task, base_url, final_answer,
                                final_url=env.current_url,
                                final_html=env.last_html)
    popup_log = None
    if popups:
        popup_log = {"task_id": task["id"], "lang": popup_lang,
                     **{name: dict(env.popup_log[name]) for name in POPUP_ORDER}}
        if env.offer_taken:
            success = False
        details = list(details) + [
            "popups: " + " · ".join(f"{name} {env.popup_log[name]['outcome']}"
                                    for name in POPUP_ORDER)]
    return success, details, popup_log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="scripted")
    ap.add_argument("--tasks", nargs="*", default=None,
                    help="task JSON globs; default: the suite of --lang")
    ap.add_argument("--max-steps", type=int, default=15)
    ap.add_argument("--limit", type=int, default=None,
                    help="run only the first N tasks (smoke tests)")
    ap.add_argument("--trace", action="store_true",
                    help="log every agent action (and the page it landed "
                         "on) under each task, for audits")
    ap.add_argument("--autostart", action="store_true",
                    help="start the Flask sites in this process")
    ap.add_argument("--popups", action="store_true",
                    help="RQ3 pop-up layer ON: a cookie notice on arrival, "
                         "then an app-install advertisement after the "
                         "agent's first page load (POPUPS_GUIDE.md)")
    ap.add_argument("--popup-log", default=None,
                    help="with --popups: write one JSON line per task here")
    ap.add_argument("--allow-unreviewed-popups", action="store_true",
                    help="PILOT ONLY: allow pop-up text that no native "
                         "speaker has signed off yet")
    ap.add_argument("--lang", choices=["portal", "portalbn", "portalhi",
                                        "portalur", "portalam", "selam", "selamam",
                                       "selambn", "selamhi", "selamur",
                                       "rail", "railbn", "railhi", "railur", "railam",
                                       "visual", "visualbn", "visualhi", "visualur", "visualam",
                                       "visualgari", "visualgaribn",
                                       "visualgarihi", "visualgariur",
                                       "visualgariam",
                                       "visualreddit", "visualredditbn",
                                       "visualreddithi", "visualredditur",
                                       "visualredditam"],
                    default="visual",
                    help="portal = government portal on :8015, "
                         "selam = airline on :8017, rail = "
                         "RailSetu on :8021, visual = ministore "
                         ":8031 / visualgari :8036 / visualreddit :8037")
    args = ap.parse_args()

    popup_lang, popup_logs = "en", []
    if args.popups:
        popup_lang = suite_lang(args.lang)
        if not REVIEWED.get(popup_lang) and not args.allow_unreviewed_popups:
            sys.exit(f"pop-up text for '{popup_lang}' has no native-speaker "
                     "sign-off (benchmark/popup_text.py REVIEWED); refusing "
                     "to run. Pilot only: --allow-unreviewed-popups")
        print(f"POP-UPS ON · language {popup_lang}"
              + ("" if REVIEWED.get(popup_lang) else " · UNREVIEWED TEXT (pilot)")
              + " · cookie on arrival, offer after the first page load", flush=True)

    site_urls = suite_urls(args.lang)
    T = "tasks/text_only"
    task_dirs = {"portal": f"{T}/portal/en",
                 "portalbn": f"{T}/portal/bn",
                 "portalhi": f"{T}/portal/hi",
                 "portalur": f"{T}/portal/ur",
                 "portalam": f"{T}/portal/am",
                 "selam": f"{T}/selam/en", "selamam": f"{T}/selam/am",
                 "selambn": f"{T}/selam/bn", "selamhi": f"{T}/selam/hi",
                 "selamur": f"{T}/selam/ur",
                 "rail": f"{T}/rail/en",
                 "railbn": f"{T}/rail/bn", "railhi": f"{T}/rail/hi",
                 "railur": f"{T}/rail/ur", "railam": f"{T}/rail/am",
                 "visual": "tasks/visual/ministore/en",
                 "visualbn": "tasks/visual/ministore/bn",
                 "visualhi": "tasks/visual/ministore/hi",
                 "visualur": "tasks/visual/ministore/ur",
                 "visualam": "tasks/visual/ministore/am",
                 "visualgari": "tasks/visual/gari/en",
                 "visualgaribn": "tasks/visual/gari/bn",
                 "visualgarihi": "tasks/visual/gari/hi",
                 "visualgariur": "tasks/visual/gari/ur",
                 "visualgariam": "tasks/visual/gari/am",
                 "visualreddit": "tasks/visual/reddit/en",
                 "visualredditbn": "tasks/visual/reddit/bn",
                 "visualreddithi": "tasks/visual/reddit/hi",
                 "visualredditur": "tasks/visual/reddit/ur",
                 "visualredditam": "tasks/visual/reddit/am"}
    if not args.tasks:
        args.tasks = [f"{task_dirs[args.lang]}/*.json"]

    if args.autostart:
        import os
        os.environ["MWA_POPUPS"] = "1" if args.popups else "0"
        start_suite(args.lang)
        time.sleep(0.5)

    from .leak_check import check_all
    if check_all(site_urls):
        sys.exit("LEAK CHECK FAILED: a harness back door is open — "
                 "see the lines above; no run was made")

    tasks = load_tasks(args.tasks)
    if args.limit:
        tasks = tasks[:args.limit]
    agent = make_agent(args.agent)

    n_ok = 0
    for task in tasks:
        ok, details, plog = run_task(agent, task, args.max_steps, site_urls,
                                     trace=args.trace, popups=args.popups,
                                     popup_lang=popup_lang)
        if plog is not None:
            popup_logs.append(dict(plog, passed=bool(ok)))
        n_ok += ok
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] ({task['site']}) {task['id']}: {task['intent']}")
        for d in details:
            print(f"        {d}")
    print(f"\nScore: {n_ok}/{len(tasks)} "
          f"({100.0 * n_ok / max(1, len(tasks)):.0f}%)")
    if args.popups:
        from collections import Counter
        parts = []
        for name in POPUP_ORDER:
            c = Counter(p[name]["outcome"] for p in popup_logs)
            parts.append(f"{name}: " + " · ".join(
                f"{o.replace('_', ' ')} {c[o]}" for o in POPUP_OUTCOMES
                if c[o] or o in ("dismissed",)))
        print("Pop-ups: " + " | ".join(parts))
        if args.popup_log:
            with open(args.popup_log, "w") as f:
                for p in popup_logs:
                    f.write(json.dumps(p, ensure_ascii=False) + "\n")
    u = getattr(agent, "usage", None)
    if u and u.get("calls"):
        print(f"API usage: {u['calls']:,} calls · input {u['in']:,} · "
              f"output {u['out']:,} · thinking {u['think']:,} tokens")
    if u and "rescues" in u:
        print(f"Format rescues: {u['rescues']:,} / {u['calls']:,} calls · "
              f"context trims: {u['trims']:,} · "
              f"empty replies: {u.get('empty', 0):,} "
              f"(of which malformed: {u.get('harmony', 0):,})")


if __name__ == "__main__":
    main()
