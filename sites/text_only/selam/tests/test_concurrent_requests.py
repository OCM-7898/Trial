from __future__ import annotations

import concurrent.futures as futures
import re
import threading
from collections import Counter

import pytest
from sqlalchemy import select

from app import create_app
from app import db as database
from app.models.booking import Booking
from app.models.requests import ServiceRequest

GEEZ = re.compile(r"[ሀ-፿]")
ENGLISH_NAV = re.compile(
    r"\b(Book a flight|Manage booking|Baggage allowance|Flight status|"
    r"Help centre|Check-in online)\b")

URLS = ["/", "/book/search", "/flight-status", "/schedules", "/help",
        "/baggage/special", "/lounges", "/offers", "/miles/join",
        "/travel-requirements", "/vouchers"]


@pytest.mark.slow
def test_two_builds_under_load_never_render_each_others_language():
    apps, seeds = {}, {}
    for language in ("en", "am"):
        app = create_app(language)
        with app.app_context():
            session = database.session()
            booking = session.scalars(select(Booking).order_by(Booking.id)).first()
            seeds[language] = (booking.pnr, booking.surname)
        apps[language] = app

    problems, lock = [], threading.Lock()

    def hammer(language: str) -> int:
        client = apps[language].test_client()
        pnr, surname = seeds[language]
        client.post("/manage", data={"pnr": pnr, "surname": surname},
                    follow_redirects=True)
        served = 0
        for _ in range(8):
            for url in URLS:
                body = client.get(url).get_data(as_text=True)
                served += 1
                if language == "am":
                    bad = ENGLISH_NAV.search(body) or not GEEZ.search(body)
                else:
                    bad = bool(GEEZ.search(body))
                if bad:
                    with lock:
                        problems.append(f"{language} {url}")
        return served

    with futures.ThreadPoolExecutor(max_workers=12) as pool:
        jobs = [pool.submit(hammer, language)
                for _ in range(6) for language in ("en", "am")]
        served = sum(job.result() for job in jobs)

    assert served > 1000, f"only {served} requests issued; the test did not run"
    assert not problems, (
        f"{len(problems)} responses in the wrong language under load, e.g. "
        f"{problems[:5]}")


@pytest.mark.slow
def test_concurrent_writes_never_duplicate_a_reference_number():
    app = create_app("en")
    failures, lock = [], threading.Lock()

    def write(index: int) -> int:
        client = app.test_client()
        for round_ in range(12):
            for url, payload in (
                ("/vouchers/buy", {"recipient": f"P{index}", "amount": "100"}),
                ("/help/feedback", {"category": "baggage", "name": "A",
                                    "email": "a@example.com", "message": "m"}),
            ):
                response = client.post(url, data=payload)
                if response.status_code >= 500:
                    with lock:
                        failures.append(f"{url} -> {response.status_code}")
        return 24

    with futures.ThreadPoolExecutor(max_workers=10) as pool:
        list(job.result() for job in [pool.submit(write, i) for i in range(10)])

    with app.app_context():
        session = database.session()
        references = [row[0] for row in
                      session.execute(select(ServiceRequest.reference_no))]

    duplicates = {ref: n for ref, n in Counter(references).items() if n > 1}
    assert not failures, f"server errors during concurrent writes: {failures[:5]}"
    assert not duplicates, f"duplicate reference numbers allocated: {duplicates}"
