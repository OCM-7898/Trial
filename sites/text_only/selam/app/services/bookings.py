from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..models import translated_column
from ..models.booking import Booking, Passenger, SeatAssignment, Segment
from ..models.network import Airport, FareClass, Flight, Route


@dataclass(frozen=True)
class SegmentView:
    segment: Segment
    flight: Flight
    route: Route
    origin: Airport
    destination: Airport
    fare_class: FareClass
    seats: dict[int, SeatAssignment]


def retrieve(session: Session, pnr: str, surname: str) -> Booking | None:
    if not pnr or not surname:
        return None

    column = translated_column(Booking, "surname")
    stmt = (
        select(Booking)
        .where(func.upper(Booking.pnr) == pnr.strip().upper())
        .where(func.lower(column) == surname.strip().lower())
        .options(
            selectinload(Booking.passengers),
            selectinload(Booking.segments),
        )
    )
    return session.scalars(stmt).one_or_none()


def by_pnr(session: Session, pnr: str) -> Booking | None:
    return session.scalars(
        select(Booking)
        .where(func.upper(Booking.pnr) == (pnr or "").strip().upper())
        .options(selectinload(Booking.passengers), selectinload(Booking.segments))
    ).one_or_none()


def itinerary(session: Session, booking: Booking) -> list[SegmentView]:
    views: list[SegmentView] = []
    for segment in sorted(booking.segments, key=lambda s: s.sequence):
        flight = session.get(Flight, segment.flight_id)
        route = session.get(Route, flight.route_id)
        assignments = session.scalars(
            select(SeatAssignment).where(SeatAssignment.segment_id == segment.id)
        ).all()
        views.append(SegmentView(
            segment=segment,
            flight=flight,
            route=route,
            origin=session.get(Airport, route.origin_id),
            destination=session.get(Airport, route.destination_id),
            fare_class=session.get(FareClass, segment.fare_class_id),
            seats={a.passenger_id: a for a in assignments},
        ))
    return views


def business_fares(session: Session, flight_id: int) -> list:
    from ..models.network import Fare

    return list(session.scalars(
        select(Fare).join(FareClass, FareClass.id == Fare.fare_class_id)
        .where(Fare.flight_id == flight_id, FareClass.cabin == "business")
        .order_by(Fare.id)
    ))


def passenger_label(passenger: Passenger) -> str:
    return passenger.full_name
