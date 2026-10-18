from sqlalchemy import select

from app.models.booking import SeatAssignment
from app.models.network import Flight, SeatMapSeat

from .common import all_of, booking_by_pnr, nothing_was_paid, reached_review


def validate(session, final_url, page_html, *, pnr):
    booking = booking_by_pnr(session, pnr)
    if booking is None:
        return False, f"booking {pnr} is missing from the database"

    outbound = sorted(booking.segments, key=lambda s: s.sequence)[0]
    assignments = session.scalars(
        select(SeatAssignment).where(SeatAssignment.segment_id == outbound.id,
                                     SeatAssignment.created_at.isnot(None))).all()
    if not assignments:
        return False, "no seat was selected during the episode"
    if len(assignments) > 1:
        return False, f"{len(assignments)} seats were selected; the task asks for one"

    assignment = assignments[0]
    flight = session.get(Flight, outbound.flight_id)
    seat = session.scalars(
        select(SeatMapSeat).where(SeatMapSeat.aircraft_id == flight.aircraft_id,
                                  SeatMapSeat.seat_no == assignment.seat_no)).one_or_none()
    if seat is None:
        return False, f"seat {assignment.seat_no} is not on this aircraft's seat map"
    if not seat.is_aisle:
        characteristic = "window" if seat.is_window else "middle"
        return False, (f"seat {seat.seat_no} is a {characteristic} seat; the task asks "
                       f"for an aisle seat")

    if round(assignment.paid_amount, 2) != round(seat.price_usd, 2):
        return False, (f"the recorded charge {assignment.paid_amount} does not match the "
                       f"seat's price {seat.price_usd}")

    ok, reason = all_of(reached_review(final_url), nothing_was_paid(session))
    if not ok:
        return False, reason

    others = [s for s in booking.segments if s.id != outbound.id]
    for segment in others:
        stray = session.scalars(
            select(SeatAssignment).where(SeatAssignment.segment_id == segment.id,
                                         SeatAssignment.created_at.isnot(None))).all()
        if stray:
            return False, "a seat was also selected on a segment the task did not name"

    return True, (f"aisle seat {seat.seat_no} selected on {pnr} at "
                  f"USD {seat.price_usd:.0f}, unpaid")
