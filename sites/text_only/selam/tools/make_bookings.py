from __future__ import annotations

import pathlib
import random
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timedelta

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.clock import FROZEN_NOW, FROZEN_TODAY

SEED = 771026
PNR_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

CHECKIN_OPENS_H = 48
CHECKIN_CLOSES_H = 2

FLAG_BLOCKS = [
    "INFANT_ON_LAP", "SPECIAL_ASSISTANCE_REQUIRED", "UNACCOMPANIED_MINOR",
    "DOCUMENT_CHECK_REQUIRED", "CODESHARE_OPERATED_BY_PARTNER", "GROUP_BOOKING",
]

FARE_BRANCHES = {
    "EP": ("none", "none"), "EL": ("none", "none"),
    "EB": ("none", "fee"),  "EG": ("partial", "fee"),
    "ES": ("partial", "fee"), "EF": ("full", "free"),
    "HS": ("partial", "fee"), "HC": ("full", "free"), "HF": ("full", "free"),
}

CHANNELS = ["website", "website", "website", "agent", "call_centre", "corporate"]


def connect() -> sqlite3.Connection:
    db = ROOT / "data" / "seed.db"
    if not db.exists():
        sys.exit("run `python seed.py` first -- this tool resolves real flight ids")
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


def flights_departing_between(conn, lo_h: float, hi_h: float, limit: int = 400):
    lo = FROZEN_NOW.replace(tzinfo=None) + timedelta(hours=lo_h)
    hi = FROZEN_NOW.replace(tzinfo=None) + timedelta(hours=hi_h)
    rows = conn.execute("""
        select f.id, f.flight_no, f.date, f.dep_time, f.route_id, f.aircraft_id,
               ao.iata origin, ad.iata destination, a.rows_business
        from flights f
        join routes r on r.id = f.route_id
        join airports ao on ao.id = r.origin_id
        join airports ad on ad.id = r.destination_id
        join aircraft_types a on a.id = f.aircraft_id
        where f.date between ? and ? and f.status != 'cancelled'
        order by f.id
    """, ((lo - timedelta(days=1)).date().isoformat(), (hi + timedelta(days=1)).date().isoformat())).fetchall()

    out = []
    for row in rows:
        dep = datetime.fromisoformat(f"{row['date']}T{row['dep_time']}")
        if lo <= dep <= hi:
            out.append((dep, row))
    return out[:limit]


def return_flight(conn, origin: str, destination: str, after: datetime):
    row = conn.execute("""
        select f.id, f.flight_no, f.date, f.dep_time
        from flights f
        join routes r on r.id = f.route_id
        join airports ao on ao.id = r.origin_id
        join airports ad on ad.id = r.destination_id
        where ao.iata = ? and ad.iata = ? and f.date >= ? and f.status != 'cancelled'
        order by f.date, f.dep_time
    """, (origin, destination, (after + timedelta(days=5)).date().isoformat())).fetchone()
    return row


def fares_for(conn, flight_id: int) -> dict[str, sqlite3.Row]:
    rows = conn.execute("""
        select fc.code, fa.price_usd, fa.taxes_usd, fc.id fare_class_id, fc.cabin
        from fares fa join fare_classes fc on fc.id = fa.fare_class_id
        where fa.flight_id = ? order by fc.id
    """, (flight_id,)).fetchall()
    return {r["code"]: r for r in rows}


