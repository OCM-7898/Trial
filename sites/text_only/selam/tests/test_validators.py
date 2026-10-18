import importlib
import json

import pytest
from sqlalchemy import select

from app import create_app
from app import db as database
from conftest import ROOT

TASKS = json.loads((ROOT / "tasks" / "tasks_en.json").read_text("utf-8"))
BY_ID = {task["task_id"]: task for task in TASKS}


def args_for(task_id: int) -> dict:
    return BY_ID[task_id]["eval"].get("validator_args", {})


def run_validator(app, task_id: int, final_url: str, html: str = ""):
    module = importlib.import_module(BY_ID[task_id]["eval"]["validator"])
    with app.test_request_context():
        return module.validate(database.session(), final_url, html, **args_for(task_id))


def retrieve(client, pnr: str, app) -> str:
    with app.test_request_context():
        from app.services.bookings import by_pnr
        booking = by_pnr(database.session(), pnr)
        surname = booking.surname_en
    response = client.post("/manage", data={"pnr": pnr, "surname": surname},
                           follow_redirects=True)
    assert response.status_code == 200
    return surname


@pytest.mark.slow
def test_task_13_passes_on_a_correct_run():
    task_args = args_for(13)
    app = create_app("en")
    with app.test_client() as client:
        retrieve(client, task_args["pnr"], app)
        with app.test_request_context():
            from app.services.bookings import by_pnr, itinerary
            booking = by_pnr(database.session(), task_args["pnr"])
            segment_id = itinerary(database.session(), booking)[0].segment.id
        response = client.post(f"/manage/{task_args['pnr']}/baggage",
                               data={"segment_id": segment_id,
                                     "extra_kg": task_args["expected_extra_kg"]})
        final_url = response.headers["Location"]
        html = client.get(final_url).get_data(as_text=True)

    ok, reason = run_validator(app, 13, final_url, html)
    assert ok, reason


@pytest.mark.slow
def test_task_13_fails_when_the_wrong_weight_is_added():
    task_args = args_for(13)
    app = create_app("en")
    with app.test_client() as client:
        retrieve(client, task_args["pnr"], app)
        with app.test_request_context():
            from app.services.bookings import by_pnr, itinerary
            booking = by_pnr(database.session(), task_args["pnr"])
            segment_id = itinerary(database.session(), booking)[0].segment.id
        response = client.post(f"/manage/{task_args['pnr']}/baggage",
                               data={"segment_id": segment_id, "extra_kg": 20})
        final_url = response.headers["Location"]

    ok, reason = run_validator(app, 13, final_url)
    assert not ok and "20 kg" in reason, reason


@pytest.mark.slow
def test_task_13_fails_when_the_flow_never_reaches_review():
    app = create_app("en")
    ok, reason = run_validator(app, 13, "/manage/XXXXXX/baggage")
    assert not ok and "review" in reason


@pytest.mark.slow
def test_task_10_passes_on_an_aisle_seat_and_fails_on_a_window_seat():
    task_args = args_for(10)
    pnr = task_args["pnr"]

    def choose(predicate):
        app = create_app("en")
        with app.test_client() as client:
            retrieve(client, pnr, app)
            with app.test_request_context():
                from app.services.bookings import by_pnr, itinerary
                from app.services.seats import seat_map
                session = database.session()
                booking = by_pnr(session, pnr)
                view = itinerary(session, booking)[0]
                seat = next(cell.seat.seat_no
                            for row in seat_map(session, view.segment, view.flight)
                            for cell in row.cells
                            if cell and not cell.taken and predicate(cell.seat))
                segment_id = view.segment.id
            response = client.post(f"/manage/{pnr}/seats",
                                   data={"segment_id": segment_id, "seat_no": seat})
            return app, response.headers["Location"], seat

    app, url, seat = choose(lambda s: s.is_aisle)
    ok, reason = run_validator(app, 10, url)
    assert ok, f"aisle seat {seat} rejected: {reason}"

    app, url, seat = choose(lambda s: s.is_window)
    ok, reason = run_validator(app, 10, url)
    assert not ok and "window" in reason, f"window seat {seat} accepted: {reason}"


@pytest.mark.slow
def test_task_7_passes_when_the_refusal_is_shown_and_nothing_is_written():
    task_args = args_for(7)
    app = create_app("en")
    with app.test_client() as client:
        retrieve(client, task_args["pnr"], app)
        html = client.get(f"/manage/{task_args['pnr']}/refund").get_data(as_text=True)
    ok, reason = run_validator(app, 7, f"/manage/{task_args['pnr']}/refund", html)
    assert ok, reason


