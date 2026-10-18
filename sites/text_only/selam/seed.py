from __future__ import annotations

import hashlib
import random
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

import yaml
from sqlalchemy import create_engine, insert
from sqlalchemy.schema import CreateIndex, CreateTable

from app.clock import WINDOW_END, WINDOW_START
from app.lang import LANGS
from app.models import Base
from app.models.ancillary import BaggageRule
from app.models.content import (
    ContactOffice, ContentPage, EntertainmentItem, Lounge, Promotion,
    SpecialBaggageItem, StopoverPackage, TravelRequirement,
)
from app.models.loyalty import AwardInventory, LoyaltyMember, MilesTransaction
from app.models.onboard import MealMenu, SpecialMealCode, WifiPackage
from app.models.partners import (
    CarOffer, HotelRoom, InsuranceProduct, RailConnection, VisaType,
)
from app.models.booking import Booking, Passenger, SeatAssignment, Segment
from app.models.network import (
    Aircraft, Airport, Fare, FareClass, Flight, Route, SeatMapSeat,
)

ROOT = Path(__file__).resolve().parent
SEED_DATA = ROOT / "spec" / "seed_data"
DB_PATH = ROOT / "data" / "seed.db"

SEED = 20260316

FLIGHT_ID_BASE = 100_000
FARE_ID_BASE = 1_000_000


def load(name: str):
    return yaml.safe_load((SEED_DATA / f"{name}.yaml").read_text("utf-8"))


def expand_seat_map(aircraft: dict, next_id: int) -> tuple[list[dict], int]:
    rows: list[dict] = []
    row_no = 1

    for cabin, count, layout in (
        ("business", aircraft["rows_business"], aircraft["business_layout"]),
        ("economy", aircraft["rows_economy"], aircraft["economy_layout"]),
    ):
        if not count or not layout:
            continue
        letters = [c for c in layout if c != "-"]
        aisle = set()
        for i, ch in enumerate(layout):
            if ch == "-":
                if i > 0:
                    aisle.add(layout[i - 1])
                if i + 1 < len(layout):
                    aisle.add(layout[i + 1])
        window = {letters[0], letters[-1]}

        first_row = row_no
        exit_row = int(count * 0.55) if count >= 6 else None
        for r in range(count):
            row_no = first_row + r
            is_exit = r == exit_row
            for col in letters:
                rows.append({
                    "id": next_id,
                    "aircraft_id": aircraft["id"],
                    "seat_no": f"{row_no}{col}",
                    "row": row_no,
                    "col": col,
                    "cabin": cabin,
                    "is_exit": is_exit,
                    "is_aisle": col in aisle,
                    "is_window": col in window,
                    "is_bassinet": r == 0 and cabin == "economy",
                    "extra_legroom": is_exit or r == 0,
                    "price_usd": _seat_price(cabin, is_exit or r == 0, col in aisle, col in window),
                })
                next_id += 1
        row_no += 1

    return rows, next_id


def _seat_price(cabin: str, extra_legroom: bool, aisle: bool, window: bool) -> float:
    if cabin == "business":
        return 0.0
    if extra_legroom:
        return 45.0
    if aisle or window:
        return 18.0
    return 10.0


def pick_aircraft(distance_km: int) -> int:
    if distance_km < 500:
        return 1
    if distance_km < 1200:
        return 2
    if distance_km < 2600:
        return 3
    if distance_km < 4200:
        return 4
    if distance_km < 7000:
        return 5
    return 6


def departure_time(route_id: int, rng: random.Random) -> time:
    slot = rng.choice([6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23])
    return time(hour=slot, minute=rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]))


