from __future__ import annotations

from flask import (
    Blueprint, abort, g, redirect, render_template, request,
    session as flask_session,
)
from sqlalchemy import select

from .. import db as database
from ..clock import now
from ..i18n import labels, t
from ..models.ancillary import (
    BaggagePurchase, ChangeRequest, RefundRequest, UpgradePurchase,
)
from ..models.booking import SeatAssignment
from ..models.network import Fare, FareClass, Flight
from ..params import bounded_int, row_id
from ..routes_map import SLUGS, path
from ..services import baggage as baggage_service
from ..services import bookings as booking_service
from ..services import eligibility, references
from ..services import references
from ..services import seats as seat_service

bp = Blueprint("flows", __name__)

PAY_ACTION = "pay"


def _authorised(pnr: str):
    known = {p.upper() for p in flask_session.get("retrieved_pnrs", [])}
    booking = booking_service.by_pnr(database.session(), pnr)
    if booking is None or booking.pnr.upper() not in known:
        return None
    return booking


def _reauth(pnr: str):
    return render_template(
        "manage/retrieve.html", error=t("manage.reauth"), pnr=pnr, surname=""
    ), 404


def _segment_view(booking, segment_id: int | None):
    views = booking_service.itinerary(database.session(), booking)
    if segment_id is None:
        return views[0]
    return next((v for v in views if v.segment.id == segment_id), None)


def _paid_notice() -> str | None:
    if request.method == "POST" and request.form.get("action") == PAY_ACTION:
        return t("review.payment_disabled")
    return None


@bp.route(SLUGS["seats"], methods=["GET", "POST"])
def seats(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)

    db = database.session()
    requested = row_id(request.values.get("segment_id"))
    view = _segment_view(booking, requested)
    if view is None:
        abort(404)

    if request.method == "POST" and request.form.get("seat_no"):
        return _select_seat(db, booking, view, request.form["seat_no"],
                            row_id(request.form.get("passenger_id")))

    rows = seat_service.seat_map(db, view.segment, view.flight)
    return render_template(
        "flows/seats.html",
        booking=booking, view=view, rows=rows,
        guide=seat_service.column_guide(rows),
        views=booking_service.itinerary(db, booking),
        error=None,
    )


def _select_seat(db, booking, view, seat_no: str, passenger_id: int | None):
    seat = seat_service.find_seat(db, view.flight, seat_no)
    taken = seat_service.occupied(db, view.segment.id)

    if seat is None or (seat_no in taken):
        rows = seat_service.seat_map(db, view.segment, view.flight)
        return render_template(
            "flows/seats.html", booking=booking, view=view, rows=rows,
            guide=seat_service.column_guide(rows),
            views=booking_service.itinerary(db, booking),
            error=t("seats.unavailable"),
        ), 409

    passenger = next(
        (p for p in booking.passengers if p.id == passenger_id),
        next((p for p in booking.passengers if p.pax_type != "infant"), None),
    )
    if passenger is None:
        abort(404)

    existing = db.scalars(select(SeatAssignment).where(
        SeatAssignment.segment_id == view.segment.id,
        SeatAssignment.passenger_id == passenger.id,
    )).one_or_none()

    if existing is not None:
        existing.seat_no = seat.seat_no
        existing.paid_amount = seat.price_usd
        existing.is_paid = False
        existing.created_at = now().replace(tzinfo=None)
    else:
        db.add(SeatAssignment(
            segment_id=view.segment.id, passenger_id=passenger.id,
            seat_no=seat.seat_no, paid_amount=seat.price_usd,
            is_paid=False, created_at=now().replace(tzinfo=None),
        ))
    db.commit()
    return redirect(f"{path('seats_review', pnr=booking.pnr)}?segment_id={view.segment.id}")


@bp.route(SLUGS["seats_review"], methods=["GET", "POST"])
def seats_review(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)

    db = database.session()
    view = _segment_view(booking, row_id(request.values.get("segment_id")))
    if view is None:
        abort(404)

    assignments = db.scalars(select(SeatAssignment).where(
        SeatAssignment.segment_id == view.segment.id
    ).order_by(SeatAssignment.id)).all()
    names = {p.id: p.full_name for p in booking.passengers}
    lines = [{
        "label": names.get(a.passenger_id, ""),
        "detail": a.seat_no,
        "amount": a.paid_amount,
    } for a in assignments]

    return render_template(
        "flows/review.html",
        booking=booking, view=view,
        heading=t("seats.review_title"),
        lines=lines,
        total=sum(line["amount"] for line in lines),
        notice=_paid_notice(),
        back_url=f"{path('seats', pnr=booking.pnr)}?segment_id={view.segment.id}",
    )


