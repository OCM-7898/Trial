import sqlite3

import pytest
from sqlalchemy import select

from app import create_app
from app import db as database
from app.models.loyalty import LoyaltyMember, MissingMilesClaim
from app.services.loyalty import TIERS, progress, tier_for
from conftest import ROOT


def _seeded_member(language="en"):
    with sqlite3.connect(ROOT / "data" / "seed.db") as conn:
        return conn.execute(
            f"select member_no, last_name_{language}, tier, qualifying_miles, miles_balance "
            "from loyalty_members order by id limit 1").fetchone()


@pytest.mark.parametrize("language", ["en", "am"])
def test_enrolment_returns_a_predictable_membership_number(language):
    app = create_app(language)
    with app.test_request_context():
        highest = database.session().scalars(
            select(LoyaltyMember.member_no).order_by(LoyaltyMember.member_no.desc())
        ).first()
    expected = f"SM{int(highest[2:]) + 1:08d}"

    with app.test_client() as client:
        response = client.post("/miles/join", data={
            "first_name": "Test", "last_name": "Person",
            "email": "new.member@example.com", "country_code": "ET",
        })
    assert response.status_code == 200
    assert expected in response.get_data(as_text=True), \
        f"expected the next number in sequence, {expected}"

    with app.test_request_context():
        member = database.session().scalars(
            select(LoyaltyMember).where(LoyaltyMember.member_no == expected)).one()
        assert member.tier == "blue" and member.miles_balance == 0
        assert member.created_at_runtime is True, \
            "runtime enrolments must be distinguishable from seeded members"


def test_duplicate_email_is_rejected():
    app = create_app("en")
    with app.test_request_context():
        existing = database.session().scalars(select(LoyaltyMember)).first().email
    with app.test_client() as client:
        response = client.post("/miles/join", data={
            "first_name": "A", "last_name": "B", "email": existing, "country_code": "ET"})
    assert response.status_code == 400
    with create_app("en").test_request_context():
        count = database.session().scalars(
            select(LoyaltyMember).where(LoyaltyMember.email == existing)).all()
    assert len(count) == 1, "a duplicate account was created"


def test_missing_miles_claim_returns_a_sequential_reference():
    member_no = _seeded_member()[0]
    app = create_app("en")
    with app.test_client() as client:
        response = client.post("/miles/claim", data={
            "member_no": member_no, "ticket_no": "0712345678901",
            "flight_no": "SM222", "flight_date": "2026-02-14"})
    assert response.status_code == 200
    body = response.get_data(as_text=True)

    with app.test_request_context():
        record = database.session().scalars(select(MissingMilesClaim)).one()
    assert record.reference_no.startswith("MC-") and len(record.reference_no) == 9
    assert record.reference_no in body, "the reference must be shown to the agent"
    assert record.status == "under_review"


def test_claim_for_a_future_flight_is_rejected():
    member_no = _seeded_member()[0]
    with create_app("en").test_client() as client:
        response = client.post("/miles/claim", data={
            "member_no": member_no, "ticket_no": "0712345678901",
            "flight_no": "SM222", "flight_date": "2026-05-20"})
    assert response.status_code == 400
    with create_app("en").test_request_context():
        assert not database.session().scalars(select(MissingMilesClaim)).all()


def test_seeded_tiers_agree_with_their_qualifying_miles():
    with sqlite3.connect(ROOT / "data" / "seed.db") as conn:
        rows = conn.execute(
            "select member_no, tier, qualifying_miles from loyalty_members").fetchall()
    wrong = [(m, t, q) for m, t, q in rows if tier_for(q) != t]
    assert not wrong, f"tier does not match qualifying miles: {wrong}"


def test_statement_sums_to_the_displayed_balance():
    with sqlite3.connect(ROOT / "data" / "seed.db") as conn:
        rows = conn.execute("""
            select m.member_no, m.miles_balance, m.qualifying_miles,
                   coalesce(sum(t.miles), 0), coalesce(sum(t.qualifying_miles), 0)
            from loyalty_members m
            left join miles_transactions t on t.member_id = m.id
            group by m.id""").fetchall()
    bad = [r for r in rows if r[1] != r[3] or r[2] != r[4]]
    assert not bad, f"statement disagrees with the headline figures: {bad}"


def test_award_search_shows_available_seats_and_hides_sold_out():
    with sqlite3.connect(ROOT / "data" / "seed.db") as conn:
        available = conn.execute("""
            select ao.iata, ad.iata, f.date, ai.miles_required
            from award_inventory ai
            join flights f on f.id = ai.flight_id
            join routes r on r.id = f.route_id
            join airports ao on ao.id = r.origin_id
            join airports ad on ad.id = r.destination_id
            where ai.seats > 0 order by ai.id limit 1""").fetchone()
        sold_out_total = conn.execute(
            "select count(*) from award_inventory where seats = 0").fetchone()[0]

    assert available, "no bookable award inventory at all"
    assert sold_out_total > 0, "no sold-out rows, so the filter is untested"

    origin, destination, day, miles = available
    with create_app("en").test_client() as client:
        html = client.get(f"/miles/award-search?origin={origin}&destination={destination}"
                          f"&date={day}").get_data(as_text=True)
    assert str(miles) in html, f"{origin}-{destination} on {day} should offer {miles} miles"


def test_sold_out_awards_are_not_listed():
    with sqlite3.connect(ROOT / "data" / "seed.db") as conn:
        row = conn.execute("""
            select ao.iata, ad.iata, f.date
            from award_inventory ai
            join flights f on f.id = ai.flight_id
            join routes r on r.id = f.route_id
            join airports ao on ao.id = r.origin_id
            join airports ad on ad.id = r.destination_id
            where ai.seats = 0
              and not exists (select 1 from award_inventory x
                              where x.flight_id = ai.flight_id and x.seats > 0)
            order by ai.id limit 1""").fetchone()
    if not row:
        pytest.skip("every flight with a sold-out award also has an available one")
    origin, destination, day = row
    with create_app("en").test_client() as client:
        html = client.get(f"/miles/award-search?origin={origin}&destination={destination}"
                          f"&date={day}").get_data(as_text=True)
    assert "notice-warn" in html, "a sold-out flight was presented as bookable"


@pytest.mark.parametrize("qualifying,expected", [
    (0, "blue"), (24_999, "blue"), (25_000, "silver"),
    (49_999, "silver"), (50_000, "gold"), (99_999, "gold"), (100_000, "platinum"),
])
def test_tier_boundaries(qualifying, expected):
    assert tier_for(qualifying) == expected
