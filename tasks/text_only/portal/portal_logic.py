import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DATA = os.path.join(ROOT, "sites", "text_only", "portal",
                    "portal_clone", "data")
SRC_TASKS = os.path.join(HERE, "src_tasks_en.json")

import sys

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "sites", "text_only", "portal"))
sys.path.insert(0, ROOT)
from portal_i18n import I18N, LIT
from translate_portal_data import Vocab
from sites.text_only.portal.portal_clone.content import DIGITS

V_EN = {
    "cred": (" Log in as citizen 9999708182203 (password: citizen1234) "
             "if needed."),
    "name": "Delwar Haque", "father": "Monir Islam",
    "mother": "Ferdousi Bhuiyan", "dob": "1987-08-28",
    "present": "House 16, Road 5, Moulvibazar Ganj, Moulvibazar",
    "perm": "Village Uttarpara, Moulvibazar Ganj, Moulvibazar",
    "mobile": "01853445903",
    "office_passport": "Barguna Passport and Immigration Office",
    "office_licence": "Barishal Transport Licensing Office",
    "board": "Rajshahi",
    "subjects": "Mathematics, English",
    "circle": "Circle 1", "income": "Salary",
    "purpose": "employment abroad",
    "nid_new_name": "Delwara Haque",
    "new_addr": "House 9, Lake Road, Sylhet",
    "new_dob": "1987-08-27",
    "a_awaiting": "Awaiting payment",
    "a_name": "Delwar Haque",
}

INTENTS_EN_NEW = {
    34: "Open your electricity bill history and note the amount of the "
        "2026-01 bill. In the electricity fee schedule, find the fee "
        "whose amount is the highest that is still below that bill "
        "amount, and answer with that fee's variant name. Then settle "
        "the oldest outstanding bill on your meter.",
    35: "Find khatian number 4438 somewhere in Meherpur district "
        "through the land record search (the upazila and mouza are not "
        "given) and report the plot number recorded on it.",
    36: "Look up the secondary exam result of 2021 for roll number "
        "763370 (the board is not given — the lookup page lists the "
        "boards) and report the candidate's institution.",
    37: "Verify the birth registration record with registration number "
        "20000000000373 and report its registration date.",
    38: "On the electricity service page, three notices share the same "
        "title. Report the category of the one issued on 2025-10-12.",
    39: "Check passport application PPA04000017 to read its booklet "
        "pages and validity, then use the passport fee schedule to "
        "report the express-delivery fee for exactly that "
        "pages/validity combination.",
    40: "Open your electricity bill history and report the total "
        "amount billed across all six billing periods.",
}

SAY_SO = "If no such record exists, say so."
SAY_TOKEN = "If no such record exists, answer NO_RECORD."

LIT_EN_EXTRA = {
    "centre": "Moulvibazar Identity Registration Office",
    "rafiqul": "Rafiqul Islam", "hoque": "Delwar Hoque",
    "haque_sr": "Delwar Haque Sr", "cat_licence": "Licence",
    "var_motorcycle": "Motorcycle", "closure": "closure",
}


def make_V(lang):
    V = dict(V_EN, **LIT_EN_EXTRA)
    L = LIT[lang]
    V.update(cred=L["cred"], income=L["income"], purpose=L["purpose"],
             new_addr=L["new_addr"], math=L["math"], eng=L["eng"],
             damaged=L["damaged"])
    if lang != "en":
        vb = Vocab(lang)
        T = vb.t
        for k in ("name", "father", "mother", "nid_new_name", "a_name",
                  "rafiqul", "hoque", "haque_sr"):
            V[k] = vb.name(V[k])
        for k in ("present", "perm"):
            V[k] = vb.place(V[k])
        for k in ("office_passport", "office_licence", "centre"):
            V[k] = vb.office(V[k])
        V["board"] = vb.district(V["board"])
        V["circle"] = f"{T['tin_words']['Circle']} 1"
        V["cat_licence"] = T["fee_categories"]["Licence"]
        V["var_motorcycle"] = T["fee_variants"]["Motorcycle"]
        V["closure"] = T["notice_categories"]["closure"]
        V["a_awaiting"] = T["statuses"]["Awaiting payment"]
    return V


def load(name):
    with open(os.path.join(DATA, "en", name + ".json"),
              encoding="utf-8") as f:
        return json.load(f)


sys.path.insert(0, ROOT)
from sites.text_only.portal.portal_clone.seed import (
    SERVICES, content as site_content, load as load_ml)


def geo_ids_for_khatian(khatian_no):
    kh = next(k for k in load("land_khatians")
              if k["khatian_no"] == khatian_no)
    mouza = next(m for m in load("land_mouzas") if m["id"] == kh["mouza_id"])
    upz = next(u for u in load("geo_upazilas")
               if u["id"] == mouza["upazila_id"])
    dist = next(d for d in load("geo_districts")
                if d["id"] == upz["district_id"])
    return dist["division_id"], dist["id"], upz["id"], mouza["id"]


def geo_names_for_khatian(khatian_no, lang):
    kh = next(k for k in load_ml("land_khatians", lang)
              if k["khatian_no"] == khatian_no)
    mouza = next(m for m in load_ml("land_mouzas", lang)
                 if m["id"] == kh["mouza_id"])
    upz = next(u for u in load_ml("geo_upazilas", lang)
               if u["id"] == mouza["upazila_id"])
    dist = next(d for d in load_ml("geo_districts", lang)
                if d["id"] == upz["district_id"])
    div = next(v for v in load_ml("geo_divisions", lang)
               if v["id"] == dist["division_id"])
    return kh, mouza, upz, dist, div


def no_collide(*vals):
    ss = [str(v) for v in vals]
    assert all(a not in b for a in ss for b in ss if a is not b), ss


