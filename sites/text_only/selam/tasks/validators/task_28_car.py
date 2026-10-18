from sqlalchemy import select

from app.models.partners import CarBooking, CarOffer

from .common import all_of, exactly_one, nothing_was_paid


def validate(session, final_url, page_html, *, partner):
    if partner not in (final_url or ""):
        return False, (f"the flow did not end on the {partner} site "
                       f"(final URL: {final_url!r})")

    rows = session.scalars(select(CarBooking)).all()
    ok, reason = all_of(exactly_one(rows, "car booking"), nothing_was_paid(session))
    if not ok:
        return False, reason

    booking = rows[0]
    if booking.is_paid:
        return False, "the car booking is marked paid"
    if booking.passengers < 2:
        return False, (f"booked for {booking.passengers} passenger(s); the task names "
                       f"two arriving passengers")

    offer = session.get(CarOffer, booking.offer_id)
    if offer is None:
        return False, "the booking points at an offer that does not exist"
    if offer.airport_iata != "NBO":
        return False, f"the transport is at {offer.airport_iata}, not Nairobi"
    if offer.seats < booking.passengers:
        return False, (f"{offer.name_en} seats {offer.seats}; it cannot carry "
                       f"{booking.passengers}")
    if round(booking.price_usd, 2) != round(offer.price_usd, 2):
        return False, "the recorded price does not match the offer"

    return True, (f"{offer.name_en} at {offer.airport_iata} for {booking.passengers} "
                  f"passengers, {booking.reference_no}, unpaid")
