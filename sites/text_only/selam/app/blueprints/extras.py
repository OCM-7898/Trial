from __future__ import annotations

import json
from datetime import timedelta

from flask import Blueprint, abort, g, render_template, request
from sqlalchemy import func, select

from .. import db as database
from ..clock import WINDOW_END, WINDOW_START, now, today
from ..i18n import labels, t
from ..models.content import (
    ContactOffice, EntertainmentItem, Promotion, TravelRequirement,
)
from ..models.network import Airport, Flight, Route
from ..models.onboard import MealMenu
from ..params import bounded_int, get_row
from ..routes_map import SLUGS, path
from ..services import onboard as onboard_service
from ..services import references, search as search_service

bp = Blueprint("extras", __name__)


def _promotion_state(promotion) -> str:
    if promotion.valid_to < today():
        return "expired"
    if promotion.valid_from > today():
        return "upcoming"
    return "live"


@bp.route(SLUGS["offers"])
def offers():
    g.nav_section = "book"
    db = database.session()
    rows = [{"promotion": p, "state": _promotion_state(p),
             "region": labels.region_label(p.region)}
            for p in db.scalars(select(Promotion).order_by(Promotion.id))]
    return render_template("extras/offers.html", rows=rows,
                           live=[r for r in rows if r["state"] == "live"],
                           other=[r for r in rows if r["state"] != "live"])


@bp.route(SLUGS["offer_detail"])
def offer_detail(offer_id: str):
    g.nav_section = "book"
    db = database.session()
    promotion = get_row(db, Promotion, offer_id)
    if promotion is None:
        return _offer_by_code(db, offer_id)
    return render_template("extras/offer_detail.html", promotion=promotion,
                           state=_promotion_state(promotion),
                           region=labels.region_label(promotion.region))


def _offer_by_code(db, code: str):
    promotion = db.scalars(
        select(Promotion).where(Promotion.code == code.upper())).one_or_none()
    if promotion is None:
        abort(404)
    return render_template("extras/offer_detail.html", promotion=promotion,
                           state=_promotion_state(promotion),
                           region=labels.region_label(promotion.region))


@bp.route(SLUGS["fare_calendar"])
def fare_calendar():
    g.nav_section = "book"
    db = database.session()
    origin = (request.args.get("origin") or "").strip().upper()[:3]
    destination = (request.args.get("destination") or "").strip().upper()[:3]

    rows = []
    if origin and destination:
        start = today()
        for offset in range(0, 30):
            day = start + timedelta(days=offset)
            if not (WINDOW_START <= day <= WINDOW_END):
                continue
            found = search_service.search(db, origin, destination, day, max_stops=0)
            rows.append({"day": day,
                         "cheapest": min((f.total_usd for f in found), default=None)})

    priced = [r["cheapest"] for r in rows if r["cheapest"]]
    return render_template("extras/fare_calendar.html", origin=origin,
                           destination=destination, rows=rows,
                           best=min(priced) if priced else None,
                           searched=bool(origin and destination))


@bp.route(SLUGS["destination"])
def destination(city: str):
    g.nav_section = "book"
    db = database.session()
    airport = db.scalars(
        select(Airport).where(func.upper(Airport.iata) == city.upper())).one_or_none()
    if airport is None:
        abort(404)

    routes = db.scalars(select(Route).where(Route.destination_id == airport.id)).all()
    origins = [db.get(Airport, r.origin_id) for r in routes]
    office = db.scalars(select(ContactOffice).where(
        ContactOffice.country_code == airport.country_code)).one_or_none()
    requirement = db.scalars(select(TravelRequirement).where(
        TravelRequirement.country_code == airport.country_code)).one_or_none()

    return render_template("extras/destination.html", airport=airport,
                           origins=origins, office=office, requirement=requirement)


@bp.route(SLUGS["destination_things"])
def destination_attractions(city: str):
    g.nav_section = "book"
    db = database.session()
    airport = db.scalars(
        select(Airport).where(func.upper(Airport.iata) == city.upper())).one_or_none()
    if airport is None:
        abort(404)
    return render_template("extras/attractions.html", airport=airport)


