import sqlite3

import pytest
from sqlalchemy import select

from app import create_app
from app import db as database
from app.models.ancillary import (
    BaggagePurchase, ChangeRequest, RefundRequest, UpgradePurchase,
)
from app.models.booking import Booking, SeatAssignment
from app.models.network import FareClass, Flight
from app.services import bookings as booking_service
from app.services import eligibility
from conftest import ROOT

PENDING_TABLES = ("change_requests", "refund_requests", "baggage_purchases",
                  "upgrade_purchases")


def _find(predicate, language="en"):
    app = create_app(language)
    with app.test_request_context():
        session = database.session()
        for booking in session.scalars(select(Booking).order_by(Booking.id)):
            segment = booking.segments[0]
            flight = session.get(Flight, segment.flight_id)
            fare_class = session.get(FareClass, segment.fare_class_id)
            if predicate(session, booking, segment, flight, fare_class):
                return booking.pnr, booking.surname_en, segment.id
    return None


def _retrieve(client, pnr, surname):
    response = client.post("/manage", data={"pnr": pnr, "surname": surname},
                           follow_redirects=True)
    assert response.status_code == 200, "retrieval failed, so the flow cannot start"


def _assert_nothing_paid(app):
    live = app.config["SELAM"].db_path
    with sqlite3.connect(live) as conn:
        for table in PENDING_TABLES:
            count = conn.execute(f"select count(*) from {table} where is_paid = 1").fetchone()[0]
            assert count == 0, f"{table} has {count} row(s) marked paid"
        count = conn.execute(
            "select count(*) from seat_assignments where is_paid = 1 and created_at is not null"
        ).fetchone()[0]
        assert count == 0, "a seat assignment created during the episode is marked paid"


def test_seat_selection_reaches_review_and_stays_unpaid():
    found = _find(lambda s, b, seg, f, fc: True)
    pnr, surname, segment_id = found
    app = create_app("en")

    with app.test_client() as client:
        _retrieve(client, pnr, surname)
        page = client.get(f"/manage/{pnr}/seats?segment_id={segment_id}")
        assert page.status_code == 200

        with app.test_request_context():
            session = database.session()
            booking = booking_service.by_pnr(session, pnr)
            view = next(v for v in booking_service.itinerary(session, booking)
                        if v.segment.id == segment_id)
            from app.services.seats import seat_map
            free = next(cell.seat.seat_no
                        for row in seat_map(session, view.segment, view.flight)
                        for cell in row.cells if cell and not cell.taken)

        response = client.post(f"/manage/{pnr}/seats",
                               data={"segment_id": segment_id, "seat_no": free},
                               follow_redirects=False)
        assert response.status_code == 302
        assert "/review" in response.headers["Location"]

        review = client.get(response.headers["Location"])
        assert review.status_code == 200
        assert free in review.get_data(as_text=True)

    with app.test_request_context():
        session = database.session()
        row = session.scalars(select(SeatAssignment).where(
            SeatAssignment.segment_id == segment_id, SeatAssignment.seat_no == free
        )).one()
        assert row.is_paid is False, "seat was marked paid; payment must never succeed"
    _assert_nothing_paid(app)


def test_taken_seat_is_refused():
    found = _find(lambda s, b, seg, f, fc: bool(
        s.scalars(select(SeatAssignment).where(SeatAssignment.segment_id == seg.id)).first()
    ))
    assert found, "no seeded booking has an assigned seat to collide with"
    pnr, surname, segment_id = found
    app = create_app("en")
    with app.test_request_context():
        session = database.session()
        taken = session.scalars(select(SeatAssignment.seat_no).where(
            SeatAssignment.segment_id == segment_id)).first()

    with app.test_client() as client:
        _retrieve(client, pnr, surname)
        response = client.post(f"/manage/{pnr}/seats",
                               data={"segment_id": segment_id, "seat_no": taken})
    assert response.status_code == 409


def test_refund_eligible_creates_pending_request():
    found = _find(lambda s, b, seg, f, fc: eligibility.refund_decision(b, fc).allowed)
    assert found, "no seeded booking is refundable online"
    pnr, surname, _ = found
    app = create_app("en")

    with app.test_client() as client:
        _retrieve(client, pnr, surname)
        response = client.post(f"/manage/{pnr}/refund", data={"confirm": "1"})
        assert response.status_code == 302 and "/review" in response.headers["Location"]
        review = client.get(response.headers["Location"])
        assert review.status_code == 200

    with app.test_request_context():
        session = database.session()
        booking = booking_service.by_pnr(session, pnr)
        row = session.scalars(select(RefundRequest).where(
            RefundRequest.booking_id == booking.id)).one()
        assert row.status == "pending" and row.is_paid is False
        assert row.reference_no.startswith("RF-") and len(row.reference_no) == 9
        assert row.quoted_amount_usd >= 0
    _assert_nothing_paid(app)


def test_agent_booking_cannot_refund_online():
    found = _find(lambda s, b, seg, f, fc:
                  eligibility.refund_decision(b, fc).code == "OFFLINE_CHANNEL_ONLY")
    assert found, "no seeded booking is refund-blocked by channel"
    pnr, surname, _ = found
    app = create_app("en")
    with app.test_client() as client:
        _retrieve(client, pnr, surname)
        page = client.get(f"/manage/{pnr}/refund")
        assert page.status_code == 200
        assert "notice-warn" in page.get_data(as_text=True)
        blocked = client.post(f"/manage/{pnr}/refund", data={"confirm": "1"})
        assert blocked.status_code == 409

    with app.test_request_context():
        session = database.session()
        booking = booking_service.by_pnr(session, pnr)
        assert not session.scalars(select(RefundRequest).where(
            RefundRequest.booking_id == booking.id)).all(), \
            "a refund request was written for an ineligible booking"


