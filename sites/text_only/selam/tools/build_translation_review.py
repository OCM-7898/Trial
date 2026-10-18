from __future__ import annotations

import csv
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from back_translations import BACK

OUT = ROOT / "spec" / "translation_review.csv"
FIELDS = ["key", "context", "kind", "english", "amharic", "back_translation",
          "reviewed", "note"]

CONTEXTS = [
    ("site.", "00 chrome"), ("brand.", "00 chrome"), ("nav.", "00 chrome"),
    ("footer.", "00 chrome"), ("common.", "00 chrome"), ("error.", "00 errors"),
    ("home.", "01 home"), ("search.", "02 search"), ("results.", "03 results"),
    ("manage.", "04 manage booking"), ("pax.", "04 manage booking"),
    ("status.", "05 flight status"), ("schedules.", "06 timetable"),
    ("checkin.", "07 check-in"), ("boarding.", "08 boarding pass"),
    ("seats.", "09 seat selection"), ("change.", "10 flight change"),
    ("refund.", "11 refund"), ("upgrade.", "12 upgrade"),
    ("baggage.", "13 baggage"), ("region.", "13 baggage"),
    ("lounge.", "14 lounges"), ("review.", "15 payment boundary"),
    ("join.", "16 loyalty enrolment"), ("miles.", "17 loyalty account"),
    ("claim.", "18 missing miles"), ("award.", "19 award search"),
    ("content.", "20 help centre"), ("category.", "20 help centre"),
    ("contact.", "22 contact directory"), ("wifi.", "23 on-board wi-fi"),
    ("dining.", "24 in-flight dining"),
    ("book.", "25 booking completion"), ("stopover.", "26 stopover"),
    ("partner.", "27 partner sites"), ("redirect.", "00 chrome"),
    ("partner_air.", "27 partner sites"),
    ("form.", "28 service request forms"), ("network.", "29 route network"),
    ("redeem.", "17 loyalty account"),
    ("weekday.", "21 formats"),
]


ENCODING = "utf-8-sig"


def context_for(key: str) -> str:
    for prefix, label in CONTEXTS:
        if key.startswith(prefix):
            return label
    return "99 unfiled"


def load_existing() -> dict[str, dict]:
    if not OUT.exists():
        return {}
    with OUT.open(encoding=ENCODING, newline="") as handle:
        return {row["key"]: row for row in csv.DictReader(handle)}


def ui_rows() -> list[dict]:
    en = json.loads((ROOT / "app" / "i18n" / "en.json").read_text("utf-8"))
    am = json.loads((ROOT / "app" / "i18n" / "am.json").read_text("utf-8"))
    rows = []
    for key in sorted(en):
        rows.append({
            "key": key, "context": context_for(key), "kind": "ui",
            "english": en[key], "amharic": am.get(key, ""),
            "back_translation": BACK.get(key, ""),
        })
    return rows


SEEDED = [
    ("airports", "iata", [("city", "transliteration"), ("name", "transliteration"),
                          ("country", "transliteration")]),
    ("aircraft_types", "code", [("name", "transliteration")]),
    ("fare_classes", "code", [("name", "brand")]),
    ("lounges", "id", [("name", "brand"), ("hours", "prose"),
                       ("location", "prose"), ("amenities", "prose")]),
    ("contact_offices", "country_code", [("country", "transliteration"),
                                         ("city", "transliteration"),
                                         ("hours", "prose"), ("address", "formulaic")]),
    ("content_pages", "slug", [("title", "prose"), ("summary", "prose"),
                               ("body_html", "long prose")]),
    ("bookings", "pnr", [("surname", "name")]),
    ("passengers", "id", [("first_name", "name"), ("last_name", "name"),
                          ("allergy_note", "prose")]),
    ("loyalty_members", "member_no", [("first_name", "name"), ("last_name", "name")]),
    ("miles_transactions", "id", [("description", "prose")]),
    ("segments", "id", [("operated_by", "brand")]),
    ("special_baggage_items", "id", [("item", "prose"), ("notes", "prose")]),
    ("entertainment_items", "id", [("title", "prose"), ("genre", "prose"),
                                   ("language", "transliteration")]),
    ("promotions", "code", [("title", "prose"), ("body", "prose"),
                            ("terms", "prose")]),
    ("travel_requirements", "country_code", [("visa_required", "prose"),
                                             ("health", "prose")]),
    ("stopover_packages", "id", [("name", "prose"), ("description", "prose")]),
    ("special_meal_codes", "code", [("name", "prose"), ("description", "prose")]),
    ("meal_menus", "id", [("courses", "prose"), ("beverages", "prose")]),
    ("wifi_packages", "id", [("name", "brand")]),
    ("hotel_rooms", "id", [("name", "prose"), ("description", "prose")]),
    ("car_offers", "id", [("name", "prose")]),
    ("insurance_products", "id", [("name", "brand"), ("coverage", "prose")]),
    ("rail_connections", "id", [("operator", "brand"), ("destination", "transliteration"),
                                ("ticket_type", "prose"), ("booking_note", "prose")]),
    ("visa_types", "id", [("name", "prose"), ("eligibility", "prose"),
                          ("documents", "prose")]),
]