@bp.route(SLUGS["change"], methods=["GET", "POST"])
def change(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)

    db = database.session()
    view = _segment_view(booking, row_id(request.values.get("segment_id")))
    if view is None:
        abort(404)

    decision = eligibility.change_decision(view.fare_class, view.segment, view.flight)
    alternatives = _alternative_flights(db, view)

    if request.method == "POST" and request.form.get("new_flight_id"):
        if not decision.allowed:
            return render_template(
                "flows/change.html", booking=booking, view=view, decision=decision,
                label=labels.change_label(decision.code), alternatives=alternatives,
                error=labels.change_label(decision.code),
            ), 409
        return _request_change(db, booking, view, decision,
                               row_id(request.form.get("new_flight_id")))

    return render_template(
        "flows/change.html", booking=booking, view=view, decision=decision,
        label=labels.change_label(decision.code), alternatives=alternatives, error=None,
    )


def _alternative_flights(db, view, span: int = 14):
    from datetime import timedelta

    flights = db.scalars(
        select(Flight)
        .where(Flight.route_id == view.flight.route_id)
        .where(Flight.date >= view.flight.date - timedelta(days=span // 2))
        .where(Flight.date <= view.flight.date + timedelta(days=span))
        .where(Flight.id != view.flight.id)
        .where(Flight.status != "cancelled")
        .order_by(Flight.date, Flight.dep_time)
    ).all()

    out = []
    for flight in flights:
        fare = db.scalars(select(Fare).where(
            Fare.flight_id == flight.id,
            Fare.fare_class_id == view.segment.fare_class_id,
            Fare.seats_available > 0,
        )).one_or_none()
        if fare is not None:
            out.append({"flight": flight, "fare": fare})
    return out


def _request_change(db, booking, view, decision, new_flight_id: int | None):
    chosen = next((a for a in _alternative_flights(db, view)
                   if a["flight"].id == new_flight_id), None)
    if chosen is None:
        abort(404)

    current = db.scalars(select(Fare).where(
        Fare.flight_id == view.flight.id,
        Fare.fare_class_id == view.segment.fare_class_id,
    )).one_or_none()
    old_price = current.price_usd if current else 0.0
    difference = round(max(0.0, chosen["fare"].price_usd - old_price), 2)
    fee = decision.detail["fee_usd"]

    db.add(ChangeRequest(
        booking_id=booking.id, segment_id=view.segment.id,
        new_flight_id=chosen["flight"].id,
        reference_no=references.next_reference(db, "change", ChangeRequest.reference_no),
        status="pending", created_at=now().replace(tzinfo=None), is_paid=False,
        eligibility_reason=None,
        fare_difference_usd=difference, change_fee_usd=fee,
        total_due_usd=round(difference + fee, 2),
    ))
    db.commit()
    return redirect(f"{path('change_review', pnr=booking.pnr)}?segment_id={view.segment.id}")


@bp.route(SLUGS["change_review"], methods=["GET", "POST"])
def change_review(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)

    db = database.session()
    view = _segment_view(booking, row_id(request.values.get("segment_id")))
    record = db.scalars(select(ChangeRequest)
                        .where(ChangeRequest.booking_id == booking.id)
                        .order_by(ChangeRequest.id.desc())).first()
    if view is None or record is None:
        abort(404)

    new_flight = db.get(Flight, record.new_flight_id)
    lines = [
        {"label": t("change.fare_difference"), "detail": new_flight.flight_no,
         "amount": record.fare_difference_usd},
        {"label": t("change.change_fee"), "detail": "", "amount": record.change_fee_usd},
    ]
    return render_template(
        "flows/review.html", booking=booking, view=view,
        heading=t("change.review_title"), lines=lines,
        total=record.total_due_usd, reference=record.reference_no,
        notice=_paid_notice(),
        back_url=f"{path('change', pnr=booking.pnr)}?segment_id={view.segment.id}",
    )


@bp.route(SLUGS["refund"], methods=["GET", "POST"])
def refund(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)

    db = database.session()
    views = booking_service.itinerary(db, booking)
    decision = eligibility.refund_decision(booking, views[0].fare_class)

    if request.method == "POST" and request.form.get("confirm"):
        if not decision.allowed:
            return render_template(
                "flows/refund.html", booking=booking, view=views[0], decision=decision,
                label=labels.refund_label(decision.code), error=labels.refund_label(decision.code),
            ), 409
        db.add(RefundRequest(
            booking_id=booking.id,
            reference_no=references.next_reference(db, "refund", RefundRequest.reference_no),
            status="pending", created_at=now().replace(tzinfo=None), is_paid=False,
            eligibility_reason=None,
            refund_pct=decision.detail["refund_pct"],
            gross_usd=decision.detail["gross_usd"],
            fee_usd=decision.detail["fee_usd"],
            quoted_amount_usd=decision.detail["quoted_usd"],
        ))
        db.commit()
        return redirect(path("refund_review", pnr=booking.pnr))

    return render_template(
        "flows/refund.html", booking=booking, view=views[0], decision=decision,
        label=labels.refund_label(decision.code), error=None,
    )


@bp.route(SLUGS["refund_review"], methods=["GET", "POST"])
def refund_review(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)

    db = database.session()
    record = db.scalars(select(RefundRequest)
                        .where(RefundRequest.booking_id == booking.id)
                        .order_by(RefundRequest.id.desc())).first()
    if record is None:
        abort(404)

    views = booking_service.itinerary(db, booking)
    lines = [
        {"label": t("refund.gross"), "detail": "", "amount": record.gross_usd},
        {"label": t("refund.percentage", pct=record.refund_pct), "detail": "",
         "amount": round(record.gross_usd * record.refund_pct / 100.0, 2)},
        {"label": t("refund.fee"), "detail": "", "amount": -record.fee_usd},
    ]
    return render_template(
        "flows/review.html", booking=booking, view=views[0],
        heading=t("refund.review_title"), lines=lines,
        total=record.quoted_amount_usd, reference=record.reference_no,
        notice=_paid_notice(), is_refund=True,
        back_url=path("refund", pnr=booking.pnr),
    )


@bp.route(SLUGS["upgrade"], methods=["GET", "POST"])
def upgrade(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)

    db = database.session()
    view = _segment_view(booking, row_id(request.values.get("segment_id")))
    if view is None:
        abort(404)

    business = booking_service.business_fares(db, view.flight.id)
    decision = eligibility.upgrade_decision(view.fare_class, business)

    if request.method == "POST" and request.form.get("confirm"):
        if not decision.allowed:
            return render_template(
                "flows/upgrade.html", booking=booking, view=view, decision=decision,
                label=labels.upgrade_label(decision.code),
                error=labels.upgrade_label(decision.code),
            ), 409
        db.add(UpgradePurchase(
            booking_id=booking.id, segment_id=view.segment.id,
            reference_no=references.next_reference(db, "upgrade", UpgradePurchase.reference_no),
            status="pending", created_at=now().replace(tzinfo=None), is_paid=False,
            target_fare_class_id=decision.detail["fare_class_id"],
            price_usd=decision.detail["price_usd"],
        ))
        db.commit()
        return redirect(f"{path('upgrade_review', pnr=booking.pnr)}?segment_id={view.segment.id}")

    return render_template(
        "flows/upgrade.html", booking=booking, view=view, decision=decision,
        label=labels.upgrade_label(decision.code), error=None,
    )


@bp.route(SLUGS["upgrade_review"], methods=["GET", "POST"])
def upgrade_review(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)

    db = database.session()
    view = _segment_view(booking, row_id(request.values.get("segment_id")))
    record = db.scalars(select(UpgradePurchase)
                        .where(UpgradePurchase.booking_id == booking.id)
                        .order_by(UpgradePurchase.id.desc())).first()
    if view is None or record is None:
        abort(404)

    target = db.get(FareClass, record.target_fare_class_id)
    lines = [{"label": t("upgrade.to_cabin"), "detail": target.name, "amount": record.price_usd}]
    return render_template(
        "flows/review.html", booking=booking, view=view,
        heading=t("upgrade.review_title"), lines=lines,
        total=record.price_usd, reference=record.reference_no,
        notice=_paid_notice(),
        back_url=f"{path('upgrade', pnr=booking.pnr)}?segment_id={view.segment.id}",
    )


@bp.route(SLUGS["bag_add"], methods=["GET", "POST"])
def baggage(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)

    db = database.session()
    view = _segment_view(booking, row_id(request.values.get("segment_id")))
    if view is None:
        abort(404)

    rule = baggage_service.rule_for_route(db, view.route, view.fare_class.cabin, "adult")

    if request.method == "POST" and request.form.get("extra_kg"):
        extra_kg = max(0, min(60, bounded_int(request.form.get("extra_kg"), low=0, high=60, default=0) or 0))
        if extra_kg == 0 or rule is None:
            return render_template(
                "flows/baggage.html", booking=booking, view=view, rule=rule,
                error=t("baggage.choose_amount"),
            ), 400
        db.add(BaggagePurchase(
            booking_id=booking.id, segment_id=view.segment.id,
            reference_no=references.next_reference(db, "baggage", BaggagePurchase.reference_no),
            status="pending", created_at=now().replace(tzinfo=None), is_paid=False,
            extra_kg=extra_kg, extra_pieces=0,
            price_usd=baggage_service.quote_extra(rule, extra_kg),
        ))
        db.commit()
        return redirect(f"{path('bag_review', pnr=booking.pnr)}?segment_id={view.segment.id}")

    return render_template(
        "flows/baggage.html", booking=booking, view=view, rule=rule, error=None,
    )


@bp.route(SLUGS["bag_review"], methods=["GET", "POST"])
def baggage_review(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)

    db = database.session()
    view = _segment_view(booking, row_id(request.values.get("segment_id")))
    record = db.scalars(select(BaggagePurchase)
                        .where(BaggagePurchase.booking_id == booking.id)
                        .order_by(BaggagePurchase.id.desc())).first()
    if view is None or record is None:
        abort(404)

    lines = [{"label": t("baggage.extra_checked"),
              "detail": t("manage.kg", n=record.extra_kg),
              "amount": record.price_usd}]
    return render_template(
        "flows/review.html", booking=booking, view=view,
        heading=t("baggage.review_title"), lines=lines,
        total=record.price_usd, reference=record.reference_no,
        notice=_paid_notice(),
        back_url=f"{path('bag_add', pnr=booking.pnr)}?segment_id={view.segment.id}",
    )


@bp.route(SLUGS["manage_receipt"])
def receipt(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)
    db = database.session()
    views = booking_service.itinerary(db, booking)
    lines = []
    for view in views:
        fare = db.scalars(select(Fare).where(
            Fare.flight_id == view.flight.id,
            Fare.fare_class_id == view.segment.fare_class_id)).one_or_none()
        lines.append({"view": view,
                      "fare": fare.price_usd if fare else 0.0,
                      "taxes": fare.taxes_usd if fare else 0.0})
    return render_template("flows/receipt.html", booking=booking, lines=lines,
                           passengers=len(booking.passengers))


@bp.route(SLUGS["seats_legend"])
def seats_legend(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)
    return render_template("flows/seats_legend.html", booking=booking)


@bp.route(SLUGS["manage_contact"], methods=["GET", "POST"])
def contact_details(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)
    db = database.session()

    errors, saved = {}, False
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        if "@" not in email or "." not in email.split("@")[-1]:
            errors["email"] = t("book.error_email")
        if len(phone) < 6:
            errors["phone"] = t("book.error_phone")
        if not errors:
            booking.email, booking.phone = email, phone
            db.commit()
            saved = True

    return render_template("flows/contact_details.html", booking=booking,
                           errors=errors, saved=saved)


@bp.route(SLUGS["manage_cancel"], methods=["GET", "POST"])
def cancel(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)
    db = database.session()
    views = booking_service.itinerary(db, booking)
    refund = eligibility.refund_decision(booking, views[0].fare_class)

    cancelled = False
    if request.method == "POST" and request.form.get("confirm") == "yes":
        booking.status = "cancelled"
        db.commit()
        cancelled = True

    return render_template("flows/cancel.html", booking=booking, refund=refund,
                           refund_label=labels.refund_label(refund.code),
                           cancelled=cancelled)


@bp.route(SLUGS["change_route"], methods=["GET", "POST"])
def change_route(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)
    db = database.session()
    view = _segment_view(booking, row_id(request.values.get("segment_id")))
    if view is None:
        abort(404)
    decision = eligibility.change_decision(view.fare_class, view.segment, view.flight)
    return render_template("flows/change_route.html", booking=booking, view=view,
                           decision=decision,
                           label=labels.change_label(decision.code),
                           rerouting_fee=180.0)


@bp.route(SLUGS["change_same_day"])
def change_same_day(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)
    db = database.session()
    view = _segment_view(booking, row_id(request.values.get("segment_id")))
    if view is None:
        abort(404)
    from ..clock import hours_until
    from ..services.eligibility import departure_of

    hours = hours_until(departure_of(view.segment, view.flight))
    return render_template("flows/change_same_day.html", booking=booking, view=view,
                           hours=round(hours, 1), eligible=0 < hours <= 24,
                           fee=75.0)


@bp.route(SLUGS["bag_bundles"], methods=["GET", "POST"])
def baggage_bundles(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)
    db = database.session()
    view = _segment_view(booking, row_id(request.values.get("segment_id")))
    if view is None:
        abort(404)
    rule = baggage_service.rule_for_route(db, view.route, view.fare_class.cabin, "adult")
    bundles = [
        {"kg": 20, "price": round(rule.extra_kg_price_usd * 20 * 0.80, 2)},
        {"kg": 40, "price": round(rule.extra_kg_price_usd * 40 * 0.70, 2)},
        {"kg": 60, "price": round(rule.extra_kg_price_usd * 60 * 0.65, 2)},
    ] if rule else []
    return render_template("flows/baggage_bundles.html", booking=booking, view=view,
                           bundles=bundles, rule=rule)


@bp.route(SLUGS["upgrade_bid"], methods=["GET", "POST"])
def upgrade_bid(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)
    db = database.session()
    view = _segment_view(booking, row_id(request.values.get("segment_id")))
    if view is None:
        abort(404)
    business = booking_service.business_fares(db, view.flight.id)
    offer = eligibility.upgrade_decision(view.fare_class, business)
    floor = round((offer.detail.get("price_usd", 0) or 0) * 0.4, 2) if offer.allowed else 0

    record = error = None
    if request.method == "POST" and offer.allowed:
        amount = bounded_int(request.form.get("amount"), low=0, high=5000, default=0)
        if amount < floor:
            error = t("upgrade.bid_too_low", n=int(floor))
        else:
            from ..models.requests import ServiceRequest
            import json as _json

            record = ServiceRequest(
                kind="upgrade_bid",
                reference_no=references.next_reference(db, "upgrade_bid",
                                                       ServiceRequest.reference_no),
                status="pending", created_at=now().replace(tzinfo=None),
                payload=_json.dumps({"pnr": booking.pnr, "segment_id": view.segment.id,
                                     "amount": amount}),
                quoted_usd=float(amount))
            db.add(record)
            db.commit()

    return render_template("flows/upgrade_bid.html", booking=booking, view=view,
                           offer=offer, label=labels.upgrade_label(offer.code),
                           floor=floor, record=record, error=error)


@bp.route(SLUGS["upgrade_miles"])
def upgrade_with_miles(pnr: str):
    g.nav_section = "manage"
    booking = _authorised(pnr)
    if booking is None:
        return _reauth(pnr)
    db = database.session()
    view = _segment_view(booking, row_id(request.values.get("segment_id")))
    if view is None:
        abort(404)
    business = booking_service.business_fares(db, view.flight.id)
    offer = eligibility.upgrade_decision(view.fare_class, business)
    miles = int((offer.detail.get("price_usd", 0) or 0) * 120) if offer.allowed else 0
    return render_template("flows/upgrade_miles.html", booking=booking, view=view,
                           offer=offer, label=labels.upgrade_label(offer.code),
                           miles=miles)


@bp.route(SLUGS["refund_status"])
def refund_status():
    g.nav_section = "manage"
    db = database.session()
    reference = (request.args.get("reference") or "").strip().upper()
    record = None
    if reference:
        record = db.scalars(select(RefundRequest).where(
            RefundRequest.reference_no == reference)).one_or_none()
    return render_template("flows/refund_status.html", reference=reference,
                           record=record, searched=bool(reference))