@bp.route(SLUGS["entertainment"])
def entertainment():
    g.nav_section = "help"
    db = database.session()
    counts = dict(db.execute(
        select(EntertainmentItem.category, func.count(EntertainmentItem.id))
        .group_by(EntertainmentItem.category)).all())
    return render_template("extras/entertainment.html", counts=counts)


@bp.route(SLUGS["entertainment_cat"])
def entertainment_catalog():
    g.nav_section = "help"
    db = database.session()
    query = (request.args.get("q") or "").strip()
    category = request.args.get("category")
    if category not in ("film", "series", "music"):
        category = None

    stmt = select(EntertainmentItem).order_by(EntertainmentItem.category,
                                              EntertainmentItem.id)
    if category:
        stmt = stmt.where(EntertainmentItem.category == category)
    rows = list(db.scalars(stmt))
    if query:
        needle = query.lower()
        rows = [r for r in rows
                if needle in r.title.lower() or needle in r.genre.lower()
                or needle in r.language.lower()]

    return render_template("extras/catalog.html", rows=rows, query=query,
                           category=category,
                           categories=[("film", t("entertainment.films")),
                                       ("series", t("entertainment.series")),
                                       ("music", t("entertainment.music"))])


@bp.route(SLUGS["dining_menu"])
def dining_menu(flight_no: str):
    g.nav_section = "help"
    db = database.session()
    flight = db.scalars(select(Flight).where(
        Flight.flight_no == "".join(flight_no.split()).upper())
        .order_by(Flight.date)).first()
    if flight is None:
        abort(404)
    menus = [{"cabin": cabin,
              "label": (t("brand.cabin_business") if cabin == "business"
                        else t("brand.cabin_economy")),
              "menu": onboard_service.menu_for(db, flight, cabin)}
             for cabin in ("economy", "business")]
    route = db.get(Route, flight.route_id)
    return render_template("extras/dining_menu.html", flight=flight,
                           origin=db.get(Airport, route.origin_id),
                           destination=db.get(Airport, route.destination_id),
                           menus=[m for m in menus if m["menu"]])


@bp.route(SLUGS["travel_requirements"])
def travel_requirements():
    g.nav_section = "help"
    db = database.session()
    rows = list(db.scalars(select(TravelRequirement).order_by(
        TravelRequirement.country_code)))
    offices = {o.country_code: o for o in db.scalars(select(ContactOffice))}
    return render_template("extras/requirements.html", rows=rows, offices=offices)


@bp.route(SLUGS["travel_req_pair"])
def travel_requirements_pair(origin: str, destination: str):
    g.nav_section = "help"
    db = database.session()
    destination_airport = db.scalars(select(Airport).where(
        func.upper(Airport.iata) == destination.upper())).one_or_none()
    if destination_airport is None:
        abort(404)
    requirement = db.scalars(select(TravelRequirement).where(
        TravelRequirement.country_code == destination_airport.country_code)).one_or_none()
    origin_airport = db.scalars(select(Airport).where(
        func.upper(Airport.iata) == origin.upper())).one_or_none()
    return render_template("extras/requirements_pair.html", origin=origin_airport,
                           destination=destination_airport, requirement=requirement)


@bp.route(SLUGS["vouchers"])
def vouchers():
    g.nav_section = "help"
    return render_template("extras/vouchers.html",
                           amounts=[50, 100, 250, 500])


