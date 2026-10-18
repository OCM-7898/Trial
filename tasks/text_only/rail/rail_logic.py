import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)

import importlib

sd = importlib.import_module("sites.text_only.rail.railapp.seed")
st = importlib.import_module("sites.text_only.rail.railapp.strings")

LOGIN = ["goto /login", "fill 0 username=priya_sharma; password=travel123"]

WEEK = [f"2026-04-{i:02d}" for i in range(6, 13)]


def hi_d(x):
    return str(x).translate(sd.DIGITS_HI)


def _variants(x):
    s = str(x)
    out = [s]
    if s.isdigit() and len(s) > 3 and s[0] != "0":
        g = f"{int(s):,}"
        if g != s:
            out.append(g)
    return out


def t_var(t):
    return [t, t[1:]] if t.startswith("0") else [t]


def dur_var(d):
    return [d,
            d.replace("h ", " hours ").replace("m", " minutes"),
            d.replace("h ", " hr ").replace("m", " min")]


def _bounded_in(target, text):
    t = " ".join(str(target).strip().lower().split())
    x = " ".join(str(text).strip().lower().split())
    pre = r"(?<!\d)(?<!\d\.)(?<!\d,)" if t and t[0].isdigit() else ""
    suf = r"(?!\d)(?!\.\d)(?!,\d)" if t and t[-1].isdigit() else ""
    return re.search(pre + re.escape(t) + suf, x) is not None


def no_collide(*parts):
    for i, a in enumerate(parts):
        for j, b in enumerate(parts):
            if i == j:
                continue
            for ta in a:
                for tb in b:
                    assert not _bounded_in(ta, tb), (ta, tb)


def halt_min(no, code):
    s = next(s for s in sd.TRAIN_BY_NO[no]["stops"] if s[0] == code)
    return ((int(s[2][:2]) * 60 + int(s[2][3:]))
            - (int(s[1][:2]) * 60 + int(s[1][3:])))


def booking_fare(b):
    return sd.fare(b[1], b[5], b[2], b[3])


sys.path.insert(0, HERE)
from rail_i18n import I18N, LIT, nd

I18N_CHECK = __import__("rail_i18n").check()


def make_V(lang):
    V = dict(LIT[lang])
    V["c_name"] = sd.user_name(lang)
    return V


