from __future__ import annotations

from flask import (
    Blueprint, abort, current_app, g, render_template, request, send_file,
)
from sqlalchemy import select

from .. import db as database
from ..clock import now
from ..i18n import labels, t
from ..models.booking import Booking, Passenger, SeatAssignment, Segment
from ..models.checkin import BoardingPass, Checkin
from ..params import bounded_int, get_row
from ..routes_map import SLUGS, path
from ..services import boarding_pass as pass_service
from ..services import bookings as booking_service
from ..services import eligibility

bp = Blueprint("checkin", __name__)


@bp.route(SLUGS["checkin"], methods=["GET", "POST"])
def start():
    g.nav_section = "checkin"
    pnr = (request.values.get("pnr") or "").strip()
    surname = (request.values.get("surname") or "").strip()

    if not pnr or not surname:
        return render_template("checkin/start.html", error=None, pnr=pnr, surname=surname)

    db = database.session()
    booking = booking_service.retrieve(db, pnr, surname)
    if booking is None:
        return render_template(
            "checkin/start.html", error=t("manage.not_found"), pnr=pnr, surname=surname
        ), 404

    rows = []
    for view in booking_service.itinerary(db, booking):
        decision = eligibility.checkin_decision(booking, view.segment, view.flight)
        rows.append({
            "view": view,
            "decision": decision,
            "label": labels.checkin_label(decision.code),
            "status_label": labels.flight_status_label(view.flight.status),
        })

    if request.method == "POST" and request.form.get("segment_id"):
        return _perform(db, booking, rows, int(request.form["segment_id"]))

    return render_template("checkin/segments.html", booking=booking, rows=rows, refused=None)


def _perform(db, booking, rows, segment_id: int):
    row = next((r for r in rows if r["view"].segment.id == segment_id), None)
    if row is None:
        abort(404)

    if not row["decision"].allowed:
        return render_template(
            "checkin/segments.html", booking=booking, rows=rows,
            refused=row["label"],
        ), 409

    view = row["view"]
    generated = current_app.config["SELAM"].generated_dir
    passes = []

    for index, passenger in enumerate(booking.passengers, start=1):
        if passenger.pax_type == "infant":
            continue
        existing = db.scalars(
            select(Checkin).where(
                Checkin.segment_id == view.segment.id,
                Checkin.passenger_id == passenger.id,
            )
        ).one_or_none()
        if existing is not None:
            passes.append(db.get(BoardingPass, existing.boarding_pass_id))
            continue

        seat = db.scalars(
            select(SeatAssignment).where(
                SeatAssignment.segment_id == view.segment.id,
                SeatAssignment.passenger_id == passenger.id,
            )
        ).one_or_none()

        payload = pass_service.barcode_payload(booking.pnr, view.segment.id, index)
        boarding = pass_service.boarding_time(view.flight.dep_time)
        pdf_name = f"{booking.pnr}-{view.segment.id}-{index}.pdf"

        record = BoardingPass(
            barcode_payload=payload,
            pdf_path=str(generated / pdf_name),
            gate=view.flight.gate,
            boarding_time=boarding,
            sequence_no=index,
            seat_no=seat.seat_no if seat else None,
        )
        db.add(record)
        db.flush()

        pass_service.render(
            generated / pdf_name,
            pnr=booking.pnr,
            passenger_name=passenger.full_name,
            flight_no=view.flight.flight_no,
            origin_iata=view.origin.iata, origin_city=view.origin.city,
            destination_iata=view.destination.iata, destination_city=view.destination.city,
            date_label=_date_label(view.flight.date),
            dep_time_label=view.flight.dep_time.strftime("%H:%M"),
            boarding_label=boarding,
            gate=view.flight.gate or "",
            terminal=view.flight.terminal_dep or "",
            seat_no=seat.seat_no if seat else "",
            cabin_label=view.fare_class.name,
            sequence_no=index,
            payload=payload,
        )

        db.add(Checkin(
            segment_id=view.segment.id,
            passenger_id=passenger.id,
            checked_in_at=now().replace(tzinfo=None),
            boarding_pass_id=record.id,
        ))
        passes.append(record)

    view.segment.checked_in = True
    db.commit()

    return render_template(
        "checkin/done.html", booking=booking, view=view, passes=passes,
    )


def _date_label(day) -> str:
    from ..i18n.formats import format_date
    from ..lang import active

    return format_date(day, active())


@bp.route(SLUGS["boarding_pass"])
def boarding_pass_pdf(checkin_id: str):
    db = database.session()
    record = get_row(db, BoardingPass, checkin_id)
    if record is None:
        abort(404)
    from pathlib import Path

    pdf = Path(record.pdf_path)
    if not pdf.exists():
        abort(404)
    return send_file(pdf, mimetype="application/pdf", as_attachment=False,
                     download_name=pdf.name)


