import sqlite3

import pytest

from app import create_app
from conftest import ROOT

NASTY = [
    "", " ", "'", '"', "--", "; drop table bookings; --", "' or '1'='1",
    "<script>alert(1)</script>", "../../etc/passwd", "%00", "\x00",
    "ሰላም", "🙂", "A" * 2000,
    "-1", "0", "999999999999999999999", "1e400", "NaN", "null", "None",
    "2026-13-45", "not-a-date", "2026/04/12", "12-04-2026", "0000-00-00",
]

QUERY_TARGETS = [
    ("/book/results", ["origin", "destination", "depart", "return", "adults",
                       "cabin", "sort", "stops", "depart_band"]),
    ("/flight-status", ["flight_no", "date"]),
    ("/schedules", ["origin", "destination"]),
    ("/baggage/allowance", ["origin", "destination", "cabin", "pax_type"]),
    ("/lounges", ["airport"]),
    ("/lounges/eligibility", ["airport", "cabin", "tier"]),
    ("/miles/award-search", ["origin", "destination", "date", "cabin"]),
    ("/onboard/wifi", ["flight_no", "date"]),
    ("/onboard/dining", ["pnr"]),
    ("/help/contact", ["country"]),
    ("/stopover", ["origin", "destination", "date"]),
    ("/book/passengers", ["itinerary", "adults"]),
    ("/book/review", ["ref"]),
    ("/partners/evisa", ["code"]),
    ("/partners/eurorail", ["arrival"]),
    ("/partners/riftdrive", ["airport", "passengers", "pickup"]),
    ("/partners/safevoyage", ["fare"]),
    ("/partners/zena-hotel", ["arrival", "hours", "ref"]),
]

FORM_TARGETS = [
    ("/manage", ["pnr", "surname"]),
    ("/checkin", ["pnr", "surname", "segment_id"]),
    ("/miles/join", ["first_name", "last_name", "email", "country_code"]),
    ("/miles/claim", ["member_no", "ticket_no", "flight_no", "flight_date"]),
    ("/miles/account", ["member_no", "surname"]),
    ("/lounges/purchase", ["lounge_id", "passenger_name", "guests"]),
    ("/onboard/wifi", ["flight_no", "date", "package_id"]),
    ("/onboard/dining", ["pnr", "meal_code", "passenger_id"]),
    ("/book/passengers", ["itinerary", "adults", "first_name_1", "last_name_1",
                          "contact_email", "contact_phone"]),
    ("/partners/zena-hotel", ["room_id", "arrival", "hours", "guest_name"]),
    ("/partners/riftdrive", ["offer_id", "airport", "passengers", "pickup"]),
]


def _sample_pnr() -> str:
    with sqlite3.connect(ROOT / "data" / "seed.db") as conn:
        return conn.execute("select pnr from bookings order by id limit 1").fetchone()[0]


@pytest.fixture(scope="module")
def client():
    return create_app("en").test_client()


@pytest.mark.slow
@pytest.mark.parametrize("value", NASTY)
def test_query_parameters_survive_hostile_values(client, value):
    failures = []
    for url, parameters in QUERY_TARGETS:
        for parameter in parameters:
            response = client.get(url, query_string={parameter: value})
            if response.status_code >= 500:
                failures.append(f"GET {url}?{parameter}={value!r} -> {response.status_code}")
    assert not failures, "\n".join(failures)


@pytest.mark.slow
@pytest.mark.parametrize("value", NASTY)
def test_form_fields_survive_hostile_values(client, value):
    failures = []
    for url, fields in FORM_TARGETS:
        for field in fields:
            response = client.post(url, data={field: value})
            if response.status_code >= 500:
                failures.append(f"POST {url} {field}={value!r} -> {response.status_code}")
    assert not failures, "\n".join(failures)


@pytest.mark.slow
def test_all_query_parameters_at_once():
    client = create_app("en").test_client()
    for value in NASTY:
        response = client.get("/book/results", query_string={
            "origin": value, "destination": value, "depart": value,
            "return": value, "adults": value, "cabin": value, "sort": value,
            "stops": value, "depart_band": value,
        })
        assert response.status_code < 500, f"combined hostile query {value!r} -> {response.status_code}"


@pytest.mark.slow
def test_flow_routes_reject_nonsense_without_crashing():
    client = create_app("en").test_client()
    pnr = _sample_pnr()
    templates = [
        "/manage/{p}", "/manage/{p}/seats", "/manage/{p}/seats/review",
        "/help/contact/{p}", "/lounges/{p}", "/help/topics/{p}",
        "/manage/{p}/change", "/manage/{p}/change/review",
        "/manage/{p}/refund", "/manage/{p}/refund/review",
        "/manage/{p}/upgrade", "/manage/{p}/upgrade/review",
        "/manage/{p}/baggage", "/manage/{p}/baggage/review",
    ]
    for template in templates:
        for candidate in ("ZZZZZZ", "1", "a" * 300, "%20", "..", pnr.lower()):
            url = template.format(p=candidate)
            for method in ("GET", "POST"):
                response = client.open(url, method=method)
                assert response.status_code < 500, f"{method} {url} -> {response.status_code}"


@pytest.mark.slow
def test_seat_and_segment_ids_are_validated():
    client = create_app("en").test_client()
    with sqlite3.connect(ROOT / "data" / "seed.db") as conn:
        first = conn.execute(
            "select b.pnr, b.surname_en, s.id from bookings b "
            "join segments s on s.booking_id = b.id order by b.id limit 1").fetchone()
        other = conn.execute(
            "select s.id from segments s where s.booking_id != "
            "(select id from bookings order by id limit 1) order by s.id limit 1").fetchone()

    pnr, surname, _ = first
    foreign_segment = other[0]

    client.post("/manage", data={"pnr": pnr, "surname": surname}, follow_redirects=True)
    response = client.get(f"/manage/{pnr}/seats?segment_id={foreign_segment}")
    assert response.status_code == 404, (
        "a segment from another booking was accepted; a task could then mutate "
        "a booking it was never given"
    )


def test_no_row_id_is_passed_straight_to_session_get():
    import re
    from pathlib import Path

    from tests.conftest import python_sources

    pattern = re.compile(r"\.get\([^()]*,\s*row_id\(")
    offenders = [
        f"{path.name}:{index}"
        for path in python_sources()
        if path.name != Path(__file__).name
        for index, line in enumerate(path.read_text("utf-8").splitlines(), 1)
        if pattern.search(line)
    ]
    assert not offenders, (
        f"use get_row(session, Model, raw) instead: {offenders}")
