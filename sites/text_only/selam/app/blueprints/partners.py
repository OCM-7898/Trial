from __future__ import annotations

from datetime import datetime

from flask import Blueprint, abort, g, redirect, render_template, request
from sqlalchemy import select

from .. import db as database
from ..clock import WINDOW_END, WINDOW_START, now
from ..i18n import t
from ..models.partners import (
    CarBooking, CarOffer, HotelBooking, HotelRoom, InsuranceProduct,
    RailConnection, VisaType,
)
from ..params import bounded_float, bounded_int, get_row
from ..routes_map import SLUGS, path
from ..services import references

bp = Blueprint("partners", __name__)


def _partner(slug: str) -> dict:
    table = {
        "zena-hotel": (t("brand.hotel"), t("partner.hotel_tagline"), "#7A3E2B", "ZT",
                       SLUGS["partner_hotel"]),
        "evisa": (t("brand.evisa"), t("partner.evisa_tagline"), "#1F3A6E", "EV",
                  SLUGS["partner_evisa"]),
        "eurorail": (t("brand.rail"), t("partner.rail_tagline"), "#2E5E3A", "ER",
                     SLUGS["partner_rail"]),
        "riftdrive": (t("brand.car_partner"), t("partner.car_tagline"), "#8A5A00", "RD",
                      SLUGS["partner_car"]),
        "safevoyage": (t("brand.insurance"), t("partner.insurance_tagline"), "#5B2A6E",
                       "SV", SLUGS["partner_insurance"]),
    }
    name, tagline, accent, initials, home = table[slug]
    return {"slug": slug, "name": name, "tagline": tagline,
            "accent": accent, "initials": initials, "home": home}