def build(lang):
    V = make_V(lang)
    NR = LIT[lang]["nr"]
    src = {t["task_id"]: t for t in
           json.load(open(SRC_TASKS, encoding="utf-8"))}
    PK = I18N[lang]

    def I(key, **kw):
        return PK[key].format(**{**V, **kw})

    fees_en = load("fee_schedules")

    fees = load_ml("fee_schedules", lang)
    meters = load_ml("meters", lang)
    bills = load_ml("bills", lang)
    dues = load_ml("land_tax_dues", lang)
    notices = load_ml("notices", lang)
    passports = load_ml("passports", lang)
    licences = load_ml("licences", lang)
    tins = load_ml("tins", lang)
    vaccines = load_ml("vaccine_records", lang)
    civils = load_ml("civil_records", lang)
    exams = load_ml("exam_results", lang)
    boards = load_ml("exam_boards", lang)
    offices = load_ml("offices", lang)
    cz = load_ml("citizens", lang)
    citizen_of = {c["id"]: c for c in cz}
    cont = site_content(lang)
    svc_name = {sid: cont[slug]["name"] for sid, slug, _ in SERVICES}

    def bills_of(consumer_no):
        m = next(x for x in meters if x["consumer_no"] == consumer_no)
        return sorted((b for b in bills if b["meter_id"] == m["id"]),
                      key=lambda b: b["period"])

    my_bills = bills_of("08000007")
    my_unpaid = [b for b in my_bills if not b["is_paid"]]
    assert [b["bill_no"] for b in my_unpaid] == ["BL0000005", "BL0000006"]

    T = []
    n = 0
    P = "/services"
    LOGIN = ["goto /login",
             "fill 1 citizen_id=9999708182203; password=citizen1234"]

    def task(intent, eval_, solution, login=True, steps=30):
        nonlocal n
        n += 1
        T.append({"id": f"portal-{n:03d}", "site": "portal",
                  "intent": intent + (V["cred"] if login else ""),
                  "start_path": "/", "eval": eval_, "solution": solution,
                  "max_steps": steps})

    def variants(answer):
        answer = str(answer)
        out = [answer]
        if answer.isdigit() and len(answer) > 3 and \
                not answer.startswith("0"):
            out.append(f"{int(answer):,}")
        if lang in DIGITS and answer.isascii() and \
                any(ch.isdigit() for ch in answer):
            nd = str.maketrans("0123456789", DIGITS[lang])
            out += [v.translate(nd) for v in list(out)]
        return list(dict.fromkeys(out))

    def answer_ev(answer, also=None, exact=False, none_of=None):
        ev = {"type": "answer_match"}
        if exact:
            ev["mode"] = "exact"
        vs = variants(answer) + (also or [])
        if len(vs) > 1:
            ev["any_of"] = vs
        else:
            ev["answer"] = vs[0]
        if none_of:
            bad = sorted({str(x) for x in none_of} - set(vs)
                         - {str(answer)})
            bad = [x for x in bad if not any(
                x.lower() in str(t).lower() for t in vs)]
            if bad:
                ev["none_of"] = bad
        return ev

    def pay_ev(match):
        return {"type": "db_record_exists", "table": "payments",
                "match": match}

    def sub_ev(kind, payload_part=None):
        m = {"kind": kind}
        if payload_part is not None:
            m["payload"] = f"%{payload_part}%"
        return {"type": "db_record_exists", "table": "submissions",
                "match": m}

    _, m4438, u4438, d4438, v4438 = geo_names_for_khatian("4438", lang)

    def src_task(tid, eval_, solution):
        s = src[tid]
        intent = I(f"src_{tid}", mouza=m4438["name"], upazila=u4438["name"],
                   district=d4438["name"], division=v4438["name"])
        if lang == "en":
            ref = s["intent"].replace(SAY_SO, SAY_TOKEN).replace(
                "If no such result exists, say so.",
                "If no such result exists, answer NO_RECORD.")
            assert intent == ref, (tid, intent, ref)
        task(intent, eval_, solution, login=s["login"])

    src_task(2, [{"type": "db_record_exists", "table": "record_overrides",
                  "match": {"table_name": "citizens", "field_name": "name",
                            "new_value": V["nid_new_name"],
                            "document": "%.%"}}],
             LOGIN + [f"goto {P}/national-id/panel/name-correction/",
                      f"fill 1 new_value={V['nid_new_name']}; "
                      "document=secondary-school-certificate-1.pdf"])
    src_task(6, [sub_ev("passport-new")],
             LOGIN + [f"goto {P}/passport/panel/new-application/",
                      f"fill 1 name={V['name']}; dob={V['dob']}; "
                      f"father_name={V['father']}",
                      f"fill 1 present_addr={V['present']}; "
                      f"perm_addr={V['perm']}",
                      "fill 1 pages=48; validity=5; delivery=regular"])
    src_task(8, [{"type": "db_record_exists", "table": "appointments",
                  "match": {"service_id": 2, "slot_date": "2026-06-22",
                            "slot_time": "10:30",
                            "office": V["office_passport"]}}],
             LOGIN + [f"goto {P}/passport/panel/appointment-booking/",
                      f"fill 1 office={V['office_passport']}; "
                      "slot_date=2026-06-22; slot_time=10:30"])
    src_task(16, [pay_ev({"target_kind": "bill", "ref": "BL0000005"})],
             LOGIN + [f"goto {P}/electricity/panel/bill-payment/"
                      "?consumer_no=08000007",
                      "fill 1 method=card"])
    src_task(25, [sub_ev("tin-registration")],
             LOGIN + [f"goto {P}/tax/panel/tin-registration/",
                      f"fill 1 name={V['name']}; "
                      f"father_name={V['father']}; dob={V['dob']}; "
                      f"address={V['present']}",
                      f"fill 1 circle={V['circle']}; "
                      f"income_source={V['income']}"])

    def new_task(old_tid, eval_, solution, login=True):
        intent = I(f"new_{old_tid}", district=d4438["name"])
        if lang == "en":
            assert intent == INTENTS_EN_NEW[old_tid], old_tid
        task(intent, eval_, solution, login=login, steps=40)

    jan = next(b for b in my_bills if b["period"] == "2026-01")
    fee_row = max((f for f in fees
                   if f["service_id"] == 5 and f["amount"] <= jan["amount"]),
                  key=lambda f: f["amount"])
    oldest_unpaid = my_unpaid[0]
    total_billed = sum(b["amount"] for b in my_bills)
    k4438 = next(k for k in load_ml("land_khatians", lang)
                 if k["khatian_no"] == "4438")
    r763370 = next(r for r in exams if r["roll_no"] == "763370")
    board763 = next(b for b in boards if b["id"] == r763370["board_id"])
    c373 = next(c for c in civils
                if c["registration_no"] == "20000000000373")
    n1012 = next(x for x in notices if x["service_id"] == 5
                 and x["issued_date"] == "2025-10-12")
    p17 = next(p for p in passports
               if p["application_id"] == "PPA04000017")

    def fee_of(service_id, **kw):
        hits = [f for f in fees_en if f["service_id"] == service_id
                and all(str(v).lower() in str(f[k]).lower()
                        for k, v in kw.items())
                and f["amount"] > 0]
        assert len(hits) == 1, (service_id, kw, hits)
        return next(f for f in fees if f["id"] == hits[0]["id"])

    express17 = fee_of(2, category="Ordinary",
                       variant=str(p17["pages"]), delivery="express",
                       validity=str(p17["validity_years"]))

    new_task(34, [answer_ev(fee_row["variant"]),
                  pay_ev({"target_kind": "bill",
                          "ref": oldest_unpaid["bill_no"]})],
             LOGIN + [f"goto {P}/electricity/panel/bill-history/",
                      f"goto {P}/electricity/fees/",
                      f"goto {P}/electricity/panel/bill-payment/"
                      "?consumer_no=08000007",
                      "fill 1 method=card",
                      f"stop {fee_row['variant']}"])
    dv, dt, up, mz = geo_ids_for_khatian("4438")
    cascade4438 = (f"goto {P}/land/panel/record-search/?division={dv}"
                   f"&district={dt}&upazila={up}&mouza={mz}")
    other_plots = [k["plot_no"] for k in load_ml("land_khatians", lang)
                   if k["khatian_no"] != "4438"
                   and geo_names_for_khatian(k["khatian_no"], lang)[3]["id"]
                   == d4438["id"]]
    new_task(35, [answer_ev(k4438["plot_no"], none_of=other_plots)],
             LOGIN + [cascade4438, "fill 1 khatian_no=4438",
                      f"stop {k4438['plot_no']}"])
    new_task(36, [answer_ev(r763370["institution"])],
             [f"goto {P}/exam-results/panel/result-lookup/",
              f"fill 1 exam=secondary; board={board763['name']}; "
              "year=2021; roll_no=763370",
              f"stop {r763370['institution']}"], login=False)
    new_task(37, [answer_ev(c373["registered_date"])],
             LOGIN + [f"goto {P}/civil-registration/panel/birth-status/",
                      "fill 1 registration_no=20000000000373",
                      f"stop {c373['registered_date']}"])
    new_task(38, [answer_ev(n1012["category"])],
             [f"goto {P}/electricity/", f"stop {n1012['category']}"],
             login=False)
    new_task(39, [answer_ev(express17["amount"], none_of=[
                      f["amount"] for f in fees if f["service_id"] == 2
                      and f["amount"] != express17["amount"]])],
             LOGIN + [f"goto {P}/passport/panel/application-status/",
                      "fill 1 application_id=PPA04000017",
                      f"goto {P}/passport/fees/",
                      f"stop {express17['amount']}"])
    new_task(40, [answer_ev(total_billed)],
             LOGIN + [f"goto {P}/electricity/panel/bill-history/",
                      f"stop {total_billed}"])

    src_task(31, [answer_ev("NO_RECORD")],
             LOGIN + [f"goto {P}/national-id/panel/correction-status/",
                      "fill 1 slip_no=NI9999999", "stop NO_RECORD"])
    src_task(32, [answer_ev("NO_RECORD")],
             LOGIN + [cascade4438, "fill 1 khatian_no=99999",
                      "stop NO_RECORD"])
    src_task(33, [answer_ev("NO_RECORD")],
             [f"goto {P}/exam-results/panel/result-lookup/",
              f"fill 1 exam=secondary; board={V['board']}; year=2021; "
              "roll_no=999999", "stop NO_RECORD"])
    assert n == 15, n

    lic_below = max((f for f in fees if f["service_id"] == 7
                     and f["amount"] < jan["amount"]),
                    key=lambda f: f["amount"])
    assert sum(1 for f in fees if f["service_id"] == 7
               and f["amount"] == lic_below["amount"]) == 1
    task(I("a1"),
         [answer_ev(lic_below["amount"], none_of=[
              f["amount"] for f in fees if f["service_id"] == 7
              and f["amount"] != lic_below["amount"]]),
          pay_ev({"service_id": 7, "target_kind": "fee",
                  "amount": lic_below["amount"]})],
         LOGIN + [f"goto {P}/electricity/panel/bill-history/",
                  f"goto {P}/driving-licence/fees/",
                  f"goto {P}/driving-licence/panel/fee-challan/",
                  f"fill 1 category={lic_below['category']}; "
                  f"variant={lic_below['variant']}; method=card",
                  f"stop {lic_below['amount']}"],
         steps=40)

    out49 = sum(b["amount"] for b in bills_of("08000049")
                if not b["is_paid"])
    half49 = out49 // 2
    elec_below = max((f for f in fees if f["service_id"] == 5
                      and f["amount"] < half49),
                     key=lambda f: f["amount"])
    assert sum(1 for f in fees if f["service_id"] == 5
               and f["amount"] == elec_below["amount"]) == 1
    task(I("a2"),
         [answer_ev(elec_below["variant"])],
         LOGIN + [f"goto {P}/electricity/panel/due-check/",
                  "fill 1 consumer_no=08000049",
                  f"goto {P}/electricity/fees/",
                  f"stop {elec_below['variant']}"],
         steps=40)

    task(I("b1"),
         [pay_ev({"target_kind": "bill", "ref": "BL0000005"}),
          pay_ev({"target_kind": "bill", "ref": "BL0000006"})],
         LOGIN + [f"goto {P}/electricity/panel/bill-payment/"
                  "?consumer_no=08000007", "fill 1 method=card",
                  f"goto {P}/electricity/panel/bill-payment/"
                  "?consumer_no=08000007", "fill 1 method=card"],
         steps=40)

    u21 = [b for b in bills_of("08000021") if not b["is_paid"]]
    assert len(u21) == 2
    task(I("b2"),
         [pay_ev({"target_kind": "bill", "ref": u21[0]["bill_no"]}),
          {"type": "db_record_absent", "table": "payments",
           "match": {"target_kind": "bill", "ref": u21[1]["bill_no"]}}],
         LOGIN + [f"goto {P}/electricity/panel/bill-payment/"
                  "?consumer_no=08000021", "fill 1 method=card"])

    out35 = sum(b["amount"] for b in bills_of("08000035")
                if not b["is_paid"])
    assert out49 != out35
    task(I("b3"),
         [answer_ev(out49 - out35)],
         LOGIN + [f"goto {P}/electricity/panel/due-check/",
                  "fill 1 consumer_no=08000049",
                  f"goto {P}/electricity/panel/due-check/",
                  "fill 1 consumer_no=08000035",
                  f"stop {out49 - out35}"],
         steps=40)

    my_out = sum(b["amount"] for b in my_unpaid)
    d1 = [d for d in dues if d["holding_id"] == 1 and not d["is_paid"]]
    land1 = sum(d["amount"] for d in d1)
    assert my_out != land1
    bigger_cd = max(my_out, land1)
    task(I("b4"),
         [answer_ev(bigger_cd)],
         LOGIN + [f"goto {P}/electricity/panel/due-check/",
                  "fill 1 consumer_no=08000007",
                  f"goto {P}/land/panel/tax-payment/?holding_no=HLD00001",
                  f"stop {bigger_cd}"],
         steps=40)

    over2000 = sum(1 for b in my_bills if b["amount"] > 2000)
    task(I("b5"),
         [answer_ev(over2000)],
         LOGIN + [f"goto {P}/electricity/panel/bill-history/",
                  f"stop {over2000}"])

    kA, mA, uA, dA, vA = geo_names_for_khatian("5265", lang)
    assert geo_names_for_khatian("5265", "en")[4]["name"] == "Khulna"
    dv2, dt2, up2, mz2 = geo_ids_for_khatian("5265")
    task(I("c1", district=dA["name"], division=vA["name"]),
         [answer_ev(kA["owner_name"])],
         LOGIN + [f"goto {P}/land/panel/record-search/?division={dv2}"
                  f"&district={dt2}&upazila={up2}&mouza={mz2}",
                  "fill 1 khatian_no=5265", f"stop {kA['owner_name']}"],
         steps=40)

    kB, mB, uB, dB, vB = geo_names_for_khatian("9458", lang)
    no_collide(kB["owner_name"], kB["land_type"], kB["area_decimal"])
    dv3, dt3, up3, mz3 = geo_ids_for_khatian("9458")
    task(I("c2", mouza=mB["name"], upazila=uB["name"], district=dB["name"],
           division=vB["name"]),
         [answer_ev(kB["owner_name"]), answer_ev(kB["land_type"]),
          answer_ev(kB["area_decimal"])],
         LOGIN + [f"goto {P}/land/panel/record-search/?division={dv3}"
                  f"&district={dt3}&upazila={up3}&mouza={mz3}",
                  "fill 1 khatian_no=9458",
                  f"stop {kB['owner_name']}, {kB['land_type']}, "
                  f"{kB['area_decimal']}"],
         steps=40)

    kC, mC, uC, dC, vC = geo_names_for_khatian("6743", lang)
    dv4, dt4, up4, mz4 = geo_ids_for_khatian("6743")
    task(I("c3", mouza=mC["name"], upazila=uC["name"], district=dC["name"],
           division=vC["name"]),
         [sub_ev("land-mutation", kC["owner_name"]),
          sub_ev("land-mutation", f'"plot_no": "{kC["plot_no"]}"'),
          sub_ev("land-mutation", '"khatian_no": "6743"'),
          sub_ev("land-mutation", '"buyer_id": "9999708182203"'),
          sub_ev("land-mutation", '"seller_id": "9999000000002"'),
          sub_ev("land-mutation", f'"area": "{kC["area_decimal"]}"')],
         LOGIN + [f"goto {P}/land/panel/record-search/?division={dv4}"
                  f"&district={dt4}&upazila={up4}&mouza={mz4}",
                  "fill 1 khatian_no=6743",
                  f"goto {P}/land/panel/mutation-apply/",
                  f"fill 1 buyer_name={V['name']}; "
                  f"buyer_id=9999708182203; "
                  f"seller_name={kC['owner_name']}; "
                  "seller_id=9999000000002; khatian_no=6743; "
                  f"plot_no={kC['plot_no']}; area={kC['area_decimal']}"],
         steps=40)

    d3 = sorted((d for d in dues if d["holding_id"] == 3
                 and not d["is_paid"]), key=lambda d: d["fiscal_year"])
    assert len(d3) == 3
    assert len({d["amount"] for d in d3}) == 3
    task(I("c4"),
         [pay_ev({"target_kind": "tax", "ref": "HLD00003",
                  "amount": d["amount"]}) for d in d3],
         LOGIN + sum([[f"goto {P}/land/panel/tax-payment/"
                       "?holding_no=HLD00003", "fill 1 method=card"]
                      for _ in d3], []),
         steps=40)

    tot3 = sum(d["amount"] for d in d3)
    tot4 = sum(d["amount"] for d in dues
               if d["holding_id"] == 4 and not d["is_paid"])
    assert tot3 != tot4
    win_c5 = "HLD00003" if tot3 > tot4 else "HLD00004"
    task(I("c5"),
         [answer_ev(win_c5, none_of=["HLD00003", "HLD00004"])],
         LOGIN + [f"goto {P}/land/panel/tax-payment/?holding_no=HLD00003",
                  f"goto {P}/land/panel/tax-payment/?holding_no=HLD00004",
                  f"stop {win_c5}"],
         steps=40)

    kD, mD, uD, dD, vD = geo_names_for_khatian("7181", lang)
    dv5, dt5, up5, _ = geo_ids_for_khatian("7181")
    task(I("c6", upazila=uD["name"], district=dD["name"],
           division=vD["name"], mouza=mD["name"]),
         [answer_ev(mD["jl_no"], none_of=[
              m["jl_no"] for m in load_ml("land_mouzas", lang)
              if m["upazila_id"] == uD["id"] and m["id"] != mD["id"]])],
         LOGIN + [f"goto {P}/land/panel/record-search/?division={dv5}"
                  f"&district={dt5}&upazila={up5}",
                  f"stop {mD['jl_no']}"],
         steps=40)

    kE, mE, uE, dE, vE = geo_names_for_khatian("2052", lang)
    dv6, dt6, up6, mz6 = geo_ids_for_khatian("2052")
    task(I("c7", division=vE["name"]),
         [answer_ev(kE["owner_name"])],
         LOGIN + [f"goto {P}/land/panel/record-search/?division={dv6}"
                  f"&district={dt6}&upazila={up6}&mouza={mz6}",
                  "fill 1 khatian_no=2052", f"stop {kE['owner_name']}"],
         steps=40)

    kF, mF, uF, dF, vF = geo_names_for_khatian("8630", lang)
    no_collide(kF["owner_name"], kF["area_decimal"])
    dv7, dt7, up7, mz7 = geo_ids_for_khatian("8630")
    task(I("c8", district=dF["name"], division=vF["name"]),
         [answer_ev(kF["owner_name"]), answer_ev(kF["area_decimal"])],
         LOGIN + [f"goto {P}/land/panel/record-search/?division={dv7}"
                  f"&district={dt7}&upazila={up7}&mouza={mz7}",
                  "fill 1 khatian_no=8630",
                  f"stop {kF['owner_name']}, {kF['area_decimal']}"],
         steps=40)

    kG, mG, uG, dG, vG = geo_names_for_khatian("3232", lang)
    dv8, dt8, up8, mz8 = geo_ids_for_khatian("3232")
    task(I("c9", district=dG["name"], division=vG["name"]),
         [answer_ev(kG["land_type"])],
         LOGIN + [f"goto {P}/land/panel/record-search/?division={dv8}"
                  f"&district={dt8}&upazila={up8}&mouza={mz8}",
                  "fill 1 khatian_no=3232", f"stop {kG['land_type']}"],
         steps=40)

    task(I("c10"),
         [pay_ev({"target_kind": "tax", "ref": "HLD00003",
                  "amount": d3[0]["amount"]}),
          pay_ev({"target_kind": "tax", "ref": "HLD00003",
                  "amount": d3[1]["amount"]}),
          {"type": "db_record_absent", "table": "payments",
           "match": {"target_kind": "tax", "ref": "HLD00003",
                     "amount": d3[2]["amount"]}}],
         LOGIN + [f"goto {P}/land/panel/tax-payment/"
                  "?holding_no=HLD00003", "fill 1 method=card",
                  f"goto {P}/land/panel/tax-payment/"
                  "?holding_no=HLD00003", "fill 1 method=card"],
         steps=40)

    tot5h = sum(d["amount"] for d in dues
                if d["holding_id"] == 5 and not d["is_paid"])
    assert tot4 != tot5h
    win_h45 = "HLD00004" if tot4 > tot5h else "HLD00005"
    task(I("c11"),
         [answer_ev(win_h45, none_of=["HLD00004", "HLD00005"])],
         LOGIN + [f"goto {P}/land/panel/tax-payment/?holding_no=HLD00004",
                  f"goto {P}/land/panel/tax-payment/?holding_no=HLD00005",
                  f"stop {win_h45}"],
         steps=40)

    r244 = next(r for r in exams if r["roll_no"] == "244479")
    board244 = next(b for b in boards if b["id"] == r244["board_id"])
    task(I("e1"),
         [sub_ev("exam-rescrutiny", r244["registration_no"]),
          sub_ev("exam-rescrutiny", '"roll_no": "244479"'),
          sub_ev("exam-rescrutiny", f'"subjects": "{V["math"]}"'),
          sub_ev("exam-rescrutiny", f'"board": "{board244["name"]}"'),
          sub_ev("exam-rescrutiny", '"year": "2021"')],
         [f"goto {P}/exam-results/panel/result-lookup/",
          f"fill 1 exam=secondary; board={board244['name']}; year=2021; "
          "roll_no=244479",
          f"goto {P}/exam-results/panel/rescrutiny-apply/",
          f"fill 1 roll_no=244479; "
          f"registration_no={r244['registration_no']}; "
          f"board={board244['name']}; year=2021; subjects={V['math']}"],
         login=False, steps=40)

    r969 = next(r for r in exams if r["roll_no"] == "969953")
    b969 = next(b for b in boards if b["id"] == r969["board_id"])
    task(I("e2", exam=r969["exam"], exam_l=LIT[lang]["exam_l"][r969["exam"]],
           year=r969["exam_year"]),
         [sub_ev("exam-rescrutiny", r969["registration_no"]),
          sub_ev("exam-rescrutiny", '"roll_no": "969953"'),
          sub_ev("exam-rescrutiny", f'"subjects": "{V["eng"]}"'),
          sub_ev("exam-rescrutiny", f'"board": "{b969["name"]}"'),
          sub_ev("exam-rescrutiny", f'"year": "{r969["exam_year"]}"')],
         [f"goto {P}/exam-results/panel/result-lookup/",
          f"fill 1 exam={r969['exam']}; board={b969['name']}; "
          f"year={r969['exam_year']}; roll_no=969953",
          f"goto {P}/exam-results/panel/rescrutiny-apply/",
          f"fill 1 roll_no=969953; "
          f"registration_no={r969['registration_no']}; "
          f"board={b969['name']}; year={r969['exam_year']}; "
          f"subjects={V['eng']}"],
         login=False, steps=40)

    from collections import Counter as _C
    land_cat = _C(x["category"] for x in notices if x["service_id"] == 4)
    (top_cat, tc_k), (_, tc2_k) = land_cat.most_common(2)
    assert tc_k > tc2_k
    task(I("e3"),
         [answer_ev(top_cat)],
         [f"goto /notices/?service={svc_name[4]}", f"stop {top_cat}"],
         login=False, steps=40)

    inc, ded = 640000, 640000 // 8
    tax_p = (inc - ded) // 10
    no_collide(inc, ded, tax_p)
    task(I("e4"),
         [sub_ev("individual-return", '"tin_no": "972871718941"'),
          sub_ev("individual-return", '"assessment_year": "2025-2026"'),
          sub_ev("individual-return", '"declaration": "YES"'),
          sub_ev("individual-return", f'"total_income": "{inc}"'),
          sub_ev("individual-return", f'"deductions": "{ded}"'),
          sub_ev("individual-return", f'"tax_payable": "{tax_p}"')],
         LOGIN + [f"goto {P}/tax/panel/ereturn-submit/",
                  "fill 1 assessment_year=2025-2026; "
                  f"tin_no=972871718941; total_income={inc}; "
                  f"deductions={ded}; tax_payable={tax_p}; "
                  "declaration=YES"])

    tl_notices = sorted((x for x in notices if x["service_id"] == 12),
                        key=lambda x: x["issued_date"])
    tl_ref = tl_notices[-1]["ref_no"]
    tl_fees = [f for f in fees if f["service_id"] == 12]
    tl_min = min(tl_fees, key=lambda f: f["amount"])
    assert sum(1 for f in tl_fees if f["amount"] == tl_min["amount"]) == 1
    task(I("e5", ref=tl_ref),
         [answer_ev(tl_min["amount"], none_of=[
              f["amount"] for f in tl_fees
              if f["amount"] != tl_min["amount"]])],
         ["goto /notices/", f"goto {P}/trade-licence/fees/",
          f"stop {tl_min['amount']}"],
         login=False, steps=40)

    task(I("g1"),
         [pay_ev({"target_kind": "bill", "ref": "BL0000006"}),
          pay_ev({"target_kind": "recharge", "ref": "MTR000006",
                  "amount": 750})],
         LOGIN + [f"goto {P}/electricity/panel/bill-payment/"
                  "?consumer_no=08000007", "fill 2 method=card",
                  f"goto {P}/electricity/panel/prepaid-recharge/",
                  "fill 1 meter_no=MTR000006; amount=750; method=card"],
         steps=40)

    task(I("g2"),
         [sub_ev("nid-voter-registration",
                 f'"centre": "{V["centre"]}"'),
          {"type": "db_record_exists", "table": "appointments",
           "match": {"service_id": 2, "slot_date": "2026-06-25",
                     "slot_time": "15:00",
                     "office": V["office_passport"]}}],
         LOGIN + [f"goto {P}/national-id/panel/voter-registration/",
                  f"fill 1 name={V['name']}; "
                  f"father_name={V['father']}; dob={V['dob']}; "
                  f"present_addr={V['present']}; "
                  f"perm_addr={V['perm']}; "
                  f"centre={V['centre']}",
                  f"goto {P}/passport/panel/appointment-booking/",
                  f"fill 1 office={V['office_passport']}; "
                  "slot_date=2026-06-25; slot_time=15:00"],
         steps=40)

    task(I("g3"),
         [sub_ev("police-clearance", V["purpose"]),
          sub_ev("police-clearance", f'"name": "{V["name"]}"'),
          sub_ev("police-clearance", f'"father_name": "{V["father"]}"'),
          sub_ev("pilgrimage-pre-registration",
                 '"passport_no": "PPA04000017"'),
          sub_ev("pilgrimage-pre-registration", f'"name": "{V["name"]}"'),
          sub_ev("pilgrimage-pre-registration",
                 f'"father_name": "{V["father"]}"'),
          sub_ev("pilgrimage-pre-registration", '"package": "government"'),
          sub_ev("pilgrimage-pre-registration",
                 f'"next_of_kin": "{V["mother"]}"')],
         LOGIN + [f"goto {P}/police-clearance/panel/clearance-apply/",
                  f"fill 1 name={V['name']}; "
                  f"father_name={V['father']}; dob={V['dob']}; "
                  f"present_addr={V['present']}; "
                  f"perm_addr={V['perm']}; purpose={V['purpose']}",
                  f"goto {P}/pilgrimage/panel/pre-registration/",
                  f"fill 1 name={V['name']}; "
                  f"father_name={V['father']}; passport_no=PPA04000017; "
                  f"address={V['present']}; mobile={V['mobile']}; "
                  f"next_of_kin={V['mother']}; package=government"],
         steps=40)

    task(I("g4"),
         [sub_ev("land-mutation", f'"seller_name": "{V["rafiqul"]}"'),
          sub_ev("land-mutation", '"khatian_no": "4438"'),
          sub_ev("land-mutation", '"plot_no": "357"'),
          sub_ev("land-mutation", '"area": "25"'),
          pay_ev({"target_kind": "tax", "ref": "HLD00002"})],
         LOGIN + [f"goto {P}/land/panel/mutation-apply/",
                  f"fill 1 buyer_name={V['name']}; "
                  f"buyer_id=9999708182203; seller_name={V['rafiqul']}; "
                  "seller_id=9999000000001; khatian_no=4438; "
                  "plot_no=357; area=25",
                  f"goto {P}/land/panel/tax-payment/?holding_no=HLD00002",
                  "fill 1 method=card"],
         steps=40)

    task(I("g5"),
         [pay_ev({"target_kind": "bill", "ref": "BL0000006"}),
          {"type": "db_record_absent", "table": "payments",
           "match": {"target_kind": "bill", "ref": "BL0000005"}}],
         LOGIN + [f"goto {P}/electricity/panel/bill-payment/"
                  "?consumer_no=08000007", "fill 2 method=card"])

    feb = sum(1 for x in notices if x["issued_date"].startswith("2026-02"))
    task(I("h1"),
         [answer_ev(feb)],
         ["goto /notices/?period=2026-02", f"stop {feb}"],
         login=False, steps=40)

    from collections import Counter
    c25 = Counter(x["service_id"] for x in notices
                  if x["issued_date"].startswith("2025"))
    (top_sid, top_k), (_, second_k) = c25.most_common(2)
    assert top_k > second_k
    task(I("h2"),
         [answer_ev(svc_name[top_sid])],
         ["goto /notices/?period=2025", "goto /notices/?period=2025&page=2",
          "goto /notices/?period=2025&page=3",
          f"stop {svc_name[top_sid]}"],
         login=False, steps=40)

    oldest_n = min(notices, key=lambda x: (x["issued_date"], x["id"]))
    assert sum(1 for x in notices
               if x["issued_date"] == oldest_n["issued_date"]) == 1
    task(I("h3"),
         [answer_ev(oldest_n["title"])],
         [f"goto /notices/?page={(len(notices) + 19) // 20}",
          f"stop {oldest_n['title']}"],
         login=False, steps=40)

    clos26 = sum(1 for x in notices if x["category"] == V["closure"]
                 and x["issued_date"].startswith("2026"))
    assert clos26 == sum(1 for x in load("notices")
                         if x["category"] == "closure"
                         and x["issued_date"].startswith("2026"))
    task(I("h4"),
         [answer_ev(clos26)],
         [f"goto /notices/?period=2026&category={V['closure']}",
          f"stop {clos26}"], login=False, steps=40)

    r496 = next(r for r in exams if r["roll_no"] == "496396")
    b496 = next(b for b in boards if b["id"] == r496["board_id"])
    assert r496["gpa"] not in r496["institution"]
    task(I("n1", exam=r496["exam"], exam_l=LIT[lang]["exam_l"][r496["exam"]],
           year=r496["exam_year"]),
         [answer_ev(r496["gpa"]), answer_ev(r496["institution"])],
         [f"goto {P}/exam-results/panel/result-lookup/",
          f"fill 1 exam={r496['exam']}; board={b496['name']}; "
          f"year={r496['exam_year']}; roll_no=496396",
          f"stop {r496['gpa']}, {r496['institution']}"],
         login=False, steps=40)

    r9695 = next(r for r in exams if r["roll_no"] == "969525")
    b9695 = next(b for b in boards if b["id"] == r9695["board_id"])
    no_collide(r9695["gpa"], r9695["candidate_name"])
    task(I("n2", exam=r9695["exam"],
           exam_l=LIT[lang]["exam_l"][r9695["exam"]],
           year=r9695["exam_year"]),
         [answer_ev(r9695["candidate_name"]), answer_ev(r9695["gpa"])],
         [f"goto {P}/exam-results/panel/result-lookup/",
          f"fill 1 exam={r9695['exam']}; board={b9695['name']}; "
          f"year={r9695['exam_year']}; roll_no=969525",
          f"stop {r9695['candidate_name']}, {r9695['gpa']}"],
         login=False, steps=40)

    kH, mH, uH, dH, vH = geo_names_for_khatian("7191", lang)
    dv9, dt9, up9, mz9 = geo_ids_for_khatian("7191")
    task(I("n3", district=dH["name"], division=vH["name"]),
         [answer_ev(kH["land_type"])],
         LOGIN + [f"goto {P}/land/panel/record-search/?division={dv9}"
                  f"&district={dt9}&upazila={up9}&mouza={mz9}",
                  "fill 1 khatian_no=7191", f"stop {kH['land_type']}"],
         steps=40)

    kI, mI, uI, dI, vI = geo_names_for_khatian("1022", lang)
    no_collide(kI["owner_name"], kI["share"])
    dv10, dt10, up10, mz10 = geo_ids_for_khatian("1022")
    task(I("n4", district=dI["name"], division=vI["name"]),
         [answer_ev(kI["owner_name"]), answer_ev(kI["share"])],
         LOGIN + [f"goto {P}/land/panel/record-search/?division={dv10}"
                  f"&district={dt10}&upazila={up10}&mouza={mz10}",
                  "fill 1 khatian_no=1022",
                  f"stop {kI['owner_name']}, {kI['share']}"],
         steps=40)

    jun = [x for x in notices if x["issued_date"].startswith("2026-06")]
    assert len(jun) == 1
    no_collide(jun[0]["ref_no"], svc_name[jun[0]["service_id"]])
    task(I("n5"),
         [answer_ev(jun[0]["ref_no"]),
          answer_ev(svc_name[jun[0]["service_id"]])],
         ["goto /notices/?period=2026-06",
          f"stop {jun[0]['ref_no']}, "
          f"{svc_name[jun[0]['service_id']]}"],
         login=False, steps=40)

    m26 = _C(x["issued_date"][:7] for x in notices
             if x["issued_date"].startswith("2026"))
    low_m, low_k = min(m26.items(), key=lambda kv: (kv[1], kv[0]))
    assert sum(1 for v in m26.values() if v == low_k) == 1
    task(I("n6"),
         [answer_ev(low_m)],
         [f"goto /notices/?period={low_m}", f"stop {low_m}"],
         login=False, steps=40)

    out21 = sum(b["amount"] for b in bills_of("08000021")
                if not b["is_paid"])
    tri = out21 + out35 + out49
    task(I("n7"),
         [answer_ev(tri)],
         LOGIN + [f"goto {P}/electricity/panel/due-check/",
                  "fill 1 consumer_no=08000021",
                  f"goto {P}/electricity/panel/due-check/",
                  "fill 1 consumer_no=08000035",
                  f"goto {P}/electricity/panel/due-check/",
                  "fill 1 consumer_no=08000049", f"stop {tri}"],
         steps=40)

    tri_h = sum(d["amount"] for d in dues if not d["is_paid"]
                and d["holding_id"] in (3, 4, 5))
    task(I("n8"),
         [answer_ev(tri_h)],
         LOGIN + [f"goto {P}/land/panel/tax-payment/?holding_no=HLD00003",
                  f"goto {P}/land/panel/tax-payment/?holding_no=HLD00004",
                  f"goto {P}/land/panel/tax-payment/?holding_no=HLD00005",
                  f"stop {tri_h}"],
         steps=40)

    units_all = sum(b["units_kwh"] for b in my_bills)
    task(I("n9"),
         [answer_ev(units_all)],
         LOGIN + [f"goto {P}/electricity/panel/bill-history/",
                  f"stop {units_all}"])

    pp_nz = [f["amount"] for f in fees if f["service_id"] == 2
             and f["amount"] > 0]
    span = max(pp_nz) - min(pp_nz)
    task(I("n10"),
         [answer_ev(span)],
         [f"goto {P}/passport/fees/", f"stop {span}"], login=False)

    big_fees = sum(1 for f in fees if f["service_id"] in (2, 7)
                   and f["amount"] > 5000)
    task(I("n11"),
         [answer_ev(big_fees)],
         [f"goto {P}/passport/fees/", f"goto {P}/driving-licence/fees/",
          f"stop {big_fees}"], login=False, steps=40)

    inc2, ded2 = 720000, 720000 // 4
    tax2 = (inc2 - ded2) * 15 // 100
    no_collide(inc2, ded2, tax2)
    task(I("n12"),
         [sub_ev("individual-return", '"tin_no": "972871718941"'),
          sub_ev("individual-return", '"assessment_year": "2025-2026"'),
          sub_ev("individual-return", '"declaration": "YES"'),
          sub_ev("individual-return", f'"total_income": "{inc2}"'),
          sub_ev("individual-return", f'"deductions": "{ded2}"'),
          sub_ev("individual-return", f'"tax_payable": "{tax2}"')],
         LOGIN + [f"goto {P}/tax/panel/ereturn-submit/",
                  "fill 1 assessment_year=2025-2026; "
                  f"tin_no=972871718941; total_income={inc2}; "
                  f"deductions={ded2}; tax_payable={tax2}; "
                  "declaration=YES"])

    task(I("n13"),
         [sub_ev("birth-registration",
                 f'"child_name": "{c373["mother_name"]}"'),
          sub_ev("birth-registration", f'"place": "{c373["place"]}"'),
          sub_ev("birth-registration", '"dob": "2026-03-01"'),
          sub_ev("birth-registration", f'"father_name": "{V["name"]}"'),
          sub_ev("birth-registration",
                 f'"mother_name": "{V["mother"]}"')],
         LOGIN + [f"goto {P}/civil-registration/panel/birth-status/",
                  "fill 1 registration_no=20000000000373",
                  f"goto {P}/civil-registration/panel/birth-apply/",
                  f"fill 1 child_name={c373['mother_name']}; "
                  "dob=2026-03-01; "
                  f"place={c373['place']}; father_name={V['name']}; "
                  f"mother_name={V['mother']}"],
         steps=40)

    pen_fees = [f for f in fees if f["service_id"] == 13]
    pen_max = max(pen_fees, key=lambda f: f["amount"])
    assert sum(1 for f in pen_fees
               if f["amount"] == pen_max["amount"]) == 1
    task(I("n14"),
         [answer_ev(pen_max["amount"], none_of=[
              f["amount"] for f in pen_fees
              if f["amount"] != pen_max["amount"]])],
         [f"goto /notices/?page={(len(notices) + 19) // 20}",
          f"goto {P}/pension/fees/", f"stop {pen_max['amount']}"],
         login=False, steps=40)

    ren_pro = fee_of(7, category="Renewal", variant="Professional")
    task(I("n15"),
         [{"type": "db_record_exists", "table": "appointments",
           "match": {"service_id": 7, "slot_date": "2026-06-23",
                     "slot_time": "09:00",
                     "office": V["office_licence"]}},
          pay_ev({"service_id": 7, "target_kind": "fee",
                  "amount": ren_pro["amount"]}),
          answer_ev(ren_pro["amount"], none_of=[
              f["amount"] for f in fees if f["service_id"] == 7
              and f["amount"] != ren_pro["amount"]])],
         LOGIN + [f"goto {P}/driving-licence/panel/test-booking/",
                  f"fill 1 office={V['office_licence']}; "
                  "slot_date=2026-06-23; slot_time=09:00",
                  f"goto {P}/driving-licence/panel/fee-challan/",
                  f"fill 1 category={ren_pro['category']}; "
                  f"variant={ren_pro['variant']}; "
                  "method=card", f"stop {ren_pro['amount']}"],
         steps=40)

    p34 = next(p for p in passports
               if p["application_id"] == "PPA04000034")
    p68b = next(p for p in passports
                if p["application_id"] == "PPA04000068")
    f34 = fee_of(2, category="Ordinary", variant=str(p34["pages"]),
                 delivery="regular", validity=str(p34["validity_years"]))
    f68 = fee_of(2, category="Ordinary", variant=str(p68b["pages"]),
                 delivery="regular",
                 validity=str(p68b["validity_years"]))
    assert f34["amount"] != f68["amount"]
    win_pp = "PPA04000034" if f34["amount"] > f68["amount"] \
        else "PPA04000068"
    task(I("n16"),
         [answer_ev(win_pp)],
         LOGIN + [f"goto {P}/passport/panel/application-status/",
                  "fill 1 application_id=PPA04000034",
                  f"goto {P}/passport/panel/application-status/",
                  "fill 1 application_id=PPA04000068",
                  f"goto {P}/passport/fees/", f"stop {win_pp}"],
         steps=40)

    task(I("n17"),
         [pay_ev({"target_kind": "bill", "ref": "BL0000005"}),
          pay_ev({"target_kind": "tax", "ref": "HLD00002"}),
          {"type": "db_record_exists", "table": "appointments",
           "match": {"service_id": 2, "slot_date": "2026-06-24",
                     "slot_time": "11:30",
                     "office": V["office_passport"]}}],
         LOGIN + [f"goto {P}/electricity/panel/bill-payment/"
                  "?consumer_no=08000007", "fill 1 method=card",
                  f"goto {P}/land/panel/tax-payment/?holding_no=HLD00002",
                  "fill 1 method=card",
                  f"goto {P}/passport/panel/appointment-booking/",
                  f"fill 1 office={V['office_passport']}; "
                  "slot_date=2026-06-24; slot_time=11:30"],
         steps=40)

    task(I("n18"),
         [pay_ev({"target_kind": "tax", "ref": "HLD00003",
                  "amount": d3[1]["amount"]}),
          {"type": "db_record_absent", "table": "payments",
           "match": {"target_kind": "tax", "ref": "HLD00003",
                     "amount": d3[0]["amount"]}},
          {"type": "db_record_absent", "table": "payments",
           "match": {"target_kind": "tax", "ref": "HLD00003",
                     "amount": d3[2]["amount"]}}],
         LOGIN + [f"goto {P}/land/panel/tax-payment/"
                  "?holding_no=HLD00003", "fill 2 method=card"])

    task(I("n19"),
         [{"type": "db_record_exists", "table": "record_overrides",
           "match": {"table_name": "citizens",
                     "field_name": "present_addr",
                     "new_value": V["new_addr"], "document": "%.%"}},
          {"type": "db_record_exists", "table": "record_overrides",
           "match": {"table_name": "citizens", "field_name": "dob",
                     "new_value": V["new_dob"], "document": "%.%"}},
          {"type": "db_record_exists", "table": "record_overrides",
           "match": {"table_name": "civil_records",
                     "new_value": V["hoque"], "document": "%.%"}}],
         LOGIN + [f"goto {P}/national-id/panel/address-correction/",
                  f"fill 1 new_value={V['new_addr']}; "
                  "document=secondary-school-certificate-1.pdf",
                  f"goto {P}/national-id/panel/dob-correction/",
                  f"fill 1 new_value={V['new_dob']}; "
                  "document=secondary-school-certificate-1.pdf",
                  f"goto {P}/civil-registration/panel/birth-correction/",
                  f"fill 1 new_value={V['hoque']}; "
                  "document=secondary-school-certificate-1.pdf"],
         steps=40)

    task(I("n20"),
         [sub_ev("passport-new", '"pages": "64"'),
          sub_ev("passport-new", '"validity": "10"'),
          sub_ev("passport-new", '"delivery": "express"'),
          sub_ev("passport-reissue", '"passport_no": "A6053903"'),
          sub_ev("passport-reissue", f'"reason": "{V["damaged"]}"')],
         LOGIN + [f"goto {P}/passport/panel/new-application/",
                  f"fill 1 name={V['name']}; dob={V['dob']}; "
                  f"father_name={V['father']}",
                  f"fill 1 present_addr={V['present']}; "
                  f"perm_addr={V['perm']}",
                  "fill 1 pages=64; validity=10; delivery=express",
                  f"goto {P}/passport/panel/reissue-application/",
                  f"fill 1 passport_no=A6053903; reason={V['damaged']}"],
         steps=40)

    task(I("i1") + NR,
         [answer_ev("NO_RECORD"),
          {"type": "db_record_absent", "table": "payments",
           "match": {"target_kind": "recharge"}}],
         LOGIN + [f"goto {P}/electricity/panel/prepaid-recharge/",
                  "fill 1 meter_no=MTR000001; amount=300; method=card",
                  "stop NO_RECORD"])

    task(I("i2") + NR,
         [answer_ev("NO_RECORD")],
         [f"goto {P}/health/panel/vaccine-certificate/",
          "fill 1 identity_no=9999708182203; registered_date=2023-09-16",
          "stop NO_RECORD"], login=False)

    task(I("i3") + NR,
         [answer_ev("NO_RECORD")],
         LOGIN + [f"goto {P}/passport/panel/application-status/",
                  "fill 1 application_id=PPA04000017", "stop NO_RECORD"])

    assert not [f for f in fees_en if f["category"] == "Licence"
                and f["variant"] == "Motorcycle"]
    task(I("i4") + NR,
         [answer_ev("NO_RECORD"),
          {"type": "db_record_absent", "table": "payments",
           "match": {"service_id": 7, "target_kind": "fee"}}],
         LOGIN + [f"goto {P}/driving-licence/panel/fee-challan/",
                  f"fill 1 category={V['cat_licence']}; "
                  f"variant={V['var_motorcycle']}; "
                  "method=card", "stop NO_RECORD"])

    task(I("i5") + NR,
         [answer_ev("NO_RECORD"),
          {"type": "db_record_absent", "table": "record_overrides",
           "match": {"table_name": "civil_records"}}],
         LOGIN + [f"goto {P}/civil-registration/panel/death-correction/",
                  "stop NO_RECORD"])

    task(I("i6") + NR,
         [answer_ev("NO_RECORD"),
          {"type": "db_record_absent", "table": "appointments",
           "match": {"service_id": 2, "slot_date": "2026-06-23"}}],
         LOGIN + [f"goto {P}/passport/panel/appointment-booking/",
                  "stop NO_RECORD"])

    task(I("i7") + NR,
         [answer_ev("NO_RECORD")],
         LOGIN + [f"goto {P}/tax/panel/tin-verify/",
                  "fill 1 tin_no=111111111111", "stop NO_RECORD"])

    me = citizen_of[1]
    no_collide(me["mother_name"], me["perm_addr"])
    task(I("j1"),
         [answer_ev(me["mother_name"]), answer_ev(me["perm_addr"])],
         LOGIN + [f"goto {P}/national-id/panel/id-card-copy/",
                  f"stop {me['mother_name']}, {me['perm_addr']}"])

    assert n == 75, n
    assert len(T) == 75
    import re as _re
    for t in T:
        if _re.search(r"\bcard\b", t["intent"], _re.I):
            for e in t["eval"]:
                if e["type"] == "db_record_exists" \
                        and e.get("table") == "payments":
                    e["match"].setdefault("method", "card")
    return T


def write(lang, out_dir):
    T = build(lang)
    out = os.path.join(out_dir, "portal_tasks.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(T, f, indent=1, ensure_ascii=False)
    print(f"wrote {len(T)} tasks to {out}")
