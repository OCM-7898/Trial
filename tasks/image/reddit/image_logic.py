import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "sites", "visual"))
sys.path.insert(0, os.path.join(ROOT, "tasks", "visual", "reddit"))
sys.path.insert(0, HERE)

from build_reddit_content import load_pack
from reddit_i18n import I18N
from image_i18n import COMMENT, QUOTE, SEP, TPL

LANGS = ["en", "bn", "hi", "ur", "am"]
POST_IMG = "sites/visual/reddit/static/post_images/{}_1.jpg"
DEMO_IMG = "assets/trap_photos/p{}.jpg"
LOGIN = ["goto /login", "fill 0 username=agent_smith; password=password123"]
FORUM = "whatisthisthing"
DIGITS = {"bn": "০১২৩৪৫৬৭৮৯", "hi": "०१२३४५६७८९", "ur": "۰۱۲۳۴۵۶۷۸۹"}
URDU_ALT = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "٠١٢٣٤٥٦٧٨٩")


def build(lang):
    plan = json.load(open(os.path.join(HERE, "draft_plan.json"), encoding="utf-8"))
    C = json.load(open(os.path.join(ROOT, "sites/visual/reddit",
                                    "content.json" if lang == "en" else f"content_{lang}.json"), encoding="utf-8"))
    posts = {p["id"]: p for p in C["posts"]}
    first = {}
    for c in sorted(C["comments"], key=lambda c: c["id"]):
        if c["parent_id"] is None:
            first.setdefault(c["post_id"], c)
    pre, suf = load_pack(lang)["WITT_ID"].split("{name}")
    q0, q1 = QUOTE[lang]
    cred = " " + I18N[lang]["cred"]
    forum = f"f/{FORUM}"
    nd = str.maketrans("0123456789", DIGITS[lang]) if lang in DIGITS else None

    def nums(n):
        out = [str(n)] + ([str(n).translate(nd)] if nd else [])
        if lang == "ur":
            out.append(str(n).translate(nd).translate(URDU_ALT))
        if n < 0:
            out += [v.replace("-", "−") for v in out]
        return list(dict.fromkeys(out))

    def witt_name(pid):
        b = first[pid]["body"]
        assert b.startswith(pre) and b.endswith(suf), (lang, pid, b)
        return b[len(pre):len(b) - len(suf)]

    def title(pid):
        return f"{q0}{posts[pid]['title']}{q1}"

    T = []
    for t in plan:
        n, kind, tgt = t["n"], t["kind"], t["target"]
        cands = [c["id"] for c in t["candidates"]]
        others = [c for c in cands if c != tgt]
        login = False
        if kind.startswith("W") or kind == "T_not_posted":
            visit = [f"goto /f/{FORUM}"] + ([f"goto /post/{tgt}"] if tgt else [])
        else:
            visit = [f"goto /post/{c}" for c in cands] + [f"goto /post/{tgt}"]
        cand_str = SEP[lang].join(title(c) for c in cands)
        fmt = dict(forum=forum, cands=cand_str, c=COMMENT[lang])
        intent = TPL[lang][kind].format(**fmt)
        if kind == "W1_what":
            ev = [{"type": "answer_match", "mode": "contains", "any_of": [witt_name(tgt)]}]
            sol = visit + [f"stop {witt_name(tgt)}"]
        elif kind in ("W2_save", "C2_save"):
            login = True
            ev = ([{"type": "db_record_exists", "table": "saved", "match": {"user_id": 1, "post_id": tgt}}] +
                  [{"type": "db_record_absent", "table": "saved", "match": {"user_id": 1, "post_id": o}}
                   for o in (others if kind == "C2_save" else [])])
            sol = LOGIN + visit + ["fill 2"]
        elif kind in ("W3_author", "C4_author"):
            a = posts[tgt]["author"]
            ev = [{"type": "answer_match", "mode": "contains", "any_of": [a],
                   "none_of": sorted({posts[o]["author"] for o in others} - {a})
                   if kind == "C4_author" else []}]
            sol = visit + [f"stop {a}"]
        elif kind in ("W4_score", "C1_score"):
            s = posts[tgt]["score"]
            ev = [{"type": "answer_match", "mode": "contains", "any_of": nums(s),
                   "none_of": [v for o in (others if kind == "C1_score" else []) for v in nums(posts[o]["score"])]}]
            sol = visit + [f"stop {s}"]
        elif kind == "C3_comment":
            login = True
            ev = ([{"type": "db_record_exists", "table": "comments",
                    "match": {"post_id": tgt, "author_id": 1, "body": COMMENT[lang]}}] +
                  [{"type": "db_record_absent", "table": "comments",
                    "match": {"post_id": o, "author_id": 1, "body": COMMENT[lang]}} for o in others])
            sol = LOGIN + visit + [f"fill 3 body={COMMENT[lang]}"]
        elif kind == "T_not_posted":
            ev = [{"type": "answer_match", "mode": "contains", "any_of": ["N/A"]}]
            sol = visit + ["stop N/A"]
        else:
            raise SystemExit(f"unknown kind {kind}")
        image = DEMO_IMG.format(t["demo_id"]) if kind == "T_not_posted" else POST_IMG.format(tgt)
        assert os.path.exists(os.path.join(ROOT, image)), image
        if tgt:
            assert not posts[tgt]["locked"], tgt
        T.append({"id": f"image-reddit-{n:03d}", "site": "reddit", "kind": kind,
                  "intent": intent + (cred if login else ""),
                  "image": image, "start_path": "/", "eval": ev, "solution": sol,
                  "max_steps": max(30, len(sol) + 15)})
    assert len(T) == 50
    return T


def write(lang):
    out_dir = os.path.join(HERE, lang)
    os.makedirs(out_dir, exist_ok=True)
    T = build(lang)
    path = os.path.join(out_dir, "image_tasks.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(T, f, indent=1, ensure_ascii=False)
    print(f"wrote {len(T)} tasks to {path}")


if __name__ == "__main__":
    for lang in (sys.argv[1:] or LANGS):
        write(lang)