def _parse_date(raw: str | None):
    if not raw:
        return None
    try:
        parsed = datetime.strptime(raw.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None
    return parsed if WINDOW_START <= parsed <= WINDOW_END else None


@bp.route(SLUGS["partners"])
def hub():
    g.nav_section = "help"
    return render_template("partners/hub.html", partners=[
        {"info": _partner(slug), "url": url, "blurb": blurb}
        for slug, url, blurb in (
            ("zena-hotel", SLUGS["partner_hotel"], t("partner.hotel_blurb")),
            ("evisa", SLUGS["partner_evisa"], t("partner.evisa_blurb")),
            ("eurorail", SLUGS["partner_rail"], t("partner.rail_blurb")),
            ("riftdrive", SLUGS["partner_car"], t("partner.car_blurb")),
            ("safevoyage", SLUGS["partner_insurance"], t("partner.insurance_blurb")),
        )])


@bp.route(SLUGS["partner_hotel"], methods=["GET", "POST"])
def hotel():
    db = database.session()
    rooms = list(db.scalars(select(HotelRoom).order_by(HotelRoom.id)))
    arrival = _parse_date(request.values.get("arrival"))
    hours = bounded_int(request.values.get("hours", 12), low=4, high=72, default=12)

    record = error = None
    if request.method == "POST" and request.form.get("room_id"):
        room = get_row(db, HotelRoom, request.form.get("room_id"))
        guest = (request.form.get("guest_name") or "").strip()
        if room is None or arrival is None or not guest:
            error = t("partner.hotel_error")
        elif room.rooms_available <= 0:
            error = t("partner.hotel_sold_out")
        else:
            blocks = -(-hours // room.block_hours)
            record = HotelBooking(
                room_id=room.id,
                reference_no=references.next_reference(db, "hotel", HotelBooking.reference_no),
                guest_name=guest, arrival=arrival, hours=hours,
                price_usd=round(room.price_per_block_usd * blocks, 2),
                status="pending", created_at=now().replace(tzinfo=None), is_paid=False,
            )
            db.add(record)
            db.commit()
            return redirect(f"{SLUGS['partner_hotel']}?ref={record.reference_no}")

    reference = (request.args.get("ref") or "").strip()
    if reference:
        record = db.scalars(select(HotelBooking).where(
            HotelBooking.reference_no == reference)).one_or_none()

    return render_template("partners/hotel.html", partner=_partner("zena-hotel"),
                           rooms=rooms, arrival=request.values.get("arrival", ""),
                           hours=hours, record=record, error=error,
                           room_for=lambda rid: db.get(HotelRoom, rid),
                           notice=_pay_notice())


def _pay_notice():
    if request.method == "POST" and request.form.get("action") == "pay":
        return t("review.payment_disabled")
    return None


@bp.route(SLUGS["partner_evisa"])
def evisa():
    db = database.session()
    visas = list(db.scalars(select(VisaType).order_by(VisaType.id)))
    selected = None
    code = (request.args.get("code") or "").strip().upper()
    if code:
        selected = next((v for v in visas if v.code == code), None)
    return render_template("partners/evisa.html", partner=_partner("evisa"),
                           visas=visas, selected=selected)


@bp.route(SLUGS["partner_rail"])
def rail():
    db = database.session()
    arrival = (request.args.get("arrival") or "").strip().upper()[:3]
    rows = list(db.scalars(
        select(RailConnection).order_by(RailConnection.arrival_iata, RailConnection.id)))
    if arrival:
        rows = [r for r in rows if r.arrival_iata == arrival]
    return render_template("partners/rail.html", partner=_partner("eurorail"),
                           connections=rows, arrival=arrival,
                           searched=bool(request.args.get("arrival")))


@bp.route(SLUGS["partner_car"], methods=["GET", "POST"])
def car():
    db = database.session()
    airport = (request.values.get("airport") or "").strip().upper()[:3]
    passengers = bounded_int(request.values.get("passengers", 1), low=1, high=9, default=1)
    pickup = _parse_date(request.values.get("pickup"))

    offers = list(db.scalars(select(CarOffer).order_by(CarOffer.price_usd)))
    if airport:
        offers = [o for o in offers if o.airport_iata == airport]
    offers = [o for o in offers if o.seats >= passengers]

    record = error = None
    if request.method == "POST" and request.form.get("offer_id"):
        offer = get_row(db, CarOffer, request.form.get("offer_id"))
        if offer is None or pickup is None:
            error = t("partner.car_error")
        elif offer.seats < passengers:
            error = t("partner.car_too_small")
        else:
            record = CarBooking(
                offer_id=offer.id,
                reference_no=references.next_reference(db, "car", CarBooking.reference_no),
                passengers=passengers, pickup_date=pickup,
                price_usd=offer.price_usd, status="pending",
                created_at=now().replace(tzinfo=None), is_paid=False,
            )
            db.add(record)
            db.commit()
            return redirect(f"{SLUGS['partner_car']}?ref={record.reference_no}")

    reference = (request.args.get("ref") or "").strip()
    if reference:
        record = db.scalars(select(CarBooking).where(
            CarBooking.reference_no == reference)).one_or_none()

    return render_template("partners/car.html", partner=_partner("riftdrive"),
                           offers=offers, airport=airport, passengers=passengers,
                           pickup=request.values.get("pickup", ""), record=record,
                           error=error, offer_for=lambda oid: db.get(CarOffer, oid),
                           notice=_pay_notice(), searched=bool(airport))


@bp.route(SLUGS["partner_insurance"])
def insurance():
    db = database.session()
    products = list(db.scalars(select(InsuranceProduct).order_by(InsuranceProduct.id)))
    fare = bounded_float(request.args.get("fare", 0), low=0.0, high=1_000_000.0)

    quotes = [{
        "product": product,
        "premium": round(max(product.price_min_usd, fare * product.price_pct / 100.0), 2),
        "at_floor": fare * product.price_pct / 100.0 < product.price_min_usd,
    } for product in products]

    return render_template("partners/insurance.html",
                           partner=_partner("safevoyage"), quotes=quotes, fare=fare)