def assert_seeded_is_complete() -> None:
    from app.models import Base

    annotated = {(table, field) for table, _, fields in SEEDED for field, _ in fields}
    schema = set()
    for table_name, table in Base.metadata.tables.items():
        columns = {c.name for c in table.columns}
        for field in ({c[:-3] for c in columns if c.endswith("_en")} &
                      {c[:-3] for c in columns if c.endswith("_am")}):
            schema.add((table_name, field))

    unannotated = sorted(schema - annotated)
    assert not unannotated, (
        "these paired columns are seeded in Amharic but not listed in SEEDED, so "
        f"no reviewer would ever see them: {unannotated}")
    stale = sorted(annotated - schema)
    assert not stale, f"SEEDED names columns that no longer exist: {stale}"


def _mechanical(kind: str, english: str) -> str:
    if kind in ("transliteration", "name", "brand"):
        return f"{english} [transliteration -- check the spelling, not the meaning]"
    if kind == "formulaic":
        return (f"{english} [same template in both: "
                "'<city> City Office, <n> Airport Road, <city>, <country>']")
    return ""


def split_html(markup: str) -> list[str]:
    import re as _re

    parts = _re.findall(r"<(?:h2|p|li)>(.*?)</(?:h2|p|li)>", markup or "", _re.S)
    return [_re.sub(r"\s+", " ", part).strip() for part in parts if part.strip()]


def seeded_rows() -> list[dict]:
    conn = sqlite3.connect(ROOT / "data" / "seed.db")
    conn.row_factory = sqlite3.Row
    rows, seen = [], set()

    for table, key_column, fields in SEEDED:
        columns = ", ".join(f"{f}_en, {f}_am" for f, _ in fields)
        for record in conn.execute(f"select {key_column}, {columns} from {table}"):
            for field, kind in fields:
                english, amharic = record[f"{field}_en"], record[f"{field}_am"]
                if not english and not amharic:
                    continue

                if kind == "long prose":
                    english_parts, amharic_parts = split_html(english), split_html(amharic)
                    if len(english_parts) != len(amharic_parts):
                        raise SystemExit(
                            f"{table}.{record[key_column]}.{field}: the English body has "
                            f"{len(english_parts)} blocks and the Amharic has "
                            f"{len(amharic_parts)}. They must correspond one to one, or "
                            f"the page is not a translation of itself.")
                    for index, (part_en, part_am) in enumerate(zip(english_parts, amharic_parts), 1):
                        signature = ("prose", part_en, part_am)
                        if signature in seen:
                            continue
                        seen.add(signature)
                        key = f"{table}.{record[key_column]}.{field}.{index:02d}"
                        rows.append({
                            "key": key,
                            "context": f"50 seeded: {table}", "kind": "prose",
                            "english": part_en, "amharic": part_am,
                            "back_translation": BACK.get(key, ""),
                        })
                    continue
                signature = (kind, english, amharic)
                if signature in seen:
                    continue
                seen.add(signature)
                rows.append({
                    "key": f"{table}.{record[key_column]}.{field}",
                    "context": f"50 seeded: {table}", "kind": kind,
                    "english": english or "", "amharic": amharic or "",
                    "back_translation": (
                        BACK.get(f"{table}.{record[key_column]}.{field}")
                        or _mechanical(kind, english)),
                })
    conn.close()
    return rows


def main() -> None:
    assert_seeded_is_complete()
    existing = load_existing()
    rows = ui_rows() + seeded_rows()

    carried = superseded = new = 0
    for row in rows:
        previous = existing.get(row["key"])
        if previous is None:
            row["reviewed"] = "n"
            row["note"] = ""
            new += 1
            continue
        if previous.get("amharic", "") != row["amharic"]:
            row["reviewed"] = "n"
            row["note"] = f"changed since review; was: {previous.get('amharic', '')[:60]}"
            superseded += 1
            continue
        row["reviewed"] = previous.get("reviewed", "n")
        row["back_translation"] = (previous.get("back_translation")
                                   or row["back_translation"])
        row["note"] = previous.get("note", "")
        carried += 1

    rows.sort(key=lambda r: (r["context"], r["key"]))
    with OUT.open("w", encoding=ENCODING, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    with_back = sum(1 for r in rows if r["back_translation"])
    reviewed = sum(1 for r in rows if r["reviewed"] == "y")
    print(f"wrote {OUT.relative_to(ROOT)} -- {len(rows)} strings")
    print(f"  new {new}, carried {carried}, superseded {superseded}")
    print(f"  back-translated   {with_back}/{len(rows)} ({100*with_back/len(rows):.0f}%)")
    print(f"  reviewed          {reviewed}/{len(rows)}")
    print()
    by_context: dict[str, int] = {}
    for row in rows:
        by_context[row["context"]] = by_context.get(row["context"], 0) + 1
    for context, count in sorted(by_context.items()):
        done = sum(1 for r in rows if r["context"] == context and r["back_translation"])
        print(f"  {context:28s} {count:>5} strings, {done:>5} back-translated")


if __name__ == "__main__":
    main()
