from __future__ import annotations

from datetime import date, datetime

from flask import Blueprint, abort, g, redirect, render_template, request
from sqlalchemy import select

from .. import db as database
from ..clock import WINDOW_END, WINDOW_START, now, today
from ..i18n import t
from ..params import bounded_int, row_id
from ..routes_map import SLUGS, path
from ..services import search as search_service

bp = Blueprint("booking", __name__)

CABINS = ("economy", "business")
MAX_ADULTS = 9


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        parsed = datetime.strptime(raw.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None
    return parsed if WINDOW_START <= parsed <= WINDOW_END else None


@bp.route(SLUGS["search"])
def search_form():
    g.nav_section = "book"
    return render_template(
        "booking/search.html",
        window_start=WINDOW_START,
        window_end=WINDOW_END,
        today=today(),
    )


@bp.route(SLUGS["results"])
def results():
    g.nav_section = "book"
    origin = (request.args.get("origin") or "").strip().upper()[:3]
    destination = (request.args.get("destination") or "").strip().upper()[:3]
    depart = _parse_date(request.args.get("depart"))
    return_on = _parse_date(request.args.get("return"))
    cabin = request.args.get("cabin") if request.args.get("cabin") in CABINS else None
    sort = request.args.get("sort", "price")
    stops = request.args.get("stops")
    band = request.args.get("depart_band")

    try:
        adults = max(1, min(9, int(request.args.get("adults", 1))))
    except ValueError:
        adults = 1

    if not (origin and destination and depart):
        return redirect(path("search"))

    session = database.session()
    outbound = search_service.search(session, origin, destination, depart, cabin)
    inbound = (
        search_service.search(session, destination, origin, return_on, cabin)
        if return_on else []
    )

    return render_template(
        "booking/results.html",
        origin=origin,
        destination=destination,
        depart=depart,
        return_on=return_on,
        adults=adults,
        cabin=cabin,
        sort=sort,
        stops=stops,
        band=band,
        outbound=search_service.apply_filters(outbound, stops, band, sort),
        inbound=search_service.apply_filters(inbound, stops, band, sort),
        outbound_alternatives=(
            search_service.nearby_dates(session, origin, destination, depart)
            if not outbound else []
        ),
        inbound_alternatives=(
            search_service.nearby_dates(session, destination, origin, return_on)
            if return_on and not inbound else []
        ),
        sort_options=[
            (key, label) for key, label in (
                ("price", t("results.sort_price")),
                ("duration", t("results.sort_duration")),
                ("departure", t("results.sort_departure")),
                ("arrival", t("results.sort_arrival")),
            )
        ],
        stop_options=[
            ("", t("results.stops_any")),
            ("nonstop", t("results.stops_nonstop")),
            ("onestop", t("results.stops_onestop")),
        ],
        band_options=[
            ("", t("results.band_any")),
            ("early", t("results.band_early")),
            ("morning", t("results.band_morning")),
            ("afternoon", t("results.band_afternoon")),
            ("evening", t("results.band_evening")),
        ],
    )


def _parse_itinerary(key: str):
    legs = []
    for part in (key or "").split("-"):
        if "." not in part:
            return None
        flight_id, fare_class_id = part.split(".", 1)
        flight, fare = row_id(flight_id), row_id(fare_class_id)
        if flight is None or fare is None:
            return None
        legs.append((flight, fare))
    return legs or None


def _price_legs(session, legs):
    from ..models.network import Fare, Flight

    priced = []
    for flight_id, fare_class_id in legs:
        flight = session.get(Flight, flight_id)
        fare = session.scalars(select(Fare).where(
            Fare.flight_id == flight_id, Fare.fare_class_id == fare_class_id)).one_or_none()
        if flight is None or fare is None:
            return None
        priced.append((flight, fare))
    return priced


@bp.route(SLUGS["passengers"], methods=["GET", "POST"])
def passengers():
    g.nav_section = "book"
    db = database.session()
    legs = _parse_itinerary(request.values.get("itinerary", ""))
    priced = _price_legs(db, legs) if legs else None
    if priced is None:
        return redirect(path("search"))

    try:
        adults = max(1, min(MAX_ADULTS, int(request.values.get("adults", 1))))
    except ValueError:
        adults = 1

    views = _leg_views(db, priced)
    errors, values = {}, {}

    if request.method == "POST":
        values = {k: (request.form.get(k) or "").strip() for k in request.form}
        errors = _validate_passengers(values, adults)
        if not errors:
            draft = _create_draft(db, priced, adults, values)
            return redirect(f"{path('book_review')}?ref={draft.reference}")

    return render_template("booking/passengers.html", views=views, adults=adults,
                           itinerary=request.values.get("itinerary", ""),
                           errors=errors, values=values,
                           total=sum(f.price_usd + f.taxes_usd for _, f in priced) * adults)


def _leg_views(db, priced):
    from ..models.network import Airport, FareClass, Route

    views = []
    for flight, fare in priced:
        route = db.get(Route, flight.route_id)
        views.append({
            "flight": flight,
            "fare": fare,
            "fare_class": db.get(FareClass, fare.fare_class_id),
            "origin": db.get(Airport, route.origin_id),
            "destination": db.get(Airport, route.destination_id),
        })
    return views


def _validate_passengers(values: dict, adults: int) -> dict:
    errors = {}
    for index in range(1, adults + 1):
        if not values.get(f"first_name_{index}"):
            errors[f"first_name_{index}"] = t("book.error_required")
        if not values.get(f"last_name_{index}"):
            errors[f"last_name_{index}"] = t("book.error_required")
    email = values.get("contact_email", "")
    if "@" not in email or "." not in email.split("@")[-1]:
        errors["contact_email"] = t("book.error_email")
    if len(values.get("contact_phone", "")) < 6:
        errors["contact_phone"] = t("book.error_phone")
    return errors


def _create_draft(db, priced, adults: int, values: dict):
    from ..clock import now
    from ..models.draft import DraftBooking, DraftPassenger
    from ..services import references

    outbound_flight, outbound_fare = priced[0]
    draft = DraftBooking(
        reference=references.draft_reference(db, DraftBooking.reference),
        flight_id=outbound_flight.id,
        fare_class_id=outbound_fare.fare_class_id,
        return_flight_id=priced[1][0].id if len(priced) > 1 else None,
        adults=adults,
        contact_email=values.get("contact_email", ""),
        contact_phone=values.get("contact_phone", ""),
        price_usd=round(sum(f.price_usd for _, f in priced) * adults, 2),
        taxes_usd=round(sum(f.taxes_usd for _, f in priced) * adults, 2),
        created_at=now().replace(tzinfo=None),
        is_paid=False,
    )
    db.add(draft)
    db.flush()
    for index in range(1, adults + 1):
        db.add(DraftPassenger(
            draft_id=draft.id,
            first_name=values.get(f"first_name_{index}", ""),
            last_name=values.get(f"last_name_{index}", ""),
            pax_type="adult",
        ))
    db.commit()
    return draft


@bp.route(SLUGS["book_review"], methods=["GET", "POST"])
def review():
    g.nav_section = "book"
    db = database.session()
    from ..models.draft import DraftBooking

    reference = (request.values.get("ref") or "").strip().upper()
    draft = db.scalars(
        select(DraftBooking).where(DraftBooking.reference == reference)).one_or_none()
    if draft is None:
        draft = db.scalars(select(DraftBooking).order_by(DraftBooking.id.desc())).first()
    if draft is None:
        return redirect(path("search"))

    from ..models.network import Fare
    legs = [(draft.flight_id, draft.fare_class_id)]
    if draft.return_flight_id:
        legs.append((draft.return_flight_id, draft.fare_class_id))
    priced = _price_legs(db, legs)
    if priced is None:
        return redirect(path("search"))

    notice = (t("review.payment_disabled")
              if request.method == "POST" and request.form.get("action") == "pay" else None)

    return render_template("booking/review.html", draft=draft,
                           views=_leg_views(db, priced), notice=notice)


@bp.route(SLUGS["multi_city"])
def multi_city():
    g.nav_section = "book"
    db = database.session()
    legs, results = [], []
    for index in (1, 2, 3, 4):
        origin = (request.args.get(f"origin_{index}") or "").strip().upper()[:3]
        destination = (request.args.get(f"destination_{index}") or "").strip().upper()[:3]
        day = _parse_date(request.args.get(f"date_{index}"))
        legs.append({"index": index, "origin": origin, "destination": destination,
                     "date": request.args.get(f"date_{index}", "")})
        if origin and destination and day:
            found = search_service.search(db, origin, destination, day)
            results.append({"leg": index, "origin": origin, "destination": destination,
                            "day": day,
                            "options": search_service.apply_filters(found, sort="price")[:5]})

    total = sum(min((o.total_usd for o in r["options"]), default=0) for r in results)
    return render_template("booking/multi_city.html", legs=legs, results=results,
                           total=total, searched=bool(results))


@bp.route(SLUGS["flexible_dates"])
def flexible_dates():
    g.nav_section = "book"
    db = database.session()
    origin = (request.args.get("origin") or "").strip().upper()[:3]
    destination = (request.args.get("destination") or "").strip().upper()[:3]
    day = _parse_date(request.args.get("depart"))

    rows = []
    if origin and destination and day:
        from datetime import timedelta

        from ..clock import WINDOW_END, WINDOW_START
        for offset in range(-3, 4):
            candidate = day + timedelta(days=offset)
            if not (WINDOW_START <= candidate <= WINDOW_END):
                continue
            found = search_service.search(db, origin, destination, candidate)
            rows.append({"day": candidate,
                         "cheapest": min((f.total_usd for f in found), default=None),
                         "count": len(found), "is_chosen": offset == 0})

    return render_template("booking/flexible_dates.html", origin=origin,
                           destination=destination,
                           date_value=request.args.get("depart", ""), rows=rows,
                           searched=bool(origin and destination and day))


@bp.route(SLUGS["fare_rules"])
def fare_rules(fare_class: str):
    g.nav_section = "book"
    db = database.session()
    from ..models.network import FareClass

    entry = db.scalars(select(FareClass).where(
        FareClass.code == fare_class.upper())).one_or_none()
    if entry is None:
        abort(404)
    others = list(db.scalars(select(FareClass).order_by(FareClass.id)))
    return render_template("booking/fare_rules.html", entry=entry, others=others)


@bp.route(SLUGS["promo_code"], methods=["GET", "POST"])
def promo_code():
    g.nav_section = "book"
    codes = {
        "SELAM10": ("valid", t("promo.valid", pct=10)),
        "HIGHLAND25": ("route", t("promo.wrong_route")),
        "SUMMER24": ("expired", t("promo.expired")),
        "WELCOME": ("used", t("promo.already_used")),
    }
    entered = (request.values.get("code") or "").strip().upper()
    outcome = codes.get(entered) if entered else None
    return render_template("booking/promo_code.html", entered=entered,
                           outcome=outcome, unknown=bool(entered and outcome is None))


@bp.route(SLUGS["hold"], methods=["GET", "POST"])
def hold():
    g.nav_section = "book"
    db = database.session()
    from datetime import timedelta

    from ..models.requests import ServiceRequest

    legs = _parse_itinerary(request.values.get("itinerary", ""))
    priced = _price_legs(db, legs) if legs else None
    record = None

    if request.method == "POST" and priced:
        import json as _json

        from ..services import references

        record = ServiceRequest(
            kind="hold",
            reference_no=references.next_reference(db, "hold", ServiceRequest.reference_no),
            status="held", created_at=now().replace(tzinfo=None),
            payload=_json.dumps({"itinerary": request.form.get("itinerary", "")}),
            quoted_usd=round(sum(f.price_usd + f.taxes_usd for _, f in priced), 2))
        db.add(record)
        db.commit()

    return render_template("booking/hold.html",
                           views=_leg_views(db, priced) if priced else [],
                           itinerary=request.values.get("itinerary", ""),
                           record=record, expires=now().replace(tzinfo=None) + timedelta(hours=48),
                           total=sum(f.price_usd + f.taxes_usd for _, f in priced) if priced else 0)


@bp.route(SLUGS["book_seats"])
def book_seats():
    g.nav_section = "book"
    db = database.session()
    legs = _parse_itinerary(request.values.get("itinerary", ""))
    priced = _price_legs(db, legs) if legs else None
    if priced is None:
        return redirect(path("search"))
    return render_template("booking/book_seats.html", views=_leg_views(db, priced),
                           itinerary=request.values.get("itinerary", ""))


@bp.route(SLUGS["book_extras"])
def book_extras():
    g.nav_section = "book"
    db = database.session()
    legs = _parse_itinerary(request.values.get("itinerary", ""))
    priced = _price_legs(db, legs) if legs else None
    if priced is None:
        return redirect(path("search"))
    extras = [
        {"title": t("extras.baggage"), "body": t("extras.baggage_body"),
         "url": path("bag_allowance")},
        {"title": t("extras.seats"), "body": t("extras.seats_body"),
         "url": f"{path('book_seats')}?itinerary={request.values.get('itinerary', '')}"},
        {"title": t("extras.lounge"), "body": t("extras.lounge_body"),
         "url": path("lounges")},
        {"title": t("extras.insurance"), "body": t("extras.insurance_body"),
         "url": path("partner_insurance")},
    ]
    return render_template("booking/book_extras.html", views=_leg_views(db, priced),
                           extras=extras,
                           itinerary=request.values.get("itinerary", ""))
