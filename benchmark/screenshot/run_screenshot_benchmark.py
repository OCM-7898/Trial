import argparse
import glob
import json
import sys
import time

from launch.sites import LANGS, start, url
from benchmark.evaluator import evaluate
from benchmark.screenshot.env import ScreenshotBrowserEnv

SUITES = [(site, lang) for site in ("ministore", "gari", "reddit") for lang in LANGS]


def make_agent(name):
    if name == "scripted":
        from agents.scripted_agent import ScriptedAgent
        return ScriptedAgent()
    if name == "local-screenshot":
        from agents.vision.screenshot_agent import ScreenshotAgent
        return ScreenshotAgent()
    if name == "gemini-screenshot":
        from agents.vision.api_screenshot import GeminiScreenshotAgent
        return GeminiScreenshotAgent()
    if name == "openai-screenshot":
        from agents.vision.api_screenshot import OpenAIScreenshotAgent
        return OpenAIScreenshotAgent()
    raise SystemExit(f"Unknown screenshot agent: {name} "
                     "(scripted | local-screenshot | gemini-screenshot | openai-screenshot)")


def run_task(agent, task, site_urls, trace=False):
    base_url = site_urls[task["site"]]
    env = ScreenshotBrowserEnv(base_url)
    obs = env.reset(task.get("start_path", "/"))
    agent.begin(task)
    final_answer = None
    for step_no in range(task.get("max_steps", 30)):
        action = agent.act(task, obs)
        try:
            obs, done, answer = env.step(action)
        except Exception as e:
            agent.on_error(str(e))
            if trace:
                print(f"      {step_no + 1:>2}. {action[:160]}  !! {e}")
            continue
        if trace:
            print(f"      {step_no + 1:>2}. {action[:160]}{'' if done else '  -> ' + env.current_url}")
        if done:
            final_answer = answer
            break
    return evaluate(task, base_url, final_answer, final_url=env.current_url,
                    final_html=env.last_html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="scripted")
    ap.add_argument("--site", default="ministore", choices=sorted({s for s, _ in SUITES}))
    ap.add_argument("--lang", default="en", choices=["en", "bn", "hi", "ur", "am"])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--autostart", action="store_true")
    args = ap.parse_args()

    site_urls = {args.site: url(args.site, args.lang)}
    if args.autostart:
        start(args.site, args.lang)
        time.sleep(0.5)
    from benchmark.leak_check import check_all
    if check_all(site_urls):
        sys.exit("LEAK CHECK FAILED: a harness back door is open — no run was made")

    tasks = []
    for p in sorted(glob.glob(f"tasks/image/{args.site}/{args.lang}/*.json")):
        tasks.extend(json.load(open(p, encoding="utf-8")))
    if args.limit:
        tasks = tasks[:args.limit]
    agent = make_agent(args.agent)
    n_ok = 0
    for task in tasks:
        ok, details = run_task(agent, task, site_urls, trace=args.trace)
        n_ok += ok
        print(f"[{'PASS' if ok else 'FAIL'}] ({task['site']}/{task['kind']}) {task['id']}: {task['intent']}")
        for d in details:
            print(f"        {d}")
    print(f"\nScore: {n_ok}/{len(tasks)} ({100.0 * n_ok / max(1, len(tasks)):.0f}%)")
    print(f"Screenshot failures: {ScreenshotBrowserEnv.render_failures}")
    u = getattr(agent, "usage", None)
    if u and u.get("calls"):
        print(f"API usage: {u['calls']:,} calls · input {u['in']:,} · output {u['out']:,} · "
              f"thinking {u['think']:,} tokens")
        if "rescues" in u:
            print(f"Format rescues: {u['rescues']:,} / {u['calls']:,} calls · context trims: "
                  f"{u['trims']:,} · empty replies: {u.get('empty', 0):,} "
                  f"(of which malformed: {u.get('harmony', 0):,})")


if __name__ == "__main__":
    main()
