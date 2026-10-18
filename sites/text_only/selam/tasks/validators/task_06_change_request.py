from sqlalchemy import select

from app.models.ancillary import ChangeRequest
from app.models.network import Flight

from .common import (all_of, booking_by_pnr, exactly_one, nothing_was_paid,
                     only_this_booking_changed, reached_review)


def validate(session, final_url, page_html, *, pnr):
    booking = booking_by_pnr(session, pnr)
    if booking is None:
        return False, f"booking {pnr} is missing from the database"

    rows = session.scalars(
        select(ChangeRequest).where(ChangeRequest.booking_id == booking.id)).all()
    ok, reason = all_of(
        reached_review(final_url),
        exactly_one(rows, "change request"),
        nothing_was_paid(session),
        only_this_booking_changed(session, ChangeRequest, booking.id),
    )
    if not ok:
        return False, reason

    request = rows[0]
    if request.status != "pending":
        return False, f"change request status is {request.status!r}, expected 'pending'"

    original = {segment.flight_id for segment in booking.segments}
    if request.new_flight_id in original:
        return False, "the requested flight is the one already booked"

    new_flight = session.get(Flight, request.new_flight_id)
    old_flight = session.get(Flight, sorted(original)[0])
    if new_flight is None:
        return False, "the change points at a flight that does not exist"
    if new_flight.route_id != old_flight.route_id:
        return False, "the change moves the passenger to a different route, not a new date"

    expected = round(request.fare_difference_usd + request.change_fee_usd, 2)
    if round(request.total_due_usd, 2) != expected:
        return False, (f"quoted total {request.total_due_usd} does not equal fare "
                       f"difference plus fee ({expected})")

    if any(segment.flight_id == request.new_flight_id for segment in booking.segments):
        return False, "the booking was rewritten; a change request must stay pending"

    return True, (f"change request {request.reference_no} pending on {pnr}: "
                  f"{old_flight.date} -> {new_flight.date}, "
                  f"total due {request.total_due_usd}, nothing paid")
