import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "portal_clone", "data")


def load_en(name):
    with open(os.path.join(DATA, "en", name + ".json"), encoding="utf-8") as f:
        return json.load(f)


class Vocab:
    def __init__(self, lang):
        with open(os.path.join(HERE, "hand_portal", f"{lang}.json"),
                  encoding="utf-8") as f:
            self.t = json.load(f)
        self.districts = sorted(self.t["districts"], key=len, reverse=True)
        self.office_types = sorted(self.t["office_types"], key=len,
                                   reverse=True)

    def name(self, full):
        parts = full.split()
        out = [self.t["first_names"].get(p) or self.t["surnames"].get(p)
               or self.t["misc"].get(p) for p in parts]
        assert all(out), ("name part missing", full)
        return " ".join(out)

    def district(self, d):
        return self.t["districts"][d]

    def upazila(self, name):
        for d in self.districts:
            if name.startswith(d + " "):
                suf = name[len(d) + 1:]
                return f"{self.district(d)} {self.t['upazila_suffixes'][suf]}"
        raise KeyError(("upazila", name))

    def place(self, s):
        parts = [p.strip() for p in s.split(",")]
        W = self.t["address_words"]
        if parts[0].startswith("House "):
            house, road, upz, dist = parts
            return (f"{W['House']} {house.split()[1]}, "
                    f"{W['Road']} {road.split()[1]}, "
                    f"{self.upazila(upz)}, {self.district(dist)}")
        if parts[0].startswith("Village "):
            vil, upz, dist = parts
            return (f"{W['Village']} {self.t['villages'][vil.split()[1]]}, "
                    f"{self.upazila(upz)}, {self.district(dist)}")
        raise KeyError(("place", s))

    def office(self, name):
        for d in self.districts:
            if name.startswith(d + " "):
                typ = name[len(d) + 1:]
                return f"{self.district(d)} {self.t['office_types'][typ]}"
        raise KeyError(("office", name))

    def office_address(self, s):
        m = re.fullmatch(r"(\d+) Administrative Block, (.+)", s)
        assert m, s
        return (f"{m.group(1)} {self.t['address_words']['Administrative Block']}, "
                f"{self.district(m.group(2))}")

    def notice_title(self, title):
        for tmpl, out in self.t["notice_title_templates"].items():
            pre, suf = tmpl.split("{svc}")
            if title.startswith(pre) and title.endswith(suf):
                svc = title[len(pre):len(title) - len(suf)]
                return out.replace("{svc}", self.t["notice_service_phrases"][svc])
        raise KeyError(("notice title", title))

    def notice_body(self, body):
        for tmpl, out in self.t["notice_body_template"].items():
            pre, suf = tmpl.split("{svc}")
            if body.startswith(pre) and body.endswith(suf):
                svc = body[len(pre):len(body) - len(suf)]
                return out.replace("{svc}", self.t["notice_service_phrases"][svc])
        raise KeyError(("notice body", body[:40]))


def compose(lang):
    v = Vocab(lang)
    T = v.t
    out = {}

    def table(name, fn):
        rows = []
        for r in load_en(name):
            o = fn(r)
            if o:
                rows.append({"id": r["id"], **o})
        out[name] = rows

    table("accounts", lambda r: {"display_name": v.name(r["display_name"])})
    table("citizens", lambda r: {
        "name": v.name(r["name"]), "father_name": v.name(r["father_name"]),
        "mother_name": v.name(r["mother_name"]),
        "present_addr": v.place(r["present_addr"]),
        "perm_addr": v.place(r["perm_addr"])})
    table("civil_records", lambda r: {
        "person_name": v.name(r["person_name"]),
        "father_name": v.name(r["father_name"]),
        "mother_name": v.name(r["mother_name"]),
        "place": v.place(r["place"])})
    table("exam_boards", lambda r: {"name": T["boards"][r["name"]]})
    table("exam_results", lambda r: {
        "candidate_name": v.name(r["candidate_name"]),
        "institution": T["institutions"][r["institution"]],
        "group_name": T["groups"][r["group_name"]],
        "result_status": T["result_status"][r["result_status"]]})
    table("fee_schedules", lambda r: {
        "category": T["fee_categories"][r["category"]],
        "variant": T["fee_variants"][r["variant"]],
        "validity": T["fee_validity"][str(r["validity"])],
        "delivery": T["delivery"][r["delivery"]]})
    table("geo_divisions", lambda r: {"name": T["divisions"][r["name"]]})
    table("geo_districts", lambda r: {"name": v.district(r["name"])})
    table("geo_upazilas", lambda r: {"name": v.upazila(r["name"])})
    table("land_khatians", lambda r: {
        "khatian_type": T["khatian_types"][r["khatian_type"]],
        "owner_name": v.name(r["owner_name"]),
        "father_name": v.name(r["father_name"]),
        "land_type": T["land_types"][r["land_type"]]})
    table("land_mouzas", lambda r: {"name": T["mouzas"][r["name"]]})
    table("licences", lambda r: {
        "licence_class": T["licence_classes"][r["licence_class"]],
        "status": T["statuses"][r["status"]]})
    table("meters", lambda r: {"tariff": T["tariffs"][r["tariff"]],
                               "address": v.place(r["address"])})
    table("notices", lambda r: {
        "title": v.notice_title(r["title"]), "body": v.notice_body(r["body"]),
        "category": T["notice_categories"][r["category"]]})
    table("offices", lambda r: {
        "name": v.office(r["name"]),
        "address": v.office_address(r["address"]),
        "hours": T["office_hours"][r["hours"]]})
    table("passports", lambda r: {"delivery": T["delivery"][r["delivery"]],
                                  "status": T["statuses"][r["status"]]})
    table("tins", lambda r: {
        "registered_name": v.name(r["registered_name"]),
        "circle": f"{T['tin_words']['Circle']} {r['circle'].split()[1]}",
        "zone": f"{T['tin_words']['Zone']} {r['zone'].split()[1]}"})
    table("vaccine_records", lambda r: {
        "vaccine_name": T["vaccines"][r["vaccine_name"]],
        "centre_name": v.district(r["centre_name"].replace(" Vaccination Centre", ""))
                       + " " + T["vaccination_centre"]["Vaccination Centre"]})
    table("applications", lambda r: {
        "status": T["statuses"][r["status"]],
        "detail": T["application_detail"].replace(
            "{kind}", T["application_kinds"][r["kind"]])})
    outdir = os.path.join(DATA, lang)
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for name, rows in out.items():
        with open(os.path.join(outdir, name + ".json"), "w",
                  encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        n += len(rows)
        for r in rows:
            for val in r.values():
                assert not re.search(r"[০-৯०-९۰-۹]", str(val)), (name, val)
    print(f"{lang}: wrote {len(out)} overlays, {n} rows to {outdir}")


if __name__ == "__main__":
    compose(sys.argv[1])
