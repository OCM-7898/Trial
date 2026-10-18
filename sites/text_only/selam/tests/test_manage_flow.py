import sqlite3

import pytest

from app import create_app
from conftest import ROOT


def _seeded_bookings():
    with sqlite3.connect(ROOT / "data" / "seed.db") as conn:
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute(
            "select pnr, surname_en, surname_am from bookings order by id"
        )]


BOOKINGS = _seeded_bookings()


@pytest.mark.slow
@pytest.mark.parametrize("language", ["en", "am"])
def test_every_booking_retrieves_and_renders(language):
    app = create_app(language)
    surname_key = f"surname_{language}"
    failures = []

    with app.test_client() as client:
        for booking in BOOKINGS:
            response = client.post(
                "/manage",
                data={"pnr": booking["pnr"], "surname": booking[surname_key]},
                follow_redirects=True,
            )
            if response.status_code != 200:
                failures.append(f"{booking['pnr']}: retrieve -> {response.status_code}")
                continue
            body = response.get_data(as_text=True)
            if booking["pnr"] not in body:
                failures.append(f"{booking['pnr']}: detail page does not show the reference")

    assert not failures, f"{len(failures)} of {len(BOOKINGS)} failed in {language}:\n" + "\n".join(failures[:10])


@pytest.mark.parametrize("language", ["en", "am"])
def test_wrong_surname_is_refused(language):
    app = create_app(language)
    booking = BOOKINGS[0]
    with app.test_client() as client:
        response = client.post(
            "/manage", data={"pnr": booking["pnr"], "surname": "Notaname"}
        )
    assert response.status_code == 404


def test_surname_from_the_other_language_is_refused():
    booking = BOOKINGS[0]
    with create_app("am").test_client() as client:
        response = client.post(
            "/manage", data={"pnr": booking["pnr"], "surname": booking["surname_en"]}
        )
    assert response.status_code == 404, "Amharic build accepted the English surname"

    with create_app("en").test_client() as client:
        response = client.post(
            "/manage", data={"pnr": booking["pnr"], "surname": booking["surname_am"]}
        )
    assert response.status_code == 404, "English build accepted the Amharic surname"


def test_detail_requires_prior_retrieval():
    with create_app("en").test_client() as client:
        response = client.get(f"/manage/{BOOKINGS[0]['pnr']}")
    assert response.status_code == 404


def test_retrieval_is_case_and_space_insensitive():
    booking = BOOKINGS[0]
    with create_app("en").test_client() as client:
        response = client.post(
            "/manage",
            data={"pnr": f"  {booking['pnr'].lower()} ", "surname": f" {booking['surname_en'].upper()} "},
            follow_redirects=True,
        )
    assert response.status_code == 200 and booking["pnr"] in response.get_data(as_text=True)
