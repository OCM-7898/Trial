import glob
import json
import os
import random
import sys
from collections import Counter

SEED = 20261005
N_TRAIN = 15
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "train_test_split.json")
SITES = {"portal": "text_only/portal", "rail": "text_only/rail", "selam": "text_only/selam",
         "ministore": "visual/ministore", "gari": "visual/gari", "reddit": "visual/reddit"}
LANGS = ("en", "bn", "hi", "ur", "am")
STATE = {"db_record_exists", "db_field_equals", "selam_score", "order_contains", "db_reply_to"}
TRAP = {"N/A", "NO_RECORD"}


def load(site, lang):
    return [t for p in sorted(glob.glob(os.path.join(HERE, SITES[site], lang, "*.json")))
            for t in json.load(open(p, encoding="utf-8"))]


def task_type(t):
    answers = [str(x) for e in t["eval"] if e["type"] == "answer_match"
               for x in (e.get("any_of") or []) + ([e["answer"]] if "answer" in e else [])]
    if any(a in TRAP for a in answers):
        return "N/A trap"
    if {e["type"] for e in t["eval"]} & STATE:
        return "state-changing"
    return "information-seeking"


def quotas(counts):
    total = sum(counts.values())
    raw = {k: N_TRAIN * v / total for k, v in counts.items()}
    q = {k: int(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: raw[k] - q[k], reverse=True)[:N_TRAIN - sum(q.values())]:
        q[k] += 1
    return q


def split():
    rng = random.Random(SEED)
    out = {"seed": SEED, "rule": "Freeze the train/test split of the 75 tasks of every site (2026-10-05).", "train": {}, "test": {}, "types": {}}
    for site in SITES:
        tasks = load(site, "en")
        ids = [t["id"] for t in tasks]
        for lang in LANGS[1:]:
            assert [t["id"] for t in load(site, lang)] == ids, (site, lang)
        by_type = {}
        for t in tasks:
            by_type.setdefault(task_type(t), []).append(t["id"])
        q = quotas({k: len(v) for k, v in by_type.items()})
        train = []
        for k in sorted(by_type):
            pool = sorted(by_type[k])
            rng.shuffle(pool)
            train += pool[:q[k]]
        out["train"][site] = sorted(train)
        out["test"][site] = sorted(set(ids) - set(train))
        out["types"][site] = {tid: task_type(t) for tid, t in ((t["id"], t) for t in tasks)}
    return out


def summary(s):
    lines = []
    for site in SITES:
        types = s["types"][site]
        tr = Counter(types[i] for i in s["train"][site])
        te = Counter(types[i] for i in s["test"][site])
        lines.append(f"{site:10s} train {len(s['train'][site])} / test {len(s['test'][site])}   " +
                     "  ".join(f"{k}: {tr[k]}+{te[k]}" for k in ("information-seeking", "state-changing", "N/A trap")))
    return "\n".join(lines)


if __name__ == "__main__":
    s = split()
    if "--check" in sys.argv:
        assert json.load(open(OUT))["train"] == s["train"], "train_test_split.json differs from the seeded split"
        print("train_test_split.json matches the seeded split")
    else:
        json.dump(s, open(OUT, "w"), indent=1)
        print(f"wrote {OUT}")
    print("(type: train+test)")
    print(summary(s))
