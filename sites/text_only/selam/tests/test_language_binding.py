import re

import pytest

from app import create_app

GEEZ = re.compile(r"[ሀ-፿]")
LATIN = re.compile(r"[A-Za-z]{3,}")


@pytest.fixture(scope="module")
def clients():
    english = create_app("en")
    amharic = create_app("am")
    return english.test_client(), amharic.test_client()


def test_english_build_stays_english_after_amharic_is_constructed(clients):
    english, _ = clients
    html = english.get("/").get_data(as_text=True)
    assert not GEEZ.search(html), "the English build rendered Ge'ez"
    assert "Selam Airways" in html


def test_amharic_build_stays_amharic(clients):
    _, amharic = clients
    html = amharic.get("/").get_data(as_text=True)
    assert GEEZ.search(html), "the Amharic build rendered no Ge'ez"
    assert "ሰላም አየር መንገድ" in html


def test_interleaved_requests_do_not_bleed(clients):
    english, amharic = clients
    for _ in range(4):
        en_html = english.get("/").get_data(as_text=True)
        am_html = amharic.get("/").get_data(as_text=True)
        assert not GEEZ.search(en_html)
        assert GEEZ.search(am_html)


def test_database_reads_follow_the_requesting_build(clients):
    english, amharic = clients
    en_html = english.get("/schedules?origin=ADD&destination=NBO").get_data(as_text=True)
    am_html = amharic.get("/schedules?origin=ADD&destination=NBO").get_data(as_text=True)
    assert not GEEZ.search(en_html)
    assert GEEZ.search(am_html)


def test_no_request_input_can_change_the_language():
    amharic = create_app("am").test_client()
    baseline = amharic.get("/").get_data(as_text=True)
    for probe in ("/?lang=en", "/?language=en", "/?locale=en_US", "/?hl=en"):
        assert amharic.get(probe).get_data(as_text=True) == baseline, f"{probe} changed output"
    for header in ({"Accept-Language": "en"}, {"X-Language": "en"}, {"X-Locale": "en"}):
        assert amharic.get("/", headers=header).get_data(as_text=True) == baseline
    amharic.set_cookie("lang", "en")
    assert amharic.get("/").get_data(as_text=True) == baseline


def test_each_build_writes_to_its_own_database():
    import sqlite3

    from app import db as database

    english = create_app("en")
    amharic = create_app("am")

    def count(app) -> int:
        with sqlite3.connect(app.config["SELAM"].db_path) as conn:
            return conn.execute("select count(*) from lounge_purchases").fetchone()[0]

    assert count(english) == 0 and count(amharic) == 0

    with english.test_client() as client:
        lounge_id = 1
        client.post("/lounges/purchase", data={
            "lounge_id": lounge_id, "passenger_name": "Test Passenger", "guests": 0,
        })

    assert count(english) == 1, "the English write did not reach the English database"
    assert count(amharic) == 0, "the English write leaked into the Amharic database"


def test_reset_only_affects_the_calling_build():
    import sqlite3

    english = create_app("en")
    amharic = create_app("am")

    with amharic.test_client() as client:
        client.post("/lounges/purchase", data={
            "lounge_id": 1, "passenger_name": "ሙከራ ተሳፋሪ", "guests": 0,
        })

    def count(app) -> int:
        with sqlite3.connect(app.config["SELAM"].db_path) as conn:
            return conn.execute("select count(*) from lounge_purchases").fetchone()[0]

    assert count(amharic) == 1
    english.test_client().post("/reset")
    assert count(amharic) == 1, "resetting the English build wiped the Amharic build"
