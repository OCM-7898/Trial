import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "sites"))

from visual.gari import finance_quote
from visual.gari.seed import (DEALER_INFO, PRESEEDED_SAVED,
                             hand_table)
from visual.gari.strings import LANG_META, STRINGS
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "sites", "visual"))
from gari_i18n import I18N, LIT
from translate_gari_listings import localize_listing

DEALERS = [{"id": d[0], "name": d[1], "city": d[2], "rating": d[3],
            "since": d[4], "phone": d[5]} for d in DEALER_INFO]

CRED = {l: p["cred"] for l, p in I18N.items()}
NA_SUFFIX = {l: p["na"] for l, p in I18N.items()}

LOGIN = ["goto /login",
         "fill 0 email=ahmed.raza@garibazaar.test; password=garibazaar2026"]


def load_listings():
    p = os.path.join(ROOT, "sites", "visual", "gari", "listings.json")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def grp(n):
    return f"{n:,}"


def money_variants(n):
    return list(dict.fromkeys([grp(n), str(n)]))


def name(l):
    return f"{l['year']} {l['brand']} {l['model']}"


def pct_floor100(price, pct):
    return price * pct // 100 // 100 * 100


def min_offer100(price):
    exact_min = -(-(price * 80) // 100)
    return -(-exact_min // 100) * 100


def sell_fill(d):
    keys = ("brand", "model", "year", "mileage_km", "price", "city",
            "color", "transmission", "fuel", "engine_cc", "phone",
            "description")
    return "fill 0 " + "; ".join(f"{k}={d[k]}" for k in keys if k in d)


def build(lang="en"):
    L = load_listings()
    by_id = {l["id"]: l for l in L}
    active = [l for l in L if l["status"] == "active"]
    cred = CRED[lang]
    na = NA_SUFFIX[lang]
    HT = hand_table(lang)
    TPL, LIT_L, STR = I18N[lang], LIT[lang], STRINGS[lang]
    META = LANG_META[lang]
    rate, cur = META["rate"], META["cur"]
    _ND = str.maketrans("0123456789", META["digits"])

    def cv(usd):
        return usd * rate

    def mp(n):
        return cur + (str(n) if lang == "en" else grp(n).translate(_ND))

    def mg(n):
        return cur + (grp(n) if lang == "en" else grp(n).translate(_ND))

    def num(n):
        return mp(n)[len(cur):]

    def V(kind, en_word):
        return HT[kind][en_word] if HT else en_word

    def F(en_feature):
        return V("features", en_feature)

    def DN(en_dealer):
        return V("dealers", en_dealer)

    def LZ(l):
        return localize_listing(l, HT) if HT else l

    def I(key, **kw):
        return TPL[key].format(cred=cred, na=na, cur=cur, **kw)

    def loc_ad(ad, desc_key):
        ad = dict(ad)
        for k, kind in (("city", "city"), ("color", "color"),
                        ("transmission", "transmission"), ("fuel", "fuel")):
            ad[k] = V(kind, ad[k])
        ad["description"] = LIT_L[desc_key]
        ad["price"] = cv(ad["price"])
        return ad

    def adf(ad, **extra):
        d = {"year": ad["year"], "km": ad["mileage_km"],
             "price": num(ad["price"]),
             "city": ad["city"], "color": ad["color"],
             "trans": ad["transmission"], "fuel": ad["fuel"],
             "cc": ad["engine_cc"], "phone": ad["phone"],
             "desc": ad["description"]}
        d.update(extra)
        return d

    AD_KEYS = ("brand", "model", "year", "mileage_km", "price", "city",
               "color", "transmission", "fuel", "engine_cc", "phone",
               "description")

    def ad_ev(ad, **over):
        m = {k: ad[k] for k in AD_KEYS}
        m.update(over)
        m["status"] = "active"
        return {"type": "db_record_exists", "table": "ads", "match": m}

    def review_ev(ad):
        return {"type": "final_page_contains",
                "strings": [str(ad[k]) for k in AD_KEYS if k != "price"]
                + [f"{ad['price']:,}"]}

    T = []

    def add(diff, intent, eval_, solution, start="/", steps=30, tags=None):
        T.append({"id": f"visualgari-{len(T) + 1:03d}", "site": "gari",
                  "difficulty": diff, "intent": intent, "start_path": start,
                  "eval": eval_, "solution": solution, "max_steps": steps})
        if tags:
            T[-1]["tags"] = list(tags)

    def uniq_min(pool, key):
        pool = list(pool)
        assert pool, "empty candidate pool"
        best = min(pool, key=key)
        ties = [l for l in pool if key(l)[:1] == key(best)[:1]]
        assert len(ties) == 1, f"ambiguous target: {[t['id'] for t in ties]}"
        return best

    def binding_min(pool, cond, min_reject=1, max_reject=8):
        pool = sorted(pool, key=lambda l: (l["price"], l["id"]))
        matching = [l for l in pool if cond(l)]
        if not matching:
            return None
        tgt = matching[0]
        if sum(1 for l in matching if l["price"] == tgt["price"]) != 1:
            return None
        n_rej = sum(1 for l in pool if l["price"] < tgt["price"]
                    and not cond(l))
        if not min_reject <= n_rej <= max_reject:
            return None
        return tgt

    def feats(l):
        return set(l["features"].split(", "))

    ad2 = {"brand": "Honda", "model": "Vezel", "year": 2020,
           "mileage_km": 45000, "price": 31800, "city": "Karachi",
           "color": "Blue", "transmission": "Automatic", "fuel": "Hybrid",
           "engine_cc": 1500, "phone": "0321-7788990",
           "description": "Fresh import, auction grade 4.5."}
    ad2 = loc_ad(ad2, "ad2_desc")
    add("hard",
        I("a1", **adf(ad2)),
        [ad_ev(ad2)],
        LOGIN + ["goto /sell", sell_fill(ad2), "fill 0"])

    ad3 = {"brand": "Suzuki", "model": "Alto VXL", "year": 2022,
           "mileage_km": 18000, "price": 7700, "city": "Islamabad",
           "color": "Silver", "transmission": "Automatic", "fuel": "Petrol",
           "engine_cc": 660, "phone": "0333-4455667",
           "description": "Like new."}
    ad3 = loc_ad(ad3, "ad3_desc")
    add("hard",
        I("a2", **adf(ad3, newprice=num(cv(7150)))),
        [ad_ev(ad3, price=cv(7150)),
         {"type": "db_record_absent", "table": "ads",
          "match": {"model": "Alto VXL", "price": cv(7700)}}],
        LOGIN + ["goto /sell", sell_fill(ad3), "fill 0",
                 f"fill 0 price={cv(7150)}"])

    ad4 = {"brand": "Kia", "model": "Picanto", "year": 2021,
           "mileage_km": 30000, "price": 10400, "city": "Multan",
           "color": "Red", "transmission": "Manual", "fuel": "Petrol",
           "engine_cc": 1000, "phone": "0345-1112233",
           "description": "First owner."}
    ad4 = loc_ad(ad4, "ad4_desc")
    add("hard",
        I("a3", **adf(ad4)),
        [{"type": "final_url", "path": "/sell/review"}, review_ev(ad4),
         {"type": "db_record_absent", "table": "ads",
          "match": {"model": "Picanto"}}],
        LOGIN + ["goto /sell", sell_fill(ad4)])

    ad6 = {"brand": "BMW", "model": "X5 xDrive40i", "year": 2019,
           "mileage_km": 60000, "price": 76800, "city": "Lahore",
           "color": "Black", "transmission": "Automatic", "fuel": "Petrol",
           "engine_cc": 3000, "phone": "0300-1231234",
           "description": "Fully loaded, M sport package."}
    ad6 = loc_ad(ad6, "ad6_desc")
    add("hard",
        I("a4", **adf(ad6)),
        [ad_ev(ad6)],
        LOGIN + ["goto /sell", sell_fill(ad6), "fill 0"])

    ad7a = {"brand": "Hyundai", "model": "Tucson AWD", "year": 2022,
            "mileage_km": 22000, "price": 35000, "city": "Karachi",
            "color": "Gray", "transmission": "Automatic", "fuel": "Petrol",
            "engine_cc": 2000, "phone": "0311-5556677",
            "description": "Under warranty."}
    ad7a = loc_ad(ad7a, "ad7a_desc")
    ad7b = {"brand": "Kia", "model": "Sportage Alpha", "year": 2021,
            "mileage_km": 41000, "price": 30400, "city": "Karachi",
            "color": "White", "transmission": "Automatic", "fuel": "Petrol",
            "engine_cc": 2000, "phone": "0311-5556677",
            "description": "Alloy rims, cruise control."}
    ad7b = loc_ad(ad7b, "ad7b_desc")
    add("hard",
        I("a5", **{k + '1': v for k, v in adf(ad7a).items()}, **{k + '2': v for k, v in adf(ad7b).items()}),
        [ad_ev(ad7a), ad_ev(ad7b)],
        LOGIN + ["goto /sell", sell_fill(ad7a), "fill 0",
                 "goto /sell", sell_fill(ad7b), "fill 0"])

    l205 = by_id[210]
    ad8_price = pct_floor100(cv(l205["price"]), 95)
    add("hard",
        I("a6", city=V('city', 'Lahore'), phone='0307-4041122', desc=LIT_L['ad8_desc']),
        [{"type": "db_record_exists", "table": "ads",
          "match": {"brand": l205["brand"], "model": l205["model"],
                    "year": l205["year"],
                    "mileage_km": l205["mileage_km"],
                    "color": LZ(l205)["color"],
                    "transmission": LZ(l205)["transmission"],
                    "fuel": LZ(l205)["fuel"],
                    "engine_cc": l205["engine_cc"],
                    "price": ad8_price, "city": V("city", "Lahore"),
                    "phone": "0307-4041122",
                    "description": LIT_L["ad8_desc"],
                    "status": "active"}}],
        LOGIN + ["goto /car/210", "goto /sell",
                 sell_fill({"brand": l205["brand"], "model": l205["model"],
                            "year": l205["year"],
                            "mileage_km": l205["mileage_km"],
                            "price": ad8_price, "city": V("city", "Lahore"),
                            "color": LZ(l205)["color"],
                            "transmission": LZ(l205)["transmission"],
                            "fuel": LZ(l205)["fuel"],
                            "engine_cc": l205["engine_cc"],
                            "phone": "0307-4041122",
                            "description": LIT_L["ad8_desc"]}),
                 "fill 0"])

    aud_brand, aud = next(
        (b, t) for b in ("Audi", "BMW", "Mercedes-Benz", "Lexus",
                         "Toyota", "Honda", "Kia")
        if (t := binding_min([l for l in active if l["brand"] == b],
                             lambda l: "Sunroof" in feats(l))))
    add("hard",
        I("b1", brand=aud_brand, f_sunroof=F('Sunroof')),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": aud["id"]}}],
        LOGIN + [f"goto /car/{aud['id']}", "fill 0"])

    toyl = uniq_min((l for l in active if l["brand"] == "Toyota"
                     and l["city"] == "Lahore"
                     and "Leather Seats" in feats(l)),
                    key=lambda l: (l["price"], l["id"]))
    amt10 = pct_floor100(cv(toyl["price"]), 90)
    add("hard",
        I("b2", city=V('city', 'Lahore'), f_leather=F('Leather Seats')),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": toyl["id"], "amount": amt10}}],
        LOGIN + [f"goto /car/{toyl['id']}", f"fill 1 amount={amt10}"])

    nav_city, isbnav = next(
        (c, t) for c in ("Islamabad", "Karachi", "Lahore", "Rawalpindi",
                         "Faisalabad", "Multan")
        if (t := binding_min([l for l in active
                              if l["body_type"] == "SUV"
                              and l["city"] == c],
                             lambda l: "Navigation" in feats(l)
                             and "Sunroof" not in feats(l))))
    add("hard",
        I("b3", suv=V('body_type', 'SUV'), city=V('city', nav_city), f_nav=F('Navigation'), f_sunroof=F('Sunroof')),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": isbnav["id"]}}],
        LOGIN + [f"goto /car/{isbnav['id']}", "fill 0"])

    vws = uniq_min((l for l in active if l["brand"] == "Volkswagen"
                    and "Sunroof" in feats(l)),
                   key=lambda l: (l["price"], l["id"]))
    add("hard",
        I("b4", f_sunroof=F('Sunroof')),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": vws["id"]}}],
        LOGIN + [f"goto /car/{vws['id']}", "fill 0"])

    nisc = uniq_min((l for l in active if l["brand"] == "Nissan"
                     and l["city"] == "Karachi"
                     and "Rear Camera" in feats(l)),
                    key=lambda l: (l["price"], l["id"]))
    amt14 = pct_floor100(cv(nisc["price"]), 90)
    add("hard",
        I("b5", city=V('city', 'Karachi'), f_cam=F('Rear Camera')),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": nisc["id"], "amount": amt14}}],
        LOGIN + [f"goto /car/{nisc['id']}", f"fill 1 amount={amt14}"])

    two_brand, hyu2 = next(
        (b, t) for b in ("Hyundai", "Toyota", "Honda", "Kia", "Nissan",
                         "Volkswagen", "Ford", "Chevrolet")
        if (t := binding_min([l for l in active if l["brand"] == b],
                             lambda l: {"Cruise Control", "Sunroof"}
                             <= feats(l))))
    add("hard",
        I("b6", brand=two_brand, f_cruise=F('Cruise Control'), f_sunroof=F('Sunroof')),
        [{"type": "answer_match",
          "any_of": money_variants(cv(hyu2["price"]))}],
        [f"goto /car/{hyu2['id']}", f"stop {mg(cv(hyu2['price']))}"])

    tesla_ids = sorted(l["id"] for l in active if l["brand"] == "Tesla")
    n_dt = sum(1 for i in tesla_ids
               if by_id[i]["seller_type"] == "Dealer")
    add("hard",
        I("c1"),
        [{"type": "answer_match", "answer": str(n_dt)}],
        [f"goto /car/{i}" for i in tesla_ids] + [f"stop {n_dt}"],
        tags=["memory"])

    dlr_brand, dtes = next(
        (b, t) for b in ("Tesla", "Porsche", "Land Rover", "Lexus",
                         "Hummer", "Audi", "BMW", "Volvo")
        if (t := binding_min([l for l in active if l["brand"] == b],
                             lambda l: l["seller_type"] == "Dealer")))
    add("hard",
        I("c2", brand=dlr_brand),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": dtes["id"]}}],
        LOGIN + [f"goto /car/{dtes['id']}", "fill 0"])

    dsuvk = uniq_min((l for l in active if l["body_type"] == "SUV"
                      and l["city"] == "Karachi"
                      and l["seller_type"] == "Dealer"),
                     key=lambda l: (l["price"], l["id"]))
    amt19 = pct_floor100(cv(dsuvk["price"]), 85)
    add("hard",
        I("c3", suv=V('body_type', 'SUV'), city=V('city', 'Karachi')),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": dsuvk["id"], "amount": amt19}}],
        LOGIN + [f"goto /car/{dsuvk['id']}", f"fill 1 amount={amt19}"])

    tsuv = sorted((l for l in active if l["brand"] == "Toyota"
                   and l["body_type"] == "SUV" and l["city"] == "Karachi"),
                  key=lambda l: (l["price"], l["id"]))
    assert len(tsuv) >= 2 and tsuv[0]["price"] != tsuv[1]["price"] \
        != tsuv[2]["price"]
    toy2 = tsuv[1]
    amt20 = pct_floor100(cv(toy2["price"]), 90)
    add("hard",
        I("d1", suv=V('body_type', 'SUV'), city=V('city', 'Karachi')),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": toy2["id"], "amount": amt20}}],
        LOGIN + [f"goto /car/{toy2['id']}", f"fill 1 amount={amt20}"])

    sim40 = sorted((l for l in active if l["brand"] == by_id[40]["brand"]
                    and l["id"] != 40), key=lambda l: l["id"])[:4]
    simch = uniq_min(sim40, key=lambda l: (l["price"], l["id"]))
    add("hard",
        I("d2"),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": simch["id"]}}],
        LOGIN + ["goto /car/40", f"goto /car/{simch['id']}", "fill 0"])

    suvl = uniq_min((l for l in active if l["body_type"] == "SUV"
                     and l["city"] == "Lahore"),
                    key=lambda l: (l["price"], l["id"]))
    suvk = uniq_min((l for l in active if l["body_type"] == "SUV"
                     and l["city"] == "Karachi"),
                    key=lambda l: (l["price"], l["id"]))
    assert suvl["price"] != suvk["price"]
    winner = suvk if suvk["price"] < suvl["price"] else suvl
    amt24 = pct_floor100(cv(winner["price"]), 85)
    add("hard",
        I("d3", suv=V('body_type', 'SUV'), city1=V('city', 'Lahore'), city2=V('city', 'Karachi')),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": winner["id"], "amount": amt24}}],
        LOGIN + [f"goto /car/{winner['id']}", f"fill 1 amount={amt24}"])

    isb3 = sorted((l for l in active if l["city"] == "Islamabad"),
                  key=lambda l: (l["posted_on"], l["id"]),
                  reverse=True)[2]
    add("hard",
        I("d4", city=V('city', 'Islamabad')),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": isb3["id"]}}],
        LOGIN + [f"goto /car/{isb3['id']}", "fill 0"])

    add("hard",
        I("e1"),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": 55}},
         {"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": 88}},
         {"type": "db_record_absent", "table": "saved",
          "match": {"listing_id": 25}}],
        LOGIN + ["goto /car/55", "fill 0", "goto /car/88", "fill 0",
                 "goto /saved", "fill 0"])

    l16, l17 = by_id[16], by_id[17]
    a27lo = pct_floor100(cv(l16["price"]), 85)
    a27b = pct_floor100(cv(l17["price"]), 85)
    a27hi = pct_floor100(cv(l16["price"]), 92)
    add("hard",
        I("e2", hi=num(a27hi), lo=num(a27lo), b=num(a27b)),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": 16, "amount": a27hi}},
         {"type": "db_record_absent", "table": "offers",
          "match": {"listing_id": 16, "amount": a27lo}},
         {"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": 17, "amount": a27b}}],
        LOGIN + ["goto /car/16", f"fill 1 amount={a27lo}",
                 "goto /car/17", f"fill 1 amount={a27b}",
                 "goto /car/16", f"fill 1 amount={a27hi}"])

    ad28 = {"brand": "Volkswagen", "model": "Golf GTI", "year": 2018,
            "mileage_km": 88000, "price": 15000, "city": "Lahore",
            "color": "Gray", "transmission": "Automatic", "fuel": "Petrol",
            "engine_cc": 2000, "phone": "0308-6667788",
            "description": "Stage 1 tuned, all stock parts available."}
    ad28 = loc_ad(ad28, "ad28_desc")
    add("hard",
        I("e3", **adf(ad28, newprice=num(cv(14500)))),
        [ad_ev(ad28, price=cv(14500)),
         {"type": "db_record_absent", "table": "ads",
          "match": {"model": "Golf GTI", "price": cv(15000)}}],
        LOGIN + ["goto /sell", sell_fill(ad28), "goto /sell",
                 f"fill 0 price={cv(14500)}", "fill 0"])

    l30, l31 = by_id[30], by_id[31]
    a29a = pct_floor100(cv(l30["price"]), 88)
    a29b = pct_floor100(cv(l31["price"]), 88)
    add("hard",
        I("e4", a=num(a29a), n30=name(l30), b=num(a29b), n31=name(l31)),
        [{"type": "db_record_absent", "table": "offers",
          "match": {"listing_id": 30}},
         {"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": 31, "amount": a29b}}],
        LOGIN + ["goto /car/30", f"fill 1 amount={a29a}",
                 "goto /car/31", f"fill 1 amount={a29b}",
                 "goto /offers", "fill 0"])

    l44, l71, l83 = by_id[44], by_id[71], by_id[83]
    a31a = pct_floor100(cv(l44["price"]), 92)
    a31b = pct_floor100(cv(l71["price"]), 86)
    a31c = pct_floor100(cv(l83["price"]), 90)
    add("hard",
        I("e5", a=num(a31a), b=num(a31b), c=num(a31c)),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": 44, "amount": a31a}},
         {"type": "db_record_absent", "table": "offers",
          "match": {"listing_id": 71}},
         {"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": 83, "amount": a31c}}],
        LOGIN + ["goto /car/44", f"fill 1 amount={a31a}",
                 "goto /car/71", f"fill 1 amount={a31b}",
                 "goto /car/83", f"fill 1 amount={a31c}",
                 "goto /offers", "fill 1"])

    l302 = by_id[302]
    a32 = pct_floor100(cv(l302["price"]), 90)
    add("hard",
        I("e6", a=num(a32), n302=name(l302), subject=LIT_L['e32_subject'], message=LIT_L['e32_message']),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": 302, "amount": a32}},
         {"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": 305}},
         {"type": "db_record_exists", "table": "messages",
          "match": {"subject": LIT_L["e32_subject"],
                    "body": "%" + LIT_L["e32_key"] + "%"}}],
        LOGIN + ["goto /car/302", f"fill 1 amount={a32}",
                 "goto /car/305", "fill 0", "goto /contact",
                 f"fill 0 subject={LIT_L['e32_subject']}; "
                 f"message={LIT_L['e32_message']}"])

    add("hard",
        I("e7"),
        [{"type": "db_record_absent", "table": "saved",
          "match": {"listing_id": 25}},
         {"type": "db_record_absent", "table": "saved",
          "match": {"listing_id": 210}},
         {"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": 330}}],
        LOGIN + ["goto /saved", "fill 0", "fill 0"])

    l210 = by_id[210]
    add("hard",
        I("f1", n210=name(l210), local=V('assembly', 'Local'), imported=V('assembly', 'Imported')),
        [{"type": "answer_match",
          "any_of": money_variants(l210["mileage_km"])},
         {"type": "answer_match", "answer": str(l210["owners"])},
         {"type": "answer_match", "answer": LZ(l210)["assembly"],
          "none_of": [V("assembly", "Imported" if l210["assembly"] == "Local"
                        else "Local")]}],
        ["goto /car/210",
         f"stop {grp(l210['mileage_km'])} km, {l210['owners']} "
         f"owner(s), {LZ(l210)['assembly']}"])

    l297 = by_id[297]
    assert l297["status"] == "active" and l297["price"] % 200 == 0
    assert cv(l297["price"]) * 15 % 1000 == 0
    comm = cv(l297["price"]) * 15 // 1000
    add("hard",
        I("f2"),
        [{"type": "answer_match", "any_of": money_variants(comm)}],
        ["goto /rules", "goto /car/297", f"stop {mg(comm)}"])

    p200, p201 = by_id[200], by_id[201]
    s38 = cv(p200["price"]) + cv(p201["price"])
    lowmi = p200 if (p200["mileage_km"], p200["id"]) < \
        (p201["mileage_km"], p201["id"]) else p201
    assert p200["mileage_km"] != p201["mileage_km"]
    add("hard",
        I("f3"),
        [{"type": "answer_match", "any_of": money_variants(s38)},
         {"type": "answer_match", "answer": str(lowmi["id"]),
          "none_of": [str(p201["id"] if lowmi is p200 else p200["id"])]}],
        ["goto /compare", "fill 0 a=200; b=201",
         f"stop combined {mg(s38)}, lower mileage: {lowmi['id']}"])

    combo = {}
    for l in active:
        k = (l["color"], l["year"], l["brand"], l["model"], l["city"])
        combo.setdefault(k, []).append(l)
    uniq_combo = [ls[0] for ls in combo.values() if len(ls) == 1]
    l39 = sorted(uniq_combo, key=lambda l: l["id"])[120]
    add("hard",
        I("f4", color=LZ(l39)['color'], n39=name(l39), city=LZ(l39)['city']),
        [{"type": "answer_match", "any_of": money_variants(cv(l39["price"]))},
         {"type": "answer_match", "answer": LZ(l39)["transmission"],
          "none_of": [V("transmission", "Manual" if l39["transmission"]
                        == "Automatic" else "Automatic")]}],
        [f"goto /car/{l39['id']}",
         f"stop {mg(cv(l39['price']))}, {LZ(l39)['transmission']}"])

    m3 = finance_quote(cv(24000), 20, 3)["monthly"]
    m5 = finance_quote(cv(24000), 20, 5)["monthly"]
    d40 = m3 - m5
    add("hard",
        I("g1", p1=num(cv(24000))),
        [{"type": "answer_match", "any_of": money_variants(d40)}],
        ["goto /finance", f"fill 0 price={cv(24000)}; down_pct=20; years=3",
         f"fill 0 price={cv(24000)}; down_pct=20; years=5",
         f"stop {mg(d40)}"])

    cap42 = cv(450)
    yrs42 = next(y for y in range(1, 8)
                 if finance_quote(cv(20000), 25, y)["monthly"] <= cap42)
    assert 1 < yrs42 < 7, yrs42
    add("hard",
        I("g2", p1=num(cv(20000)), cap=num(cap42)),
        [{"type": "answer_match",
          "any_of": [str(yrs42), f"{yrs42} years"]}],
        ["goto /finance",
         f"fill 0 price={cv(20000)}; down_pct=25; years={yrs42 - 1}",
         f"fill 0 price={cv(20000)}; down_pct=25; years={yrs42}",
         f"stop {yrs42}"])

    la, lb = by_id[210], by_id[25]
    ma = finance_quote(cv(la["price"]), 25, 4)["monthly"]
    mb = finance_quote(cv(lb["price"]), 25, 4)["monthly"]
    cheaper43 = la if (ma, la["id"]) < (mb, lb["id"]) else lb
    assert ma != mb
    add("hard",
        I("g3", n210=name(la), n25=name(lb)),
        [{"type": "answer_match", "answer": str(cheaper43["id"]),
          "none_of": [str(lb["id"] if cheaper43 is la else la["id"])]}],
        ["goto /car/210", "goto /car/25", "goto /finance",
         f"fill 0 price={cv(la['price'])}; down_pct=25; years=4",
         f"fill 0 price={cv(lb['price'])}; down_pct=25; years=4",
         f"stop {cheaper43['id']}"])

    m16 = finance_quote(cv(l16["price"]), 20, 4)["monthly"]
    m17 = finance_quote(cv(l17["price"]), 20, 4)["monthly"]
    d44 = abs(m16 - m17)
    assert d44 > 0
    add("hard",
        I("g4"),
        [{"type": "answer_match", "any_of": money_variants(d44)}],
        ["goto /car/16", "goto /car/17", "goto /finance",
         f"fill 0 price={cv(l16['price'])}; down_pct=20; years=4",
         f"fill 0 price={cv(l17['price'])}; down_pct=20; years=4",
         f"stop {mg(d44)}"])

    cap46 = cv(400)
    dp46 = next(d for d in range(0, 91, 10)
                if finance_quote(cv(18000), d, 4)["monthly"] <= cap46)
    assert 0 < dp46 < 90, dp46
    add("hard",
        I("g5", p1=num(cv(18000)), cap=num(cap46)),
        [{"type": "answer_match",
          "any_of": [str(dp46), f"{dp46}%"],
          "none_of": [f"{dp46 - 10}%", f"{dp46 + 10}%"]}],
        ["goto /finance",
         f"fill 0 price={cv(18000)}; down_pct={dp46 - 10}; years=4",
         f"fill 0 price={cv(18000)}; down_pct={dp46}; years=4",
         f"stop {dp46}%"])

    p55 = cv(by_id[55]["price"])
    cap47 = (finance_quote(p55, 40, 4)["monthly"] // 10) * 10 + 10
    dp47 = next(d for d in range(0, 91, 10)
                if finance_quote(p55, d, 4)["monthly"] <= cap47)
    assert 10 < dp47 < 80, dp47
    add("hard",
        I("g6", cap=num(cap47)),
        [{"type": "answer_match",
          "any_of": [str(dp47), f"{dp47}%"],
          "none_of": [f"{dp47 - 10}%", f"{dp47 + 10}%"]}],
        ["goto /car/55", "goto /finance",
         f"fill 0 price={p55}; down_pct={dp47 - 10}; years=4",
         f"fill 0 price={p55}; down_pct={dp47}; years=4",
         f"stop {dp47}%"])

    sv_cheap = by_id[210] if by_id[210]["price"] < by_id[25]["price"] \
        else by_id[25]
    assert by_id[210]["price"] != by_id[25]["price"]
    amt48 = pct_floor100(cv(sv_cheap["price"]), 90)
    add("hard",
        I("h1", message=LIT_L['h48_message']),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": sv_cheap["id"], "amount": amt48,
                    "message": LIT_L["h48_message"]}}],
        LOGIN + [f"goto /car/{sv_cheap['id']}",
                 f"fill 1 amount={amt48}; message={LIT_L['h48_message']}"])

    l62 = by_id[62]
    amt49 = min_offer100(cv(l62["price"])) + cv(150)
    add("hard",
        I("h2", asking=mg(cv(l62['price']))[len(cur):], delta=num(cv(150))),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": 62, "amount": amt49}}],
        LOGIN + ["goto /car/62", f"fill 1 amount={amt49}"])

    l75 = by_id[75]
    amt51 = pct_floor100(cv(l75["price"]), 90)
    add("hard",
        I("h3", amt=num(amt51), n75=name(l75)),
        [{"type": "db_record_absent", "table": "offers",
          "match": {"listing_id": 75}},
         {"type": "final_url", "path": "/offers"}],
        LOGIN + ["goto /car/75", f"fill 1 amount={amt51}", "fill 0"])

    l90 = by_id[90]
    low52 = pct_floor100(cv(l90["price"]), 60)
    add("hard",
        I("h4", amt=num(low52), n90=name(l90), asking=mg(cv(l90['price']))[len(cur):]),
        [{"type": "answer_match", "any_of": ["below 80%", "80%"]},
         {"type": "db_record_absent", "table": "offers",
          "match": {"listing_id": 90}}],
        LOGIN + ["goto /car/90", f"fill 1 amount={low52}",
                 "stop Offer rejected: offers below 80% of the asking "
                 "price are not accepted."])

    l55o = by_id[55]
    amt53 = min_offer100(cv(l55o["price"]))
    add("hard",
        I("h5", n55=name(l55o), asking=mg(cv(l55o['price']))[len(cur):]),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": 55, "amount": amt53}}],
        LOGIN + ["goto /rules", "goto /car/55",
                 f"fill 1 amount={amt53}"])

    l20 = by_id[20]
    s85 = pct_floor100(cv(l20["price"]), 85)
    s90 = pct_floor100(cv(l20["price"]), 90)
    s95 = pct_floor100(cv(l20["price"]), 95)
    add("hard",
        I("h6", n20=name(l20), s95=num(s95), s85=num(s85), s90=num(s90)),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": 20, "amount": s95}},
         {"type": "db_record_absent", "table": "offers",
          "match": {"listing_id": 20, "amount": s85}},
         {"type": "db_record_absent", "table": "offers",
          "match": {"listing_id": 20, "amount": s90}}],
        LOGIN + ["goto /car/20", f"fill 1 amount={s85}",
                 "goto /car/20", f"fill 1 amount={s90}",
                 "goto /car/20", f"fill 1 amount={s95}"])

    p157 = by_id[157]
    assert p157["status"] == "active"
    newp = cv(p157["price"]) - cv(500)
    add("hard",
        I("i1", delta=num(cv(500))),
        [{"type": "db_field_equals", "table": "ads", "match": {"id": 1},
          "field": "price", "value": newp}],
        LOGIN + ["goto /car/157", "goto /account/ads/1",
                 f"fill 0 price={newp}"])

    add("hard",
        I("i2"),
        [{"type": "db_field_equals", "table": "ads", "match": {"id": 1},
          "field": "status", "value": "sold"}],
        LOGIN + ["goto /account/ads/1/sold", "fill 0"])

    add("hard",
        I("i3"),
        [{"type": "db_record_absent", "table": "ads", "match": {"id": 2}},
         {"type": "db_record_exists", "table": "ads", "match": {"id": 1}}],
        LOGIN + ["goto /account/ads/2/delete", "fill 0"])

    add("hard",
        I("j1", p=num(cv(10500))),
        [{"type": "answer_match", "answer": "N/A"},
         {"type": "db_field_equals", "table": "ads", "match": {"id": 2},
          "field": "price", "value": cv(12150)}],
        LOGIN + ["goto /account/ads/2", "stop N/A"])

    sold = by_id[205]
    assert sold["status"] == "sold"
    add("hard",
        I("j2", price=num(cv(sold['price']))),
        [{"type": "answer_match", "answer": "N/A"},
         {"type": "db_record_absent", "table": "offers",
          "match": {"listing_id": 205}}],
        LOGIN + ["goto /car/205", "stop N/A"])

    add("hard",
        I("j3"),
        [{"type": "answer_match", "answer": "N/A"},
         {"type": "db_record_absent", "table": "saved",
          "match": {"listing_id": 5}}],
        LOGIN + ["goto /car/5", "stop N/A"])

    add("hard",
        I("j4"),
        [{"type": "answer_match", "answer": "N/A"}],
        ["goto /cars?q=Bugatti", "stop N/A"])

    add("hard",
        I("j5"),
        [{"type": "answer_match", "answer": "N/A"}],
        ["goto /car/226", "stop N/A"])

    add("hard",
        I("k1"),
        [{"type": "db_record_absent", "table": "saved",
          "match": {"listing_id": 330}},
         {"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": 25}},
         {"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": 210}}],
        LOGIN + ["goto /saved", "fill 2"])

    dts = sorted(l["id"] for l in active if l["brand"] == "Tesla"
                 and l["seller_type"] == "Dealer")
    assert 3 <= len(dts) <= 6, dts
    pvt_teslas = sorted(l["id"] for l in active if l["brand"] == "Tesla"
                        and l["seller_type"] != "Dealer")
    assert pvt_teslas and not set(pvt_teslas) & set(PRESEEDED_SAVED)
    add("hard",
        I("k2"),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": i}} for i in dts] +
        [{"type": "db_record_absent", "table": "saved",
          "match": {"listing_id": i}} for i in pvt_teslas],
        LOGIN + sum([[f"goto /car/{i}", "fill 0"] for i in dts], []))

    dbyname = {d["name"]: d for d in DEALERS}

    def dealer_cars(dname):
        return [l for l in active if l["seller_type"] == "Dealer"
                and l["seller_name"] == dname]

    khi_d = [d for d in DEALERS if d["city"] == "Karachi"]
    top_khi = max(khi_d, key=lambda d: d["rating"])
    assert sum(1 for d in khi_d if d["rating"] == top_khi["rating"]) == 1
    l1car = uniq_min(dealer_cars(top_khi["name"]),
                     key=lambda l: (l["price"], l["id"]))
    add("hard",
        I("l1", city=V('city', 'Karachi')),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": l1car["id"]}}],
        LOGIN + ["goto /dealers", f"goto /dealer/{top_khi['id']}",
                 f"goto /car/{l1car['id']}", "fill 0"])

    old_d = min(DEALERS, key=lambda d: d["since"])
    assert sum(1 for d in DEALERS if d["since"] == old_d["since"]) == 1
    add("hard",
        I("l2"),
        [{"type": "answer_match", "answer": DN(old_d["name"]),
          "none_of": [DN(d["name"]) for d in DEALERS if d is not old_d]},
         {"type": "answer_match", "answer": old_d["phone"]}],
        ["goto /dealers", f"goto /dealer/{old_d['id']}",
         f"stop {DN(old_d['name'])}, phone {old_d['phone']}"])

    isb_d = [d for d in DEALERS if d["city"] == "Islamabad"]
    assert len(isb_d) == 2
    n_a, n_b = (len(dealer_cars(isb_d[0]["name"])),
                len(dealer_cars(isb_d[1]["name"])))
    assert n_a != n_b
    win_l3 = isb_d[0] if n_a > n_b else isb_d[1]
    add("hard",
        I("l3", city=V('city', 'Islamabad')),
        [{"type": "answer_match", "answer": DN(win_l3["name"]),
          "none_of": [DN(d["name"]) for d in isb_d if d is not win_l3]}],
        ["goto /dealers", f"goto /dealer/{isb_d[0]['id']}",
         f"goto /dealer/{isb_d[1]['id']}", f"stop {DN(win_l3['name'])}"])

    star_d = dbyname["Star Motors"]
    star = uniq_min(dealer_cars(star_d["name"]),
                    key=lambda l: (l["price"], l["id"]))
    amt_l4 = min_offer100(cv(star["price"]))
    add("hard",
        I("l4", dealer=DN('Star Motors')),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": star["id"], "amount": amt_l4}}],
        LOGIN + ["goto /dealers", f"goto /dealer/{star_d['id']}",
                 f"goto /car/{star['id']}", f"fill 1 amount={amt_l4}"])

    gal = dbyname["Galaxy Car Centre"]
    gcar = min((l for l in dealer_cars(gal["name"])
                if l["id"] > len(DEALERS)), key=lambda l: l["id"])
    assert str(gal["rating"]) not in str(gal["since"]) \
        and str(gal["since"]) not in str(gal["rating"])
    add("hard",
        I("l5", id=gcar['id']),
        [{"type": "answer_match", "answer": str(gal["rating"])},
         {"type": "answer_match", "answer": str(gal["since"])}],
        [f"goto /car/{gcar['id']}", f"goto /dealer/{gal['id']}",
         f"stop rating {gal['rating']}, member since {gal['since']}"])

    insp_act = sorted((l for l in active if l["inspection"]),
                      key=lambda l: l["id"])
    trio = []
    for l in insp_act:
        if l["id"] >= 100 and all(
                l["inspection"]["overall"] != t["inspection"]["overall"]
                for t in trio):
            trio.append(l)
        if len(trio) == 3:
            break
    assert len(trio) == 3
    best_m1 = max(trio, key=lambda l: l["inspection"]["overall"])
    ids_m1 = [l["id"] for l in trio]
    add("hard",
        I("m1", a=ids_m1[0], b=ids_m1[1], c=ids_m1[2]),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": best_m1["id"]}}],
        LOGIN + [f"goto /car/{i}/inspection" for i in ids_m1]
        + [f"goto /car/{best_m1['id']}", "fill 0"])

    def frac(v):
        return round(v * 10) % 10 != 0

    m2 = next(l for l in insp_act if l["id"] >= 150
              and frac(l["inspection"]["engine"])
              and frac(l["inspection"]["tires"])
              and str(l["inspection"]["engine"])
              not in str(l["inspection"]["tires"])
              and str(l["inspection"]["tires"])
              not in str(l["inspection"]["engine"]))
    e_m2, t_m2 = m2["inspection"]["engine"], m2["inspection"]["tires"]
    m2_other = [str(m2["inspection"][k]) for k in ("body", "interior")
                if m2["inspection"][k] not in (e_m2, t_m2)]
    add("hard",
        I("m2", id=m2['id'], engine=STR['insp_engine'], tires=STR['insp_tires']),
        [{"type": "answer_match", "answer": str(e_m2),
          "none_of": m2_other},
         {"type": "answer_match", "answer": str(t_m2),
          "none_of": m2_other}],
        [f"goto /car/{m2['id']}/inspection",
         f"stop engine {e_m2}, tires {t_m2}"])

    win_m3 = next(l for l in insp_act if l["id"] >= 300)
    non_m3 = [l for l in active if not l["inspection"]
              and l["id"] > win_m3["id"]][:3]
    assert len(non_m3) == 3
    ids_m3 = sorted([win_m3["id"]] + [l["id"] for l in non_m3])
    assert not {l["id"] for l in non_m3} & set(PRESEEDED_SAVED)
    add("hard",
        I("m3", a=ids_m3[0], b=ids_m3[1], c=ids_m3[2], d=ids_m3[3]),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": win_m3["id"]}}] +
        [{"type": "db_record_absent", "table": "saved",
          "match": {"listing_id": l["id"]}} for l in non_m3],
        LOGIN + [f"goto /car/{i}" for i in ids_m3]
        + [f"goto /car/{win_m3['id']}", "fill 0"])

    no_insp = next(l for l in active if not l["inspection"]
                   and l["id"] >= 250)
    add("hard",
        I("m4", id=no_insp['id']),
        [{"type": "answer_match", "answer": "N/A"}],
        [f"goto /car/{no_insp['id']}", "stop N/A"])

    CATS = [("engine", STR["insp_engine"]), ("body", STR["insp_body"]),
            ("interior", STR["insp_interior"]), ("tires", STR["insp_tires"])]

    def low_cat(l):
        vals = sorted((l["inspection"][k], k) for k, _ in CATS)
        return vals[0][1] if vals[0][0] != vals[1][0] else None

    m5 = next(l for l in insp_act if l["id"] >= 200 and low_cat(l))
    lbl5 = dict(CATS)[low_cat(m5)]
    add("hard",
        I("m5", id=m5['id']),
        [{"type": "answer_match",
          "any_of": list(dict.fromkeys([lbl5, lbl5.split(" ")[0]])),
          "none_of": list(dict.fromkeys(
              x for k, lb in CATS if k != low_cat(m5)
              for x in (lb, lb.split(" ")[0])))}],
        [f"goto /car/{m5['id']}/inspection", f"stop {lbl5}"])

    drops = sorted((l for l in active if l["prev_price"]),
                   key=lambda l: l["id"])
    n1 = next(l for l in drops if l["id"] >= 120
              and l["prev_price"] - l["price"] >= 500)
    d_n1 = cv(n1["prev_price"] - n1["price"])
    add("hard",
        I("n1", id=n1['id']),
        [{"type": "answer_match", "any_of": money_variants(d_n1)}],
        [f"goto /car/{n1['id']}", f"stop {mg(d_n1)}"])

    win_n2 = next(l for l in drops if l["id"] >= 350)
    plain_n2 = [l for l in active if not l["prev_price"]
                and l["id"] > win_n2["id"]][:2]
    assert len(plain_n2) == 2
    ids_n2 = sorted([win_n2["id"]] + [l["id"] for l in plain_n2])
    amt_n2 = pct_floor100(cv(win_n2["price"]), 90)
    add("hard",
        I("n2", a=ids_n2[0], b=ids_n2[1], c=ids_n2[2]),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": win_n2["id"], "amount": amt_n2}}] +
        [{"type": "db_record_absent", "table": "offers",
          "match": {"listing_id": l["id"]}} for l in plain_n2],
        LOGIN + [f"goto /car/{i}" for i in ids_n2]
        + [f"goto /car/{win_n2['id']}", f"fill 1 amount={amt_n2}"])

    n3 = next(l for l in drops if l["id"] >= 60 and l["id"] != n1["id"]
              and l["prev_price"] - l["price"] >= 800)
    amt_n3 = cv(2 * n3["price"] - n3["prev_price"])
    assert amt_n3 * 100 >= cv(n3["price"]) * 80
    add("hard",
        I("n3", id=n3['id']),
        [{"type": "db_record_exists", "table": "offers",
          "match": {"listing_id": n3["id"], "amount": amt_n3}}],
        LOGIN + [f"goto /car/{n3['id']}", f"fill 1 amount={amt_n3}"])

    l42 = by_id[42]
    add("easy",
        I("z1", n42=name(l42)),
        [{"type": "answer_match", "any_of": money_variants(cv(l42["price"]))}],
        ["goto /car/42", f"stop {mg(cv(l42['price']))}"])

    l303 = by_id[303]
    add("medium",
        I("z2", n303=name(l303)),
        [{"type": "answer_match",
          "any_of": [str(l303["days_listed"]),
                     f"{l303['days_listed']} days"]}],
        ["goto /car/303", f"stop {l303['days_listed']} days"])

    l120 = by_id[120]
    add("easy",
        I("z3", n120=name(l120)),
        [{"type": "answer_match", "answer": LZ(l120)["color"]},
         {"type": "answer_match", "answer": LZ(l120)["fuel"]}],
        ["goto /car/120", f"stop {LZ(l120)['color']}, {LZ(l120)['fuel']}"])

    n_tesla = sum(1 for l in active if l["brand"] == "Tesla")
    add("medium",
        I("z4"),
        [{"type": "answer_match", "answer": str(n_tesla)}],
        ["goto /cars?brand=Tesla", f"stop {n_tesla}"])

    metro = dbyname["Metro Cars"]
    add("easy",
        I("z5", dealer=DN('Metro Cars')),
        [{"type": "answer_match", "answer": str(metro["rating"])}],
        ["goto /dealers", f"stop {metro['rating']} stars"])

    c15, c16 = by_id[15], by_id[16]
    cheap71 = c15 if c15["price"] < c16["price"] else c16
    assert c15["price"] != c16["price"]
    add("easy",
        I("z6"),
        [{"type": "answer_match", "answer": str(cheap71["id"]),
          "none_of": [str(c16["id"] if cheap71 is c15 else c15["id"])]}],
        ["goto /compare", "fill 0 a=15; b=16", f"stop {cheap71['id']}"])

    q72 = finance_quote(cv(20000), 25, 4)
    add("medium",
        I("z7", p1=num(cv(20000))),
        [{"type": "answer_match", "any_of": money_variants(q72["monthly"])}],
        ["goto /finance", f"fill 0 price={cv(20000)}; down_pct=25; years=4",
         f"stop {mg(q72['monthly'])}"])

    add("easy",
        I("z8"),
        [{"type": "answer_match",
          "any_of": list(dict.fromkeys([mg(cv(10))] + money_variants(cv(10))))}],
        ["goto /rules", f"stop {mg(cv(10))}"])

    l33 = by_id[33]
    add("easy",
        I("z9", n33=name(l33)),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"listing_id": 33}}],
        LOGIN + ["goto /car/33", "fill 0"])

    add("medium",
        I("z10", city=V('city', 'Islamabad')),
        [{"type": "db_field_equals", "table": "users", "match": {"id": 1},
          "field": "phone", "value": "0345-2223344"},
         {"type": "db_field_equals", "table": "users", "match": {"id": 1},
          "field": "city", "value": V("city", "Islamabad")}],
        LOGIN + ["goto /account",
                 f"fill 0 phone=0345-2223344; city={V('city', 'Islamabad')}"])

    assert len(T) == 75, len(T)
    n_hard = sum(1 for t in T if t["difficulty"] == "hard")
    assert n_hard == 65, n_hard
    return T


def write(lang, out_dir):
    tasks = build(lang)
    out = os.path.join(out_dir, "visual_gari_tasks.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=1, ensure_ascii=False)
    n_hard = sum(1 for t in tasks if t["difficulty"] == "hard")
    print(f"wrote {len(tasks)} tasks ({n_hard} hard) to {out}")
