import re
import sqlite3

import pytest

from app import create_app
from app import db as database
from app.models.booking import Booking
from app.models.network import Flight
from app.services.eligibility import checkin_decision

GEEZ = re.compile(r"[ሀ-፿]")


@pytest.fixture(scope="module")
def builds():
    return {"en": create_app("en"), "am": create_app("am")}


def _rows(app, table: str) -> int:
    with sqlite3.connect(app.config["SELAM"].db_path) as conn:
        return conn.execute(f"select count(*) from {table}").fetchone()[0]


def _assert_language(app, html: str, language: str, where: str) -> None:
    has_geez = bool(GEEZ.search(html))
    if language == "am":
        assert has_geez, f"{where}: Amharic build rendered no Ge'ez"
    else:
        assert not has_geez, f"{where}: English build rendered Ge'ez"


@pytest.mark.slow
def test_interleaved_reads_keep_their_language(builds):
    pages = ["/", "/book/search", "/manage", "/checkin", "/lounges", "/help",
             "/schedules?origin=ADD&destination=NBO",
             "/baggage/allowance?origin=ADD&destination=LHR",
             "/flight-status?flight_no=SM222&date=2026-04-12",
             "/no-such-page"]
    clients = {lang: app.test_client() for lang, app in builds.items()}
    for page in pages:
        for language in ("en", "am", "am", "en"):
            html = clients[language].get(page).get_data(as_text=True)
            _assert_language(builds[language], html, language, f"GET {page}")


@pytest.mark.slow
def test_interleaved_writes_stay_in_their_own_database(builds):
    before = {lang: _rows(app, "lounge_purchases") for lang, app in builds.items()}
    clients = {lang: app.test_client() for lang, app in builds.items()}

    plan = ["en", "am", "en", "en", "am", "en", "en"]
    for language in plan:
        clients[language].post("/lounges/purchase", data={
            "lounge_id": 1,
            "passenger_name": "ሙከራ ተሳፋሪ" if language == "am" else "Test Passenger",
            "guests": 0,
        })

    expected = {"en": before["en"] + plan.count("en"), "am": before["am"] + plan.count("am")}
    actual = {lang: _rows(app, "lounge_purchases") for lang, app in builds.items()}
    assert actual == expected, f"writes crossed builds: expected {expected}, got {actual}"


@pytest.mark.slow
def test_boarding_passes_render_in_each_build_regardless_of_order(builds):
    from pypdf import PdfReader
    import io

    produced = {}
    for language in ("am", "en"):
        app = builds[language]
        client = app.test_client()
        with app.test_request_context():
            session = database.session()
            target = None
            for booking in session.query(Booking).order_by(Booking.id):
                segment = booking.segments[0]
                flight = session.get(Flight, segment.flight_id)
                if checkin_decision(booking, segment, flight).allowed:
                    target = (booking.pnr,
                              booking.surname_am if language == "am" else booking.surname_en,
                              segment.id)
                    break
        assert target, "no checkin-eligible booking"
        pnr, surname, segment_id = target
        client.post("/checkin", data={"pnr": pnr, "surname": surname})
        client.post("/checkin", data={"pnr": pnr, "surname": surname, "segment_id": segment_id})

        with app.test_request_context():
            from app.models.checkin import BoardingPass
            record = database.session().query(BoardingPass).order_by(
                BoardingPass.id.desc()).first()
        pdf = client.get(f"/checkin/{record.id}/boarding-pass.pdf").data
        text = "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(pdf)).pages)
        produced[language] = text

    assert GEEZ.search(produced["am"]), "Amharic boarding pass has no Ge'ez"
    assert not GEEZ.search(produced["en"]), "English boarding pass contains Ge'ez"


@pytest.mark.slow
def test_reset_is_scoped_to_one_build(builds):
    clients = {lang: app.test_client() for lang, app in builds.items()}
    for language in ("en", "am"):
        clients[language].post("/lounges/purchase", data={
            "lounge_id": 1, "passenger_name": "X", "guests": 0})

    clients["en"].post("/reset")
    assert _rows(builds["en"], "lounge_purchases") == 0
    assert _rows(builds["am"], "lounge_purchases") > 0, \
        "resetting one build cleared the other"

    html = clients["en"].get("/").get_data(as_text=True)
    _assert_language(builds["en"], html, "en", "after reset")
    html = clients["am"].get("/").get_data(as_text=True)
    _assert_language(builds["am"], html, "am", "after other build reset")
