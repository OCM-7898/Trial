from sqlalchemy import select

from app.models.ancillary import RefundRequest
from app.services.eligibility import refund_decision

from .common import booking_by_pnr, fare_class_of_first_segment, nothing_was_paid


def validate(session, final_url, page_html, *, pnr, expected_code):
    booking = booking_by_pnr(session, pnr)
    if booking is None:
        return False, f"booking {pnr} is missing from the database"

    fare_class = fare_class_of_first_segment(session, booking)
    decision = refund_decision(booking, fare_class)
    if decision.code != expected_code:
        return False, (f"the seeded booking no longer produces {expected_code}; "
                       f"it now yields {decision.code!r}. The task needs re-instantiating.")

    rows = session.scalars(
        select(RefundRequest).where(RefundRequest.booking_id == booking.id)).all()
    if rows:
        return False, ("a refund request was created for a booking the site refuses to "
                       "refund online")

    ok, reason = nothing_was_paid(session)
    if not ok:
        return False, reason

    if page_html and "notice-warn" not in page_html and "notice-error" not in page_html:
        return False, "the refusal was never displayed to the agent"

    return True, (f"{pnr} was correctly refused an online refund "
                  f"({expected_code}) and no request row was written")
