import argparse
import json
import statistics
import sys

from benchmark.env import BrowserEnv
from benchmark.run_benchmark import load_tasks
from launch.sites import site_urls

SUITES = {suite: (site_urls(suite), f"tasks/{root}/en/*.json") for suite, root in (
    ("portal", "text_only/portal"), ("selam", "text_only/selam"), ("rail", "text_only/rail"),
    ("visual", "visual/ministore"), ("visualgari", "visual/gari"), ("visualreddit", "visual/reddit"))}

SYSTEM_TOKENS_TEXT = """You are a web agent completing tasks on simple websites.
You will be given a TASK and an OBSERVATION of the current page
(text, numbered links, numbered forms). Reply with EXACTLY ONE action:

goto <path>                       e.g. goto /login
click <link_index>                e.g. click 3
fill <form_index> k=v; k=v        fills the form's fields then submits it
stop <answer>                     finish; include the answer if asked for one

Credentials for this site if login is needed: username=agent_smith password=password123
Think silently; output only the single action line, nothing else."""
WINDOW_EXCHANGES = 4
PER_MESSAGE_OVERHEAD = 8


def make_counter():
    try:
        import tiktoken
        enc = tiktoken.get_encoding("o200k_base")
        return (lambda s: len(enc.encode(s))), "tiktoken o200k_base"
    except ImportError:
        return (lambda s: (len(s) + 3) // 4), "chars/4 heuristic"


def episode_tokens(count, sys_tok, prompts, actions, n_calls):
    mean_p = statistics.mean(prompts)
    mean_a = statistics.mean(actions)
    p = lambda i: prompts[i] if i < len(prompts) else mean_p
    a = lambda i: actions[i] if i < len(actions) else mean_a
    tin = tout = 0
    for i in range(n_calls):
        window = range(max(0, i - WINDOW_EXCHANGES), i)
        tin += sys_tok + PER_MESSAGE_OVERHEAD + p(i)
        for j in window:
            tin += p(j) + a(j) + 2 * PER_MESSAGE_OVERHEAD
        tout += a(i)
    return int(round(tin)), int(round(tout))


def measure_suite(lang, count):
    site_urls, pattern = SUITES[lang]
    tasks = load_tasks([pattern])
    sys_tok = count(SYSTEM_TOKENS_TEXT)
    rows = []
    for t in tasks:
        env = BrowserEnv(site_urls[t["site"]])
        obs = env.reset(t.get("start_path", "/"))
        prompts, actions = [], []
        for act in t["solution"]:
            prompt = (f"TASK: {t['intent']}\n\nOBSERVATION:\n"
                      f"{obs.render()}\n\nYour single action line:")
            prompts.append(count(prompt))
            actions.append(count(act))
            try:
                nxt, done, _ = env.step(act)
            except Exception:
                continue
            if done:
                break
            obs = nxt
        n_min = len(prompts)
        n_max = t.get("max_steps", 15)
        rows.append((episode_tokens(count, sys_tok, prompts, actions,
                                    n_min),
                     episode_tokens(count, sys_tok, prompts, actions,
                                    n_max),
                     n_min, n_max))
    lo_in = sum(r[0][0] for r in rows)
    lo_out = sum(r[0][1] for r in rows)
    hi_in = sum(r[1][0] for r in rows)
    hi_out = sum(r[1][1] for r in rows)
    lo_calls = sum(r[2] for r in rows)
    hi_calls = sum(r[3] for r in rows)
    return dict(tasks=len(tasks), lo_in=lo_in, lo_out=lo_out,
                hi_in=hi_in, hi_out=hi_out,
                mid_in=(lo_in + hi_in) // 2,
                mid_out=(lo_out + hi_out) // 2,
                lo_calls=lo_calls, hi_calls=hi_calls,
                mid_calls=(lo_calls + hi_calls) // 2)


def fmt(n):
    return f"{n:,}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="all",
                    choices=["all"] + list(SUITES))
    ap.add_argument("--price-in", type=float, default=None,
                    help="$ per 1M input tokens (optional)")
    ap.add_argument("--price-out", type=float, default=None,
                    help="$ per 1M output tokens (optional)")
    ap.add_argument("--think-tokens", type=int, default=0,
                    help="assumed hidden reasoning tokens billed as "
                         "output PER API CALL (0 for non-thinking "
                         "models; try 500-2000 for reasoning models)")
    args = ap.parse_args()
    count, enc_name = make_counter()
    print(f"tokenizer: {enc_name}; window: last {WINDOW_EXCHANGES} "
          "exchanges + current (all LLM agents)")
    print(f"output = visible action lines + {args.think_tokens} "
          "thinking tokens/call (--think-tokens)\n")

    langs = list(SUITES) if args.lang == "all" else [args.lang]
    tot = dict(mid_in=0, mid_out=0, lo_in=0, hi_in=0, lo_out=0,
               hi_out=0, lo_calls=0, hi_calls=0, mid_calls=0)
    hdr = (f"{'suite':<13}{'tasks':>6}{'in (min)':>12}"
           f"{'in (realistic)':>16}{'in (worst)':>13}"
           f"{'calls (real)':>13}{'out (real)':>12}{'out (worst)':>13}")
    print(hdr)
    print("-" * len(hdr))

    def out_est(m, level):
        return m[f"{level}_out"] + args.think_tokens * m[f"{level}_calls"]

    for lang in langs:
        try:
            m = measure_suite(lang, count)
        except Exception as e:
            print(f"{lang:<13}  SKIPPED ({str(e)[:60]} — site running?)")
            continue
        for k in tot:
            tot[k] += m[k]
        print(f"{lang:<13}{m['tasks']:>6}{fmt(m['lo_in']):>12}"
              f"{fmt(m['mid_in']):>16}{fmt(m['hi_in']):>13}"
              f"{fmt(m['mid_calls']):>13}{fmt(out_est(m, 'mid')):>12}"
              f"{fmt(out_est(m, 'hi')):>13}")
    if len(langs) > 1:
        print("-" * len(hdr))
        print(f"{'TOTAL':<13}{'':>6}{fmt(tot['lo_in']):>12}"
              f"{fmt(tot['mid_in']):>16}{fmt(tot['hi_in']):>13}"
              f"{fmt(tot['mid_calls']):>13}"
              f"{fmt(out_est(tot, 'mid')):>12}"
              f"{fmt(out_est(tot, 'hi')):>13}")
    if args.price_in is not None and args.price_out is not None:
        cost = (tot["mid_in"] * args.price_in
                + out_est(tot, "mid") * args.price_out) / 1e6
        worst = (tot["hi_in"] * args.price_in
                 + out_est(tot, "hi") * args.price_out) / 1e6
        print(f"\ncost @ ${args.price_in}/M in, ${args.price_out}/M "
              f"out, {args.think_tokens} think/call: "
              f"realistic ${cost:,.2f} · worst ${worst:,.2f}")


if __name__ == "__main__":
    main()
