from __future__ import annotations

from sqlalchemy import func, select

from app.models.ancillary import (
    BaggagePurchase, ChangeRequest, LoungePurchase, RefundRequest, UpgradePurchase,
)
from app.models.booking import Booking, SeatAssignment

PENDING_MODELS = (ChangeRequest, RefundRequest, BaggagePurchase, UpgradePurchase,
                  LoungePurchase)


def reached_review(final_url: str) -> tuple[bool, str]:
    if "/review" not in (final_url or ""):
        return False, f"the flow did not end on a review page (final URL: {final_url!r})"
    return True, ""


def nothing_was_paid(session) -> tuple[bool, str]:
    for model in PENDING_MODELS:
        paid = session.scalars(select(model).where(model.is_paid.is_(True))).all()
        if paid:
            return False, (f"{model.__tablename__} has {len(paid)} row(s) marked paid; "
                           f"no payment may ever complete")
    runtime_paid = session.scalars(
        select(SeatAssignment).where(SeatAssignment.is_paid.is_(True),
                                     SeatAssignment.created_at.isnot(None))
    ).all()
    if runtime_paid:
        return False, "a seat assignment created during the episode is marked paid"
    return True, ""


def booking_by_pnr(session, pnr: str) -> Booking | None:
    return session.scalars(
        select(Booking).where(func.upper(Booking.pnr) == pnr.upper())).one_or_none()


def only_this_booking_changed(session, model, booking_id: int) -> tuple[bool, str]:
    strays = session.scalars(
        select(model).where(model.booking_id.isnot(None),
                            model.booking_id != booking_id)).all()
    if strays:
        pnrs = sorted({session.get(Booking, row.booking_id).pnr for row in strays})
        return False, (f"{model.__tablename__} rows were also created on other "
                       f"bookings: {pnrs}")
    return True, ""


def fare_class_of_first_segment(session, booking):
    from app.models.network import FareClass

    first = sorted(booking.segments, key=lambda s: s.sequence)[0]
    return session.get(FareClass, first.fare_class_id)


def exactly_one(rows, what: str) -> tuple[bool, str]:
    if not rows:
        return False, f"no {what} was created"
    if len(rows) > 1:
        return False, f"{len(rows)} {what} rows were created; the task asks for one"
    return True, ""


def all_of(*checks: tuple[bool, str]) -> tuple[bool, str]:
    for ok, reason in checks:
        if not ok:
            return False, reason
    return True, ""
