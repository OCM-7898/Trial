from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models.loyalty import AwardInventory, LoyaltyMember, MilesTransaction
from ..models.network import Airport, Fare, Flight, Route

TIERS = (("blue", 0), ("silver", 25_000), ("gold", 50_000), ("platinum", 100_000))


@dataclass(frozen=True)
class TierProgress:
    tier: str
    next_tier: str | None
    qualifying: int
    needed: int


def tier_for(qualifying_miles: int) -> str:
    current = TIERS[0][0]
    for name, floor in TIERS:
        if qualifying_miles >= floor:
            current = name
    return current


def progress(member: LoyaltyMember) -> TierProgress:
    index = [name for name, _ in TIERS].index(member.tier)
    if index + 1 >= len(TIERS):
        return TierProgress(member.tier, None, member.qualifying_miles, 0)
    next_name, next_floor = TIERS[index + 1]
    return TierProgress(member.tier, next_name, member.qualifying_miles,
                        max(0, next_floor - member.qualifying_miles))


def find_member(session: Session, member_no: str, surname: str,
                surname_column) -> LoyaltyMember | None:
    if not member_no or not surname:
        return None
    return session.scalars(
        select(LoyaltyMember)
        .where(func.upper(LoyaltyMember.member_no) == member_no.strip().upper())
        .where(func.lower(surname_column) == surname.strip().lower())
    ).one_or_none()


def statement(session: Session, member: LoyaltyMember,
              since: date | None = None) -> list[MilesTransaction]:
    stmt = select(MilesTransaction).where(MilesTransaction.member_id == member.id)
    if since:
        stmt = stmt.where(MilesTransaction.posted_on >= since)
    return list(session.scalars(stmt.order_by(MilesTransaction.posted_on.desc(),
                                              MilesTransaction.id.desc())))


@dataclass(frozen=True)
class AwardOption:
    flight: Flight
    origin: Airport
    destination: Airport
    inventory: AwardInventory


def award_search(session: Session, origin: str, destination: str, day: date,
                 cabin: str | None = None) -> list[AwardOption]:
    origin_row = session.scalars(select(Airport).where(Airport.iata == origin.upper())).one_or_none()
    destination_row = session.scalars(
        select(Airport).where(Airport.iata == destination.upper())).one_or_none()
    if origin_row is None or destination_row is None:
        return []

    stmt = (
        select(AwardInventory, Flight)
        .join(Flight, Flight.id == AwardInventory.flight_id)
        .join(Route, Route.id == Flight.route_id)
        .where(Route.origin_id == origin_row.id,
               Route.destination_id == destination_row.id,
               Flight.date == day,
               AwardInventory.seats > 0)
        .order_by(AwardInventory.miles_required, Flight.dep_time)
    )
    if cabin:
        stmt = stmt.where(AwardInventory.cabin == cabin)

    return [AwardOption(flight=flight, origin=origin_row, destination=destination_row,
                        inventory=inventory)
            for inventory, flight in session.execute(stmt)]


def nearby_award_dates(session: Session, origin: str, destination: str,
                       day: date, span: int = 10) -> list[tuple[date, int]]:
    from datetime import timedelta

    from ..clock import WINDOW_END, WINDOW_START

    out = []
    for offset in range(-span, span + 1):
        candidate = day + timedelta(days=offset)
        if candidate == day or not (WINDOW_START <= candidate <= WINDOW_END):
            continue
        options = award_search(session, origin, destination, candidate)
        if options:
            out.append((candidate, min(o.inventory.miles_required for o in options)))
    return sorted(out, key=lambda pair: abs((pair[0] - day).days))
