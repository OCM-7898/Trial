import argparse
import glob
import json
import os
import sys

import requests

from .env import BrowserEnv
from .evaluator import _contains
from .harness import headers as harness_headers
from .popup_env import PopupEnv
from .popup_site import FORWARDED
from .popup_text import POPUP_TEXT, check_packs

ROOTS = {"portal": "tasks/text_only/portal", "selam": "tasks/text_only/selam",
         "rail": "tasks/text_only/rail", "ministore": "tasks/visual/ministore",
         "gari": "tasks/visual/gari", "reddit": "tasks/visual/reddit"}


def load_suite_tasks(root, lang):
    tasks = []
    for p in sorted(glob.glob(f"{root}/{lang}/*.json")):
        tasks.extend(json.load(open(p, encoding="utf-8")))
    return tasks


def targets(task):
    for e in task["eval"]:
        if e["type"] == "answer_match":
            for x in (e.get("any_of") or [e.get("answer", "")]):
                if x:
                    yield str(x)


def static():
    check_packs()
    bad = []
    for root in ROOTS.values():
        for lang in POPUP_TEXT:
            strings = [s for p in POPUP_TEXT[lang].values()
                       for s in [p["message"]] + [l for _, l in p["links"]]]
            for t in load_suite_tasks(root, lang):
                for target in targets(t):
                    if any(_contains(target, s) for s in strings):
                        bad.append((t["id"], lang, target))
    assert not bad, f"pop-up text contains answer targets: {bad[:10]}"
    from flask import Flask
    from .harness import protect
    saved = os.environ.pop("MWA_POPUPS", None)
    try:
        app = Flask("off_check")
        before = len(app.before_request_funcs.get(None, []))
        after = len(app.after_request_funcs.get(None, []))
        protect(app)
        assert len(app.before_request_funcs.get(None, [])) == before + 1, "extra before hook"
        assert len(app.after_request_funcs.get(None, [])) == after, "pop-up hook installed while off"
    finally:
        if saved is not None:
            os.environ["MWA_POPUPS"] = saved
    print("static: packs OK · no answer collisions in any of the 30 suites · "
          "no pop-up hook when MWA_POPUPS is unset")


class Recording:
    def __init__(self, session):
        self.s, self.forwarded = session, None

    def __getattr__(self, name):
        attr = getattr(self.s, name)
        if name in ("get", "post", "request"):
            def wrapped(*a, **k):
                r = attr(*a, **k)
                if FORWARDED in r.headers:
                    self.forwarded = int(r.headers[FORWARDED])
                return r
            return wrapped
        return attr


class ReferenceEnv(BrowserEnv):
    def reset(self, start_path="/"):
        self.session = requests.Session()
        self.session.headers.update(harness_headers())
        self.session.post(self.base_url + "/__reset__", timeout=10)
        return self.goto(start_path)


def first_action(task):
    return next(a for a in task["solution"] if not a.startswith("stop"))


def popup_env(base, lang, start):
    env = PopupEnv(base, lang=lang)
    obs = env.reset(start)
    env.session = Recording(env.session)
    env.session.forwarded = None
    return env, obs


def live(suite):
    from launch.sites import parse_suite, url
    from .run_benchmark import run_task
    site, lang = parse_suite(suite)
    root, base = ROOTS[site], url(site, lang)
    tasks = load_suite_tasks(root, lang)
    fails, start_answers = [], []
    for t in tasks:
        tid, start, act = t["id"], t.get("start_path", "/"), first_action(t)
        ref = ReferenceEnv(base)
        want_start = ref.reset(start).render()
        if any(_contains(x, ref.reset(start).text) for x in targets(t)
               if x not in ("N/A", "NO_RECORD")):
            start_answers.append(tid)
        want_first = ref.step(act)[0].render()

        env, obs = popup_env(base, lang, start)
        env.step("goto /")
        n = env.session.forwarded
        if env.popup_active != "cookie":
            fails.append((tid, "P2 goto got past the cookie notice"))
        got = env.step(obs.popup["dismiss"])[0]
        if env.session.forwarded != n:
            fails.append((tid, "P2 the site ran a request again"))
        if got.render() != want_start:
            fails.append((tid, "P2 start page differs"))

        obs = env.step(act)[0]
        if env.popup_active != "offer":
            fails.append((tid, "P3 no offer after the first action"))
            continue
        n = env.session.forwarded
        env.step("goto /")
        if env.popup_active != "offer" or env.session.forwarded != n:
            fails.append((tid, "P3 goto got past the offer or reached the site"))
        got = env.step(obs.popup["dismiss"])[0]
        if env.session.forwarded != n:
            fails.append((tid, "P3 the site ran a request again"))
        if got.render() != want_first:
            fails.append((tid, "P3 page differs"))

        env, obs = popup_env(base, lang, start)
        env.step(obs.popup["dismiss"])
        env.step(act)
        n = env.session.forwarded
        _, done, _ = env.step("click 0")
        if not (done and env.offer_taken and env.session.forwarded == n
                and env.popup_log["offer"]["outcome"] == "took_offer"):
            fails.append((tid, "P4"))

    class TakeOffer:
        def begin(self, task): self.s = list(task["solution"])
        def act(self, task, obs):
            if getattr(obs, "popup", None):
                return "click 0"
            return self.s.pop(0) if self.s else "stop"
        def on_error(self, m): pass
    for t in tasks[:10]:
        ok, _, plog = run_task(TakeOffer(), t, 15, {site: base}, popups=True, popup_lang=lang)
        if ok or plog["offer"]["outcome"] != "took_offer":
            fails.append((t["id"], "P4 run_task"))

    t = tasks[0]
    env, _ = popup_env(base, lang, "/")
    env.step("stop x")
    if env.popup_log["cookie"]["outcome"] != "stopped_on_popup" or env.showing() != "cookie":
        fails.append((t["id"], "P5 cookie"))
    env, obs = popup_env(base, lang, "/")
    env.step(obs.popup["dismiss"]); env.step(first_action(t)); env.step("stop x")
    if env.popup_log["offer"]["outcome"] != "stopped_on_popup" or env.showing() != "offer":
        fails.append((t["id"], "P5 offer"))
    env, obs = popup_env(base, lang, "/")
    env.step(obs.popup["dismiss"]); env.step("stop N/A")
    if env.popup_log["offer"]["outcome"] != "never_shown":
        fails.append((t["id"], "P6"))

    print(f"live {suite}: {len(tasks)} tasks · " +
          ("ALL CHECKS PASSED" if not fails else f"FAILURES: {fails[:12]}"))
    print(f"P7 answer text on the start page: {len(start_answers)} task(s)"
          + (f" {start_answers}" if start_answers else ""))
    return not fails


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["static", "live"])
    ap.add_argument("--lang", default="rail")
    args = ap.parse_args()
    if args.mode == "static":
        static()
    else:
        sys.exit(0 if live(args.lang) else 1)
