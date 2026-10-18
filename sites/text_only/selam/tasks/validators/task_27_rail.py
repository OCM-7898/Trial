from sqlalchemy import select

from app.models.partners import RailConnection

from .common import nothing_was_paid


def validate(session, final_url, page_html, *, partner):
    url = final_url or ""
    if partner not in url:
        return False, f"the agent did not reach the {partner} site (final URL: {url!r})"

    rows = session.scalars(
        select(RailConnection).where(RailConnection.arrival_iata == "FRA")).all()
    if not rows:
        return False, "no rail connection is seeded from Frankfurt; the task is unanswerable"

    cologne = next((r for r in rows if r.destination_en == "Cologne"), None)
    if cologne is None:
        return False, "the Cologne connection is missing from the seed data"

    if page_html and cologne.booking_note_en[:40] not in page_html \
            and cologne.booking_note_am[:40] not in page_html:
        return False, "the booking note for the Cologne leg was never displayed"

    ok, reason = nothing_was_paid(session)
    if not ok:
        return False, reason
    return True, (f"Frankfurt-Cologne shown on the {partner} site as "
                  f"{cologne.ticket_type_en!r}")
