from __future__ import annotations

from datetime import datetime

from flask import (
    Blueprint, abort, g, redirect, render_template, request,
    session as flask_session,
)
from sqlalchemy import select

from .. import db as database
from ..clock import WINDOW_END, WINDOW_START, now
from ..i18n import t
from ..models.network import Flight
from ..models.onboard import MealRequest, WifiPackage, WifiPurchase
from ..params import bounded_int, get_row, row_id
from ..routes_map import SLUGS, path
from ..services import bookings as booking_service
from ..services import onboard as onboard_service
from ..services import references

bp = Blueprint("onboard", __name__)


def _find_flight(flight_no: str, raw_date: str) -> Flight | None:
    if not flight_no or not raw_date:
        return None
    try:
        day = datetime.strptime(raw_date.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None
    if not WINDOW_START <= day <= WINDOW_END:
        return None
    cleaned = "".join(flight_no.split()).upper()
    return database.session().scalars(
        select(Flight).where(Flight.flight_no == cleaned, Flight.date == day)
    ).one_or_none()


@bp.route(SLUGS["wifi"], methods=["GET", "POST"])
def wifi():
    g.nav_section = "help"
    db = database.session()
    flight_no = (request.values.get("flight_no") or "").strip()
    date_value = (request.values.get("date") or "").strip()
    flight = _find_flight(flight_no, date_value)

    packages = onboard_service.packages_for(db, flight) if flight else []
    searched = bool(flight_no and date_value)

    if request.method == "POST" and request.form.get("package_id"):
        package = get_row(db, WifiPackage, request.form.get("package_id"))
        if package is None:
            abort(404)
        if flight is None or package.flight_id != flight.id:
            abort(404)
        db.add(WifiPurchase(
            package_id=package.id, booking_id=None,
            reference_no=references.next_reference(db, "wifi", WifiPurchase.reference_no),
            status="pending", created_at=now().replace(tzinfo=None),
            price_usd=package.price_usd, is_paid=False,
        ))
        db.commit()
        flask_session["wifi_flight"] = f"{flight.flight_no}|{flight.date.isoformat()}"
        return redirect(path("wifi_review"))

    return render_template(
        "onboard/wifi.html", flight=flight, packages=packages, searched=searched,
        flight_no=flight_no, date_value=date_value,
        not_equipped=bool(flight and not flight.wifi_equipped),
    )


@bp.route(SLUGS["wifi_review"], methods=["GET", "POST"])
def wifi_review():
    g.nav_section = "help"
    db = database.session()
    record = db.scalars(select(WifiPurchase).order_by(WifiPurchase.id.desc())).first()
    if record is None:
        abort(404)
    package = db.get(WifiPackage, record.package_id)
    flight = db.get(Flight, package.flight_id)

    notice = (t("review.payment_disabled")
              if request.method == "POST" and request.form.get("action") == "pay" else None)
    return render_template("onboard/wifi_review.html", record=record, package=package,
                           flight=flight, notice=notice)


@bp.route(SLUGS["wifi_coverage"])
def wifi_coverage():
    g.nav_section = "help"
    db = database.session()
    from ..models.network import Aircraft

    rows = list(db.scalars(select(Aircraft).order_by(Aircraft.id)))
    return render_template("onboard/coverage.html", aircraft=rows)


@bp.route(SLUGS["dining"], methods=["GET", "POST"])
def dining():
    g.nav_section = "help"
    db = database.session()
    pnr = (request.values.get("pnr") or "").strip()
    known = {p.upper() for p in flask_session.get("retrieved_pnrs", [])}

    booking = booking_service.by_pnr(db, pnr) if pnr else None
    if booking is not None and booking.pnr.upper() not in known:
        booking = None

    views = booking_service.itinerary(db, booking) if booking else []
    menu = onboard_service.menu_for(db, views[0].flight, views[0].fare_class.cabin) if views else None
    codes = onboard_service.meal_codes(db)

    error = requested = None
    if request.method == "POST" and booking is not None and request.form.get("meal_code"):
        code = onboard_service.meal_code(db, request.form["meal_code"])
        passenger_id = row_id(request.form.get("passenger_id"))
        passenger = next((p for p in booking.passengers if p.id == passenger_id),
                         next((p for p in booking.passengers if p.pax_type != "infant"), None))
        if code is None or passenger is None:
            error = t("dining.unknown_code")
        else:
            existing = db.scalars(select(MealRequest).where(
                MealRequest.segment_id == views[0].segment.id,
                MealRequest.passenger_id == passenger.id)).one_or_none()
            if existing is not None:
                existing.meal_code = code.code
                existing.created_at = now().replace(tzinfo=None)
            else:
                db.add(MealRequest(
                    segment_id=views[0].segment.id, passenger_id=passenger.id,
                    meal_code=code.code, created_at=now().replace(tzinfo=None),
                    status="requested"))
            db.commit()
            requested = code

    return render_template("onboard/dining.html", booking=booking, pnr=pnr,
                           view=views[0] if views else None, menu=menu, codes=codes,
                           error=error, requested=requested)


@bp.route(SLUGS["dining_special"])
def special_meals():
    g.nav_section = "help"
    return render_template("onboard/special_meals.html",
                           codes=onboard_service.meal_codes(database.session()))