def main() -> None:
    rng = random.Random(SEED)

    airports = load("airports")["airports"]
    aircraft = load("aircraft")["aircraft"]
    fare_classes = load("fare_classes")["fare_classes"]
    routes_raw = load("routes")["routes"]

    by_iata = {a["iata"]: a for a in airports}

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    engine = create_engine(f"sqlite:///{DB_PATH}")
    _create_schema(engine)

    seats: list[dict] = []
    next_seat_id = 1
    for ac in sorted(aircraft, key=lambda a: a["id"]):
        rows, next_seat_id = expand_seat_map(ac, next_seat_id)
        seats.extend(rows)

    routes = [{
        "id": r["id"],
        "origin_id": by_iata[r["origin"]]["id"],
        "destination_id": by_iata[r["destination"]]["id"],
        "distance_km": r["distance_km"],
        "block_time_min": r["block_time_min"],
        "operating_days": r["operating_days"],
        "seasonal_from": None,
        "seasonal_to": None,
    } for r in sorted(routes_raw, key=lambda r: r["id"])]

    flights: list[dict] = []
    fares: list[dict] = []
    flight_id = FLIGHT_ID_BASE
    fare_id = FARE_ID_BASE

    economy_classes = [f for f in fare_classes if f["cabin"] == "economy"]
    business_classes = [f for f in fare_classes if f["cabin"] == "business"]

    for r in sorted(routes_raw, key=lambda r: r["id"]):
        origin, dest = by_iata[r["origin"]], by_iata[r["destination"]]
        aircraft_id = pick_aircraft(r["distance_km"])
        ac = aircraft[aircraft_id - 1]
        dep = departure_time(r["id"], rng)
        block = r["block_time_min"]
        base_price = 55 + r["distance_km"] * 0.062

        day = WINDOW_START
        while day <= WINDOW_END:
            if r["operating_days"][day.weekday()] == ".":
                day += timedelta(days=1)
                continue

            arr_dt = datetime.combine(day, dep) + timedelta(minutes=block)
            status, delay = _status_for(day, dep, rng)

            flights.append({
                "id": flight_id,
                "flight_no": r["flight_no"],
                "route_id": r["id"],
                "date": day,
                "dep_time": dep,
                "arr_time": arr_dt.time(),
                "arr_day_offset": (arr_dt.date() - day).days,
                "aircraft_id": aircraft_id,
                "status": status,
                "gate": f"{rng.choice('ABCD')}{rng.randint(1, 24)}",
                "terminal_dep": str(rng.randint(1, max(1, origin["terminal_count"]))),
                "terminal_arr": str(rng.randint(1, max(1, dest["terminal_count"]))),
                "wifi_equipped": ac["has_wifi"],
                "has_lounge_access": ac["rows_business"] > 0,
                "delay_minutes": delay,
            })

            available = economy_classes + (business_classes if ac["rows_business"] else [])
            for fc in available:
                mult = FARE_MULTIPLIER[fc["code"]]
                price = round(base_price * mult / 2) * 2
                fares.append({
                    "id": fare_id,
                    "flight_id": flight_id,
                    "fare_class_id": fc["id"],
                    "price_usd": float(price),
                    "taxes_usd": float(round(price * 0.11 / 2) * 2),
                    "seats_available": rng.randint(0, 9) if fc["code"] in ("EP", "HF") else rng.randint(2, 30),
                })
                fare_id += 1

            flight_id += 1
            day += timedelta(days=1)

    with engine.begin() as conn:
        conn.execute(insert(Airport), airports)
        conn.execute(insert(Aircraft), aircraft)
        conn.execute(insert(SeatMapSeat), seats)
        conn.execute(insert(FareClass), [
            {k: v for k, v in fc.items()} | {"baggage_rule_id": None} for fc in fare_classes
        ])
        conn.execute(insert(Route), routes)
        conn.execute(insert(BaggageRule), load("baggage_rules")["baggage_rules"])
        content = load("content_pages")["content_pages"]
        if content:
            conn.execute(insert(ContentPage), content)
        conn.execute(insert(Lounge), load("lounges")["lounges"])
        conn.execute(insert(ContactOffice), load("contact_offices")["contact_offices"])
        loyalty = load("loyalty")
        conn.execute(insert(LoyaltyMember),
                     [_with_dates(row, ("joined_on",)) for row in loyalty["loyalty_members"]])
        conn.execute(insert(MilesTransaction),
                     [_with_dates(row, ("posted_on",)) for row in loyalty["miles_transactions"]])
        conn.execute(insert(AwardInventory), loyalty["award_inventory"])
        onboard = load("onboard")
        for chunk in _chunks(onboard["wifi_packages"], 5000):
            conn.execute(insert(WifiPackage), chunk)
        conn.execute(insert(SpecialMealCode), onboard["special_meal_codes"])
        conn.execute(insert(MealMenu), onboard["meal_menus"])
        conn.execute(insert(StopoverPackage), load("stopover")["stopover_packages"])
        partners = load("partners")
        conn.execute(insert(HotelRoom), partners["hotel_rooms"])
        conn.execute(insert(VisaType), partners["visa_types"])
        conn.execute(insert(RailConnection), partners["rail_connections"])
        conn.execute(insert(CarOffer), partners["car_offers"])
        conn.execute(insert(InsuranceProduct), partners["insurance_products"])
        extras = load("extras")
        conn.execute(insert(Promotion),
                     [_with_dates(row, ("valid_from", "valid_to"))
                      for row in extras["promotions"]])
        conn.execute(insert(SpecialBaggageItem),
                     load("special_baggage")["special_baggage_items"])
        conn.execute(insert(EntertainmentItem), extras["entertainment_items"])
        conn.execute(insert(TravelRequirement), extras["travel_requirements"])
        for chunk in _chunks(flights, 5000):
            conn.execute(insert(Flight), chunk)
        for chunk in _chunks(fares, 5000):
            conn.execute(insert(Fare), chunk)

    booking_counts = _seed_bookings(engine)

    digest = hashlib.sha256(DB_PATH.read_bytes()).hexdigest()
    print(f"wrote {DB_PATH.relative_to(ROOT)}")
    print(f"  airports      {len(airports):>7,}")
    print(f"  aircraft      {len(aircraft):>7,}")
    print(f"  seats         {len(seats):>7,}")
    print(f"  fare classes  {len(fare_classes):>7,}")
    print(f"  routes        {len(routes):>7,}")
    print(f"  baggage rules {len(load('baggage_rules')['baggage_rules']):>7,}")
    print(f"  content pages {len(load('content_pages')['content_pages']):>7,}")
    print(f"  lounges       {len(load('lounges')['lounges']):>7,}")
    print(f"  offices       {len(load('contact_offices')['contact_offices']):>7,}")
    _loyalty = load("loyalty")
    print(f"  members       {len(_loyalty['loyalty_members']):>7,}")
    print(f"  miles txns    {len(_loyalty['miles_transactions']):>7,}")
    print(f"  award seats   {len(_loyalty['award_inventory']):>7,}")
    _onboard = load("onboard")
    print(f"  wifi packages {len(_onboard['wifi_packages']):>7,}")
    print(f"  meal codes    {len(_onboard['special_meal_codes']):>7,}")
    print(f"  meal menus    {len(_onboard['meal_menus']):>7,}")
    print(f"  stopover pkgs {len(load('stopover')['stopover_packages']):>7,}")
    _partners = load("partners")
    print(f"  partner rows  {sum(len(v) for v in _partners.values()):>7,}")
    _extras = load("extras")
    print(f"  promotions    {len(_extras['promotions']):>7,}")
    print(f"  entertainment {len(_extras['entertainment_items']):>7,}")
    print(f"  special bags  {len(load('special_baggage')['special_baggage_items']):>7,}")
    print(f"  entry rules   {len(_extras['travel_requirements']):>7,}")
    print(f"  flights       {len(flights):>7,}")
    print(f"  fares         {len(fares):>7,}")
    for label, count in booking_counts.items():
        print(f"  {label:<13} {count:>7,}")
    print(f"  sha256        {digest}")


