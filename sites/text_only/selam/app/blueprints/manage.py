from __future__ import annotations

from flask import (
    Blueprint, current_app, g, redirect, render_template, request, send_file,
    session as flask_session,
)

from .. import db as database
from .. import lang
from ..i18n import formats, labels, t
from ..routes_map import SLUGS, path
from ..services import bookings as booking_service
from ..services import eligibility
from ..services import itinerary_pdf as itinerary_pdf_service

bp = Blueprint("manage", __name__)

SESSION_KEY = "retrieved_pnrs"


def _remember(pnr: str) -> None:
    known = set(flask_session.get(SESSION_KEY, []))
    known.add(pnr.upper())
    flask_session[SESSION_KEY] = sorted(known)


def _is_known(pnr: str) -> bool:
    return pnr.upper() in set(flask_session.get(SESSION_KEY, []))


@bp.route(SLUGS["manage"], methods=["GET", "POST"])
def retrieve():
    g.nav_section = "manage"
    pnr = (request.values.get("pnr") or "").strip()
    surname = (request.values.get("surname") or "").strip()

    if not pnr and not surname:
        return render_template("manage/retrieve.html", error=None, pnr="", surname="")

    booking = booking_service.retrieve(database.session(), pnr, surname)
    if booking is None:
        return render_template(
            "manage/retrieve.html",
            error=t("manage.not_found"), pnr=pnr, surname=surname,
        ), 404

    _remember(booking.pnr)
    return redirect(path("manage_pnr", pnr=booking.pnr))


@bp.route(SLUGS["manage_pnr"])
def detail(pnr: str):
    g.nav_section = "manage"
    db = database.session()
    booking = booking_service.by_pnr(db, pnr)

    if booking is None or not _is_known(booking.pnr):
        return render_template(
            "manage/retrieve.html", error=t("manage.reauth"), pnr=pnr, surname=""
        ), 404

    views = booking_service.itinerary(db, booking)
    rows = []
    for view in views:
        checkin = eligibility.checkin_decision(booking, view.segment, view.flight)
        rows.append({
            "view": view,
            "checkin": checkin,
            "checkin_label": labels.checkin_label(checkin.code),
            "status_label": labels.flight_status_label(view.flight.status),
            "change": eligibility.change_decision(view.fare_class, view.segment, view.flight),
            "upgrade": eligibility.upgrade_decision(
                view.fare_class, booking_service.business_fares(db, view.flight.id)
            ),
        })

    refund = eligibility.refund_decision(booking, views[0].fare_class)
    return render_template(
        "manage/detail.html",
        booking=booking,
        rows=rows,
        refund=refund,
        refund_label=labels.refund_label(refund.code),
        channel_label=labels.channel_label(booking.booked_channel),
        pax_labels={k: labels.pax_type_label(k) for k in ("adult", "child", "infant")},
    )


@bp.route(SLUGS["manage_itinerary_pdf"])
def itinerary_pdf(pnr: str):
    db = database.session()
    booking = booking_service.by_pnr(db, pnr)
    if booking is None or not _is_known(booking.pnr):
        return render_template(
            "manage/retrieve.html", error=t("manage.reauth"), pnr=pnr, surname=""
        ), 404

    views = booking_service.itinerary(db, booking)
    legs = [
        itinerary_pdf_service.ItineraryLeg(
            flight_no=view.flight.flight_no,
            date_label=formats.format_date(view.flight.date, lang.active()),
            origin=f"{view.origin.city} ({view.origin.iata})",
            destination=f"{view.destination.city} ({view.destination.iata})",
            dep_time=formats.format_time(view.flight.dep_time),
            arr_time=formats.format_time(view.flight.arr_time),
            cabin_label=view.fare_class.name,
            seat_labels=", ".join(
                sorted(a.seat_no for a in view.seats.values())) or "",
        )
        for view in views
    ]

    target = (current_app.config["SELAM"].generated_dir
              / f"itinerary-{booking.pnr}-{lang.active()}.pdf")
    itinerary_pdf_service.render(
        target, pnr=booking.pnr,
        passenger_names=[p.full_name for p in booking.passengers],
        legs=legs,
        total_label=formats.format_money(booking.total_paid or 0),
    )
    return send_file(target, mimetype="application/pdf",
                     download_name=f"itinerary-{booking.pnr}.pdf")