@bp.route(SLUGS["vouchers_buy"], methods=["GET", "POST"])
def vouchers_buy():
    g.nav_section = "help"
    db = database.session()
    from ..models.requests import ServiceRequest

    amounts = [50, 100, 250, 500]
    record = error = None
    if request.method == "POST":
        amount = bounded_int(request.form.get("amount"), low=0, high=1000, default=0)
        recipient = (request.form.get("recipient") or "").strip()
        if amount not in amounts:
            error = t("voucher.pick_amount")
        elif len(recipient) < 2:
            error = t("voucher.need_recipient")
        else:
            record = ServiceRequest(
                kind="voucher_purchase",
                reference_no=references.next_reference(db, "voucher",
                                                       ServiceRequest.reference_no),
                status="pending", created_at=now().replace(tzinfo=None),
                payload=json.dumps({"recipient": recipient, "amount": amount},
                                   ensure_ascii=False),
                quoted_usd=float(amount))
            db.add(record)
            db.commit()

    return render_template("extras/vouchers_buy.html", amounts=amounts,
                           record=record, error=error)


@bp.route(SLUGS["vouchers_balance"])
def vouchers_balance():
    g.nav_section = "help"
    db = database.session()
    from ..models.requests import ServiceRequest

    reference = (request.args.get("reference") or "").strip().upper()
    record = None
    if reference:
        record = db.scalars(select(ServiceRequest).where(
            func.upper(ServiceRequest.reference_no) == reference,
            ServiceRequest.kind.in_(("voucher", "voucher_purchase")))).one_or_none()
    return render_template("extras/vouchers_balance.html", reference=reference,
                           record=record, searched=bool(reference),
                           payload=json.loads(record.payload) if record else {})


@bp.route(SLUGS["cargo"])
def cargo():
    g.nav_section = "help"
    return render_template("extras/cargo.html")


@bp.route(SLUGS["cargo_restrictions"])
def cargo_restrictions():
    g.nav_section = "help"
    return render_template("extras/cargo_restrictions.html")


@bp.route(SLUGS["status_subscribe"], methods=["GET", "POST"])
def status_subscribe():
    g.nav_section = "status"
    db = database.session()
    from ..models.requests import ServiceRequest

    record = error = None
    if request.method == "POST":
        flight_no = "".join((request.form.get("flight_no") or "").split()).upper()
        email = (request.form.get("email") or "").strip()
        if not flight_no:
            error = t("form.error_required")
        elif "@" not in email:
            error = t("form.error_email")
        else:
            record = ServiceRequest(
                kind="status_alert",
                reference_no=references.next_reference(db, "status_alert",
                                                       ServiceRequest.reference_no),
                status="active", created_at=now().replace(tzinfo=None),
                payload=json.dumps({"flight_no": flight_no, "email": email}))
            db.add(record)
            db.commit()
    return render_template("extras/subscribe.html", record=record, error=error)


@bp.route(SLUGS["help_faq"])
def faq(category: str):
    g.nav_section = "help"
    db = database.session()
    from ..models.content import ContentPage

    pages = list(db.scalars(select(ContentPage).where(
        ContentPage.category == category).order_by(ContentPage.position,
                                                   ContentPage.id)))
    if not pages:
        abort(404)
    return render_template("extras/faq.html", category=category,
                           label=labels.content_category_label(category), pages=pages)


@bp.route(SLUGS["stopover_book"], methods=["GET", "POST"])
def stopover_book():
    g.nav_section = "book"
    db = database.session()
    from ..models.content import StopoverPackage
    from ..models.requests import ServiceRequest

    packages = list(db.scalars(select(StopoverPackage).order_by(StopoverPackage.id)))
    record = error = None
    if request.method == "POST":
        package = get_row(db, StopoverPackage, request.form.get("package_id"))
        pnr = (request.form.get("pnr") or "").strip().upper()
        if package is None:
            error = t("stopover.pick_package")
        elif len(pnr) != 6:
            error = t("stopover.need_pnr")
        else:
            record = ServiceRequest(
                kind="stopover",
                reference_no=references.next_reference(db, "stopover",
                                                       ServiceRequest.reference_no),
                status="pending", created_at=now().replace(tzinfo=None),
                payload=json.dumps({"pnr": pnr, "package": package.name}))
            db.add(record)
            db.commit()
    return render_template("extras/stopover_book.html", packages=packages,
                           record=record, error=error)
