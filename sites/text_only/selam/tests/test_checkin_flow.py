import sqlite3

import pytest
from pypdf import PdfReader

from app import create_app
from app import db as database
from app.models.booking import Booking
from app.models.checkin import BoardingPass, Checkin
from app.models.network import Flight
from app.services.eligibility import checkin_decision
from conftest import ROOT

GEEZ_RANGE = range(0x1200, 0x137D)


def _eligible_pnrs(language="en", limit=6):
    app = create_app(language)
    found = []
    with app.test_request_context():
        session = database.session()
        for booking in session.query(Booking).order_by(Booking.id):
            segment = booking.segments[0]
            flight = session.get(Flight, segment.flight_id)
            if checkin_decision(booking, segment, flight).allowed:
                found.append((booking.pnr, booking.surname_en, booking.surname_am))
            if len(found) >= limit:
                break
    return found


ELIGIBLE = _eligible_pnrs()


@pytest.mark.slow
@pytest.mark.parametrize("language", ["en", "am"])
def test_checkin_produces_a_boarding_pass(language):
    app = create_app(language)
    client = app.test_client()
    pnr, surname_en, surname_am = ELIGIBLE[0]
    surname = surname_am if language == "am" else surname_en

    listing = client.post("/checkin", data={"pnr": pnr, "surname": surname})
    assert listing.status_code == 200

    with app.test_request_context():
        session = database.session()
        booking = session.query(Booking).filter_by(pnr=pnr).one()
        segment_id = booking.segments[0].id

    done = client.post("/checkin", data={"pnr": pnr, "surname": surname, "segment_id": segment_id})
    assert done.status_code == 200, done.get_data(as_text=True)[:400]

    with app.test_request_context():
        session = database.session()
        records = session.query(BoardingPass).all()
        checkins = session.query(Checkin).all()
        assert records, "no boarding pass row was written"
        assert checkins, "no check-in row was written"
        assert records[0].barcode_payload.startswith(f"{pnr}|{segment_id}|")
        assert session.query(Booking).filter_by(pnr=pnr).one().segments[0].checked_in

    pdf_response = client.get(f"/checkin/{records[0].id}/boarding-pass.pdf")
    assert pdf_response.status_code == 200
    assert pdf_response.data[:4] == b"%PDF"


@pytest.mark.slow
def test_amharic_boarding_pass_contains_readable_geez(tmp_path):
    app = create_app("am")
    client = app.test_client()
    pnr, _, surname_am = ELIGIBLE[1]

    client.post("/checkin", data={"pnr": pnr, "surname": surname_am})
    with app.test_request_context():
        session = database.session()
        booking = session.query(Booking).filter_by(pnr=pnr).one()
        segment_id = booking.segments[0].id
    client.post("/checkin", data={"pnr": pnr, "surname": surname_am, "segment_id": segment_id})

    with app.test_request_context():
        session = database.session()
        record = session.query(BoardingPass).order_by(BoardingPass.id.desc()).first()

    response = client.get(f"/checkin/{record.id}/boarding-pass.pdf")
    out = tmp_path / "pass.pdf"
    out.write_bytes(response.data)

    text = "\n".join(page.extract_text() or "" for page in PdfReader(out).pages)
    geez = [c for c in text if ord(c) in GEEZ_RANGE]
    assert geez, (
        "no Ge'ez codepoints extracted from the Amharic boarding pass -- the "
        f"bundled font probably failed to register. Extracted: {text[:200]!r}"
    )
    assert "ሰላም" in text, f"airline name missing from the pass: {text[:200]!r}"


@pytest.mark.slow
def test_ineligible_checkin_explains_itself():
    app = create_app("en")
    with app.test_request_context():
        session = database.session()
        blocked = None
        for booking in session.query(Booking).order_by(Booking.id):
            segment = booking.segments[0]
            flight = session.get(Flight, segment.flight_id)
            decision = checkin_decision(booking, segment, flight)
            if not decision.allowed and decision.code not in ("TOO_EARLY", "CLOSED"):
                blocked = (booking.pnr, booking.surname_en, segment.id, decision.code)
                break
    assert blocked, "no seeded booking exhibits a flag-based check-in refusal"

    pnr, surname, segment_id, code = blocked
    client = app.test_client()
    response = client.post("/checkin", data={"pnr": pnr, "surname": surname, "segment_id": segment_id})
    assert response.status_code == 409
    body = response.get_data(as_text=True)
    assert "badge-warn" in body, "refusal did not render a reason"


def test_itinerary_pdf_renders_geez_in_the_amharic_build(tmp_path):
    app = create_app("am")
    with app.test_request_context():
        session = database.session()
        booking = session.query(Booking).order_by(Booking.id).first()
        pnr, surname = booking.pnr, booking.surname_am

    client = app.test_client()
    client.post("/manage", data={"pnr": pnr, "surname": surname},
                follow_redirects=True)
    response = client.get(f"/manage/{pnr}/itinerary.pdf")
    assert response.status_code == 200, response.status_code

    out = tmp_path / "itinerary.pdf"
    out.write_bytes(response.data)
    text = "\n".join(page.extract_text() or "" for page in PdfReader(out).pages)

    assert [c for c in text if ord(c) in GEEZ_RANGE], (
        f"no Ge'ez extracted from the Amharic itinerary: {text[:200]!r}")
    assert pnr in text, f"the booking reference is missing: {text[:200]!r}"
