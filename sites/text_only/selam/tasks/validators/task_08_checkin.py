from pathlib import Path

from sqlalchemy import select

from app.models.checkin import BoardingPass, Checkin

from .common import booking_by_pnr, nothing_was_paid


def validate(session, final_url, page_html, *, pnr):
    booking = booking_by_pnr(session, pnr)
    if booking is None:
        return False, f"booking {pnr} is missing from the database"

    segment_ids = {segment.id for segment in booking.segments}
    checkins = session.scalars(
        select(Checkin).where(Checkin.segment_id.in_(segment_ids))).all()
    if not checkins:
        return False, "no check-in was recorded"

    if not any(segment.checked_in for segment in booking.segments):
        return False, "check-in rows exist but no segment is marked checked in"

    passes = [session.get(BoardingPass, c.boarding_pass_id) for c in checkins]
    missing = [c.id for c, p in zip(checkins, passes) if p is None]
    if missing:
        return False, f"check-in rows {missing} have no boarding pass"

    for record in passes:
        expected_prefix = f"{booking.pnr}|"
        if not record.barcode_payload.startswith(expected_prefix):
            return False, (f"barcode payload {record.barcode_payload!r} does not follow "
                           f"PNR|SEG|SEQ for {booking.pnr}")
        if not Path(record.pdf_path).exists():
            return False, f"the boarding pass PDF was not written to {record.pdf_path}"

    others = session.scalars(
        select(Checkin).where(Checkin.segment_id.notin_(segment_ids))).all()
    if others:
        return False, f"{len(others)} check-in(s) were made on other bookings"

    ok, reason = nothing_was_paid(session)
    if not ok:
        return False, reason

    return True, (f"{pnr} checked in; {len(passes)} boarding pass(es) generated, "
                  f"payload {passes[0].barcode_payload}")
