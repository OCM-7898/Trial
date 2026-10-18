from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..models.network import Airport, Fare, FareClass, Flight, Route

HUB_IATA = "ADD"

MIN_CONNECTION_MIN = 75

MAX_CONNECTION_MIN = 72 * 60

STOPOVER_MIN_MIN = 8 * 60
STOPOVER_MAX_MIN = 72 * 60


@dataclass(frozen=True)
class Leg:
    flight: Flight
    fare: Fare

    @property
    def depart_at(self) -> datetime:
        return datetime.combine(self.flight.date, self.flight.dep_time)

    @property
    def arrive_at(self) -> datetime:
        return datetime.combine(
            self.flight.date + timedelta(days=self.flight.arr_day_offset),
            self.flight.arr_time,
        )


@dataclass(frozen=True)
class Itinerary:
    legs: tuple[Leg, ...]
    fare_class: FareClass

    @property
    def stops(self) -> int:
        return len(self.legs) - 1

    @property
    def depart_at(self) -> datetime:
        return self.legs[0].depart_at

    @property
    def arrive_at(self) -> datetime:
        return self.legs[-1].arrive_at

    @property
    def duration_min(self) -> int:
        return int((self.arrive_at - self.depart_at).total_seconds() // 60)

    @property
    def price_usd(self) -> float:
        return sum(leg.fare.price_usd for leg in self.legs)

    @property
    def taxes_usd(self) -> float:
        return sum(leg.fare.taxes_usd for leg in self.legs)

    @property
    def total_usd(self) -> float:
        return self.price_usd + self.taxes_usd

    @property
    def seats_available(self) -> int:
        return min(leg.fare.seats_available for leg in self.legs)

    @property
    def flight_numbers(self) -> list[str]:
        return [leg.flight.flight_no for leg in self.legs]

    @property
    def arrival_day_offset(self) -> int:
        return (self.arrive_at.date() - self.depart_at.date()).days

    @property
    def layover_min(self) -> int:
        if len(self.legs) < 2:
            return 0
        return int((self.legs[1].depart_at - self.legs[0].arrive_at).total_seconds() // 60)

    @property
    def stopover_eligible(self) -> bool:
        return STOPOVER_MIN_MIN <= self.layover_min <= STOPOVER_MAX_MIN

    @property
    def key(self) -> str:
        return "-".join(f"{leg.flight.id}.{leg.fare.fare_class_id}" for leg in self.legs)


SORTS = {
    "price": lambda i: (i.total_usd, i.duration_min, i.key),
    "duration": lambda i: (i.duration_min, i.total_usd, i.key),
    "departure": lambda i: (i.depart_at, i.total_usd, i.key),
    "arrival": lambda i: (i.arrive_at, i.total_usd, i.key),
}

TIME_BANDS = {
    "early": (time(0, 0), time(7, 59)),
    "morning": (time(8, 0), time(11, 59)),
    "afternoon": (time(12, 0), time(17, 59)),
    "evening": (time(18, 0), time(23, 59)),
}


def _fares_departing(
    session: Session, origin_id: int, destination_id: int | None, day: date, cabin: str | None
) -> list[Fare]:
    stmt = (
        select(Fare)
        .join(Flight, Flight.id == Fare.flight_id)
        .join(Route, Route.id == Flight.route_id)
        .join(FareClass, FareClass.id == Fare.fare_class_id)
        .where(Route.origin_id == origin_id, Flight.date == day, Fare.seats_available > 0)
        .options(
            joinedload(Fare.flight).joinedload(Flight.route).joinedload(Route.origin),
            joinedload(Fare.flight).joinedload(Flight.route).joinedload(Route.destination),
            joinedload(Fare.flight).joinedload(Flight.aircraft),
            joinedload(Fare.fare_class),
        )
    )
    if destination_id is not None:
        stmt = stmt.where(Route.destination_id == destination_id)
    if cabin:
        stmt = stmt.where(FareClass.cabin == cabin)
    return list(session.scalars(stmt).unique())


def search(
    session: Session,
    origin: str,
    destination: str,
    day: date,
    cabin: str | None = None,
    max_stops: int = 1,
) -> list[Itinerary]:
    airports = {
        a.iata: a for a in session.scalars(
            select(Airport).where(Airport.iata.in_([origin, destination, HUB_IATA]))
        )
    }
    if origin not in airports or destination not in airports or origin == destination:
        return []

    o_id = airports[origin].id
    d_id = airports[destination].id
    itineraries: list[Itinerary] = []

    for fare in _fares_departing(session, o_id, d_id, day, cabin):
        itineraries.append(Itinerary(legs=(Leg(fare.flight, fare),), fare_class=fare.fare_class))

    if max_stops >= 1 and HUB_IATA in airports and origin != HUB_IATA and destination != HUB_IATA:
        itineraries.extend(_via_hub(session, o_id, d_id, airports[HUB_IATA].id, day, cabin))

    return sorted(itineraries, key=SORTS["price"])


def _via_hub(
    session: Session, o_id: int, d_id: int, hub_id: int, day: date, cabin: str | None
) -> list[Itinerary]:
    inbound = _fares_departing(session, o_id, hub_id, day, cabin)
    if not inbound:
        return []

    onward: dict[date, list[Fare]] = {}
    for offset in range(0, 4):
        onward[day + timedelta(days=offset)] = _fares_departing(
            session, hub_id, d_id, day + timedelta(days=offset), cabin
        )

    out: list[Itinerary] = []
    for first in inbound:
        leg1 = Leg(first.flight, first)
        for candidates in onward.values():
            for second in candidates:
                if second.fare_class_id != first.fare_class_id:
                    continue
                leg2 = Leg(second.flight, second)
                gap = (leg2.depart_at - leg1.arrive_at).total_seconds() / 60
                if MIN_CONNECTION_MIN <= gap <= MAX_CONNECTION_MIN:
                    out.append(Itinerary(legs=(leg1, leg2), fare_class=first.fare_class))
    return out


def apply_filters(
    itineraries: list[Itinerary],
    stops: str | None = None,
    depart_band: str | None = None,
    sort: str = "price",
) -> list[Itinerary]:
    result = itineraries
    if stops == "nonstop":
        result = [i for i in result if i.stops == 0]
    elif stops == "onestop":
        result = [i for i in result if i.stops == 1]
    if depart_band in TIME_BANDS:
        lo, hi = TIME_BANDS[depart_band]
        result = [i for i in result if lo <= i.depart_at.time() <= hi]
    return sorted(result, key=SORTS.get(sort, SORTS["price"]))


def cheapest_by_fare_class(itineraries: list[Itinerary]) -> dict[str, Itinerary]:
    best: dict[str, Itinerary] = {}
    for i in sorted(itineraries, key=SORTS["price"]):
        best.setdefault(i.fare_class.code, i)
    return best


def nearby_dates(
    session: Session, origin: str, destination: str, day: date, span: int = 7
) -> list[tuple[date, float]]:
    from ..clock import WINDOW_END, WINDOW_START

    out: list[tuple[date, float]] = []
    for offset in range(-span, span + 1):
        candidate = day + timedelta(days=offset)
        if candidate < WINDOW_START or candidate > WINDOW_END or candidate == day:
            continue
        found = search(session, origin, destination, candidate, max_stops=1)
        if found:
            out.append((candidate, min(i.total_usd for i in found)))
    return sorted(out, key=lambda pair: abs((pair[0] - day).days))
