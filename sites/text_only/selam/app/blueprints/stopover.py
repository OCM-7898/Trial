from __future__ import annotations

from datetime import datetime

from flask import Blueprint, g, render_template, request
from sqlalchemy import select

from .. import db as database
from ..clock import WINDOW_END, WINDOW_START
from ..i18n.labels import stopover_category_label
from ..models.content import StopoverPackage
from ..routes_map import SLUGS
from ..services import search as search_service

bp = Blueprint("stopover", __name__)

HUB = "ADD"
MIN_HOURS = 8
MAX_HOURS = 72


def _parse_date(raw: str | None):
    if not raw:
        return None
    try:
        parsed = datetime.strptime(raw.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None
    return parsed if WINDOW_START <= parsed <= WINDOW_END else None


@bp.route(SLUGS["stopover"])
def index():
    g.nav_section = "book"
    db = database.session()
    origin = (request.args.get("origin") or "").strip().upper()[:3]
    destination = (request.args.get("destination") or "").strip().upper()[:3]
    day = _parse_date(request.args.get("date"))

    results, searched = [], bool(origin and destination and day)
    if searched:
        for itinerary in search_service.search(db, origin, destination, day):
            if itinerary.stops != 1:
                continue
            hours = itinerary.layover_min / 60
            results.append({
                "itinerary": itinerary,
                "hours": int(hours),
                "minutes": itinerary.layover_min % 60,
                "eligible": itinerary.stopover_eligible,
                "packages": _packages_for(db, itinerary) if itinerary.stopover_eligible else [],
            })
        seen, unique = set(), []
        for row in results:
            key = tuple(row["itinerary"].flight_numbers)
            if key not in seen:
                seen.add(key)
                unique.append(row)
        results = unique

    return render_template(
        "stopover/index.html", origin=origin, destination=destination,
        date_value=request.args.get("date", ""), results=results, searched=searched,
        min_hours=MIN_HOURS, max_hours=MAX_HOURS,
    )


def _packages_for(db, itinerary) -> list[StopoverPackage]:
    hours = itinerary.layover_min / 60
    cabin = itinerary.fare_class.cabin
    return [
        package for package in db.scalars(
            select(StopoverPackage).order_by(StopoverPackage.id))
        if package.min_layover_h <= hours <= package.max_layover_h
        and (package.cabin_required is None or package.cabin_required == cabin)
    ]


@bp.route(SLUGS["stopover_packages"])
def packages():
    g.nav_section = "book"
    db = database.session()
    rows = list(db.scalars(select(StopoverPackage).order_by(StopoverPackage.category,
                                                            StopoverPackage.id)))
    grouped: dict[str, list] = {}
    for package in rows:
        grouped.setdefault(package.category, []).append(package)
    return render_template(
        "stopover/packages.html",
        groups=[{"label": stopover_category_label(category), "packages": items}
                for category, items in sorted(grouped.items())],
        min_hours=MIN_HOURS, max_hours=MAX_HOURS,
    )