@pytest.mark.slow
def test_task_7_fails_if_a_refund_request_was_somehow_created():
    from app.clock import now
    from app.models.ancillary import RefundRequest

    task_args = args_for(7)
    app = create_app("en")
    with app.test_request_context():
        session = database.session()
        from app.services.bookings import by_pnr
        booking = by_pnr(session, task_args["pnr"])
        session.add(RefundRequest(
            booking_id=booking.id, reference_no="RF-999999", status="pending",
            created_at=now().replace(tzinfo=None), is_paid=False,
            refund_pct=50, gross_usd=100.0, fee_usd=0.0, quoted_amount_usd=50.0))
        session.commit()

    ok, reason = run_validator(app, 7, f"/manage/{task_args['pnr']}/refund", "notice-warn")
    assert not ok and "refuse" in reason.lower(), reason


@pytest.mark.slow
def test_task_18_passes_on_enrolment_and_fails_on_the_wrong_email():
    task_args = args_for(18)
    app = create_app("en")
    with app.test_client() as client:
        client.post("/miles/join", data={
            "first_name": "Selamawit", "last_name": "Bekele",
            "email": task_args["email"], "country_code": "ET"})
    ok, reason = run_validator(app, 18, "/miles/join")
    assert ok, reason

    app = create_app("en")
    with app.test_client() as client:
        client.post("/miles/join", data={
            "first_name": "Selamawit", "last_name": "Bekele",
            "email": "someone.else@example.com", "country_code": "ET"})
    ok, reason = run_validator(app, 18, "/miles/join")
    assert not ok and "someone.else" in reason, reason


@pytest.mark.slow
def test_task_18_fails_when_nothing_was_created():
    app = create_app("en")
    ok, reason = run_validator(app, 18, "/miles/join")
    assert not ok and "no membership" in reason


@pytest.mark.slow
def test_task_19_passes_and_rejects_a_claim_for_the_wrong_flight():
    task_args = args_for(19)
    params = BY_ID[19]["instantiation"]["parameters"]

    app = create_app("en")
    with app.test_client() as client:
        response = client.post("/miles/claim", data={
            "member_no": task_args["member_no"], "ticket_no": params["ticket_no"],
            "flight_no": task_args["flight_no"], "flight_date": params["date"]})
        html = response.get_data(as_text=True)
    ok, reason = run_validator(app, 19, "/miles/claim", html)
    assert ok, reason

    app = create_app("en")
    with app.test_client() as client:
        client.post("/miles/claim", data={
            "member_no": task_args["member_no"], "ticket_no": params["ticket_no"],
            "flight_no": "SM999", "flight_date": params["date"]})
    ok, reason = run_validator(app, 19, "/miles/claim")
    assert not ok and "SM999" in reason, reason


@pytest.mark.slow
def test_task_16_passes_and_fails_on_the_wrong_lounge():
    task_args = args_for(16)
    app = create_app("en")
    with app.test_client() as client:
        client.post("/lounges/purchase", data={
            "lounge_id": task_args["lounge_id"], "passenger_name": "Test Passenger",
            "guests": 0})
    ok, reason = run_validator(app, 16, "/lounges/purchase/review")
    assert ok, reason

    app = create_app("en")
    with app.test_request_context():
        from app.models.content import Lounge
        other = database.session().scalars(
            select(Lounge).where(Lounge.walk_in_price_usd > 0,
                                 Lounge.id != task_args["lounge_id"])).first().id
    with app.test_client() as client:
        client.post("/lounges/purchase", data={
            "lounge_id": other, "passenger_name": "Test Passenger", "guests": 0})
    ok, reason = run_validator(app, 16, "/lounges/purchase/review")
    assert not ok, "a purchase at the wrong lounge was accepted"


@pytest.mark.slow
def test_task_8_passes_after_check_in_and_fails_before():
    task_args = args_for(8)
    app = create_app("en")
    ok, reason = run_validator(app, 8, "/checkin")
    assert not ok and "no check-in" in reason

    with app.test_client() as client:
        surname = retrieve(client, task_args["pnr"], app)
        with app.test_request_context():
            from app.services.bookings import by_pnr
            booking = by_pnr(database.session(), task_args["pnr"])
            segment_id = booking.segments[0].id
        client.post("/checkin", data={"pnr": task_args["pnr"], "surname": surname})
        client.post("/checkin", data={"pnr": task_args["pnr"], "surname": surname,
                                      "segment_id": segment_id})
    ok, reason = run_validator(app, 8, f"/checkin/1/boarding-pass.pdf")
    assert ok, reason
