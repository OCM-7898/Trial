from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy import select

from app import create_app
from app import db as database
from app.models.booking import Booking
from app.models.network import Flight

ROOT = Path(__file__).resolve().parent.parent
SCANNED = list((ROOT / "app" / "templates").rglob("*.html")) + [
    ROOT / "app" / "i18n" / "en.json",
    ROOT / "app" / "i18n" / "am.json",
]

FLIGHT = re.compile(r"\bSM ?(\d{3})\b")
PNR = re.compile(r'"([A-Z0-9]{6})"')


def _seeded():
    app = create_app("en")
    with app.app_context():
        session = database.session()
        flights = {row[0] for row in session.execute(select(Flight.flight_no))}
        pnrs = {row[0] for row in session.execute(select(Booking.pnr))}
    return flights, pnrs


def test_example_flight_numbers_exist():
    flights, _ = _seeded()
    missing = {
        f"SM{number}": path.relative_to(ROOT).as_posix()
        for path in SCANNED
        for number in FLIGHT.findall(path.read_text("utf-8"))
        if f"SM{number}" not in flights
    }
    assert not missing, f"example flight numbers with no seeded flight: {missing}"


def test_example_pnrs_exist():
    _, pnrs = _seeded()
    misses = {}
    for path in SCANNED:
        text = path.read_text("utf-8")
        for candidate in PNR.findall(text):
            if not re.search(r"[A-Z]", candidate) or not re.search(r"\d", candidate):
                continue
            if candidate not in pnrs:
                misses[candidate] = path.relative_to(ROOT).as_posix()
    assert not misses, f"example booking references with no seeded booking: {misses}"
