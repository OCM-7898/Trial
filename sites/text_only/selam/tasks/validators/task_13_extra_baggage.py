from sqlalchemy import select

from app.models.ancillary import BaggagePurchase
from app.models.network import Route
from app.services.baggage import quote_extra, rule_for_route

from .common import (all_of, booking_by_pnr, exactly_one,
                     fare_class_of_first_segment, nothing_was_paid,
                     only_this_booking_changed, reached_review)


def validate(session, final_url, page_html, *, pnr, expected_extra_kg):
    booking = booking_by_pnr(session, pnr)
    if booking is None:
        return False, f"booking {pnr} is missing from the database"

    rows = session.scalars(
        select(BaggagePurchase).where(BaggagePurchase.booking_id == booking.id)).all()
    ok, reason = all_of(
        reached_review(final_url),
        exactly_one(rows, "baggage purchase"),
        nothing_was_paid(session),
        only_this_booking_changed(session, BaggagePurchase, booking.id),
    )
    if not ok:
        return False, reason

    purchase = rows[0]
    if purchase.extra_kg != expected_extra_kg:
        return False, (f"{purchase.extra_kg} kg was added; the task asks for "
                       f"{expected_extra_kg} kg")

    outbound = sorted(booking.segments, key=lambda s: s.sequence)[0]
    from app.models.network import Flight

    flight = session.get(Flight, outbound.flight_id)
    route = session.get(Route, flight.route_id)
    rule = rule_for_route(session, route, fare_class_of_first_segment(session, booking).cabin,
                          "adult")
    if rule is None:
        return False, "no baggage rule applies to this route; the task is unanswerable"
    expected_price = quote_extra(rule, expected_extra_kg)
    if round(purchase.price_usd, 2) != round(expected_price, 2):
        return False, (f"charged {purchase.price_usd} but the {rule.region} rate gives "
                       f"{expected_price} for {expected_extra_kg} kg")

    if outbound.extra_baggage_kg != 0:
        return False, "the segment's allowance was altered; the purchase must stay pending"

    return True, (f"{expected_extra_kg} kg pending on {pnr} at USD {expected_price:.0f} "
                  f"({rule.region} rate), reference {purchase.reference_no}, unpaid")
