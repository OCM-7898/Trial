import json
import os
import re
import sqlite3

import requests
from bs4 import BeautifulSoup

import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from benchmark.harness import headers as _harness_headers

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SELAM = os.path.join(ROOT, "sites", "text_only", "selam", "tasks")
SEED_DB = os.path.join(ROOT, "sites", "text_only", "selam", "data",
                       "seed.db")
EN_BASE = "http://127.0.0.1:8017"
BASES = {"en": EN_BASE, "am": "http://127.0.0.1:8053",
         "bn": "http://127.0.0.1:8054", "hi": "http://127.0.0.1:8055",
         "ur": "http://127.0.0.1:8056"}
I18N_DIR = os.path.join(ROOT, "sites", "text_only", "selam", "app", "i18n")
_sys.path.insert(0, HERE)
from selam_i18n import I18N, LIT

MAX_STEPS = 40


def load_tasks(lang):
    path = os.path.join(SELAM, f"tasks_{lang}.json")
    with open(path, encoding="utf-8") as f:
        return {t["task_id"]: t for t in json.load(f)}


_CON = None


def db():
    global _CON
    if _CON is None:
        _CON = sqlite3.connect(SEED_DB)
        _CON.row_factory = sqlite3.Row
    return _CON


def q(sql, *args):
    return [dict(r) for r in db().execute(sql, args).fetchall()]


def q1(sql, *args):
    rows = q(sql, *args)
    assert len(rows) == 1, (sql, args, rows)
    return rows[0]


def surname(pnr, lang="en"):
    return q1(f"SELECT surname_{lang} s FROM bookings WHERE pnr=?", pnr)["s"]


def booking_id(pnr):
    return q1("SELECT id FROM bookings WHERE pnr=?", pnr)["id"]


def segs(pnr):
    return q("SELECT s.*, f.flight_no, f.date FROM segments s"
             " JOIN bookings b ON b.id=s.booking_id"
             " JOIN flights f ON f.id=s.flight_id"
             " WHERE b.pnr=? ORDER BY s.sequence", pnr)


def member(no):
    return q1("SELECT * FROM loyalty_members WHERE member_no=?", no)


def no_collide(*vals):
    ss = [str(v) for v in vals]
    assert all(a not in b for a in ss for b in ss if a is not b), ss


def money_forms(x):
    out = [str(int(x))] if float(x) == int(x) else []
    out += [f"{float(x):.2f}"]
    if int(x) >= 1000:
        out.append(f"{int(x):,}")
    return list(dict.fromkeys(out))