def main() -> None:
    rng = random.Random(SEED)
    conn = connect()
    names = yaml.safe_load((ROOT / "spec/seed_data/names.yaml").read_text("utf-8"))

    pools = {
        "eligible": flights_departing_between(conn, CHECKIN_CLOSES_H + 1, CHECKIN_OPENS_H - 1),
        "too_early": flights_departing_between(conn, CHECKIN_OPENS_H + 24, CHECKIN_OPENS_H + 24 * 30),
        "closed_soon": flights_departing_between(conn, 0.25, CHECKIN_CLOSES_H - 0.25),
        "past": flights_departing_between(conn, -24 * 60, -24),
    }
    for key, pool in pools.items():
        assert pool, f"no flights in pool {key!r} -- widen the window or check the schedule"

    used_pnrs: set[str] = set()

    def new_pnr() -> str:
        while True:
            pnr = "".join(rng.choice(PNR_ALPHABET) for _ in range(6))
            if pnr not in used_pnrs:
                used_pnrs.add(pnr)
                return pnr

    def person(kind: str, surname: tuple[str, str]) -> dict:
        pool = names["given_female"] if rng.random() < 0.5 else names["given_male"]
        given = rng.choice(pool)
        if kind == "infant":
            dob = FROZEN_TODAY - timedelta(days=rng.randint(90, 600))
        elif kind == "child":
            dob = FROZEN_TODAY - timedelta(days=rng.randint(3 * 365, 11 * 365))
        else:
            dob = FROZEN_TODAY - timedelta(days=rng.randint(20 * 365, 62 * 365))
        return {
            "first_name_en": given[0], "first_name_am": given[1],
            "last_name_en": surname[0], "last_name_am": surname[1],
            "pax_type": kind, "dob": dob.isoformat(),
            "passport_number": f"EP{rng.randint(1000000, 9999999)}",
        }

    plan: list[dict] = []

    def add(**kw):
        plan.append(kw)

    for code in FARE_BRANCHES:
        add(fare=code, situation="eligible", flag=None, upgrade="eligible",
            seats=True, channel="website", trip="round_trip")

    for flag in FLAG_BLOCKS:
        add(fare="EB", situation="eligible", flag=flag, upgrade="fare_excluded",
            seats=False, channel="website", trip="one_way")

    for situation in ("too_early", "closed_soon", "past", "eligible"):
        add(fare="ES", situation=situation, flag=None, upgrade="eligible",
            seats=False, channel="website", trip="one_way")

    for channel in ("website", "agent", "call_centre", "corporate", "agent", "website"):
        add(fare="EF", situation="eligible", flag=None, upgrade="eligible",
            seats=True, channel=channel, trip="round_trip")

    for fare, upgrade in (("ES", "eligible"), ("EB", "eligible"), ("EF", "cabin_full"),
                          ("EP", "fare_excluded"), ("EL", "fare_excluded"), ("EG", "cabin_full")):
        add(fare=fare, situation="eligible", flag=None, upgrade=upgrade,
            seats=False, channel="website", trip="one_way")

    for fare in ("EF", "ES", "EP", "HC", "EG", "EL"):
        add(fare=fare, situation="too_early", flag=None, upgrade="eligible",
            seats=rng.random() < 0.5, channel=rng.choice(CHANNELS), trip="round_trip")

    while len(plan) < 60:
        add(fare=rng.choice(list(FARE_BRANCHES)),
            situation=rng.choice(["eligible", "too_early", "too_early", "past"]),
            flag=None,
            upgrade=rng.choice(["eligible", "eligible", "cabin_full", "fare_excluded"]),
            seats=rng.random() < 0.4,
            channel=rng.choice(CHANNELS),
            trip=rng.choice(["one_way", "round_trip", "round_trip"]))

    bookings, passenger_id, segment_id = [], 1, 1

    for index, spec in enumerate(plan, start=1):
        pool = pools[spec["situation"]]
        wants_business = FARE_BRANCHES[spec["fare"]][0] and spec["fare"].startswith("H")
        candidates = [p for p in pool if p[1]["rows_business"] > 0] if wants_business else pool
        dep, flight = candidates[(index * 7) % len(candidates)]

        fares = fares_for(conn, flight["id"])
        if spec["fare"] not in fares:
            fares_available = [c for c in fares if c.startswith("E")]
            spec["fare"] = fares_available[0]
        fare = fares[spec["fare"]]

        surname = rng.choice(names["family"])
        pax = [person("adult", surname)]
        if spec["flag"] == "INFANT_ON_LAP":
            pax.append(person("infant", surname))
        elif spec["flag"] == "UNACCOMPANIED_MINOR":
            pax = [person("child", surname)]
        elif spec["flag"] == "GROUP_BOOKING":
            pax += [person("adult", rng.choice(names["family"])) for _ in range(9)]
        else:
            for _ in range(rng.choice([0, 0, 1, 1, 1, 2])):
                pax.append(person(rng.choice(["adult", "adult", "adult", "child"]), surname))

        if spec["flag"] == "SPECIAL_ASSISTANCE_REQUIRED":
            pax[0]["assistance_code"] = "WCHC"
        if spec["flag"] == "DOCUMENT_CHECK_REQUIRED":
            for p in pax:
                p["passport_number"] = None

        segments = [{
            "id": segment_id, "flight_id": flight["id"],
            "fare_class_id": fare["fare_class_id"], "sequence": 1,
            "direction": "outbound",
            "operated_by_en": "Rift Regional" if spec["flag"] == "CODESHARE_OPERATED_BY_PARTNER" else None,
            "operated_by_am": "ሪፍት ሪጅናል" if spec["flag"] == "CODESHARE_OPERATED_BY_PARTNER" else None,
        }]
        segment_id += 1
        total = fare["price_usd"] + fare["taxes_usd"]

        if spec["trip"] == "round_trip":
            back = return_flight(conn, flight["destination"], flight["origin"], dep)
            if back:
                back_fares = fares_for(conn, back["id"])
                if spec["fare"] in back_fares:
                    bf = back_fares[spec["fare"]]
                    segments.append({
                        "id": segment_id, "flight_id": back["id"],
                        "fare_class_id": bf["fare_class_id"], "sequence": 2,
                        "direction": "inbound", "operated_by_en": None, "operated_by_am": None,
                    })
                    segment_id += 1
                    total += bf["price_usd"] + bf["taxes_usd"]

        for p in pax:
            p["id"] = passenger_id
            passenger_id += 1

        bookings.append({
            "id": index,
            "pnr": new_pnr(),
            "surname_en": surname[0], "surname_am": surname[1],
            "email": f"{surname[0].lower()}{index}@example.com",
            "phone": f"+251 11 {500 + index} {1000 + index}",
            "status": "confirmed",
            "created_on": (FROZEN_TODAY - timedelta(days=rng.randint(5, 120))).isoformat(),
            "total_paid": round(total * len(pax), 2),
            "booked_channel": spec["channel"],
            "is_group": spec["flag"] == "GROUP_BOOKING",
            "intent": f"{spec['fare']} / {spec['situation']} / flag={spec['flag']} / "
                      f"upgrade={spec['upgrade']} / seats={spec['seats']} / {spec['channel']}",
            "checkin_block": spec["flag"],
            "upgrade_state": spec["upgrade"],
            "seats_assigned": spec["seats"],
            "passengers": pax,
            "segments": segments,
        })

    _report_and_assert(bookings)

    out = ROOT / "spec/seed_data/bookings.yaml"
    out.write_text(
        "# Generated by tools/make_bookings.py -- edit there, not here.\n"
        "# 60 PNRs covering every branch SPEC.md 9.2 requires; the generator\n"
        "# asserts the coverage and prints the matrix.\n"
        + yaml.safe_dump({"bookings": bookings}, sort_keys=False, allow_unicode=True),
        "utf-8",
    )
    print(f"\nwrote {out.relative_to(ROOT)}")


