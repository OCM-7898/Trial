import importlib
import json
import re

import pytest
from sqlalchemy import select

from app import create_app
from app import db as database
from conftest import ROOT

TASKS = {t["task_id"]: t for t in json.loads((ROOT / "tasks" / "tasks_en.json").read_text("utf-8"))}


def args_for(task_id: int) -> dict:
    return TASKS[task_id]["eval"].get("validator_args", {})


def run_validator(app, task_id, final_url, html=""):
    module = importlib.import_module(TASKS[task_id]["eval"]["validator"])
    with app.test_request_context():
        return module.validate(database.session(), final_url, html, **args_for(task_id))


def _book_one_way(client, app, origin, destination, depart, adults=1):
    html = client.get(f"/book/results?origin={origin}&destination={destination}"
                      f"&depart={depart}&adults={adults}").get_data(as_text=True)
    match = re.search(r"itinerary=([\w.\-]+)", html)
    assert match, f"no bookable itinerary {origin}-{destination} on {depart}"
    key = match.group(1)
    data = {"itinerary": key, "adults": adults, "contact_email": "a@example.com",
            "contact_phone": "+251111234567"}
    for index in range(1, adults + 1):
        data[f"first_name_{index}"] = "Test"
        data[f"last_name_{index}"] = f"Person{index}"
    response = client.post("/book/passengers", data=data)
    return response


@pytest.mark.slow
def test_task_2_passes_on_a_correct_booking():
    task_args = args_for(2)
    app = create_app("en")
    with app.test_client() as client:
        response = _book_one_way(client, app, task_args["origin"],
                                 task_args["destination"], task_args["depart"])
        assert response.status_code == 302
        url = response.headers["Location"]
        html = client.get(url).get_data(as_text=True)
    ok, reason = run_validator(app, 2, url, html)
    assert ok, reason


@pytest.mark.slow
def test_task_2_fails_on_the_wrong_route():
    task_args = args_for(2)
    app = create_app("en")
    with app.test_client() as client:
        response = _book_one_way(client, app, "ADD", "NBO", "2026-04-12")
        url = response.headers["Location"]
    ok, reason = run_validator(app, 2, url)
    assert not ok and "NBO" in reason, reason


@pytest.mark.slow
def test_task_2_fails_when_no_passenger_details_were_entered():
    app = create_app("en")
    ok, reason = run_validator(app, 2, "/book/review")
    assert not ok and "draft" in reason.lower()


@pytest.mark.slow
def test_booking_rejects_incomplete_passenger_details():
    app = create_app("en")
    with app.test_client() as client:
        html = client.get("/book/results?origin=ADD&destination=DXB&depart=2026-04-20"
                          "&adults=1").get_data(as_text=True)
        key = re.search(r"itinerary=([\w.\-]+)", html).group(1)
        response = client.post("/book/passengers", data={
            "itinerary": key, "adults": 1, "first_name_1": "", "last_name_1": "",
            "contact_email": "not-an-email", "contact_phone": "x"})
    assert response.status_code == 200, "an invalid form should re-render, not redirect"
    body = response.get_data(as_text=True)
    assert 'aria-invalid="true"' in body
    with app.test_request_context():
        from app.models.draft import DraftBooking
        assert not database.session().scalars(select(DraftBooking)).all(), \
            "a draft was written despite validation failing"


@pytest.mark.slow
def test_task_24_stopover_eligibility_holds_in_the_seed_data():
    app = create_app("en")
    ok, reason = run_validator(app, 24, "/stopover")
    assert ok, reason


@pytest.mark.slow
def test_stopover_page_marks_a_long_connection_eligible():
    app = create_app("en")
    with app.test_client() as client:
        html = client.get("/stopover?origin=NBO&destination=LHR&date=2026-04-12"
                          ).get_data(as_text=True)
    assert "badge-ok" in html, "no connection was marked eligible"
    assert "Services available" in html or "አገልግሎቶች" in html


