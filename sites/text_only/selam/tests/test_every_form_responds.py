from __future__ import annotations

import re

import pytest

from app import create_app
from app import db as database
from sqlalchemy import select

from app.models.booking import Booking

SAMPLES = {"city": "NBO", "offer_id": "1", "flight_no": "SM120", "origin": "ADD",
           "destination": "NBO", "category": "baggage", "checkin_id": "1",
           "slug": "cabin-baggage", "iata": "ADD", "country": "ET",
           "fare_class": "EF", "id": "1"}

SKIP = {"/reset"}


def _urls(app, pnr: str) -> list[str]:
    samples = dict(SAMPLES, pnr=pnr)
    urls = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        if "POST" not in rule.methods or rule.rule in SKIP:
            continue
        url = rule.rule
        for token in re.findall(r"<[^>]+>", url):
            name = token.strip("<>").split(":")[-1]
            if name not in samples:
                url = None
                break
            url = url.replace(token, samples[name])
        if url:
            urls.append(url)
    return urls


@pytest.mark.parametrize("language", ["en", "am"])
def test_every_post_route_answers_an_empty_submission(language):
    app = create_app(language)
    with app.app_context():
        session = database.session()
        booking = session.scalars(select(Booking).order_by(Booking.id)).first()
        pnr = booking.pnr
        surname = booking.surname

    client = app.test_client()
    client.post("/manage", data={"pnr": pnr, "surname": surname},
                follow_redirects=True)

    failures = []
    for url in _urls(app, pnr):
        response = client.post(url, data={}, follow_redirects=True)
        if response.status_code >= 500:
            failures.append(f"{url} -> {response.status_code}")
            continue
        body = response.get_data(as_text=True)
        if "<html" not in body.lower():
            failures.append(f"{url} -> {response.status_code}, body is not a page")

    assert not failures, (
        f"{language}: POST routes that did not answer with a page:\n  "
        + "\n  ".join(failures))


@pytest.mark.parametrize("language", ["en", "am"])
def test_every_post_route_is_reachable_by_a_get(language):
    app = create_app(language)
    with app.app_context():
        session = database.session()
        pnr = session.scalars(select(Booking.pnr).order_by(Booking.id)).first()

    get_rules = {r.rule for r in app.url_map.iter_rules() if "GET" in r.methods}
    orphans = [
        rule.rule for rule in app.url_map.iter_rules()
        if "POST" in rule.methods and rule.rule not in SKIP
        and rule.rule not in get_rules
    ]
    assert not orphans, (
        "POST-only routes with no page of their own; an agent can reach these "
        f"only by guessing the URL: {sorted(orphans)}")