def build(lang):
    V = make_V(lang)
    sn = lambda code: sd.station_name(code, lang)
    tn = lambda no: sd.train_name(no, lang)
    PK = I18N[lang]
    NAMES = {code: sn(code) for code in sd.STATIONS}
    NAMES.update({f"t{no}": tn(no) for no in sd.TRAIN_BY_NO})

    def I(key, **kw):
        return PK[key].format(**{**NAMES, **V, **kw})

    def F(no, cls, a=None, b=None):
        return sd.fare(no, cls, a, b, lang)

    def M(x):
        return sd.money(x, lang)

    def bf(b):
        return F(b[1], b[5], b[2], b[3])

    def NA(key):
        return ["N/A"] + list(V[key])

    def variants(x):
        out = _variants(x)
        if lang in ("bn", "hi", "ur"):
            out += [nd(v, lang) for v in list(out)]
        return list(dict.fromkeys(out))

    T = []

    def task(intent, eval_, solution, steps=30, tags=None):
        n = len(T) + 1
        t = {"id": f"rail-{n:03d}", "site": "rail", "intent": intent,
             "start_path": "/", "eval": eval_, "solution": solution,
             "max_steps": steps}
        if tags:
            t["tags"] = list(tags)
        T.append(t)

    def _am(targets, none_of=None):
        ev = {"type": "answer_match", "mode": "contains",
              "any_of": list(targets)}
        if none_of:
            bad = sorted({str(x) for x in none_of} - set(ev["any_of"]))
            bad = [x for x in bad if not any(
                x.lower() in str(t).lower() for t in ev["any_of"])]
            if bad:
                ev["none_of"] = bad
        return ev

    def ans(intent, targets, solution, steps=30, none_of=None,
            tags=None):
        task(intent, [_am(targets, none_of)], solution, steps, tags)

    def ans_parts(intent, parts, solution, steps=30, none_of=None,
                  tags=None):
        no_collide(*parts)
        none_of = none_of or [None] * len(parts)
        task(intent, [_am(p, n) for p, n in zip(parts, none_of)],
             solution, steps, tags)

    ALL_NOS = sorted(t["no"] for t in sd.TRAINS)
    STATUSES = ["CNF", "WL", "CAN"]

    def other_nos(no):
        return [n for n in ALL_NOS if n != no]

    dur1 = sd.dur_str(sd.seg("12903", "NDLS", "BCT")["dur_min"])
    ans(I("k1"),
        dur_var(dur1),
        ["goto /", "fill 0 from=NDLS; to=BCT; date=2026-04-06",
         f"stop {dur1}"],
        none_of=[sd.dur_str(sd.seg(no, "NDLS", "BCT")["dur_min"])
                 for no in sd.search("NDLS", "BCT", "2026-04-06")
                 if no != "12903"])

    f2 = min(F(no, "3A", "NDLS", "CNB")
             for no in sd.search("NDLS", "CNB", "2026-04-06")
             if "3A" in sd.TRAIN_BY_NO[no]["classes"])
    ans(I("k2"),
        variants(f2),
        ["goto /", "fill 0 from=NDLS; to=CNB; date=2026-04-06",
         f"stop {f2}"],
        none_of=[F(no, "3A", "NDLS", "CNB")
                 for no in sd.search("NDLS", "CNB", "2026-04-06")
                 if "3A" in sd.TRAIN_BY_NO[no]["classes"]
                 and F(no, "3A", "NDLS", "CNB") != f2])

    ans(I("k3"),
        ["CNF"], ["goto /pnr", "fill 0 pnr=6201234567", "stop CNF"],
        none_of=STATUSES)

    p4 = sd.passenger_name("6203456789", lang)
    ans(I("k4"),
        [p4], ["goto /pnr", "fill 0 pnr=6203456789", f"stop {p4}"])

    task(I("k5") + V["cred"],
         [{"type": "db_record_exists", "table": "bookings",
           "match": {"train_no": "12301", "class_code": "2A",
                     "passenger": V["kabir"], "date": "2026-04-06",
                     "from_code": "NDLS", "to_code": "HWH"}}],
         LOGIN + [
             "goto /book/12301?from=NDLS&to=HWH&date=2026-04-06&class=2A",
             f"fill 0 name={V['kabir']}; age=41; gender=M; berth=Upper",
             "fill 0"])

    task(I("k6") + V["cred"],
         [{"type": "db_record_exists", "table": "bookings",
           "match": {"passenger": V["sunita"], "class_code": "CC",
                     "train_no": "12417", "date": "2026-04-07",
                     "from_code": "NDLS", "to_code": "LKO"}}],
         LOGIN + [
             "goto /book/12417?from=NDLS&to=LKO&date=2026-04-07&class=CC",
             f"fill 0 name={V['sunita']}; age=55; gender=F; "
             "berth=No Preference",
             "fill 0"])

    task(I("k7") + V["cred"],
         [{"type": "db_record_exists", "table": "bookings",
           "match": {"passenger": V["farhan"], "berth": "Side Upper",
                     "train_no": "12841", "class_code": "SL",
                     "date": "2026-04-08",
                     "from_code": "HWH", "to_code": "MAS"}}],
         LOGIN + [
             "goto /book/12841?from=HWH&to=MAS&date=2026-04-08&class=SL",
             f"fill 0 name={V['farhan']}; age=23; gender=M; "
             "berth=Side Upper",
             "fill 0"])

    task(I("k8") + V["cred"],
         [{"type": "db_field_equals", "table": "bookings",
           "match": {"pnr": "6203456789"},
           "field": "status", "value": "CAN"}],
         LOGIN + ["goto /cancel/6203456789", "fill 0"])

    f9 = (F("12622", "2A", "HWH", "GHY")
          - F("12622", "3A", "HWH", "GHY"))
    ans(I("k9"),
        variants(f9), ["goto /train/12622", f"stop {f9}"])

    assert not sd.search("SC", "PUNE", "2026-04-07")
    assert any(sd.search("SC", "PUNE", d) for d in WEEK)
    ans(I("k10"),
        NA("na_no_train_day"),
        ["goto /", "fill 0 from=SC; to=PUNE; date=2026-04-07",
         "stop N/A"])

    assert all(b[0] != "6299999999" for b in sd.BOOKINGS)
    ans(I("k11"),
        NA("na_no_booking"), ["goto /pnr", "fill 0 pnr=6299999999", "stop N/A"])

    task(I("k12"),
         [{"type": "db_record_exists", "table": "messages",
           "match": {"subject": V["c_subject"], "name": V["c_name"],
                     "email": V["c_email"]}}],
         ["goto /contact",
          f"fill 0 name={V['c_name']}; email={V['c_email']}; "
          f"subject={V['c_subject']}; message={V['c_message']}"])

    task(I("k13") + V["cred"],
         [{"type": "db_field_equals", "table": "users",
           "match": {"username": "priya_sharma"},
           "field": "mobile", "value": "9876501234"}],
         LOGIN + ["goto /account/profile", "fill 0 mobile=9876501234"])

    ans(I("k14"),
        variants(M(240)), ["goto /rules", f"stop {M(240)}"])

    assert not any(sd.serves(t, "JP", "LKO") for t in sd.TRAINS)
    ans(I("k15"),
        NA("na_no_route"),
        ["goto /", "fill 0 from=JP; to=LKO; date=2026-04-09",
         "stop N/A"])

    assert len(T) == 15

    dists = {t["no"]: t["stops"][-1][4] for t in sd.TRAINS}
    longest = max(dists, key=dists.get)
    assert sorted(dists.values())[-1] > sorted(dists.values())[-2]
    ans_parts(I("a1"),
              [[longest], variants(dists[longest])],
              ["goto /trains", f"goto /train/{longest}",
               f"stop {longest}, {dists[longest]} km"],
              none_of=[other_nos(longest), None], tags=["memory"])

    nstops = {t["no"]: len(t["stops"]) for t in sd.TRAINS}
    most_stops = max(nstops, key=nstops.get)
    assert sorted(nstops.values())[-1] > sorted(nstops.values())[-2]
    ans_parts(I("a2"),
              [[most_stops], [str(nstops[most_stops])]],
              ["goto /trains", f"goto /train/{most_stops}",
               f"stop {most_stops} with {nstops[most_stops]} stops"],
              none_of=[other_nos(most_stops), None], tags=["memory"])

    daily = [t for t in sd.TRAINS if len(t["days"]) == 7]
    arrs = {t["no"]: t["stops"][-1][1] for t in daily}
    late = max(arrs, key=arrs.get)
    assert sorted(arrs.values())[-1] > sorted(arrs.values())[-2]
    ans_parts(I("a3"),
              [[late], t_var(arrs[late])],
              ["goto /trains", f"stop {late} at {arrs[late]}"],
              none_of=[other_nos(late), None])

    halts = [(halt_min(t["no"], s[0]), t["no"], s[0])
             for t in sd.TRAINS for s in t["stops"] if s[1] and s[2]]
    halts.sort(reverse=True)
    assert halts[0][0] > halts[1][0]
    hm, hno, hcode = halts[0]
    ans_parts(I("a4"),
              [[hno], [str(hm)]],
              ["goto /trains", f"goto /train/{hno}",
               f"stop {hno}, {hm} minutes at {sn(hcode)}"],
              none_of=[other_nos(hno), None], tags=["memory"])

    sl_full = {t["no"]: F(t["no"], "SL") for t in sd.TRAINS
               if "SL" in t["classes"]}
    sl_min = min(sl_full, key=sl_full.get)
    assert sorted(sl_full.values())[0] < sorted(sl_full.values())[1]
    ans_parts(I("a5"),
              [[sl_min], variants(sl_full[sl_min])],
              ["goto /trains", f"goto /train/{sl_min}",
               f"stop {sl_min}, {sl_full[sl_min]}"],
              none_of=[other_nos(sl_min), None], tags=["memory"])

    fa_full = {t["no"]: F(t["no"], "1A") for t in sd.TRAINS
               if "1A" in t["classes"]}
    fa_max = max(fa_full, key=fa_full.get)
    assert sorted(fa_full.values())[-1] > sorted(fa_full.values())[-2]
    ans_parts(I("a6"),
              [[fa_max], variants(fa_full[fa_max])],
              ["goto /trains", f"goto /train/{fa_max}",
               f"stop {fa_max}, {fa_full[fa_max]}"],
              none_of=[other_nos(fa_max), None], tags=["memory"])

    from collections import Counter
    scount = Counter(s[0] for t in sd.TRAINS for s in t["stops"])
    three = sorted(c for c, n in scount.items() if n == 3)
    assert len(three) == 2
    ans_parts(I("a7"),
              [[sn(three[0]), three[0]], [sn(three[1]), three[1]]],
              ["goto /trains",
               f"stop {sn(three[0])} and {sn(three[1])}"],
              none_of=[[sn(c) for c in scount if c not in three]] * 2,
              tags=["memory"])

    deps = {t["no"]: t["stops"][0][2] for t in daily}
    early = min(deps, key=deps.get)
    assert sorted(deps.values())[0] < sorted(deps.values())[1]
    ans_parts(I("a8"),
              [[early], t_var(deps[early])],
              ["goto /trains", f"stop {early} at {deps[early]}"],
              none_of=[other_nos(early), None])

    assert sd.search("PNBE", "HWH", "2026-04-07") == ["12301"]
    assert "Tue" not in sd.TRAIN_BY_NO["12301"]["days"]
    ans(I("b1"),
        ["12301"],
        ["goto /", "fill 0 from=PNBE; to=HWH; date=2026-04-07",
         "stop 12301"], none_of=other_nos("12301"))

    assert sd.search("NJP", "GHY", "2026-04-08") == ["12622"]
    assert "Wed" not in sd.TRAIN_BY_NO["12622"]["days"]
    ans(I("b2"),
        ["12622"],
        ["goto /", "fill 0 from=NJP; to=GHY; date=2026-04-08",
         "stop 12622"], none_of=other_nos("12622"))

    counts = {d: len(sd.search("NDLS", "CNB", d)) for d in WEEK}
    busiest = max(counts, key=counts.get)
    assert sorted(counts.values())[-1] > sorted(counts.values())[-2]
    ans_parts(I("b3"),
              [[busiest, V["sunday"]], variants(counts[busiest])],
              sum([["goto /", f"fill 0 from=NDLS; to=CNB; date={d}"]
                   for d in WEEK], [])
              + [f"stop {busiest}, {counts[busiest]} trains"], 40,
              none_of=[[d for d in WEEK if d != busiest], None],
              tags=["memory"])

    nd_pnbe = sum(1 for d in WEEK if sd.runs_on("12301", d, "PNBE"))
    ans(I("b4"),
        variants(nd_pnbe),
        ["goto /station/PNBE", f"stop {nd_pnbe}"])

    b_vik = next(b for b in sd.BOOKINGS if b[0] == "6203456789")
    assert b_vik[5] in ("1A", "2A", "3A", "CC") and b_vik[11] == "CNF"
    r28 = bf(b_vik) - M(240)
    ans(I("c1") + V["cred"],
        variants(r28),
        LOGIN + ["goto /account/bookings", "goto /rules",
                 f"stop {r28}"])

    b_ani = next(b for b in sd.BOOKINGS if b[0] == "6202345678")
    assert b_ani[11] == "WL"
    r29 = bf(b_ani) - M(20)
    ans(I("c2") + V["cred"],
        variants(r29),
        LOGIN + ["goto /account/bookings", "goto /rules",
                 f"stop {r29}"])

    assert sd.fare("12615", "3A") % 4 == 0
    f30 = F("12615", "3A")
    assert f30 % 4 == 0
    r30 = f30 * 3 // 4
    ans(I("c3"),
        variants(r30),
        ["goto /train/12615", "goto /rules", f"stop {r30}"])

    b_mee = next(b for b in sd.BOOKINGS if b[0] == "6204567890")
    b31 = next(b for b in sd.BOOKINGS
               if b[5] in ("1A", "2A", "3A", "CC") and b[11] == "CNF"
               and b[0] != "6203456789" and booking_fare(b) % 2 == 0)
    f31 = bf(b31)
    assert f31 % 2 == 0
    r31 = f31 // 2
    ans(I("c4", pnr=b31[0]) + V["cred"],
        variants(r31),
        LOGIN + ["goto /account/bookings", "goto /rules",
                 f"stop {r31}"])

    f32 = 2 * F("12559", "2A")
    ans(I("c5"),
        variants(f32), ["goto /train/12559", f"stop {f32}"])

    cnf_sum = sum(bf(b) for b in sd.BOOKINGS
                  if b[11] == "CNF")
    ans(I("c6") + V["cred"],
        variants(cnf_sum),
        LOGIN + ["goto /account/bookings", f"stop {cnf_sum}"])

    f34 = (F("12615", "3A", "AGC", "SC")
           - F("12615", "SL", "AGC", "SC"))
    ans(I("c7"),
        variants(f34),
        ["goto /train/12615?from=AGC&to=SC&date=2026-04-06",
         f"stop {f34}"])

    legs = (F("12301", "SL", "NDLS", "CNB")
            + F("12559", "SL", "CNB", "BSB"))
    direct = F("12559", "SL", "NDLS", "BSB")
    save = legs - direct
    assert save > 0
    ans(I("c8"),
        variants(save),
        ["goto /train/12559?from=NDLS&to=BSB&date=2026-04-07",
         "goto /train/12301?from=NDLS&to=CNB&date=2026-04-06",
         "goto /train/12559?from=CNB&to=BSB&date=2026-04-07",
         f"stop {save}"])

    seats36 = sum(sd.TRAIN_BY_NO["12904"]["classes"].values())
    assert not sd.TRAIN_BY_NO["12904"]["wl"]
    ans(I("c9"),
        variants(seats36), ["goto /train/12904", f"stop {seats36}"])

    fa, fm = bf(b_ani), bf(b_mee)
    assert fa != fm
    assert (fa > fm) == (booking_fare(b_ani) > booking_fare(b_mee))
    p_ani, p_mee2 = (sd.passenger_name("6202345678", lang),
                     sd.passenger_name("6204567890", lang))
    hi_b = p_ani if fa > fm else p_mee2
    diff37 = abs(fa - fm)
    ans_parts(I("c10", anita=p_ani, meera=p_mee2) + V["cred"],
              [[hi_b, hi_b.split()[0]], variants(diff37)],
              LOGIN + ["goto /account/bookings",
                       f"stop {hi_b} by {diff37}"])

    cls38_en = {c: sd.fare("12302", c)
                for c in sd.TRAIN_BY_NO["12302"]["classes"]}
    over_en = {c: f for c, f in cls38_en.items() if f > 1000}
    pick38 = min(over_en, key=over_en.get)
    assert any(f <= 1000 for f in cls38_en.values())
    assert sorted(over_en.values())[0] < sorted(over_en.values())[1]
    cls38 = {c: F("12302", c) for c in cls38_en}
    t1000 = M(1000)
    over = {c: f for c, f in cls38.items() if f > t1000}
    assert min(over, key=over.get) == pick38
    assert any(f <= t1000 for f in cls38.values())
    ans_parts(I("d1", t1000=nd(t1000, lang)),
              [[pick38], variants(over[pick38])],
              ["goto /train/12302",
               f"stop {pick38} at {over[pick38]}"])

    cls39_en = {c: sd.fare("12659", c)
                for c in sd.TRAIN_BY_NO["12659"]["classes"]}
    under_en = {c: f for c, f in cls39_en.items() if f <= 500}
    pick39 = max(under_en, key=under_en.get)
    assert any(f > 500 for f in cls39_en.values())
    assert len(under_en) > 1
    cls39 = {c: F("12659", c) for c in cls39_en}
    t500 = M(500)
    under = {c: f for c, f in cls39.items() if f <= t500}
    assert max(under, key=under.get) == pick39 and len(under) > 1
    assert any(f > t500 for f in cls39.values())
    ans_parts(I("d2", t500=nd(t500, lang)),
              [[pick39], variants(under[pick39])],
              ["goto /train/12659",
               f"stop {pick39} at {under[pick39]}"],
              none_of=[[c for c in cls39 if c != pick39],
                       [f for c, f in cls39.items() if c != pick39]])

    seg_sl = {no: F(no, "SL", "NDLS", "CNB")
              for t in sd.TRAINS for no in [t["no"]]
              if sd.serves(t, "NDLS", "CNB")
              and "SL" in t["classes"]}
    assert len(seg_sl) > 1
    pick40 = min(seg_sl, key=seg_sl.get)
    assert sorted(seg_sl.values())[0] < sorted(seg_sl.values())[1]
    ans_parts(I("d3"),
              [[pick40], variants(seg_sl[pick40])],
              ["goto /", "fill 0 from=NDLS; to=CNB; date=2026-04-12",
               f"stop {pick40} at {seg_sl[pick40]}"])

    a41 = F("12622", "1A")
    b41 = F("12615", "2A", "NDLS", "BPL")
    assert a41 != b41
    win41 = "12622" if a41 > b41 else "12615"
    ans_parts(I("d4"),
              [[win41], variants(max(a41, b41))],
              ["goto /train/12622",
               "goto /train/12615?from=NDLS&to=BPL&date=2026-04-06",
               f"stop {win41} at {max(a41, b41)}"])

    rtm = {t["no"]: next(s for s in t["stops"] if s[0] == "RTM")[2]
           for t in sd.TRAINS
           if any(s[0] == "RTM" and s[2] for s in t["stops"])}
    pick42 = min(rtm, key=rtm.get)
    assert sorted(rtm.values())[0] < sorted(rtm.values())[1]
    ans_parts(I("d5"),
              [[pick42], t_var(rtm[pick42])],
              ["goto /station/RTM",
               f"stop {pick42} at {rtm[pick42]}"])

    wl_pnrs = [b[0] for b in sd.BOOKINGS if b[11] == "WL"]
    assert wl_pnrs == ["6202345678"]
    task(I("e1") + V["cred"],
         [{"type": "db_field_equals", "table": "bookings",
           "match": {"pnr": "6202345678"},
           "field": "status", "value": "CAN"},
          {"type": "db_field_equals", "table": "bookings",
           "match": {"pnr": "6201234567"},
           "field": "status", "value": "CNF"},
          {"type": "db_field_equals", "table": "bookings",
           "match": {"pnr": "6208901234"},
           "field": "status", "value": "CNF"}],
         LOGIN + ["goto /account/bookings",
                  "goto /cancel/6202345678", "fill 0"])

    late_pnrs = sorted(b[0] for b in sd.BOOKINGS
                       if b[4] >= "2026-04-10" and b[11] != "CAN")
    assert late_pnrs == ["6203456789", "6208901234"]
    task(I("e2") + V["cred"],
         [{"type": "db_field_equals", "table": "bookings",
           "match": {"pnr": "6203456789"},
           "field": "status", "value": "CAN"},
          {"type": "db_field_equals", "table": "bookings",
           "match": {"pnr": "6208901234"},
           "field": "status", "value": "CAN"},
          {"type": "db_field_equals", "table": "bookings",
           "match": {"pnr": "6206789012"},
           "field": "status", "value": "CNF"},
          {"type": "db_field_equals", "table": "bookings",
           "match": {"pnr": "6201234567"},
           "field": "status", "value": "CNF"}],
         LOGIN + ["goto /account/bookings",
                  "goto /cancel/6203456789", "fill 0",
                  "goto /cancel/6208901234", "fill 0"])

    task(I("e3") + V["cred"],
         [{"type": "db_field_equals", "table": "users",
           "match": {"username": "priya_sharma"},
           "field": "email", "value": "priya.s@newmail.in"},
          {"type": "db_field_equals", "table": "users",
           "match": {"username": "priya_sharma"},
           "field": "mobile", "value": "9812399999"}],
         LOGIN + ["goto /account/profile",
                  "fill 0 email=priya.s@newmail.in; mobile=9812399999"])

    p_mee = sd.passenger_name("6204567890", lang)
    task(I("e4"),
         [{"type": "db_record_exists", "table": "messages",
           "match": {"subject": V["pnr_query"],
                     "message": V["refund_status_for"] + p_mee,
                     "name": V["c_name"], "email": V["c_email"]}}],
         ["goto /pnr", "fill 0 pnr=6204567890", "goto /contact",
          f"fill 0 name={V['c_name']}; email={V['c_email']}; "
          f"subject={V['pnr_query']}; "
          f"message={V['refund_status_for']}{p_mee}"])

    b_roh = next(b for b in sd.BOOKINGS if b[0] == "6201234567")
    assert sd.runs_on("12049", "2026-04-06", "NDLS")
    p_roh = sd.passenger_name("6201234567", lang)
    task(I("e5") + V["cred"],
         [{"type": "db_record_exists", "table": "bookings",
           "match": {"train_no": "12049", "class_code": "CC",
                     "passenger": p_roh, "age": b_roh[8],
                     "date": "2026-04-06"}}],
         LOGIN + ["goto /pnr", "fill 0 pnr=6201234567",
                  "goto /book/12049?from=NDLS&to=AGC&date=2026-04-06"
                  "&class=CC",
                  f"fill 0 name={p_roh}; age={b_roh[8]}; gender=M; "
                  "berth=No Preference",
                  "fill 0"])

    new_pnr = str(6210000000 + len(sd.BOOKINGS) + 1)
    task(I("e6") + V["cred"],
         [{"type": "db_record_exists", "table": "bookings",
           "match": {"passenger": V["nisha"], "status": "CAN",
                     "train_no": "12138", "class_code": "SL",
                     "date": "2026-04-06"}}],
         LOGIN + [
             "goto /book/12138?from=BCT&to=BPL&date=2026-04-06&class=SL",
             f"fill 0 name={V['nisha']}; age=30; gender=F; berth=Lower",
             "fill 0", f"goto /cancel/{new_pnr}", "fill 0"])

    order49 = sd.search("NDLS", "CNB", "2026-04-06")
    first49 = order49[0]
    assert "CC" in sd.TRAIN_BY_NO[first49]["classes"]
    assert len(order49) > 1
    task(I("f1") + V["cred"],
         [{"type": "db_record_exists", "table": "bookings",
           "match": {"train_no": first49, "class_code": "CC",
                     "passenger": V["anaya"],
                     "date": "2026-04-06"}}],
         LOGIN + [
             "goto /", "fill 0 from=NDLS; to=CNB; date=2026-04-06",
             f"goto /book/{first49}?from=NDLS&to=CNB&date=2026-04-06"
             "&class=CC",
             f"fill 0 name={V['anaya']}; age=27; gender=F; "
             "berth=No Preference",
             "fill 0"])

    opts50 = [(F(no, c, "NDLS", "AGC"), no, c)
              for no in sd.search("NDLS", "AGC", "2026-04-06")
              for c in sd.TRAIN_BY_NO[no]["classes"]]
    opts50.sort()
    assert opts50[0][0] < opts50[1][0]
    _, no50, cls50 = opts50[0]
    task(I("f2") + V["cred"],
         [{"type": "db_record_exists", "table": "bookings",
           "match": {"train_no": no50, "class_code": cls50,
                     "passenger": V["ritu"],
                     "date": "2026-04-06"}}],
         LOGIN + [
             "goto /", "fill 0 from=NDLS; to=AGC; date=2026-04-06",
             f"goto /book/{no50}?from=NDLS&to=AGC&date=2026-04-06"
             f"&class={cls50}",
             f"fill 0 name={V['ritu']}; age=24; gender=F; "
             "berth=No Preference",
             "fill 0"])

    order51 = sd.search("NDLS", "CNB", "2026-04-08")
    last51 = order51[-1]
    assert len(order51) > 1 and "3A" in sd.TRAIN_BY_NO[last51]["classes"]
    task(I("f3") + V["cred"],
         [{"type": "db_record_exists", "table": "bookings",
           "match": {"train_no": last51, "class_code": "3A",
                     "passenger": V["mohan"],
                     "date": "2026-04-08"}}],
         LOGIN + [
             "goto /", "fill 0 from=NDLS; to=CNB; date=2026-04-08",
             f"goto /book/{last51}?from=NDLS&to=CNB&date=2026-04-08"
             "&class=3A",
             f"fill 0 name={V['mohan']}; age=52; gender=M; berth=Lower",
             "fill 0"])

    assert not sd.search("NDLS", "HWH", "2026-04-09")
    alt52 = sd.search("NDLS", "HWH", "2026-04-10")
    assert alt52 == ["12301"]
    task(I("f4") + V["cred"],
         [{"type": "db_record_exists", "table": "bookings",
           "match": {"train_no": "12301", "class_code": "2A",
                     "passenger": V["sara"],
                     "date": "2026-04-10"}}],
         LOGIN + [
             "goto /", "fill 0 from=NDLS; to=HWH; date=2026-04-09",
             "goto /", "fill 0 from=NDLS; to=HWH; date=2026-04-10",
             "goto /book/12301?from=NDLS&to=HWH&date=2026-04-10"
             "&class=2A",
             f"fill 0 name={V['sara']}; age=33; gender=F; berth=Upper",
             "fill 0"])

    assert "1A" not in sd.TRAIN_BY_NO["12615"]["classes"]
    ans(I("g1"),
        NA("na_class"), ["goto /train/12615", "stop N/A"])

    assert not sd.runs_on("12904", "2026-04-08", "BCT")
    task(I("g2"),
         [{"type": "answer_match", "mode": "contains",
           "any_of": NA("na_book_refused")},
          {"type": "db_record_absent", "table": "bookings",
           "match": {"train_no": "12904", "date": "2026-04-08"}}],
         ["goto /train/12904?from=BCT&to=NDLS&date=2026-04-08",
          "stop N/A"])

    assert not any(sd.serves(t, "LKO", "AGC") for t in sd.TRAINS)
    ans(I("g3"),
        NA("na_no_route2"),
        ["goto /", "fill 0 from=LKO; to=AGC; date=2026-04-07",
         "stop N/A"])

    assert not sd.search("RTM", "NDLS", "2026-04-06")
    assert any(sd.search("RTM", "NDLS", d) for d in WEEK)
    ans(I("g4"),
        NA("na_no_train_day2"),
        ["goto /", "fill 0 from=RTM; to=NDLS; date=2026-04-06",
         "stop N/A"])

    assert not any(sd.serves(t, "GHY", "HWH") for t in sd.TRAINS)
    ans(I("g5"),
        NA("na_no_route3"),
        ["goto /", "fill 0 from=GHY; to=HWH; date=2026-04-08",
         "stop N/A"])

    assert not any("surcharge" in v.lower()
                   for v in st.STRINGS["en"].values())
    ans(I("g6"),
        NA("na_surcharge"), ["goto /", "goto /rules", "stop N/A"])

    n_cnb = scount["CNB"]
    ans(I("h1"),
        [str(n_cnb)], ["goto /station/CNB", f"stop {n_cnb}"])

    n_daily = len(daily)
    ans(I("h2"),
        [str(n_daily)], ["goto /trains", f"stop {n_daily}"])

    ans(I("h3"),
        ["CAN"], ["goto /pnr", "fill 0 pnr=6207890123", "stop CAN"],
        none_of=STATUSES)

    h62 = halt_min("12615", "NGP")
    ans(I("h4"),
        [str(h62)], ["goto /train/12615", f"stop {h62}"])

    after20 = sorted(t["no"] for t in sd.TRAINS
                     if t["stops"][0][2] >= "20:00")
    assert len(after20) == 2
    ans_parts(I("h5"),
              [[after20[0]], [after20[1]]],
              ["goto /trains", f"stop {after20[0]} and {after20[1]}"])

    two_short = sorted(dists.values())[:2]
    assert two_short[1] < sorted(dists.values())[2]
    s64 = sum(two_short)
    ans(I("h6"),
        variants(s64), ["goto /trains", f"stop {s64}"], tags=["memory"])

    n65 = sum(1 for b in sd.BOOKINGS if b[4] < "2026-04-09")
    ans(I("h7") + V["cred"],
        [str(n65)],
        LOGIN + ["goto /account/bookings", f"stop {n65}"])

    exp = max(sd.BOOKINGS, key=booking_fare)
    exp_f = bf(exp)
    assert sorted(map(bf, sd.BOOKINGS))[-1] > \
        sorted(map(bf, sd.BOOKINGS))[-2]
    assert max(sd.BOOKINGS, key=bf) is exp
    ans_parts(I("h8") + V["cred"],
              [[exp[0]], variants(exp_f)],
              LOGIN + ["goto /account/bookings",
                       f"stop {exp[0]} at {exp_f}"])

    arr67 = sd.TRAIN_BY_NO["12559"]["stops"][-1]
    ans_parts(I("h9"),
              [t_var(arr67[1]), [str(arr67[3]), V["two"]]],
              ["goto /train/12559",
               f"stop {arr67[1]} on day {arr67[3]}"])

    km68 = (sd._km(sd.TRAIN_BY_NO["12659"], "ABR")
            - sd._km(sd.TRAIN_BY_NO["12659"], "AII"))
    ans(I("h10"),
        [str(km68)], ["goto /train/12659", f"stop {km68}"])

    km69 = (sd._km(sd.TRAIN_BY_NO["12615"], "NGP")
            - sd._km(sd.TRAIN_BY_NO["12615"], "BPL"))
    ans(I("h11"),
        [str(km69)], ["goto /train/12615", f"stop {km69}"])

    d69 = sd.dur_str(sd.seg("12723")["dur_min"])
    ans(I("h12"),
        dur_var(d69),
        ["goto /", "fill 0 from=SC; to=PUNE; date=2026-04-06",
         f"stop {d69}"],
        none_of=[sd.dur_str(sd.seg(no, "SC", "PUNE")["dur_min"])
                 for no in sd.search("SC", "PUNE", "2026-04-06")
                 if no != "12723"])

    wl70 = sd.TRAIN_BY_NO["12301"]["wl"]["3A"]
    ans(I("h13"),
        [str(wl70)], ["goto /train/12301", f"stop WL {wl70}"])

    a_msg = V["anomaly_msg"].format(JP=sn("JP"), AII=sn("AII"))
    task(I("h14", anomaly_msg=a_msg),
         [{"type": "db_record_exists", "table": "messages",
           "match": {"subject": V["anomaly_subject"],
                     "message": a_msg,
                     "name": V["c_name"], "email": V["c_email"]}}],
         ["goto /contact",
          f"fill 0 name={V['c_name']}; email={V['c_email']}; "
          f"subject={V['anomaly_subject']}; message={a_msg}"])

    n73 = len(sd.BOOKINGS)
    ans(I("h15") + V["cred"],
        [str(n73)],
        LOGIN + ["goto /account/bookings", f"stop {n73}"])

    n74 = sd.TRAIN_BY_NO["12301"]["classes"]["2A"]
    ans(I("h16"),
        [str(n74)],
        ["goto /", "fill 0 from=NDLS; to=HWH; date=2026-04-06",
         f"stop {n74}"])

    f75 = F("12138", "SL", "BCT", "BPL")
    ans(I("h17"),
        variants(f75),
        ["goto /", "fill 0 from=BCT; to=BPL; date=2026-04-06",
         f"stop {f75}"],
        none_of=[F("12138", c, "BCT", "BPL")
                 for c in sd.TRAIN_BY_NO["12138"]["classes"] if c != "SL"])

    assert len(T) == 75, len(T)
    return T


def write(lang, out_dir):
    T = build(lang)
    out = os.path.join(out_dir, "rail_tasks.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(T, f, indent=1, ensure_ascii=False)
    print(f"wrote {len(T)} tasks to {out}")
