from sqlalchemy import select

from app.models.draft import DraftBooking
from app.models.network import Airport, Flight, Route

from .common import all_of, exactly_one, nothing_was_paid, reached_review


def validate(session, final_url, page_html, *, origin, destination, depart):
    drafts = session.scalars(select(DraftBooking)).all()
    ok, reason = all_of(
        reached_review(final_url),
        exactly_one(drafts, "draft booking"),
        nothing_was_paid(session),
    )
    if not ok:
        return False, reason

    draft = drafts[0]
    if draft.is_paid:
        return False, "the draft is marked paid; no payment may ever complete"

    flight = session.get(Flight, draft.flight_id)
    route = session.get(Route, flight.route_id)
    origin_row = session.get(Airport, route.origin_id)
    destination_row = session.get(Airport, route.destination_id)

    if origin_row.iata != origin or destination_row.iata != destination:
        return False, (f"the draft books {origin_row.iata}-{destination_row.iata}; the "
                       f"task asks for {origin}-{destination}")
    if flight.date.isoformat() != depart:
        return False, f"the draft is for {flight.date}, not {depart}"
    if draft.return_flight_id is not None:
        return False, "a return flight was added; the task asks for one way"

    if not draft.passengers:
        return False, "no passenger details were entered"
    blank = [p.id for p in draft.passengers
             if not p.first_name.strip() or not p.last_name.strip()]
    if blank:
        return False, f"passenger rows {blank} have no name"
    if not draft.contact_email.strip():
        return False, "no contact email was entered"

    from app.models.booking import Booking

    if session.scalar(select(Booking).where(Booking.status == "draft")):
        return False, "a draft was written into the seeded bookings table"

    return True, (f"draft {draft.reference} holds {origin}-{destination} on "
                  f"{flight.date} for {len(draft.passengers)} passenger(s), "
                  f"total {draft.total_usd}, unpaid")