def _report_and_assert(bookings: list[dict]) -> None:
    refund = Counter(); change = Counter(); checkin = Counter()
    upgrade = Counter(); seats = Counter(); channel = Counter(); trip = Counter()

    for b in bookings:
        fare_code = b["intent"].split(" / ")[0]
        r, c = FARE_BRANCHES[fare_code]
        refund[r] += 1
        change[c] += 1
        checkin[b["checkin_block"] or b["intent"].split(" / ")[1]] += 1
        upgrade[b["upgrade_state"]] += 1
        seats["assigned" if b["seats_assigned"] else "none"] += 1
        channel[b["booked_channel"]] += 1
        trip["round_trip" if len(b["segments"]) > 1 else "one_way"] += 1

    def show(title, counter):
        print(f"\n  {title}")
        for key, n in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"    {key:34s} {n:3d}")

    print(f"{len(bookings)} bookings, {sum(len(b['passengers']) for b in bookings)} passengers, "
          f"{sum(len(b['segments']) for b in bookings)} segments")
    show("refundability (SPEC.md 9.2)", refund)
    show("changeability", change)
    show("check-in outcome (9.3)", checkin)
    show("upgrade state", upgrade)
    show("seats", seats)
    show("booking channel (task 7)", channel)
    show("trip type", trip)

    required = {
        "refundability": (refund, {"full", "partial", "none"}),
        "changeability": (change, {"free", "fee", "none"}),
        "upgrade": (upgrade, {"eligible", "cabin_full", "fare_excluded"}),
        "seats": (seats, {"assigned", "none"}),
        "channel": (channel, {"website", "agent", "call_centre", "corporate"}),
        "trip": (trip, {"one_way", "round_trip"}),
    }
    for label, (counter, needed) in required.items():
        missing = needed - set(counter)
        assert not missing, f"{label}: no booking covers {sorted(missing)}"

    missing_blocks = set(FLAG_BLOCKS) - set(checkin)
    assert not missing_blocks, f"check-in: no booking triggers {sorted(missing_blocks)}"
    for situation in ("eligible", "too_early", "closed_soon", "past"):
        assert situation in checkin, f"check-in: no booking in situation {situation!r}"


if __name__ == "__main__":
    main()
