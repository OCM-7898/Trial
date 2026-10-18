from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..clock import hours_until
from ..models.booking import Booking, Segment
from ..models.network import Fare, FareClass, Flight

CHECKIN_OPENS_H = 48
CHECKIN_CLOSES_H = 2

CHECKIN_PRECEDENCE = (
    "GROUP_BOOKING",
    "UNACCOMPANIED_MINOR",
    "CODESHARE_OPERATED_BY_PARTNER",
    "SPECIAL_ASSISTANCE_REQUIRED",
    "INFANT_ON_LAP",
    "DOCUMENT_CHECK_REQUIRED",
    "TOO_EARLY",
    "CLOSED",
)


@dataclass(frozen=True)
class Decision:
    allowed: bool
    code: str | None = None
    detail: dict | None = None


def departure_of(segment: Segment, flight: Flight) -> datetime:
    return datetime.combine(flight.date, flight.dep_time)


def checkin_decision(booking: Booking, segment: Segment, flight: Flight) -> Decision:
    reasons: set[str] = set()

    if booking.is_group or len(booking.passengers) >= 10:
        reasons.add("GROUP_BOOKING")

    pax = booking.passengers
    if pax and all(p.pax_type == "child" for p in pax):
        reasons.add("UNACCOMPANIED_MINOR")
    if any(p.pax_type == "infant" for p in pax):
        reasons.add("INFANT_ON_LAP")
    if any(p.assistance_code for p in pax):
        reasons.add("SPECIAL_ASSISTANCE_REQUIRED")
    if any(not p.passport_number for p in pax if p.pax_type != "infant"):
        reasons.add("DOCUMENT_CHECK_REQUIRED")

    if segment.operated_by:
        reasons.add("CODESHARE_OPERATED_BY_PARTNER")

    hours = hours_until(departure_of(segment, flight))
    if hours > CHECKIN_OPENS_H:
        reasons.add("TOO_EARLY")
    elif hours < CHECKIN_CLOSES_H:
        reasons.add("CLOSED")

    for code in CHECKIN_PRECEDENCE:
        if code in reasons:
            return Decision(False, code, {"hours_to_departure": round(hours, 1)})
    return Decision(True, None, {"hours_to_departure": round(hours, 1)})


def change_decision(fare_class: FareClass, segment: Segment, flight: Flight) -> Decision:
    hours = hours_until(departure_of(segment, flight))
    if not fare_class.changeable:
        return Decision(False, "FARE_NOT_CHANGEABLE", {"fare_class": fare_class.code})
    if hours < CHECKIN_CLOSES_H:
        return Decision(False, "TOO_LATE_TO_CHANGE", {"hours_to_departure": round(hours, 1)})
    fee = 0.0 if hours > 72 else fare_class.change_fee_usd
    return Decision(True, None, {
        "fee_usd": fee,
        "fee_waived": hours > 72 and fare_class.change_fee_usd > 0,
        "hours_to_departure": round(hours, 1),
    })


def refund_decision(booking: Booking, fare_class: FareClass) -> Decision:
    if not fare_class.refundable or fare_class.refund_pct == 0:
        return Decision(False, "FARE_NON_REFUNDABLE", {"fare_class": fare_class.code})
    if booking.booked_channel != "website":
        return Decision(False, "OFFLINE_CHANNEL_ONLY", {"channel": booking.booked_channel})
    gross = booking.total_paid
    refundable = round(gross * fare_class.refund_pct / 100.0, 2)
    return Decision(True, None, {
        "refund_pct": fare_class.refund_pct,
        "fee_usd": fare_class.refund_fee_usd,
        "gross_usd": gross,
        "quoted_usd": round(max(0.0, refundable - fare_class.refund_fee_usd), 2),
    })


def upgrade_decision(
    fare_class: FareClass, business_fares: list[Fare]
) -> Decision:
    if not fare_class.upgrade_eligible:
        return Decision(False, "FARE_CLASS_EXCLUDED", {"fare_class": fare_class.code})
    if not business_fares:
        return Decision(False, "NO_BUSINESS_CABIN", {})
    open_fares = [f for f in business_fares if f.seats_available > 0]
    if not open_fares:
        return Decision(False, "CABIN_FULL", {})
    cheapest = min(open_fares, key=lambda f: f.price_usd)
    return Decision(True, None, {
        "price_usd": cheapest.price_usd,
        "fare_class_id": cheapest.fare_class_id,
        "seats_available": cheapest.seats_available,
    })
