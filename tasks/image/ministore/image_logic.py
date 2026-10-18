import collections
import json
import os
import sys
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "sites"))
sys.path.insert(0, os.path.join(ROOT, "tasks", "visual", "ministore"))
sys.path.insert(0, HERE)

import visual_logic as V
from visual.ministore.seed import build_rows, load_catalog
from visual.ministore.strings import LANG_META
from image_i18n import QUOTE, SEP, TPL

LANGS = ["en", "bn", "hi", "ur", "am"]
SHOP_IMG = "sites/visual/ministore/static/img/products/p{}.jpg"
DEMO_IMG = "assets/trap_photos/p{}.jpg"


def build(lang):
    plan = json.load(open(os.path.join(HERE, "draft_plan.json"), encoding="utf-8"))
    loc = {c["id"]: c for c in load_catalog(lang)}
    _, _, _, reviews, _, _, _, _ = build_rows(lang)
    nrev = collections.Counter(r[1] for r in reviews)
    nd = V.NATIVE_DIGITS.get(lang)
    A = [a.translate(nd) if nd else a for a in V.ADDR[lang]]
    q0, q1 = QUOTE[lang]
    one = "1".translate(nd) if nd else "1"
    na = ["N/A"] + list(V.I18N[lang]["na_alts"]["product"])

    def nums(x):
        s = str(x)
        out = [s]
        digits = s.replace(".", "")
        if digits.isdigit() and len(s.split(".")[0]) > 3:
            whole, _, frac = s.partition(".")
            out.append(f"{int(whole):,}" + ("." + frac if frac else ""))
        if nd:
            out += [v.translate(nd) for v in list(out)]
            if lang in V.EXTRA_DIGITS:
                out += [v.translate(V.EXTRA_DIGITS[lang]) for v in out[:2]]
        return list(dict.fromkeys(out))

    def name(pid):
        return loc[pid]["name"]

    def price(pid):
        return V.money(loc[pid]["price"])

    def quoted(pid):
        return f"{q0}{name(pid)}{q1}"

    T = []
    for t in plan:
        n, kind = t["n"], t["kind"]
        cands = [c["id"] for c in t["candidates"]]
        tgt = t["target"]
        others = [c for c in cands if c != tgt]
        cand_str = SEP[lang].join(quoted(c) for c in cands)
        visit = ([f"goto /?q={quote(name(tgt))}", "view 0"] if tgt else []) + \
                [f"goto /product/{c}" for c in cands]
        login = False
        if kind == "A1_price":
            intent = TPL[lang][kind].format(cands=cand_str)
            ev = [{"type": "answer_match", "mode": "contains", "any_of": nums(price(tgt)),
                   "none_of": [v for o in others for v in nums(price(o))]}]
            sol = visit + [f"stop {price(tgt)}"]
        elif kind == "A2_wishlist":
            login = True
            intent = TPL[lang][kind].format(cands=cand_str)
            ev = ([{"type": "db_record_exists", "table": "wishlist",
                    "match": {"user_id": 1, "product_id": tgt}}] +
                  [{"type": "db_record_absent", "table": "wishlist",
                    "match": {"user_id": 1, "product_id": o}} for o in others])
            sol = V.LOGIN + visit + [f"goto /product/{tgt}", "fill 2"]
        elif kind == "A3_buy":
            login = True
            a = A[n % len(A)]
            intent = TPL[lang][kind].format(one=one, addr=a, cands=cand_str)
            ev = ([{"type": "order_contains", "address": f"%{a}%",
                    "items": {str(tgt): 1}, "total": round(loc[tgt]["price"], 2)}] +
                  [{"type": "db_record_absent", "table": "order_items",
                    "match": {"product_id": o}} for o in others])
            sol = V.LOGIN + visit + [f"goto /product/{tgt}", "fill 1 qty=1",
                                     "goto /checkout", f"fill 1 address={a}", "fill 2"]
        elif kind == "A4_brand":
            intent = TPL[lang][kind].format(cands=cand_str)
            ev = [{"type": "answer_match", "mode": "contains", "any_of": [loc[tgt]["brand"]],
                   "none_of": sorted({loc[o]["brand"] for o in others} - {loc[tgt]["brand"]})}]
            sol = visit + [f"stop {loc[tgt]['brand']}"]
        elif kind == "A5_reviews":
            intent = TPL[lang][kind].format(cands=cand_str)
            ev = [{"type": "answer_match", "mode": "contains", "any_of": nums(nrev[tgt]),
                   "none_of": [v for o in others for v in nums(nrev[o])]}]
            sol = visit + [f"stop {nrev[tgt]}"]
        elif kind == "A6_not_sold":
            intent = TPL[lang][kind]
            ev = [{"type": "answer_match", "mode": "contains", "any_of": na}]
            sol = ["goto /"] + [f"goto /product/{c}" for c in cands] + ["stop N/A"]
        elif kind == "B1_pack":
            intent = TPL[lang][kind].format(name=quoted(tgt))
            ev = [{"type": "answer_match", "mode": "contains", "any_of": nums(t["pack"])}]
            sol = [f"goto /product/{tgt}", f"stop {t['pack']}"]
        else:
            raise SystemExit(f"unknown kind {kind}")
        image = DEMO_IMG.format(t["demo_id"]) if kind == "A6_not_sold" else SHOP_IMG.format(tgt)
        assert os.path.exists(os.path.join(ROOT, image)), image
        T.append({"id": f"image-ministore-{n:03d}", "site": "ministore", "kind": kind,
                  "intent": intent + (V.CRED[lang] if login else ""),
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