def _seed_bookings(engine) -> dict[str, int]:
    path = SEED_DATA / "bookings.yaml"
    if not path.exists():
        return {"bookings": 0, "passengers": 0, "segments": 0, "seat assigns": 0}

    data = yaml.safe_load(path.read_text("utf-8"))["bookings"]

    bookings, passengers, segments = [], [], []
    seat_rows: list[dict] = []
    cabin_full_flights: set[int] = set()

    for b in sorted(data, key=lambda x: x["id"]):
        bookings.append({
            "id": b["id"], "pnr": b["pnr"],
            **{f"surname_{_l}": b[f"surname_{_l}"] for _l in LANGS},
            "email": b["email"], "phone": b["phone"], "status": b["status"],
            "created_on": date.fromisoformat(b["created_on"]),
            "currency": "USD", "total_paid": b["total_paid"],
            "booked_channel": b["booked_channel"], "is_group": b["is_group"],
        })
        for p in sorted(b["passengers"], key=lambda x: x["id"]):
            passengers.append({
                "id": p["id"], "booking_id": b["id"],
                **{f"first_name_{_l}": p[f"first_name_{_l}"] for _l in LANGS},
                **{f"last_name_{_l}": p[f"last_name_{_l}"] for _l in LANGS},
                "pax_type": p["pax_type"],
                "dob": date.fromisoformat(p["dob"]) if p.get("dob") else None,
                "loyalty_number": p.get("loyalty_number"),
                "special_meal": p.get("special_meal"),
                "assistance_code": p.get("assistance_code"),
                **{f"allergy_note_{_l}": p.get(f"allergy_note_{_l}") for _l in LANGS},
                "passport_number": p.get("passport_number"),
            })
        for sg in sorted(b["segments"], key=lambda x: x["id"]):
            segments.append({
                "id": sg["id"], "booking_id": b["id"], "flight_id": sg["flight_id"],
                "fare_class_id": sg["fare_class_id"], "sequence": sg["sequence"],
                "direction": sg["direction"], "checked_in": False,
                "baggage_allowance_kg": 23, "extra_baggage_kg": 0,
                **{f"operated_by_{_l}": sg[f"operated_by_{_l}"] for _l in LANGS},
            })
        if b["upgrade_state"] == "cabin_full":
            cabin_full_flights.update(sg["flight_id"] for sg in b["segments"])

    seat_id = 1
    for b in sorted(data, key=lambda x: x["id"]):
        if not b["seats_assigned"]:
            continue
        for sg in sorted(b["segments"], key=lambda x: x["id"]):
            seats = _pick_seats(engine, sg["flight_id"], len(b["passengers"]))
            for passenger, seat_no in zip(sorted(b["passengers"], key=lambda x: x["id"]), seats):
                seat_rows.append({
                    "id": seat_id, "segment_id": sg["id"], "passenger_id": passenger["id"],
                    "seat_no": seat_no, "paid_amount": 0.0, "is_paid": True,
                    "created_at": None,
                })
                seat_id += 1

    with engine.begin() as conn:
        conn.execute(insert(Booking), bookings)
        conn.execute(insert(Passenger), passengers)
        conn.execute(insert(Segment), segments)
        if seat_rows:
            conn.execute(insert(SeatAssignment), seat_rows)
        if cabin_full_flights:
            conn.execute(
                Fare.__table__.update()
                .where(Fare.flight_id.in_(sorted(cabin_full_flights)))
                .where(Fare.fare_class_id.in_([7, 8, 9]))
                .values(seats_available=0)
            )

    return {"bookings": len(bookings), "passengers": len(passengers),
            "segments": len(segments), "seat assigns": len(seat_rows)}


