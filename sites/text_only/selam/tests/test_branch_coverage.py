from collections import Counter

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.network import Fare, FareClass, Flight
from app.services.eligibility import (
    CHECKIN_PRECEDENCE, change_decision, checkin_decision, refund_decision,
    upgrade_decision,
)
from conftest import ROOT


@pytest.fixture(scope="module")
def decisions():
    engine = create_engine(f"sqlite:///{ROOT / 'data' / 'seed.db'}")
    out = {"checkin": Counter(), "refund": Counter(), "upgrade": Counter(),
           "change": Counter(), "channel": Counter(), "seats": Counter()}
    with Session(engine) as session:
        for booking in session.scalars(select(Booking)):
            segment = booking.segments[0]
            flight = session.get(Flight, segment.flight_id)
            fare_class = session.get(FareClass, segment.fare_class_id)
            business = list(session.scalars(
                select(Fare).join(FareClass)
                .where(Fare.flight_id == flight.id, FareClass.cabin == "business")
            ))
            out["checkin"][checkin_decision(booking, segment, flight).code or "ELIGIBLE"] += 1
            out["refund"][refund_decision(booking, fare_class).code or "REFUNDABLE"] += 1
            out["upgrade"][upgrade_decision(fare_class, business).code or "OFFER"] += 1
            out["change"][change_decision(fare_class, segment, flight).code or "CHANGEABLE"] += 1
            out["channel"][booking.booked_channel] += 1
    return out


def test_all_checkin_codes_are_reachable(decisions):
    seen = set(decisions["checkin"])
    missing = (set(CHECKIN_PRECEDENCE) | {"ELIGIBLE"}) - seen
    assert not missing, f"no seeded booking produces: {sorted(missing)}"


def test_refund_branches(decisions):
    for code in ("REFUNDABLE", "FARE_NON_REFUNDABLE", "OFFLINE_CHANNEL_ONLY"):
        assert decisions["refund"][code] > 0, f"refund branch missing: {code}"


def test_upgrade_branches(decisions):
    for code in ("OFFER", "CABIN_FULL", "FARE_CLASS_EXCLUDED"):
        assert decisions["upgrade"][code] > 0, f"upgrade branch missing: {code}"


def test_change_branches(decisions):
    for code in ("CHANGEABLE", "FARE_NOT_CHANGEABLE", "TOO_LATE_TO_CHANGE"):
        assert decisions["change"][code] > 0, f"change branch missing: {code}"


def test_all_booking_channels_present(decisions):
    for channel in ("website", "agent", "call_centre", "corporate"):
        assert decisions["channel"][channel] > 0, f"no booking made via {channel}"


def test_pnrs_are_unique_and_well_formed(decisions):
    engine = create_engine(f"sqlite:///{ROOT / 'data' / 'seed.db'}")
    with Session(engine) as session:
        pnrs = [b.pnr for b in session.scalars(select(Booking))]
    assert len(pnrs) == len(set(pnrs)) == 60
    assert all(len(p) == 6 and p.isalnum() and p.isupper() for p in pnrs)
    assert not any(set(p) & set("IO01") for p in pnrs), "PNR contains a confusable character"


def test_seeded_surnames_exist_in_both_scripts():
    engine = create_engine(f"sqlite:///{ROOT / 'data' / 'seed.db'}")
    with Session(engine) as session:
        rows = session.execute(select(Booking.pnr, Booking.surname_en, Booking.surname_am)).all()
    bad = [r.pnr for r in rows if not (r.surname_en or "").strip() or not (r.surname_am or "").strip()]
    assert not bad, f"bookings missing a surname in one script: {bad}"
