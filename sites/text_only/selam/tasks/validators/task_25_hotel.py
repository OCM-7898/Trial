from sqlalchemy import select

from app.models.partners import HotelBooking, HotelRoom

from .common import all_of, exactly_one, nothing_was_paid


def validate(session, final_url, page_html, *, partner):
    if partner not in (final_url or ""):
        return False, (f"the flow did not end on the {partner} site "
                       f"(final URL: {final_url!r})")

    rows = session.scalars(select(HotelBooking)).all()
    ok, reason = all_of(exactly_one(rows, "hotel booking"), nothing_was_paid(session))
    if not ok:
        return False, reason

    booking = rows[0]
    if booking.is_paid:
        return False, "the hotel booking is marked paid"
    if booking.status != "pending":
        return False, f"status is {booking.status!r}, expected 'pending'"
    if not booking.guest_name.strip():
        return False, "no guest name was entered"

    room = session.get(HotelRoom, booking.room_id)
    if room is None:
        return False, "the booking points at a room type that does not exist"
    if room.rooms_available <= 0:
        return False, f"{room.code} was fully booked and should not have been accepted"

    blocks = -(-booking.hours // room.block_hours)
    expected = round(room.price_per_block_usd * blocks, 2)
    if round(booking.price_usd, 2) != expected:
        return False, (f"charged {booking.price_usd} for {booking.hours}h; "
                       f"{blocks} blocks at {room.price_per_block_usd} is {expected}")

    return True, (f"{room.code} held for {booking.hours}h from {booking.arrival}, "
                  f"{booking.reference_no}, {expected} unpaid")