def _pick_seats(engine, flight_id: int, count: int) -> list[str]:
    from sqlalchemy import text

    with engine.begin() as conn:
        rows = conn.execute(text("""
            select s.seat_no from seat_maps s
            join flights f on f.aircraft_id = s.aircraft_id
            where f.id = :fid and s.cabin = 'economy'
            order by s.row, s.col limit :n
        """), {"fid": flight_id, "n": count}).fetchall()
    return [r[0] for r in rows]


FARE_MULTIPLIER = {
    "EP": 0.78, "EL": 0.92, "EB": 1.00, "EG": 1.06, "ES": 1.24, "EF": 1.58,
    "HS": 2.45, "HC": 3.10, "HF": 3.85,
}


def _status_for(day: date, dep: time, rng: random.Random) -> tuple[str, int]:
    from app.clock import FROZEN_NOW, FROZEN_TODAY

    if day > FROZEN_TODAY:
        return "scheduled", 0

    roll = rng.random()
    if roll < 0.06:
        return "cancelled", 0
    if roll < 0.22:
        return "delayed", rng.choice([25, 40, 55, 70, 95, 130])
    airborne = datetime.combine(day, dep) <= FROZEN_NOW.replace(tzinfo=None)
    return ("departed" if airborne else "scheduled"), 0


def _create_schema(engine) -> None:
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            conn.execute(CreateTable(table))
        for table in Base.metadata.sorted_tables:
            for index in sorted(table.indexes, key=lambda i: i.name or ""):
                conn.execute(CreateIndex(index))


def _with_dates(row: dict, fields: tuple[str, ...]) -> dict:
    out = dict(row)
    for field in fields:
        if isinstance(out.get(field), str):
            out[field] = date.fromisoformat(out[field])
    return out


def _chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


if __name__ == "__main__":
    sys.exit(main())
