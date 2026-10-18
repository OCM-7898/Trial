from __future__ import annotations

from datetime import date, datetime, timedelta

from flask import Blueprint, abort, g, render_template, request
from sqlalchemy import func, select

from .. import db as database
from ..clock import WINDOW_END, WINDOW_START, today
from ..i18n import labels, t
from ..models import translated_column
from ..models.ancillary import BaggageRule
from ..models.network import Airport, Flight, Route
from ..routes_map import SLUGS
from ..services import baggage as baggage_service

bp = Blueprint("info", __name__)


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        parsed = datetime.strptime(raw.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None
    return parsed if WINDOW_START <= parsed <= WINDOW_END else None


def _normalise_flight_no(raw: str) -> str:
    cleaned = "".join(raw.split()).upper()
    if cleaned.isdigit():
        cleaned = f"SM{cleaned}"
    return cleaned


@bp.route(SLUGS["flight_status"])
def flight_status():
    g.nav_section = "status"
    raw_no = (request.args.get("flight_no") or "").strip()
    on = _parse_date(request.args.get("date"))

    result = None
    searched = bool(raw_no)
    if raw_no and on:
        db = database.session()
        flight = db.scalars(
            select(Flight).where(
                Flight.flight_no == _normalise_flight_no(raw_no), Flight.date == on
            )
        ).one_or_none()
        if flight is not None:
            route = db.get(Route, flight.route_id)
            result = {
                "flight": flight,
                "origin": db.get(Airport, route.origin_id),
                "destination": db.get(Airport, route.destination_id),
                "status_label": labels.flight_status_label(flight.status),
                "arrival_date": flight.date + timedelta(days=flight.arr_day_offset),
            }

    return render_template(
        "info/flight_status.html",
        flight_no=raw_no, date_value=request.args.get("date", ""),
        result=result, searched=searched, today=today(),
    )


@bp.route(SLUGS["schedules"])
def schedules():
    g.nav_section = "book"
    origin = (request.args.get("origin") or "").strip().upper()[:3]
    destination = (request.args.get("destination") or "").strip().upper()[:3]

    rows, route = [], None
    if origin and destination:
        db = database.session()
        origin_row = db.scalars(select(Airport).where(Airport.iata == origin)).one_or_none()
        destination_row = db.scalars(
            select(Airport).where(Airport.iata == destination)
        ).one_or_none()
        if origin_row and destination_row:
            route = db.scalars(select(Route).where(
                Route.origin_id == origin_row.id,
                Route.destination_id == destination_row.id,
            )).one_or_none()
        if route is not None:
            seen: dict[int, Flight] = {}
            for flight in db.scalars(
                select(Flight).where(Flight.route_id == route.id,
                                     Flight.date >= today())
                .order_by(Flight.date, Flight.dep_time)
            ):
                seen.setdefault(flight.date.weekday(), flight)
                if len(seen) == 7:
                    break
            rows = [{
                "weekday": index,
                "flight": seen[index],
                "operates": route.operating_days[index] != ".",
            } for index in range(7) if index in seen]

            rows += [{"weekday": index, "flight": None, "operates": False}
                     for index in range(7) if index not in seen]
            rows.sort(key=lambda r: r["weekday"])

    return render_template(
        "info/schedules.html",
        origin=origin, destination=destination, route=route, rows=rows,
        weekday_names=[t("weekday.monday"), t("weekday.tuesday"), t("weekday.wednesday"),
                       t("weekday.thursday"), t("weekday.friday"), t("weekday.saturday"),
                       t("weekday.sunday")],
    )


@bp.route(SLUGS["bag_allowance"])
def baggage_allowance():
    g.nav_section = "book"
    origin = (request.args.get("origin") or "").strip().upper()[:3]
    destination = (request.args.get("destination") or "").strip().upper()[:3]
    cabin = request.args.get("cabin") if request.args.get("cabin") in ("economy", "business") else "economy"
    pax_type = request.args.get("pax_type") if request.args.get("pax_type") in ("adult", "child", "infant") else "adult"

    rule, region = None, None
    if origin and destination:
        db = database.session()
        origin_row = db.scalars(select(Airport).where(Airport.iata == origin)).one_or_none()
        destination_row = db.scalars(select(Airport).where(Airport.iata == destination)).one_or_none()
        if origin_row and destination_row:
            region = baggage_service.region_for(origin_row, destination_row)
            rule = baggage_service.rule_for(db, region, cabin, pax_type)

    return render_template(
        "info/baggage_allowance.html",
        origin=origin, destination=destination, cabin=cabin, pax_type=pax_type,
        rule=rule, region=region,
        region_label=labels.region_label(region) if region else "",
        cabin_options=[("economy", t("brand.cabin_economy")), ("business", t("brand.cabin_business"))],
        pax_options=[("adult", t("pax.adult")), ("child", t("pax.child")), ("infant", t("pax.infant"))],
    )


@bp.route(SLUGS["bag_fees"])
def baggage_fees():
    g.nav_section = "book"
    db = database.session()
    rules = db.scalars(
        select(BaggageRule).where(BaggageRule.pax_type == "adult",
                                  BaggageRule.cabin == "economy")
        .order_by(BaggageRule.region)
    ).all()
    return render_template(
        "info/baggage_fees.html",
        rules=[{"rule": r, "label": labels.region_label(r.region)} for r in rules],
    )


@bp.route(SLUGS["status_route"])
def status_by_route():
    g.nav_section = "status"
    origin = (request.args.get("origin") or "").strip().upper()[:3]
    destination = (request.args.get("destination") or "").strip().upper()[:3]
    on = _parse_date(request.args.get("date"))

    rows = []
    if origin and destination and on:
        db = database.session()
        for flight in db.scalars(
            select(Flight).join(Route, Route.id == Flight.route_id)
            .join(Airport, Airport.id == Route.origin_id)
            .where(Flight.date == on)
            .order_by(Flight.dep_time)
        ):
            route = db.get(Route, flight.route_id)
            if (db.get(Airport, route.origin_id).iata != origin
                    or db.get(Airport, route.destination_id).iata != destination):
                continue
            rows.append({"flight": flight,
                         "status_label": labels.flight_status_label(flight.status)})

    return render_template("info/status_route.html", origin=origin,
                           destination=destination,
                           date_value=request.args.get("date", ""), rows=rows,
                           searched=bool(origin and destination and on))


def _board(iata: str, departures: bool):
    g.nav_section = "status"
    db = database.session()
    on = _parse_date(request.args.get("date")) or today()
    airport = db.scalars(select(Airport).where(Airport.iata == iata.upper())).one_or_none()
    if airport is None:
        abort(404)

    column = Route.origin_id if departures else Route.destination_id
    other = Route.destination_id if departures else Route.origin_id
    rows = []
    for flight in db.scalars(
        select(Flight).join(Route, Route.id == Flight.route_id)
        .where(column == airport.id, Flight.date == on)
        .order_by(Flight.dep_time)
    ):
        route = db.get(Route, flight.route_id)
        rows.append({
            "flight": flight,
            "other": db.get(Airport, getattr(route, "destination_id" if departures else "origin_id")),
            "status_label": labels.flight_status_label(flight.status),
        })

    return render_template("info/board.html", airport=airport, rows=rows,
                           departures=departures, day=on,
                           date_value=on.isoformat())


@bp.route(SLUGS["status_departures"])
def departures(iata: str):
    return _board(iata, departures=True)


@bp.route(SLUGS["status_arrivals"])
def arrivals(iata: str):
    return _board(iata, departures=False)


@bp.route(SLUGS["schedules_seasonal"])
def seasonal():
    g.nav_section = "book"
    db = database.session()
    rows = []
    for route in db.scalars(
        select(Route).where(Route.seasonal_from.isnot(None)).order_by(Route.id)
    ):
        rows.append({"route": route,
                     "origin": db.get(Airport, route.origin_id),
                     "destination": db.get(Airport, route.destination_id)})
    return render_template("info/seasonal.html", rows=rows)


@bp.route(SLUGS["network"])
def network():
    g.nav_section = "book"
    db = database.session()
    airports = list(db.scalars(select(Airport).order_by(Airport.region, Airport.iata)))
    by_region: dict[str, list] = {}
    for airport in airports:
        by_region.setdefault(airport.region, []).append(airport)
    return render_template(
        "info/network.html",
        groups=[{"label": labels.region_label(region), "airports": rows}
                for region, rows in sorted(by_region.items())],
        total=len(airports))


@bp.route(SLUGS["network_hubs"])
def hubs():
    g.nav_section = "book"
    db = database.session()
    counts = dict(db.execute(
        select(Airport.iata, func.count(Route.id))
        .join(Route, Route.origin_id == Airport.id)
        .group_by(Airport.iata)).all())
    airports = {a.iata: a for a in db.scalars(
        select(Airport).where(Airport.iata.in_(list(counts))))}
    rows = sorted(
        ({"airport": airports[iata], "routes": n} for iata, n in counts.items()),
        key=lambda r: (-r["routes"], r["airport"].iata))[:10]
    return render_template("info/hubs.html", rows=rows)


@bp.route(SLUGS["network_new_routes"])
def new_routes():
    g.nav_section = "book"
    db = database.session()
    rows = []
    for route in db.scalars(select(Route).order_by(Route.id.desc()).limit(12)):
        rows.append({"route": route,
                     "origin": db.get(Airport, route.origin_id),
                     "destination": db.get(Airport, route.destination_id)})
    return render_template("info/new_routes.html", rows=rows)


@bp.route(SLUGS["network_codeshare"])
def codeshare():
    g.nav_section = "book"
    db = database.session()
    from ..models.booking import Segment

    rows = []
    for segment in db.scalars(
        select(Segment).where(translated_column(Segment, "operated_by").isnot(None))
        .order_by(Segment.id)
    ):
        flight = db.get(Flight, segment.flight_id)
        route = db.get(Route, flight.route_id)
        rows.append({
            "flight": flight,
            "origin": db.get(Airport, route.origin_id),
            "destination": db.get(Airport, route.destination_id),
            "operator": segment.operated_by,
        })
    return render_template("info/codeshare.html", rows=rows)