class Probe:

    def __init__(self, lang="en"):
        self.lang = lang
        self.base = BASES[lang]
        self.reset()

    def reset(self):
        self.s = requests.Session()
        r = self.s.post(self.base + "/__reset__", timeout=10,
                        headers=_harness_headers())
        r.raise_for_status()

    def html(self, path):
        return self.s.get(self.base + path, timeout=10).text

    def text(self, path):
        soup = BeautifulSoup(self.html(path), "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        return " ".join(soup.get_text(" ", strip=True).split())

    def login(self, pnr):
        self.s.post(self.base + "/manage",
                    data={"pnr": pnr, "surname": surname(pnr, self.lang)},
                    timeout=10)

    def miles_login(self, member_no):
        m = member(member_no)
        self.s.post(self.base + "/miles/account",
                    data={"member_no": member_no,
                          "surname": m[f"last_name_{self.lang}"]},
                    timeout=10)

    def form_index(self, path, field):
        soup = BeautifulSoup(self.html(path), "html.parser")
        for i, f in enumerate(soup.find_all("form")):
            if f.find(attrs={"name": field}) is not None:
                return i
        raise AssertionError(f"no form with field {field!r} on {path}")

    def on_page(self, path, *needles):
        t = self.text(path)
        for n in needles:
            alts = n if isinstance(n, (list, tuple)) else [n]
            assert any(str(a) in t for a in alts), \
                f"none of {alts!r} visible on {path}: {t[:300]}"
        return t


def build(lang):
    src = load_tasks(lang)
    p = Probe(lang)
    V = dict(LIT[lang])
    PK = I18N[lang]
    with open(os.path.join(I18N_DIR, f"{lang}.json"), encoding="utf-8") as f:
        SITE_T = json.load(f)

    def I(key, **kw):
        return PK[key].format(**{**V, **kw})

    def C(base):
        return f"{base}_{lang}"

    def sn(pnr):
        return surname(pnr, lang)

    def ln(member_no):
        return member(member_no)[C("last_name")]

    T = []
    n = 0

    def task(intent, eval_, solution, steps=MAX_STEPS):
        nonlocal n
        n += 1
        T.append({"id": f"selam-{n:03d}", "site": "selam",
                  "intent": intent, "start_path": "/", "eval": eval_,
                  "solution": solution, "max_steps": steps})

    def art(tid, solution, answer=None, extra=None, intent=None):
        t = src[tid]
        refs = t["eval"].get("reference_answers", {})
        must = refs.get("must_include", [])
        if answer is None:
            answer = "; ".join(str(m) for m in must) if must else "done"
        task(intent if intent is not None else t["intent"],
             [{"type": "selam_score", "task_id": tid, "lang": lang}]
             + list(extra or []),
             solution + [f"stop {answer}"])

    def ans_ev(value, also=None, exact=False, none_of=None):
        ev = {"type": "answer_match"}
        if exact:
            ev["mode"] = "exact"
        vs = (money_forms(value) if isinstance(value, (int, float))
              else [str(value)]) + (also or [])
        vs = list(dict.fromkeys(vs))
        if len(vs) > 1:
            ev["any_of"] = vs
        else:
            ev["answer"] = vs[0]
        if none_of:
            bad = sorted({str(x) for x in none_of} - set(vs))
            bad = [x for x in bad if not any(
                x.lower() in str(t).lower() for t in vs)]
            if bad:
                ev["none_of"] = bad
        return ev

    def exists(table, match):
        return {"type": "db_record_exists", "table": table, "match": match}

    def absent(table, match):
        return {"type": "db_record_absent", "table": table, "match": match}

    NR = V["nr"]

    def manage_login(pnr):
        return ["goto /manage",
                f"fill {manage_form} pnr={pnr}; surname={sn(pnr)}"]

    def miles_login_steps(no):
        return ["goto /miles/account",
                f"fill {miles_form} member_no={no}; "
                f"surname={ln(no)}"]

    b = p.html("/book/results?origin=ADD&destination=DXB"
               "&depart=2026-04-20&adults=1")
    itinerary = re.search(
        r'href="/book/passengers\?itinerary=([^"&]+)"', b).group(1)

    p.login("W7JKUF")
    b = p.html("/manage/W7JKUF/change")
    seg6 = re.search(r'name="segment_id"[^>]*value="(\d+)"', b).group(1)
    b = p.html(f"/manage/W7JKUF/change?segment_id={seg6}"
               "&new_date=2026-04-26")
    seg6_row = segs("W7JKUF")[0]
    later6 = [r["id"] for r in q(
        "SELECT id FROM flights WHERE route_id=(SELECT route_id FROM "
        "flights WHERE id=?) AND date>? ORDER BY date",
        seg6_row["flight_id"], seg6_row["date"])]
    offered6 = [int(x) for x in
                re.findall(r'name="new_flight_id"[^>]*value="(\d+)"', b)]
    flight6 = str(next(f for f in offered6 if f in later6))

    p.reset()
    p.login("N9JKBF")
    b = p.html("/manage/N9JKBF/seats")
    seats_html = b
    def free_seat(html_, kind):
        return next(m.group(2) for m in re.finditer(
            r'<button class="seat([^"]*)"[^>]*name="seat_no" '
            r'value="([0-9]+[A-Z])"', html_)
            if kind in m.group(1) and "taken" not in m.group(1))
    seat10 = free_seat(b, "aisle")
    seat_window = free_seat(b, "window")
    assert seat10 != seat_window
    window_seats = [m.group(2) for m in re.finditer(
        r'<button class="seat([^"]*)"[^>]*name="seat_no" '
        r'value="([0-9]+[A-Z])"', b)
        if "window" in m.group(1) and "taken" not in m.group(1)]
    assert seat_window in window_seats

    b = p.html("/onboard/wifi?flight_no=SM106&date=2026-03-19")
    package21 = re.findall(r'name="package_id"[^>]*value="(\d+)"', b)[-1]
    wifi_form = p.form_index(
        "/onboard/wifi?flight_no=SM106&date=2026-03-19", "package_id")

    code26 = re.search(r'href="/partners/evisa\?code=([A-Z0-9-]+)"',
                       p.html("/partners/evisa")).group(1)
    b = p.html("/partners/riftdrive?airport=NBO&passengers=2"
               "&pickup=2026-04-12")
    offer28 = re.search(r'name="offer_id"[^>]*value="(\d+)"', b).group(1)
    rift_form = p.form_index(
        "/partners/riftdrive?airport=NBO&passengers=2&pickup=2026-04-12",
        "offer_id")

    p.reset()
    p.login("WGYBNA")
    dining_form = p.form_index("/onboard/dining?pnr=WGYBNA", "meal_code")
    baggage_form = p.form_index("/manage/WGYBNA/baggage", "extra_kg")
    hotel_form = p.form_index("/partners/zena-hotel", "room_id")
    lounge_form = p.form_index("/lounges/purchase", "lounge_id")
    join_form = p.form_index("/miles/join", "first_name")
    claim_form = p.form_index("/miles/claim", "member_no")
    manage_form = p.form_index("/manage", "pnr")
    checkin_form = p.form_index("/checkin", "pnr")
    miles_form = p.form_index("/miles/account", "member_no")
    pax_form = p.form_index(f"/book/passengers?itinerary={itinerary}",
                            "first_name_1")
    p.reset()

    art(2, ["goto /book/results?origin=ADD&destination=DXB"
            "&depart=2026-04-20&adults=1",
            f"goto /book/passengers?itinerary={itinerary}",
            f"fill {pax_form} first_name_1={V['test_first']}; "
            f"last_name_1={V['test_last']}; "
            f"contact_email={V['test_email']}; "
            f"contact_phone={V['test_phone']}",
            "goto /book/review"])
    t5 = src[5]
    fl5 = [r["flight_no"] for r in q(
        "SELECT f.flight_no FROM segments s JOIN flights f ON "
        "f.id=s.flight_id JOIN bookings b ON b.id=s.booking_id "
        "WHERE b.pnr='WGYBNA' ORDER BY s.sequence")]
    assert len(fl5) == 2
    assert V["k2_drop"] in t5["intent"], t5["intent"]
    task(t5["intent"].replace(V["k2_drop"], ""),
         [{"type": "selam_score", "task_id": 5, "lang": lang}]
         + [ans_ev(f) for f in fl5],
         manage_login("WGYBNA") + ["goto /manage/WGYBNA",
                                   f"stop {', '.join(fl5)}"])
    art(6, manage_login("W7JKUF") + [
        "goto /manage/W7JKUF/change",
        f"fill 0 new_flight_id={flight6}"],
        extra=[exists("change_requests",
                      {"booking_id": booking_id("W7JKUF"),
                       "new_flight_id": later6})])
    t7 = src[7]
    task(t7["intent"],
         [{"type": "answer_match", "any_of": list(V["k7_alts"])},
          {"type": "db_record_absent", "table": "refund_requests",
           "match": {"booking_id": booking_id("SPMVJC")}}],
         manage_login("SPMVJC") + [
             "goto /manage/SPMVJC/refund",
             f"stop {SITE_T['refund.code_offline_channel_only']}"])
    t8 = src[8]["intent"]
    assert V["k5_drop"].strip() in t8, t8
    art(8, ["goto /checkin",
            f"fill {checkin_form} pnr=WGYBNA; surname={sn('WGYBNA')}",
            "fill 0"],
        intent=t8.replace(V["k5_drop"], "").strip())
    aisle_seats = [m.group(2) for m in re.finditer(
        r'<button class="seat([^"]*)"[^>]*name="seat_no" '
        r'value="([0-9]+[A-Z])"', seats_html)
        if "aisle" in m.group(1) and "taken" not in m.group(1)]
    assert seat10 in aisle_seats
    art(10, manage_login("N9JKBF") + [
        "goto /manage/N9JKBF/seats", f"fill 0 seat_no={seat10}"],
        answer=seat10,
        extra=[{"type": "answer_match", "any_of": aisle_seats}])
    p.reset()
    p.login("WGYBNA")
    r23 = p.s.post(p.base + "/manage/WGYBNA/baggage",
                   data={"extra_kg": "23"}, timeout=10, allow_redirects=True)
    charge23 = sorted({int(x.replace(",", "")) for x in
                       re.findall(r"USD\s?([\d,]+)", r23.text)})
    assert len(charge23) == 1, charge23
    charge23 = charge23[0]
    p.reset()
    art(13, manage_login("WGYBNA") + [
        "goto /manage/WGYBNA/baggage",
        f"fill {baggage_form} extra_kg=23"],
        answer=str(charge23), extra=[ans_ev(charge23)])
    price16 = src[16]["eval"]["validator_args"]["expected_price_usd"]
    art(16, ["goto /lounges/purchase",
             f"fill {lounge_form} lounge_id="
             f"{src[16]['instantiation']['parameters']['id']}; "
             f"passenger_name={V['test_passenger']}; guests=0"],
        answer=f"{price16:g}", extra=[ans_ev(price16)])
    member18 = src[18]["eval"]["validator_args"]["expected_member_no"]
    art(18, ["goto /miles/join",
             f"fill {join_form} first_name={V['join_first']}; "
             f"last_name={V['join_last']}; "
             "email=selamawit.bekele@example.com; country_code=ET; "
             "dob=1992-05-14"],
        answer=member18, extra=[ans_ev(member18)])
    art(19, ["goto /miles/claim",
             f"fill {claim_form} member_no=SM00000001; "
             "ticket_no=0712345678901; flight_no=SM246; "
             "flight_date=2026-03-15"],
        intent=src[19]["intent"].rstrip() + V["k10_suffix"],
        extra=[exists("missing_miles_claims",
                      {"member_no": "SM00000001", "flight_no": "SM246",
                       "flight_date": "2026-03-15"})])
    art(21, ["goto /onboard/wifi?flight_no=SM106&date=2026-03-19",
             f"fill {wifi_form} package_id={package21}"])
    art(22, manage_login("WGYBNA") + [
        "goto /onboard/dining?pnr=WGYBNA",
        f"fill {dining_form} meal_code=GFML"])
    art(25, ["goto /partners/zena-hotel",
             f"fill {hotel_form} arrival=2026-04-12; hours=12; "
             f"guest_name={V['test_passenger']}"])
    docs26 = q1("SELECT * FROM visa_types WHERE code=?", code26)[C("documents")]
    doc_phrase = re.split(r"[;؛፤]", docs26)[0].strip()
    p.on_page(f"/partners/evisa?code={code26}", doc_phrase)
    art(26, ["goto /partners/evisa",
             f"goto /partners/evisa?code={code26}"],
        answer=docs26, extra=[{"type": "answer_match",
                               "any_of": list(V["k26_alts"])}])
    art(28, ["goto /partners/riftdrive?airport=NBO&passengers=2"
             "&pickup=2026-04-12",
             f"fill {rift_form} offer_id={offer28}"])
    assert n == 15, n

    fc = {r["code"]: r for r in q("SELECT * FROM fare_classes")}
    d_fee = int(fc["EG"]["refund_fee_usd"] - fc["ES"]["refund_fee_usd"])
    p.on_page("/book/fare-rules/EG", money_forms(fc["EG"]["refund_fee_usd"]))
    p.on_page("/book/fare-rules/ES", money_forms(fc["ES"]["refund_fee_usd"]))
    task(I("a1"),
         [ans_ev(d_fee)],
         ["goto /book/fare-rules/EG", "goto /book/fare-rules/ES",
          f"stop {d_fee}"])

    eco = [r for r in fc.values() if r["cabin"] == "economy"]
    top_chg = max(eco, key=lambda r: r["change_fee_usd"])
    assert sum(1 for r in eco
               if r["change_fee_usd"] == top_chg["change_fee_usd"]) == 1
    task(I("a2"),
         [ans_ev(top_chg["code"],
                 none_of=[r["code"] for r in eco if r is not top_chg])],
         [f"goto /book/fare-rules/{top_chg['code']}",
          f"stop {top_chg['code']}"])

    ins = {r["code"]: r for r in q("SELECT * FROM insurance_products")}
    prem_plus = max(1200 * ins["SV-PLUS"]["price_pct"] / 100,
                    ins["SV-PLUS"]["price_min_usd"])
    p.on_page("/partners/safevoyage?fare=1200", money_forms(prem_plus))
    task(I("a3"),
         [ans_ev(prem_plus)],
         ["goto /partners/safevoyage?fare=1200", f"stop {prem_plus:g}"])

    prem_max = max(400 * ins["SV-MAX"]["price_pct"] / 100,
                   ins["SV-MAX"]["price_min_usd"])
    assert prem_max == ins["SV-MAX"]["price_min_usd"]
    p.on_page("/partners/safevoyage?fare=400", money_forms(prem_max))
    task(I("a4"),
         [ans_ev(prem_max)],
         ["goto /partners/safevoyage?fare=400", f"stop {prem_max:g}"])

    eur = q1("SELECT extra_kg_price_usd r FROM baggage_rules WHERE "
             "region='europe' AND cabin='economy' AND pax_type='adult'")
    per_kg = eur["r"]
    p.on_page("/baggage/fees", money_forms(per_kg))
    cost15 = int(per_kg * 15)
    task(I("a5"),
         [ans_ev(cost15)],
         ["goto /baggage/fees", f"stop {cost15}"])

    aw = q1("SELECT ai.miles_required m FROM award_inventory ai"
            " JOIN flights f ON f.id=ai.flight_id"
            " JOIN routes r ON r.id=f.route_id"
            " JOIN airports o ON o.id=r.origin_id"
            " JOIN airports d ON d.id=r.destination_id"
            " WHERE o.iata='ADD' AND d.iata='NBO' AND f.date='2026-03-19'"
            " AND ai.cabin='economy'")
    m4 = member("SM00000004")
    assert aw["m"] not in (25000, 50000, 100000)
    gap = aw["m"] - m4["miles_balance"]
    p.miles_login("SM00000004")
    p.on_page("/miles/account", money_forms(m4["miles_balance"]))
    p.reset()
    task(I("a6", ln4=ln("SM00000004")),
         [ans_ev(gap)],
         ["goto /miles/award-search?origin=ADD&destination=NBO"
          "&date=2026-03-19&cabin=economy"]
         + miles_login_steps("SM00000004") + [f"stop {gap}"])

    promo = q1("SELECT * FROM promotions WHERE code='AFRICA15'")
    disc = 600 * (100 - promo["discount_pct"]) // 100
    task(I("a7", promo=promo["code"]),
         [ans_ev(disc)],
         ["goto /offers", f"stop {disc}"])

    earn = 2000 * fc["EB"]["miles_earn_pct"] // 100
    p.on_page("/book/fare-rules/EB",
              [f"{fc['EB']['miles_earn_pct']}%",
               str(fc["EB"]["miles_earn_pct"])])
    task(I("a8"),
         [ans_ev(earn)],
         ["goto /book/fare-rules/EB", f"stop {earn}"])

    t2 = q("SELECT * FROM lounges WHERE airport_iata='ADD' AND "
           "terminal='2' ORDER BY walk_in_price_usd")
    assert len(t2) == 3 and t2[0]["walk_in_price_usd"] < \
        t2[1]["walk_in_price_usd"]
    task(I("b1"),
         [exists("lounge_purchases", {"lounge_id": t2[0]["id"],
                                      "guests": 0,
                                      "passenger_name": V["test_passenger"]})],
         ["goto /lounges", f"goto /lounges/{t2[0]['id']}",
          "goto /lounges/purchase",
          f"fill {lounge_form} lounge_id={t2[0]['id']}; "
          f"passenger_name={V['test_passenger']}; guests=0"])

    hl = q("SELECT * FROM lounges WHERE name_en='Highland Lounge' AND "
           "airport_iata IN ('NBO','JNB','DAR','LOS') "
           "ORDER BY walk_in_price_usd")
    assert hl[0]["walk_in_price_usd"] < hl[1]["walk_in_price_usd"]
    task(I("b2"),
         [ans_ev(hl[0]["airport_iata"],
                 none_of=[r["airport_iata"] for r in hl[1:]])],
         ["goto /lounges", f"stop {hl[0]['airport_iata']}"])

    gold_ok = [r for r in t2 if "gold" in (r["access_free_for"] or "")]
    assert len(gold_ok) == 1
    task(I("b3"),
         [ans_ev(gold_ok[0][C("name")],
                 none_of=[r[C("name")] for r in t2 if r not in gold_ok])],
         ["goto /lounges", f"goto /lounges/{gold_ok[0]['id']}",
          f"stop {gold_ok[0][C('name')]}"])

    big29 = q1("SELECT f.flight_no fn, f.date d, MAX(w.price_usd) mx "
               "FROM wifi_packages w JOIN flights f ON f.id=w.flight_id "
               "WHERE f.date='2026-03-19' GROUP BY w.flight_id "
               "HAVING mx=29.0 LIMIT 1")
    no_collide("SM106", big29["fn"])
    task(I("b4", fn29=big29["fn"]),
         [ans_ev("SM106", none_of=[big29["fn"]]), ans_ev(22)],
         ["goto /onboard/wifi?flight_no=SM106&date=2026-03-19",
          f"goto /onboard/wifi?flight_no={big29['fn']}&date=2026-03-19",
          "stop SM106, 22"])

    fam = q1("SELECT * FROM hotel_rooms WHERE sleeps>=4")
    total_fam = int(fam["price_per_block_usd"] * 2)
    p.on_page("/partners/zena-hotel",
              money_forms(fam["price_per_block_usd"]))
    task(I("b5"),
         [ans_ev(total_fam)],
         ["goto /partners/zena-hotel", f"stop {total_fam}"])

    van_n = q1("SELECT price_usd v FROM car_offers WHERE "
               "airport_iata='NBO' AND name_en LIKE 'Private van%'")["v"]
    van_a = q1("SELECT price_usd v FROM car_offers WHERE "
               "airport_iata='ADD' AND name_en LIKE 'Private van%'")["v"]
    dv = int(abs(van_n - van_a))
    cheaper_ap = "ADD" if van_a < van_n else "NBO"
    no_collide(cheaper_ap, dv)
    task(I("b6"),
         [ans_ev(cheaper_ap, none_of=["ADD", "NBO"]), ans_ev(dv)],
         ["goto /partners/riftdrive?airport=NBO&passengers=2"
          "&pickup=2026-04-12",
          "goto /partners/riftdrive?airport=ADD&passengers=2"
          "&pickup=2026-04-12",
          f"stop {cheaper_ap}, {dv}"])

    shut = q1("SELECT * FROM car_offers WHERE airport_iata='NBO' AND "
              "name_en LIKE 'Shared shuttle%'")
    task(I("b7"),
         [exists("car_bookings", {"offer_id": shut["id"],
                                  "passengers": 2,
                                  "pickup_date": "2026-04-12"})],
         ["goto /partners/riftdrive?airport=NBO&passengers=2"
          "&pickup=2026-04-12",
          f"fill {rift_form} offer_id={shut['id']}"])

    stop_max = q1("SELECT * FROM stopover_packages ORDER BY "
                  "min_layover_h DESC LIMIT 1")
    assert len(q("SELECT id FROM stopover_packages WHERE "
                 "min_layover_h=?", stop_max["min_layover_h"])) == 1
    task(I("b8"),
         [ans_ev(stop_max[C("name")], none_of=[
              r["n"] for r in q(f"SELECT {C('name')} n FROM "
                                "stopover_packages")
              if r["n"] != stop_max[C("name")]])],
         ["goto /stopover/packages", f"stop {stop_max[C('name')]}"])

    p.miles_login("SM00000006")
    tier_txt = p.on_page("/miles/account/tier-progress",
                         money_forms(member("SM00000006")
                                     ["qualifying_miles"]))
    thresh = min(int(x.replace(",", "")) for x in
                 re.findall(r"\b(\d{2,3},?\d{3})\b", tier_txt)
                 if int(x.replace(",", "")) >
                 member("SM00000006")["qualifying_miles"])
    gap6 = thresh - member("SM00000006")["qualifying_miles"]
    p.reset()
    task(I("c1", ln6=ln("SM00000006")),
         [ans_ev(gap6)],
         miles_login_steps("SM00000006") +
         ["goto /miles/account/tier-progress", f"stop {gap6}"])

    m9 = member("SM00000009")
    task(I("c2", ln9=ln("SM00000009")),
         [ans_ev(m9["miles_balance"])],
         miles_login_steps("SM00000009") +
         [f"stop {m9['miles_balance']}"])

    m10 = member("SM00000010")
    tx10 = q("SELECT flight_no, miles FROM miles_transactions"
             " WHERE member_id=? AND miles > 0 ORDER BY miles DESC",
             m10["id"])
    assert tx10[0]["miles"] > tx10[1]["miles"]
    top_fl, top_mi = tx10[0]["flight_no"], tx10[0]["miles"]
    no_collide(top_fl, top_mi)
    p.reset()
    p.miles_login("SM00000010")
    p.on_page("/miles/account/statement", str(top_mi), top_fl)
    p.reset()
    task(I("c3", ln10=ln("SM00000010")),
         [ans_ev(top_fl, none_of=[r["flight_no"] for r in tx10
                                  if r["flight_no"] != top_fl]),
          ans_ev(top_mi)],
         miles_login_steps("SM00000010") +
         ["goto /miles/account/statement",
          f"stop {top_fl}, {top_mi}"])

    task(I("c4"),
         [exists("missing_miles_claims",
                 {"member_no": "SM00000003",
                  "ticket_no": "0709876543210", "flight_no": "SM188",
                  "flight_date": "2026-02-20"})],
         ["goto /miles/claim",
          f"fill {claim_form} member_no=SM00000003; "
          "ticket_no=0709876543210; flight_no=SM188; "
          "flight_date=2026-02-20"])

    p.on_page("/miles/award-chart", SITE_T["region.north_america"], "60000")
    na_eco = 60000
    task(I("c5"),
         [ans_ev(na_eco)],
         ["goto /miles/award-chart", f"stop {na_eco}"])

    m11 = member("SM00000011")
    task(I("c6", ln11=ln("SM00000011")),
         [ans_ev(m11["tier"], none_of=["blue", "silver", "gold",
                                        "platinum"]),
          ans_ev(m11["miles_balance"])],
         miles_login_steps("SM00000011") +
         [f"stop {m11['tier']}, {m11['miles_balance']}"])

    task(I("c7", ln4=ln("SM00000004")) + NR,
         [ans_ev("N/A", also=list(V["na_redeem"]))],
         miles_login_steps("SM00000004") + ["stop N/A"])

    dep_txt = p.text("/flight-status/departures/ADD")
    n_rows = len(re.findall(r"\bSM\d{3}\b", dep_txt))
    assert n_rows > 3
    task(I("d1"),
         [ans_ev(n_rows)],
         ["goto /flight-status/departures/ADD", f"stop {n_rows}"])

    f152 = q1("SELECT delay_minutes d FROM flights WHERE "
              "flight_no='SM152' AND date='2026-03-16'")
    p.on_page("/flight-status?flight_no=SM152&date=2026-03-16",
              str(f152["d"]))
    task(I("d2"),
         [ans_ev(f152["d"])],
         ["goto /flight-status?flight_no=SM152&date=2026-03-16",
          f"stop {f152['d']}"])

    f107 = q1("SELECT gate g, terminal_dep t FROM flights WHERE "
              "flight_no='SM107' AND date='2026-03-16'")
    no_collide(f107["g"], f107["t"])
    task(I("d3"),
         [ans_ev(f107["g"]), ans_ev(f107["t"])],
         ["goto /flight-status?flight_no=SM107&date=2026-03-16",
          f"stop gate {f107['g']}, terminal {f107['t']}"])

    task(I("d4"),
         [{"type": "answer_match",
           "any_of": ["N/A"] + list(V["seasonal_alts"])}],
         ["goto /schedules/seasonal",
          f"stop {SITE_T['schedules.no_seasonal']}"])

    days_abj = q1("SELECT r.operating_days d FROM routes r"
                  " JOIN airports o ON o.id=r.origin_id"
                  " JOIN airports x ON x.id=r.destination_id"
                  " WHERE o.iata='ADD' AND x.iata='ABJ'")["d"]
    n_abj = sum(1 for c in days_abj if c != ".")
    assert 1 < n_abj < 7, days_abj
    task(I("d5"),
         [ans_ev(n_abj)],
         ["goto /schedules?origin=ADD&destination=ABJ", f"stop {n_abj}"])

    segN = segs("N9JKBF")
    task(I("e1", snN=sn("N9JKBF")),
         [exists("seat_assignments", {"segment_id": segN[0]["id"],
                                      "seat_no": window_seats})],
         manage_login("N9JKBF") + [
             "goto /manage/N9JKBF/seats",
             f"fill 0 seat_no={seat_window}"])

    segM = segs("MDQKTR")
    task(I("e2", snM=sn("MDQKTR")),
         [exists("baggage_purchases",
                 {"booking_id": booking_id("MDQKTR"), "extra_kg": 10,
                  "segment_id": segM[0]["id"]})],
         manage_login("MDQKTR") + [
             "goto /manage/MDQKTR/baggage", "fill 0 extra_kg=10"])

    p.login("WGYBNA")
    contact_form = p.form_index("/manage/WGYBNA/contact-details", "email")
    p.reset()
    task(I("e3", snW=sn("WGYBNA")),
         [{"type": "db_field_equals", "table": "bookings",
           "match": {"pnr": "WGYBNA"}, "field": "email",
           "value": V["new_email"]},
          {"type": "db_field_equals", "table": "bookings",
           "match": {"pnr": "WGYBNA"}, "field": "phone",
           "value": V["new_phone"]}],
         manage_login("WGYBNA") + [
             "goto /manage/WGYBNA/contact-details",
             f"fill {contact_form} email={V['new_email']}; "
             f"phone={V['new_phone']}"])

    task(I("e4", snE=sn("EFC78Z")),
         [{"type": "db_field_equals", "table": "bookings",
           "match": {"pnr": "EFC78Z"}, "field": "status",
           "value": "cancelled"}],
         manage_login("EFC78Z") + [
             "goto /manage/EFC78Z/cancel", "fill 0 confirm=yes"])

    task(I("e5", snJ=sn("J4KC9R")),
         [exists("refund_requests",
                 {"booking_id": booking_id("J4KC9R")})],
         manage_login("J4KC9R") + [
             "goto /manage/J4KC9R/refund", "fill 0 confirm=1"])

    task(I("e6", snN=sn("N9JKBF")),
         [exists("meal_requests", {"segment_id": segN[0]["id"],
                                   "meal_code": "AVML"})],
         manage_login("N9JKBF") + [
             "goto /onboard/dining?pnr=N9JKBF",
             f"fill {dining_form} meal_code=AVML"])

    segV = segs("VF6ZBW")
    p.login("VF6ZBW")
    upg_html = p.html("/manage/VF6ZBW/upgrade")
    upg_form = p.form_index("/manage/VF6ZBW/upgrade", "segment_id")
    p.reset()
    task(I("e7", snV=sn("VF6ZBW")),
         [exists("upgrade_purchases", {"segment_id": segV[0]["id"]})],
         manage_login("VF6ZBW") + [
             "goto /manage/VF6ZBW/upgrade",
             f"fill {upg_form} segment_id={segV[0]['id']}"])

    task(I("e8", snW=sn("WGYBNA")),
         [exists("baggage_purchases",
                 {"booking_id": booking_id("WGYBNA"), "extra_kg": 5,
                  "segment_id": segs("WGYBNA")[0]["id"]}),
          exists("meal_requests",
                 {"meal_code": "LSML",
                  "segment_id": [r["id"] for r in segs("WGYBNA")]})],
         manage_login("WGYBNA") + [
             "goto /manage/WGYBNA/baggage",
             f"fill {baggage_form} extra_kg=5",
             "goto /onboard/dining?pnr=WGYBNA",
             f"fill {dining_form} meal_code=LSML"])

    p.login("VF6ZBW")
    bag_form_v = p.form_index("/manage/VF6ZBW/baggage", "extra_kg")
    dining_form_v = p.form_index("/onboard/dining?pnr=VF6ZBW", "meal_code")
    p.reset()
    segW = segs("WGYBNA")
    if True:
        task(I("e9a", snV=sn("VF6ZBW")),
             [exists("baggage_purchases",
                     {"booking_id": booking_id("VF6ZBW"), "extra_kg": 15,
                      "segment_id": segV[0]["id"]}),
              exists("meal_requests",
                     {"meal_code": "DBML",
                      "segment_id": [r["id"] for r in segV]})],
             manage_login("VF6ZBW") + [
                 "goto /manage/VF6ZBW/baggage",
                 f"fill {bag_form_v} extra_kg=15",
                 "goto /onboard/dining?pnr=VF6ZBW",
                 f"fill {dining_form_v} meal_code=DBML"])
    else:
        task(I("e9b", snN=sn("N9JKBF")),
             [exists("checkins", {"segment_id": segN[0]["id"]})],
             ["goto /checkin",
              f"fill {checkin_form} pnr=N9JKBF; "
              f"surname={sn('N9JKBF')}", "fill 0"])

    task(I("e10"),
         [exists("service_requests",
                 {"kind": "assistance", "payload": "%WCHR%"}),
          exists("service_requests", {"payload": "%WGYBNA%"}),
          exists("service_requests",
                 {"payload": f"%{V['test_passenger']}%"}),
          exists("service_requests",
                 {"payload": f"%{V['test_email']}%"}),
          exists("service_requests",
                 {"payload": f"%{V['aisle_note']}%"})],
         ["goto /services/assistance/wheelchair",
          f"fill 0 full_name={V['test_passenger']}; "
          f"email={V['test_email']}; "
          "booking_reference=WGYBNA; service_code=WCHR; "
          f"notes={V['aisle_note']}"])

    tr = q1("SELECT * FROM travel_requirements tr JOIN airports a ON "
            "a.country_code=tr.country_code WHERE a.iata='LHR'")
    no_collide(tr["passport_months"], tr["blank_pages"])
    p.on_page("/travel-requirements/ADD/LHR", str(tr["passport_months"]),
              str(tr["blank_pages"]))
    task(I("f1"),
         [ans_ev(tr["passport_months"]), ans_ev(tr["blank_pages"])],
         ["goto /travel-requirements/ADD/LHR",
          f"stop {tr['passport_months']} months, "
          f"{tr['blank_pages']} pages"])

    de = q1("SELECT * FROM contact_offices WHERE country_code='DE'")
    no_collide(de["emergency_phone"], de[C("city")])
    p.on_page("/help/contact/DE", de["emergency_phone"], de[C("city")])
    task(I("f2"),
         [ans_ev(de["emergency_phone"], none_of=[de["phone"]]),
          ans_ev(de[C("city")])],
         ["goto /help/contact", "goto /help/contact/DE",
          f"stop {de['emergency_phone']}, {de[C('city')]}"])

    at = q1("SELECT * FROM contact_offices WHERE country_code='AT'")
    p.on_page("/help/contact/AT", at["phone"])
    task(I("f3"),
         [ans_ev(at["phone"])],
         ["goto /help/contact", "goto /help/contact/AT",
          f"stop {at['phone']}"])

    meals48 = q("SELECT * FROM special_meal_codes WHERE cutoff_hours=48")
    assert len(meals48) == 2
    p.on_page("/onboard/dining/special-meals",
              *[m[C("name")] for m in meals48])
    task(I("f4"),
         [ans_ev(m[C("name")], none_of=[
              r["n"] for r in q(f"SELECT {C('name')} n FROM "
                                "special_meal_codes WHERE "
                                "cutoff_hours<>48")
              if not any(r["n"].lower() in x[C("name")].lower()
                         for x in meals48)])
          for m in meals48],
         ["goto /onboard/dining/special-meals",
          f"stop {meals48[0][C('name')]}, {meals48[1][C('name')]}"])

    v90 = q1("SELECT * FROM visa_types WHERE code='EV-T90'")
    vbiz = q1("SELECT * FROM visa_types WHERE code='EV-BIZ'")
    dvfee = int(abs(v90["fee_usd"] - vbiz["fee_usd"]))
    dearer = v90 if v90["fee_usd"] > vbiz["fee_usd"] else vbiz
    task(I("f5"),
         [ans_ev(dearer[C("name")],
                 also=(list(V["visa90_alts"]) if dearer is v90
                       else list(V["visabiz_alts"])),
                 none_of=([vbiz[C("name")]] if dearer is v90
                          else [v90[C("name")]] + list(V["visa90_none"]))),
          ans_ev(dvfee)],
         ["goto /partners/evisa", f"stop {dearer[C('name')]}, {dvfee}"])

    rails = q("SELECT * FROM rail_connections WHERE arrival_iata='FRA' "
              "ORDER BY journey_min")
    assert rails[0]["journey_min"] < rails[1]["journey_min"]
    no_collide(rails[0][C("destination")], rails[0]["journey_min"])
    task(I("f6"),
         [ans_ev(rails[0][C("destination")],
                 none_of=[r[C("destination")] for r in rails[1:]]),
          ans_ev(rails[0]["journey_min"])],
         ["goto /partners/eurorail?arrival=FRA",
          f"stop {rails[0][C('destination')]}, "
          f"{rails[0]['journey_min']}"])

    no_lounge = "ACC"
    assert not q("SELECT id FROM lounges WHERE airport_iata=?", no_lounge)
    task(I("g1", no_lounge=no_lounge) + NR,
         [ans_ev("N/A", also=list(V["na_lounge"])),
          absent("lounge_purchases", {"guests": 0})],
         ["goto /lounges", "stop N/A"])

    nw = q1("SELECT flight_no fn, date d FROM flights WHERE "
            "wifi_equipped=0 AND date='2026-03-17' LIMIT 1")
    task(I("g2", nw_fn=nw["fn"], nw_d=nw["d"]) + NR,
         [ans_ev("N/A", also=list(V["na_wifi"])),
          absent("wifi_purchases", {"status": "pending"})],
         [f"goto /onboard/wifi?flight_no={nw['fn']}&date={nw['d']}",
          "stop N/A"])

    no_aw = q("SELECT ai.id FROM award_inventory ai JOIN flights f ON "
              "f.id=ai.flight_id JOIN routes r ON r.id=f.route_id "
              "JOIN airports o ON o.id=r.origin_id JOIN airports d ON "
              "d.id=r.destination_id WHERE o.iata='ADD' AND "
              "d.iata='ABJ' AND f.date='2026-03-19'")
    assert not no_aw
    task(I("g3") + NR,
         [ans_ev("N/A", also=list(V["na_award"]))],
         ["goto /miles/award-search?origin=ADD&destination=ABJ"
          "&date=2026-03-19&cabin=economy", "stop N/A"])

    task(I("g4", snW=sn("WGYBNA")) + NR,
         [ans_ev("N/A", also=list(V["na_refund"])),
          absent("refund_requests",
                 {"booking_id": booking_id("WGYBNA")})],
         manage_login("WGYBNA") + ["goto /manage/WGYBNA/refund",
                                   "stop N/A"])

    task(I("g5", snJ=sn("J4KC9R")) + NR,
         [ans_ev("N/A", also=list(V["na_upgrade"])),
          absent("upgrade_purchases",
                 {"booking_id": booking_id("J4KC9R")})],
         manage_login("J4KC9R") + ["goto /manage/J4KC9R/upgrade",
                                   "stop N/A"])

    assert not q("SELECT id FROM contact_offices WHERE country_code='JP'")
    task(I("g6") + NR,
         [ans_ev("N/A", also=list(V["na_office"]))],
         ["goto /help/contact", "stop N/A"])

    assert not q("SELECT id FROM hotel_rooms WHERE sleeps>=6")
    task(I("g7") + NR,
         [ans_ev("N/A", also=list(V["na_room"])),
          absent("hotel_bookings", {"arrival": "2026-04-12"})],
         ["goto /partners/zena-hotel", "stop N/A"])

    n_add = len(q("SELECT id FROM lounges WHERE airport_iata='ADD'"))
    task(I("h1"),
         [ans_ev(n_add)],
         ["goto /lounges", f"stop {n_add}"])

    two_hl = q("SELECT walk_in_price_usd v FROM lounges WHERE "
               "airport_iata='ADD' AND name_en LIKE 'Highland%'")
    tot_hl = int(sum(r["v"] for r in two_hl))
    task(I("h2"),
         [ans_ev(tot_hl)],
         ["goto /lounges", f"stop {tot_hl}"])

    n_meals = len(q("SELECT id FROM special_meal_codes"))
    task(I("h3"),
         [ans_ev(n_meals)],
         ["goto /onboard/dining/special-meals", f"stop {n_meals}"])

    n_rail = len(q("SELECT id FROM rail_connections WHERE "
                   "arrival_iata='FRA'"))
    task(I("h4"),
         [ans_ev(n_rail)],
         ["goto /partners/eurorail?arrival=FRA", f"stop {n_rail}"])

    task(I("i1"),
         [exists("service_requests",
                 {"payload": f"%{V['feedback_msg']}%"})],
         ["goto /help/feedback",
          f"fill 0 full_name={V['test_passenger']}; "
          f"email={V['test_email']}; category=complaint; "
          f"message={V['feedback_msg']}"])

    gb = q1("SELECT * FROM bookings WHERE pnr='MBX744'")
    npax = len(q("SELECT p.id FROM passengers p JOIN bookings b ON "
                 "b.id=p.booking_id WHERE b.pnr='MBX744'"))
    no_collide(int(gb["total_paid"]), npax)
    task(I("i2", snX=sn("MBX744")),
         [ans_ev(int(gb["total_paid"])), ans_ev(npax)],
         manage_login("MBX744") + ["goto /manage/MBX744",
                                   f"stop {int(gb['total_paid'])}, "
                                   f"{npax}"])

    l1 = q1("SELECT * FROM lounges WHERE id=1")
    loc_target = ("opposite Gate A6" if lang == "en" else
                  re.split(r"[,፣،]", l1[C("location")])[-1].strip().rstrip("።۔।."))
    p.on_page("/lounges/1", l1[C("hours")], loc_target)
    _hrs = re.search(r"\d{2}:\d{2}-\d{2}:\d{2}", l1[C("hours")]).group(0)
    hours_alt = [l1[C("hours")], _hrs, _hrs.replace("-", " to ")]
    task(I("i3"),
         [{"type": "answer_match", "any_of": hours_alt},
          {"type": "answer_match", "answer": loc_target}],
         ["goto /lounges", "goto /lounges/1",
          f"stop {l1[C('hours')]}; {l1[C('location')]}"])

    ec_free = q1("SELECT checked_kg k FROM baggage_rules WHERE "
                 "region='africa' AND cabin='economy' AND "
                 "pax_type='adult'")["k"]
    extra_needed = 30 - ec_free
    cost_extra = int(extra_needed * q1(
        "SELECT extra_kg_price_usd r FROM baggage_rules WHERE "
        "region='africa' AND cabin='economy' AND pax_type='adult'")["r"])
    task(I("i4"),
         [ans_ev(cost_extra)],
         ["goto /baggage/allowance?origin=ADD&destination=NBO"
          "&cabin=economy&pax_type=adult",
          "goto /baggage/fees", f"stop {cost_extra}"])

    ins_cheap = min(ins.values(), key=lambda r: r["price_min_usd"])
    task(I("i5"),
         [ans_ev(ins_cheap[C("name")], none_of=[
              r[C("name")] for r in ins.values() if r is not ins_cheap]),
          ans_ev(max(250 * ins_cheap["price_pct"] / 100,
                     ins_cheap["price_min_usd"]))],
         ["goto /partners/safevoyage?fare=250",
          f"stop {ins_cheap[C('name')]}, "
          f"{max(250 * ins_cheap['price_pct'] / 100, ins_cheap['price_min_usd']):g}"])

    assert n == 75, n
    return T


def write(lang, out_dir):
    T = build(lang)
    out = os.path.join(out_dir, "selam_tasks.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(T, f, indent=1, ensure_ascii=False)
    print(f"wrote {len(T)} tasks to {out}")
