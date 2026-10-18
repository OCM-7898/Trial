import json
import os
import sys
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "sites"))
sys.path.insert(0, os.path.join(ROOT, "sites", "visual"))
sys.path.insert(0, os.path.join(ROOT, "tasks", "visual", "gari"))
sys.path.insert(0, HERE)

from gari_i18n import I18N
from translate_gari_listings import localize_listing
from visual.gari.seed import hand_table
from visual.gari.strings import LANG_META, STRINGS
from image_i18n import QUOTE, SEP, TPL

LANGS = ["en", "bn", "hi", "ur", "am"]
CAR_IMG = "sites/visual/gari/static/cars/{}/{}.jpg"
LOGIN = ["goto /login", "fill 0 email=ahmed.raza@garibazaar.test; password=garibazaar2026"]
URDU_ALT = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "٠١٢٣٤٥٦٧٨٩")


def pct_floor100(price, pct):
    return price * pct // 100 // 100 * 100


def build(lang):
    plan = json.load(open(os.path.join(HERE, "draft_plan.json"), encoding="utf-8"))
    L = {int(l["id"]): l for l in json.load(open(os.path.join(ROOT, "sites/visual/gari/listings.json"),
                                                  encoding="utf-8"))}
    HT = hand_table(lang)
    META = LANG_META[lang]
    nd = str.maketrans("0123456789", META["digits"])
    cur, rate = META["cur"], META["rate"]
    q0, q1 = QUOTE[lang]
    cred = " " + I18N[lang]["cred"]
    sold_word = STRINGS[lang]["sold_badge"]

    def loc(i):
        l = L[i]
        return localize_listing(l, HT) if HT else l

    def nums(n):
        out = [str(n), f"{n:,}"]
        out += [v.translate(nd) for v in out]
        if lang == "ur":
            out += [v.translate(URDU_ALT) for v in out[2:]]
        return list(dict.fromkeys(out))

    def price(i):
        return int(L[i]["price"]) * rate

    def money(n):
        return f"{cur}{n:,}".translate(nd)

    def name(i):
        l = L[i]
        return f"{q0}{l['year']} {l['brand']} {l['model']}{q1} ({loc(i)['city']})"

    T = []
    for t in plan:
        n, kind = t["n"], t["kind"]
        cands = [c["id"] for c in t["candidates"]]
        tgt = t["target"]
        others = [c for c in cands if c != tgt]
        cand_str = SEP[lang].join(name(c) for c in cands)
        models = {L[c]["model"] for c in cands}
        q = L[cands[0]]["model"] if len(models) == 1 else L[cands[0]]["brand"]
        visit = [f"goto /cars?q={quote(q)}"] + [f"goto /car/{c}" for c in cands]
        login = False
        if kind == "A1_price":
            intent = TPL[lang][kind].format(cands=cand_str)
            ev = [{"type": "answer_match", "mode": "contains", "any_of": nums(price(tgt)),
                   "none_of": [v for o in others for v in nums(price(o))]}]
            sol = visit + [f"stop {price(tgt)}"]
        elif kind == "A2_save":
            login = True
            intent = TPL[lang][kind].format(cands=cand_str)
            ev = ([{"type": "db_record_exists", "table": "saved", "match": {"listing_id": tgt}}] +
                  [{"type": "db_record_absent", "table": "saved", "match": {"listing_id": o}} for o in others])
            sol = LOGIN + visit + [f"goto /car/{tgt}", "fill 0"]
        elif kind == "A3_offer":
            login = True
            amt = pct_floor100(price(tgt), 90)
            intent = TPL[lang][kind].format(amt=money(amt), cands=cand_str)
            ev = ([{"type": "db_record_exists", "table": "offers", "match": {"listing_id": tgt, "amount": amt}}] +
                  [{"type": "db_record_absent", "table": "offers", "match": {"listing_id": o}} for o in others])
            sol = LOGIN + visit + [f"goto /car/{tgt}", f"fill 1 amount={amt}"]
        elif kind == "A4_seller":
            intent = TPL[lang][kind].format(cands=cand_str)
            want = loc(tgt)["seller_name"]
            ev = [{"type": "answer_match", "mode": "contains", "any_of": [want],
                   "none_of": sorted({loc(o)["seller_name"] for o in others} - {want})}]
            sol = visit + [f"stop {want}"]
        elif kind == "A5_mileage":
            intent = TPL[lang][kind].format(cands=cand_str)
            km = lambda i: int(L[i]["mileage_km"])
            ev = [{"type": "answer_match", "mode": "contains", "any_of": nums(km(tgt)),
                   "none_of": [v for o in others for v in nums(km(o))]}]
            sol = visit + [f"stop {km(tgt)}"]
        elif kind == "A6_sold":
            intent = TPL[lang][kind]
            ev = [{"type": "answer_match", "mode": "contains", "any_of": ["N/A", sold_word]}]
            sol = [f"goto /cars?q={quote(L[t['sold_id']]['model'])}"] + [f"goto /car/{c}" for c in cands] + ["stop N/A"]
        else:
            raise SystemExit(f"unknown kind {kind}")
        pid = t["sold_id"] if kind == "A6_sold" else tgt
        image = CAR_IMG.format(pid, t["photo_k"])
        assert os.path.exists(os.path.join(ROOT, image)), image
        T.append({"id": f"image-gari-{n:03d}", "site": "gari", "kind": kind,
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
