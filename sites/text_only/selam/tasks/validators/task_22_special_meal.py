from sqlalchemy import select

from app.models.onboard import MealRequest, SpecialMealCode

from .common import booking_by_pnr, nothing_was_paid


def validate(session, final_url, page_html, *, pnr, expected_code):
    booking = booking_by_pnr(session, pnr)
    if booking is None:
        return False, f"booking {pnr} is missing from the database"

    segment_ids = {segment.id for segment in booking.segments}
    requests = session.scalars(
        select(MealRequest).where(MealRequest.segment_id.in_(segment_ids))).all()
    if not requests:
        return False, "no special meal was requested"
    if len(requests) > 1:
        return False, (f"{len(requests)} meal requests were made; the task asks for one "
                       f"({[r.meal_code for r in requests]})")

    request = requests[0]
    if request.meal_code != expected_code:
        code = session.scalars(select(SpecialMealCode).where(
            SpecialMealCode.code == request.meal_code)).one_or_none()
        label = f" ({code.name_en})" if code else ""
        return False, (f"{request.meal_code}{label} was requested; the task asks for "
                       f"{expected_code}")

    if request.passenger_id not in {p.id for p in booking.passengers}:
        return False, "the meal was requested for a passenger on another booking"

    strays = session.scalars(
        select(MealRequest).where(MealRequest.segment_id.notin_(segment_ids))).all()
    if strays:
        return False, f"{len(strays)} meal request(s) were left on other bookings"

    ok, reason = nothing_was_paid(session)
    if not ok:
        return False, reason

    return True, f"{expected_code} requested on {pnr} for passenger {request.passenger_id}"