@pytest.mark.slow
def test_task_25_hotel_passes_and_rejects_a_sold_out_room():
    app = create_app("en")
    with app.test_request_context():
        from app.models.partners import HotelRoom
        session = database.session()
        room = session.scalars(select(HotelRoom).where(HotelRoom.rooms_available > 0)).first()
        room_id, block, rate = room.id, room.block_hours, room.price_per_block_usd

    with app.test_client() as client:
        client.post("/partners/zena-hotel", data={
            "room_id": room_id, "arrival": "2026-04-12", "hours": 12,
            "guest_name": "Test Guest"})
    ok, reason = run_validator(app, 25, "/partners/zena-hotel?ref=HT-100001")
    assert ok, reason

    ok, reason = run_validator(app, 25, "/manage/ABC123")
    assert not ok and "zena-hotel" in reason


@pytest.mark.slow
def test_task_26_evisa_rejects_the_transit_visa():
    app = create_app("en")
    ok, reason = run_validator(app, 26, "/partners/evisa?code=EV-T30")
    assert ok, reason

    ok, reason = run_validator(app, 26, "/partners/evisa?code=EV-TR")
    assert not ok and "3 days" in reason, reason

    ok, reason = run_validator(app, 26, "/partners/evisa")
    assert not ok and "no visa type was selected" in reason


@pytest.mark.slow
def test_task_27_rail_requires_the_booking_note_to_have_been_shown():
    app = create_app("en")
    with app.test_client() as client:
        html = client.get("/partners/eurorail?arrival=FRA").get_data(as_text=True)
    ok, reason = run_validator(app, 27, "/partners/eurorail?arrival=FRA", html)
    assert ok, reason

    ok, reason = run_validator(app, 27, "/partners/eurorail?arrival=FRA", "<html></html>")
    assert not ok and "never displayed" in reason


@pytest.mark.slow
def test_task_28_car_rejects_a_vehicle_too_small_for_the_party():
    app = create_app("en")
    with app.test_request_context():
        from app.models.partners import CarOffer
        session = database.session()
        big = session.scalars(select(CarOffer).where(
            CarOffer.airport_iata == "NBO", CarOffer.seats >= 2)).first().id

    with app.test_client() as client:
        client.post("/partners/riftdrive", data={
            "offer_id": big, "airport": "NBO", "passengers": 2, "pickup": "2026-04-12"})
    ok, reason = run_validator(app, 28, "/partners/riftdrive?ref=CR-100001")
    assert ok, reason

    app = create_app("en")
    with app.test_client() as client:
        client.post("/partners/riftdrive", data={
            "offer_id": big, "airport": "NBO", "passengers": 1, "pickup": "2026-04-12"})
    ok, reason = run_validator(app, 28, "/partners/riftdrive?ref=CR-100001")
    assert not ok and "1 passenger" in reason, reason


@pytest.mark.slow
def test_task_29_insurance_requires_a_trip_cost():
    app = create_app("en")
    ok, reason = run_validator(app, 29, "/partners/safevoyage?fare=800")
    assert ok, reason

    ok, reason = run_validator(app, 29, "/partners/safevoyage")
    assert not ok and "no trip cost" in reason


@pytest.mark.slow
def test_partner_pages_do_not_use_the_airline_shell():
    app = create_app("en")
    with app.test_client() as client:
        for slug in ("zena-hotel", "evisa", "eurorail", "riftdrive", "safevoyage"):
            html = client.get(f"/partners/{slug}").get_data(as_text=True)
            assert 'class="masthead"' not in html, f"{slug} reuses the airline masthead"
            assert 'class="mainnav"' not in html, f"{slug} reuses the airline navigation"
            assert "partner-head" in html, f"{slug} has no partner header"
            assert f'data-partner="{slug}"' in html


@pytest.mark.slow
def test_partner_purchases_never_complete():
    import sqlite3

    app = create_app("en")
    with app.test_client() as client:
        client.post("/partners/zena-hotel", data={
            "room_id": 1, "arrival": "2026-04-12", "hours": 12, "guest_name": "G"})
        client.post("/partners/zena-hotel", data={"action": "pay"})
    with sqlite3.connect(app.config["SELAM"].db_path) as conn:
        for table in ("hotel_bookings", "car_bookings"):
            paid = conn.execute(f"select count(*) from {table} where is_paid = 1").fetchone()[0]
            assert paid == 0, f"{table} has a paid row"
