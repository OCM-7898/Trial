from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def connect() -> sqlite3.Connection:
    db = ROOT / "data" / "seed.db"
    if not db.exists():
        raise SystemExit("data/seed.db is missing -- run `python seed.py` first")
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


@dataclass(frozen=True)
class Picked:
    value: dict
    rationale: str


def booking_where(conn, predicate_sql: str, rationale: str, params=()) -> Picked:
    row = conn.execute(f"""
        select b.id, b.pnr, b.surname_en, b.surname_am, b.booked_channel,
               b.total_paid, s.id segment_id, s.fare_class_id,
               f.id flight_id, f.flight_no, f.date, f.dep_time,
               ao.iata origin, ad.iata destination,
               ao.city_en origin_city_en, ao.city_am origin_city_am,
               ad.city_en dest_city_en, ad.city_am dest_city_am,
               fc.code fare_code, fc.cabin
        from bookings b
        join segments s on s.booking_id = b.id and s.sequence = 1
        join flights f on f.id = s.flight_id
        join routes r on r.id = f.route_id
        join airports ao on ao.id = r.origin_id
        join airports ad on ad.id = r.destination_id
        join fare_classes fc on fc.id = s.fare_class_id
        where {predicate_sql}
        order by b.id limit 1
    """, params).fetchone()
    if row is None:
        raise SystemExit(f"no seeded booking satisfies: {rationale}\n  ({predicate_sql})")
    return Picked(dict(row), rationale)


def flight_with_distinct_status(conn, status: str) -> Picked:
    row = conn.execute("""
        select f.flight_no, f.date, f.status, f.gate, f.terminal_dep, f.terminal_arr,
               f.dep_time, f.arr_time, f.delay_minutes,
               ao.iata origin, ad.iata destination,
               ao.city_en origin_city_en, ao.city_am origin_city_am,
               ad.city_en dest_city_en, ad.city_am dest_city_am,
               a.name_en aircraft_en, a.name_am aircraft_am
        from flights f
        join routes r on r.id = f.route_id
        join airports ao on ao.id = r.origin_id
        join airports ad on ad.id = r.destination_id
        join aircraft_types a on a.id = f.aircraft_id
        where f.status = ? and f.date >= date('2026-03-16')
        order by f.date, f.id limit 1
    """, (status,)).fetchone()
    if row is None:
        raise SystemExit(
            f"no flight on or after the frozen date has status {status!r}. "
            "Future flights are all 'scheduled' by design -- an airline cannot "
            "know tomorrow's delay -- so a status task must name a flight on "
            "the frozen today, where the status has settled.")
    return Picked(dict(row), f"a flight whose status is {status!r}, so the answer "
                             f"cannot be assumed to be 'scheduled'")


def route_with_partial_week(conn) -> Picked:
    row = conn.execute("""
        select ao.iata origin, ad.iata destination, r.operating_days,
               ao.city_en origin_city_en, ao.city_am origin_city_am,
               ad.city_en dest_city_en, ad.city_am dest_city_am
        from routes r
        join airports ao on ao.id = r.origin_id
        join airports ad on ad.id = r.destination_id
        where length(replace(r.operating_days, '.', '')) between 2 and 4
          and ao.iata = 'ADD'
        order by r.id limit 1
    """).fetchone()
    if row is None:
        raise SystemExit("no partial-week route; task 4 would be degenerate")
    return Picked(dict(row), "a route flying only some weekdays, so 'which days' "
                             "cannot be answered with 'every day'")


def award_with_seats(conn) -> Picked:
    row = conn.execute("""
        select ao.iata origin, ad.iata destination, f.date, f.flight_no,
               ai.cabin, ai.miles_required, ai.taxes_usd, ai.seats
        from award_inventory ai
        join flights f on f.id = ai.flight_id
        join routes r on r.id = f.route_id
        join airports ao on ao.id = r.origin_id
        join airports ad on ad.id = r.destination_id
        where ai.seats > 0 and ai.cabin = 'economy' and ao.iata = 'ADD'
        order by f.date, ai.id limit 1
    """).fetchone()
    if row is None:
        raise SystemExit("no bookable award inventory; task 20 is unanswerable")
    return Picked(dict(row), "a date with award seats actually remaining")


def lounge_needing_discrimination(conn) -> Picked:
    rows = conn.execute("""
        select id, name_en, name_am, airport_iata, terminal, hours_en, hours_am,
               location_en, location_am, access_free_for, walk_in_price_usd
        from lounges where airport_iata = 'ADD' and terminal = '2' order by id
    """).fetchall()
    if len(rows) < 2 or len({r["access_free_for"] for r in rows}) < 2:
        raise SystemExit("Addis Terminal 2 must offer lounges with differing rules")
    gold = [r for r in rows if "gold" in (r["access_free_for"] or "")]
    if not gold:
        raise SystemExit("no Terminal 2 lounge admits Gold; task 17 has no answer")
    return Picked(dict(gold[0]),
                  f"one of {len(rows)} lounges at the same terminal, only some of "
                  f"which admit a Gold member")


def seat_prices(conn, flight_id: int) -> dict:
    rows = conn.execute("""
        select min(price_usd) low, max(price_usd) high
        from seat_maps s join flights f on f.aircraft_id = s.aircraft_id
        where f.id = ? and s.cabin = 'economy' and s.extra_legroom = 1
    """, (flight_id,)).fetchone()
    return {"legroom_low": rows["low"], "legroom_high": rows["high"]}


def baggage_rule(conn, region: str, cabin: str, pax_type: str) -> dict:
    row = conn.execute("""
        select checked_pieces, checked_kg, cabin_kg, cabin_dims_cm,
               extra_kg_price_usd, extra_piece_price_usd
        from baggage_rules where region = ? and cabin = ? and pax_type = ?
    """, (region, cabin, pax_type)).fetchone()
    if row is None:
        raise SystemExit(f"no baggage rule for {region}/{cabin}/{pax_type}")
    return dict(row)


def cheapest_fares(conn, origin: str, destination: str, day: str) -> list[dict]:
    rows = conn.execute("""
        select f.flight_no, fc.code, fa.price_usd, fa.taxes_usd, fa.seats_available
        from fares fa
        join flights f on f.id = fa.flight_id
        join fare_classes fc on fc.id = fa.fare_class_id
        join routes r on r.id = f.route_id
        join airports ao on ao.id = r.origin_id
        join airports ad on ad.id = r.destination_id
        where ao.iata = ? and ad.iata = ? and f.date = ? and fa.seats_available > 0
        order by fa.price_usd
    """, (origin, destination, day)).fetchall()
    return [dict(r) for r in rows]
