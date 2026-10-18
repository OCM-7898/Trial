from sqlalchemy import select

from app.clock import today
from app.models.loyalty import MissingMilesClaim

from .common import exactly_one, nothing_was_paid


def validate(session, final_url, page_html, *, member_no, flight_no):
    rows = session.scalars(select(MissingMilesClaim)).all()
    ok, reason = exactly_one(rows, "missing-miles claim")
    if not ok:
        return False, reason

    claim = rows[0]
    if claim.member_no.upper() != member_no.upper():
        return False, f"the claim was filed for {claim.member_no}, not {member_no}"
    if claim.flight_no.replace(" ", "").upper() != flight_no.replace(" ", "").upper():
        return False, f"the claim names flight {claim.flight_no}, not {flight_no}"
    if claim.flight_date >= today():
        return False, (f"the claim is for {claim.flight_date}, which is not in the past "
                       f"relative to the frozen clock ({today()})")
    if claim.status != "under_review":
        return False, f"claim status is {claim.status!r}, expected 'under_review'"
    if not claim.reference_no.startswith("MC-") or len(claim.reference_no) != 9:
        return False, (f"reference {claim.reference_no!r} does not match the MC-<6 digits> "
                       f"format SPEC.md 9.5 requires")
    if page_html and claim.reference_no not in page_html:
        return False, "the reference number was never shown to the agent"

    ok, reason = nothing_was_paid(session)
    if not ok:
        return False, reason

    return True, (f"claim {claim.reference_no} filed for {member_no} on flight "
                  f"{claim.flight_no} ({claim.flight_date}), under review")
