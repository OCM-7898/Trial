from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.booking import SeatAssignment, Segment
from ..models.network import Flight, SeatMapSeat


@dataclass(frozen=True)
class SeatCell:
    seat: SeatMapSeat
    taken: bool

    @property
    def selectable(self) -> bool:
        return not self.taken


@dataclass(frozen=True)
class SeatRow:
    number: int
    cells: tuple[SeatCell | None, ...]
    is_exit: bool

    @property
    def has_extra_legroom(self) -> bool:
        return any(c.seat.extra_legroom for c in self.cells if c)

    @property
    def prices(self) -> tuple[float, ...]:
        return tuple(sorted({c.seat.price_usd for c in self.cells if c}))

    @property
    def price_low(self) -> float:
        return self.prices[0] if self.prices else 0.0

    @property
    def price_high(self) -> float:
        return self.prices[-1] if self.prices else 0.0

    @property
    def single_price(self) -> bool:
        return len(self.prices) <= 1


def occupied(session: Session, segment_id: int) -> set[str]:
    return set(session.scalars(
        select(SeatAssignment.seat_no).where(SeatAssignment.segment_id == segment_id)
    ))


def seat_map(session: Session, segment: Segment, flight: Flight) -> list[SeatRow]:
    taken = occupied(session, segment.id)
    seats = list(session.scalars(
        select(SeatMapSeat)
        .where(SeatMapSeat.aircraft_id == flight.aircraft_id)
        .order_by(SeatMapSeat.row, SeatMapSeat.col)
    ))
    if not seats:
        return []

    aircraft = flight.aircraft
    layouts = {"business": aircraft.business_layout, "economy": aircraft.economy_layout}

    by_row: dict[int, list[SeatMapSeat]] = {}
    for seat in seats:
        by_row.setdefault(seat.row, []).append(seat)

    rows: list[SeatRow] = []
    for number in sorted(by_row):
        row_seats = {s.col: s for s in by_row[number]}
        layout = layouts.get(by_row[number][0].cabin, "")
        cells: list[SeatCell | None] = []
        for char in layout:
            if char == "-":
                cells.append(None)
            elif char in row_seats:
                seat = row_seats[char]
                cells.append(SeatCell(seat=seat, taken=seat.seat_no in taken))
        rows.append(SeatRow(
            number=number,
            cells=tuple(cells),
            is_exit=any(s.is_exit for s in by_row[number]),
        ))
    return rows


def find_seat(session: Session, flight: Flight, seat_no: str) -> SeatMapSeat | None:
    return session.scalars(
        select(SeatMapSeat).where(
            SeatMapSeat.aircraft_id == flight.aircraft_id,
            SeatMapSeat.seat_no == seat_no,
        )
    ).one_or_none()


@dataclass(frozen=True)
class ColumnGuide:
    window: tuple[str, ...]
    aisle: tuple[str, ...]
    middle: tuple[str, ...]

    @property
    def is_useful(self) -> bool:
        return bool(self.window or self.aisle)


def column_guide(rows: list[SeatRow]) -> ColumnGuide:
    tally: dict[str, dict[str, int]] = {}
    for row in rows:
        for cell in row.cells:
            if cell is None:
                continue
            seat = cell.seat
            kind = ("window" if seat.is_window
                    else "aisle" if seat.is_aisle else "middle")
            tally.setdefault(seat.col, {}).setdefault(kind, 0)
            tally[seat.col][kind] += 1

    groups: dict[str, list[str]] = {"window": [], "aisle": [], "middle": []}
    for col in sorted(tally):
        kind = max(tally[col], key=lambda k: tally[col][k])
        groups[kind].append(col)
    return ColumnGuide(window=tuple(groups["window"]),
                       aisle=tuple(groups["aisle"]),
                       middle=tuple(groups["middle"]))
