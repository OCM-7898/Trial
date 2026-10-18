from __future__ import annotations

from flask import Blueprint, abort, g, redirect, render_template, request
from sqlalchemy import select

from .. import db as database
from ..clock import now
from ..i18n import labels, t
from ..models.ancillary import LoungePurchase
from ..models.content import Lounge
from ..models.network import Airport
from ..params import bounded_int, get_row, row_id
from ..routes_map import SLUGS, path
from ..services import lounges as lounge_service
from ..services import references

bp = Blueprint("lounges", __name__)

CABINS = ("economy", "business")


@bp.route(SLUGS["lounges"])
def index():
    g.nav_section = "help"
    db = database.session()
    iata = (request.args.get("airport") or "").strip().upper()[:3]

    if iata:
        rows = lounge_service.at_airport(db, iata)
        airport = db.scalars(select(Airport).where(Airport.iata == iata)).one_or_none()
    else:
        rows = list(db.scalars(select(Lounge).order_by(Lounge.airport_iata, Lounge.terminal, Lounge.id)))
        airport = None

    airports = {
        a.iata: a for a in db.scalars(
            select(Airport).where(Airport.iata.in_({row.airport_iata for row in rows}))
        )
    }
    return render_template("lounges/index.html", lounges=rows, airports=airports,
                           iata=iata, airport=airport)


@bp.route(SLUGS["lounge_detail"])
def detail(lounge_id: str):
    g.nav_section = "help"
    db = database.session()
    lounge = get_row(db, Lounge, lounge_id)
    if lounge is None:
        abort(404)
    airport = db.scalars(select(Airport).where(Airport.iata == lounge.airport_iata)).one_or_none()
    return render_template("lounges/detail.html", lounge=lounge, airport=airport,
                           admitted=_admitted_labels(lounge))


def _admitted_labels(lounge: Lounge) -> list[str]:
    tokens = [x.strip() for x in (lounge.access_free_for or "").split(",") if x.strip()]
    mapping = {
        "business": t("brand.cabin_business"),
        "silver": t("lounge.tier_silver"),
        "gold": t("lounge.tier_gold"),
        "platinum": t("lounge.tier_platinum"),
    }
    return [mapping[token] for token in tokens if token in mapping]


@bp.route(SLUGS["lounge_eligibility"])
def eligibility():
    g.nav_section = "help"
    db = database.session()
    iata = (request.args.get("airport") or "").strip().upper()[:3]
    cabin = request.args.get("cabin") if request.args.get("cabin") in CABINS else None
    tier = request.args.get("tier") if request.args.get("tier") in lounge_service.TIERS else None

    results = []
    if iata:
        for lounge in lounge_service.at_airport(db, iata):
            access = lounge_service.access_for(lounge, cabin, tier)
            results.append({
                "lounge": lounge,
                "access": access,
                "label": labels.lounge_access_label(access.reason),
            })

    return render_template(
        "lounges/eligibility.html", iata=iata, cabin=cabin, tier=tier, results=results,
        cabin_options=[("", t("search.cabin_any")),
                       ("economy", t("brand.cabin_economy")),
                       ("business", t("brand.cabin_business"))],
        tier_options=[("", t("lounge.tier_none")),
                      ("blue", t("lounge.tier_blue")), ("silver", t("lounge.tier_silver")),
                      ("gold", t("lounge.tier_gold")), ("platinum", t("lounge.tier_platinum"))],
    )


@bp.route(SLUGS["lounge_purchase"], methods=["GET", "POST"])
def purchase():
    g.nav_section = "help"
    db = database.session()
    lounge_id = row_id(request.values.get("lounge_id"))
    lounge = db.get(Lounge, lounge_id) if lounge_id else None

    options = list(db.scalars(
        select(Lounge).where(Lounge.walk_in_price_usd > 0)
        .order_by(Lounge.airport_iata, Lounge.id)
    ))

    if request.method == "POST" and lounge is not None:
        name = (request.form.get("passenger_name") or "").strip()
        guests = max(0, min(4, bounded_int(request.form.get("guests"), low=0, high=4, default=0) or 0))
        if not name:
            return render_template("lounges/purchase.html", options=options,
                                   lounge=lounge, error=t("lounge.name_required")), 400
        db.add(LoungePurchase(
            booking_id=None, lounge_id=lounge.id, flight_id=None,
            reference_no=references.next_reference(db, "lounge", LoungePurchase.reference_no),
            status="pending", created_at=now().replace(tzinfo=None), is_paid=False,
            passenger_name=name, guests=guests,
            price_usd=round(lounge.walk_in_price_usd * (1 + guests), 2),
        ))
        db.commit()
        return redirect(path("lounge_review"))

    return render_template("lounges/purchase.html", options=options,
                           lounge=lounge, error=None)


@bp.route(SLUGS["lounge_review"], methods=["GET", "POST"])
def review():
    g.nav_section = "help"
    db = database.session()
    record = db.scalars(
        select(LoungePurchase).order_by(LoungePurchase.id.desc())
    ).first()
    if record is None:
        abort(404)
    lounge = db.get(Lounge, record.lounge_id)

    notice = (t("review.payment_disabled")
              if request.method == "POST" and request.form.get("action") == "pay" else None)

    lines = [{"label": lounge.name, "detail": lounge.airport_iata,
              "amount": lounge.walk_in_price_usd}]
    if record.guests:
        lines.append({"label": t("lounge.guests"), "detail": str(record.guests),
                      "amount": round(lounge.walk_in_price_usd * record.guests, 2)})

    return render_template("lounges/review.html", record=record, lounge=lounge,
                           lines=lines, notice=notice)
