from __future__ import annotations

import re
from collections import deque

import pytest
from sqlalchemy import select

from app import create_app
from app import db as database
from app.models.booking import Booking
from app.routes_map import SLUGS

NOT_LINKED_ON_PURPOSE = {
    "/reset", "/reset/status",
    "/book/results", "/book/review", "/lounges/purchase/review",
    "/onboard/wifi/review",
}


def _crawl(language: str) -> set[str]:
    app = create_app(language)
    client = app.test_client()
    with app.app_context():
        booking = database.session().scalars(
            select(Booking).where(Booking.pnr == "WGYBNA")).one()
        surname = booking.surname
    client.post("/manage", data={"pnr": booking.pnr, "surname": surname},
                follow_redirects=True)
    client.post("/miles/account",
                data={"member_no": "SM00000001",
                      "surname": "Wolde" if language == "en" else "ወልደ"},
                follow_redirects=True)

    start = ["/", "/book/results?origin=ADD&destination=NBO"
                  "&depart=2026-04-12&adults=1"]
    seen, queue = {"/", "/book/results"}, deque(start)
    while queue:
        body = client.get(queue.popleft(), follow_redirects=True).get_data(as_text=True)
        for href in re.findall(r'href="(/[^"#]*)', body):
            path_only = href.split("?")[0].rstrip("/") or "/"
            if path_only.startswith("/static/") or path_only in seen:
                continue
            seen.add(path_only)
            queue.append(href)
    return seen


@pytest.mark.slow
@pytest.mark.parametrize("language", ["en", "am"])
def test_every_service_route_can_be_reached_by_clicking(language):
    reachable = _crawl(language)
    declared = {rule.rstrip("/") or "/" for rule in SLUGS.values() if "<" not in rule}
    orphaned = sorted(declared - reachable - NOT_LINKED_ON_PURPOSE)
    assert not orphaned, (
        f"{language}: {len(orphaned)} routes that nothing links to. Add a link "
        f"from the page they belong under, or list them in "
        f"NOT_LINKED_ON_PURPOSE with a reason:\n  " + "\n  ".join(orphaned))


@pytest.mark.slow
def test_both_builds_reach_exactly_the_same_pages():
    english, amharic = _crawl("en"), _crawl("am")
    assert english == amharic, {
        "only reachable in English": sorted(english - amharic)[:10],
        "only reachable in Amharic": sorted(amharic - english)[:10],
    }


def test_the_exemption_list_stays_honest():
    declared = {rule.rstrip("/") or "/" for rule in SLUGS.values() if "<" not in rule}
    stale = sorted(NOT_LINKED_ON_PURPOSE - declared)
    assert not stale, f"exemptions for routes that no longer exist: {stale}"