def _pass_or_404(db, checkin_id: str):
    record = get_row(db, BoardingPass, checkin_id)
    if record is None:
        abort(404)
    entry = db.scalars(
        select(Checkin).where(Checkin.boarding_pass_id == record.id)).one_or_none()
    if entry is None:
        abort(404)
    return record, entry


@bp.route(SLUGS["checkin_pax"])
def boarding_pass_detail(checkin_id: str):
    g.nav_section = "checkin"
    db = database.session()
    record, entry = _pass_or_404(db, checkin_id)
    segment = db.get(Segment, entry.segment_id)
    booking = db.get(Booking, segment.booking_id)
    view = next(v for v in booking_service.itinerary(db, booking)
                if v.segment.id == segment.id)
    passenger = db.get(Passenger, entry.passenger_id)
    return render_template("checkin/detail.html", record=record, view=view,
                           booking=booking, passenger=passenger)


@bp.route(SLUGS["checkin_bags"], methods=["GET", "POST"])
def declare_bags(checkin_id: str):
    g.nav_section = "checkin"
    db = database.session()
    record, entry = _pass_or_404(db, checkin_id)
    segment = db.get(Segment, entry.segment_id)
    saved = request.method == "POST"
    request_count = (bounded_int(request.form.get("bags"), low=0, high=9, default=0)
                     if saved else 0)
    return render_template("checkin/bags.html", record=record, segment=segment,
                           saved=saved, count=request_count)


@bp.route(SLUGS["checkin_seat"], methods=["GET", "POST"])
def change_seat_after_checkin(checkin_id: str):
    g.nav_section = "checkin"
    db = database.session()
    record, entry = _pass_or_404(db, checkin_id)
    segment = db.get(Segment, entry.segment_id)
    booking = db.get(Booking, segment.booking_id)
    view = next(v for v in booking_service.itinerary(db, booking)
                if v.segment.id == segment.id)
    from ..services.seats import column_guide, seat_map

    changed = error = None
    if request.method == "POST" and request.form.get("seat_no"):
        from ..services.seats import find_seat, occupied

        seat_no = request.form["seat_no"]
        if seat_no in occupied(db, segment.id):
            error = t("seats.unavailable")
        else:
            seat = find_seat(db, view.flight, seat_no)
            if seat is None:
                error = t("seats.unavailable")
            else:
                assignment = db.scalars(select(SeatAssignment).where(
                    SeatAssignment.segment_id == segment.id,
                    SeatAssignment.passenger_id == entry.passenger_id)).one_or_none()
                if assignment is None:
                    db.add(SeatAssignment(
                        segment_id=segment.id, passenger_id=entry.passenger_id,
                        seat_no=seat.seat_no, paid_amount=seat.price_usd,
                        is_paid=False, created_at=now().replace(tzinfo=None)))
                else:
                    assignment.seat_no = seat.seat_no
                    assignment.is_paid = False
                    assignment.created_at = now().replace(tzinfo=None)
                record.seat_no = seat.seat_no
                db.commit()
                changed = seat.seat_no

    rows = seat_map(db, segment, view.flight)
    return render_template("checkin/change_seat.html", record=record, view=view,
                           rows=rows, guide=column_guide(rows),
                           changed=changed, error=error)


@bp.route(SLUGS["checkin_cancel"], methods=["GET", "POST"])
def cancel_checkin(checkin_id: str):
    g.nav_section = "checkin"
    db = database.session()
    record, entry = _pass_or_404(db, checkin_id)
    segment = db.get(Segment, entry.segment_id)

    cancelled = False
    if request.method == "POST" and request.form.get("confirm") == "yes":
        remaining = db.scalars(select(Checkin).where(
            Checkin.segment_id == segment.id, Checkin.id != entry.id)).all()
        db.delete(entry)
        db.delete(record)
        if not remaining:
            segment.checked_in = False
        db.commit()
        cancelled = True

    return render_template("checkin/cancel.html", record=record, segment=segment,
                           cancelled=cancelled)


@bp.route(SLUGS["boarding_pass_email"], methods=["GET", "POST"])
def email_boarding_pass(checkin_id: str):
    g.nav_section = "checkin"
    db = database.session()
    record, entry = _pass_or_404(db, checkin_id)
    segment = db.get(Segment, entry.segment_id)
    booking = db.get(Booking, segment.booking_id)
    sent = request.method == "POST"
    return render_template("checkin/email.html", record=record, booking=booking,
                           sent=sent)