def test_upgrade_offer_creates_pending_purchase():
    found = _find(lambda s, b, seg, f, fc: eligibility.upgrade_decision(
        fc, booking_service.business_fares(s, f.id)).allowed)
    assert found, "no seeded booking has an upgrade offer"
    pnr, surname, segment_id = found
    app = create_app("en")

    with app.test_client() as client:
        _retrieve(client, pnr, surname)
        response = client.post(f"/manage/{pnr}/upgrade",
                               data={"segment_id": segment_id, "confirm": "1"})
        assert response.status_code == 302 and "/review" in response.headers["Location"]
        assert client.get(response.headers["Location"]).status_code == 200

    with app.test_request_context():
        session = database.session()
        booking = booking_service.by_pnr(session, pnr)
        row = session.scalars(select(UpgradePurchase).where(
            UpgradePurchase.booking_id == booking.id)).one()
        assert row.is_paid is False and row.price_usd > 0
        assert row.reference_no.startswith("UP-")
    _assert_nothing_paid(app)


def test_full_cabin_blocks_upgrade():
    found = _find(lambda s, b, seg, f, fc: eligibility.upgrade_decision(
        fc, booking_service.business_fares(s, f.id)).code == "CABIN_FULL")
    assert found, "no seeded booking hits a full business cabin"
    pnr, surname, segment_id = found
    app = create_app("en")
    with app.test_client() as client:
        _retrieve(client, pnr, surname)
        assert client.post(f"/manage/{pnr}/upgrade",
                           data={"segment_id": segment_id, "confirm": "1"}).status_code == 409


def test_extra_baggage_creates_pending_purchase():
    found = _find(lambda s, b, seg, f, fc: True)
    pnr, surname, segment_id = found
    app = create_app("en")

    with app.test_client() as client:
        _retrieve(client, pnr, surname)
        assert client.get(f"/manage/{pnr}/baggage?segment_id={segment_id}").status_code == 200
        response = client.post(f"/manage/{pnr}/baggage",
                               data={"segment_id": segment_id, "extra_kg": 23})
        assert response.status_code == 302 and "/review" in response.headers["Location"]
        assert client.get(response.headers["Location"]).status_code == 200

    with app.test_request_context():
        session = database.session()
        booking = booking_service.by_pnr(session, pnr)
        row = session.scalars(select(BaggagePurchase).where(
            BaggagePurchase.booking_id == booking.id)).one()
        assert row.extra_kg == 23 and row.price_usd > 0 and row.is_paid is False
    _assert_nothing_paid(app)


def test_change_creates_pending_request_with_fee_rules():
    found = _find(lambda s, b, seg, f, fc:
                  eligibility.change_decision(fc, seg, f).allowed)
    assert found, "no seeded booking is changeable"
    pnr, surname, segment_id = found
    app = create_app("en")

    with app.test_client() as client:
        _retrieve(client, pnr, surname)
        page = client.get(f"/manage/{pnr}/change?segment_id={segment_id}")
        assert page.status_code == 200

        with app.test_request_context():
            session = database.session()
            booking = booking_service.by_pnr(session, pnr)
            view = next(v for v in booking_service.itinerary(session, booking)
                        if v.segment.id == segment_id)
            from app.blueprints.flows import _alternative_flights
            alternatives = _alternative_flights(session, view)
        assert alternatives, "no alternative flights to change to"

        response = client.post(f"/manage/{pnr}/change",
                               data={"segment_id": segment_id,
                                     "new_flight_id": alternatives[0]["flight"].id})
        assert response.status_code == 302 and "/review" in response.headers["Location"]
        assert client.get(response.headers["Location"]).status_code == 200

    with app.test_request_context():
        session = database.session()
        booking = booking_service.by_pnr(session, pnr)
        row = session.scalars(select(ChangeRequest).where(
            ChangeRequest.booking_id == booking.id)).one()
        assert row.is_paid is False and row.status == "pending"
        assert row.total_due_usd == pytest.approx(row.fare_difference_usd + row.change_fee_usd)
    _assert_nothing_paid(app)


@pytest.mark.parametrize("language", ["en", "am"])
def test_pay_button_exists_enabled_and_does_nothing(language):
    found = _find(lambda s, b, seg, f, fc: True, language)
    pnr, surname_en, segment_id = found
    app = create_app(language)
    with app.test_request_context():
        session = database.session()
        booking = booking_service.by_pnr(session, pnr)
        surname = booking.surname_am if language == "am" else booking.surname_en

    with app.test_client() as client:
        _retrieve(client, pnr, surname)
        client.post(f"/manage/{pnr}/baggage", data={"segment_id": segment_id, "extra_kg": 10})
        url = f"/manage/{pnr}/baggage/review?segment_id={segment_id}"

        page = client.get(url).get_data(as_text=True)
        assert 'type="submit"' in page, "no Pay control on the review page"
        assert "disabled" not in page, "the Pay button must not render disabled"

        pressed = client.post(url, data={"segment_id": segment_id, "action": "pay"})
        assert pressed.status_code == 200
        assert "payment-notice" in pressed.get_data(as_text=True), \
            "pressing Pay produced no inline notice"

    _assert_nothing_paid(app)


def test_no_route_confirms_a_payment():
    app = create_app("en")
    suspicious = [str(r) for r in app.url_map.iter_rules()
                  if any(word in str(r) for word in ("/paid", "/payment-success",
                                                     "/confirmation", "/receipt-paid"))]
    assert not suspicious, f"routes that imply a completed payment: {suspicious}"
