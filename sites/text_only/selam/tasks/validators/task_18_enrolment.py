from sqlalchemy import select

from app.clock import today
from app.models.loyalty import LoyaltyMember

from .common import nothing_was_paid


def validate(session, final_url, page_html, *, email, expected_member_no):
    members = session.scalars(
        select(LoyaltyMember).where(LoyaltyMember.created_at_runtime.is_(True))).all()
    if not members:
        return False, "no membership was created during the episode"
    if len(members) > 1:
        return False, (f"{len(members)} memberships were created; the task asks for one "
                       f"({[m.member_no for m in members]})")

    member = members[0]
    if member.email.lower() != email.lower():
        return False, f"the account was created for {member.email!r}, not {email!r}"

    if member.member_no != expected_member_no:
        return False, (f"membership number {member.member_no} is not the next in "
                       f"sequence ({expected_member_no}); the counter is not "
                       f"deterministic after reset")

    if member.tier != "blue":
        return False, f"a new member should start on blue, not {member.tier!r}"
    if member.miles_balance or member.qualifying_miles:
        return False, "a new member should start with no miles"
    if member.joined_on != today():
        return False, (f"joined_on is {member.joined_on}, not the frozen today "
                       f"({today()}); something read the wall clock")

    ok, reason = nothing_was_paid(session)
    if not ok:
        return False, reason

    return True, f"member {member.member_no} enrolled on {member.joined_on}, blue tier, 0 miles"
