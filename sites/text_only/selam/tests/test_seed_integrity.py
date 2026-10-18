import sqlite3

import pytest

from conftest import ROOT


@pytest.fixture(scope="module")
def db():
    conn = sqlite3.connect(ROOT / "data" / "seed.db")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def q(db, sql):
    return db.execute(sql).fetchall()


def test_scale_targets(db):
    counts = {t: q(db, f"select count(*) c from {t}")[0]["c"]
              for t in ("airports", "routes", "flights", "fares", "fare_classes",
                        "aircraft_types", "seat_maps")}
    assert counts["airports"] == 75
    assert counts["aircraft_types"] == 6
    assert counts["fare_classes"] == 9
    assert counts["flights"] > 10_000
    assert counts["fares"] > 80_000


def test_every_airport_has_departures_and_arrivals(db):
    orphans = q(db, """
        select iata from airports a
        where not exists (select 1 from routes r where r.origin_id = a.id)
           or not exists (select 1 from routes r where r.destination_id = a.id)
    """)
    assert not orphans, f"airports with no service: {[r['iata'] for r in orphans]}"


def test_no_orphan_fares_or_flights(db):
    assert not q(db, "select 1 from fares f left join flights fl on fl.id=f.flight_id where fl.id is null limit 5")
    assert not q(db, "select 1 from flights f left join routes r on r.id=f.route_id where r.id is null limit 5")
    assert not q(db, "select 1 from seat_maps s left join aircraft_types a on a.id=s.aircraft_id where a.id is null limit 5")


def test_every_flight_has_fares(db):
    rows = q(db, """
        select f.id from flights f
        where not exists (select 1 from fares x where x.flight_id = f.id) limit 5
    """)
    assert not rows, f"flights with no fare: {[r['id'] for r in rows]}"


def test_business_fares_only_on_aircraft_with_a_business_cabin(db):
    rows = q(db, """
        select distinct a.code from fares fa
        join fare_classes fc on fc.id = fa.fare_class_id
        join flights f on f.id = fa.flight_id
        join aircraft_types a on a.id = f.aircraft_id
        where fc.cabin = 'business' and a.rows_business = 0
    """)
    assert not rows, f"business fares sold on all-economy aircraft: {[r['code'] for r in rows]}"


def test_flights_only_on_operating_days(db):
    rows = q(db, """
        select f.flight_no, f.date, r.operating_days
        from flights f join routes r on r.id = f.route_id limit 200000
    """)
    import datetime
    bad = [r for r in rows
           if r["operating_days"][datetime.date.fromisoformat(r["date"]).weekday()] == "."]
    assert not bad, f"{len(bad)} flights on non-operating days, e.g. {bad[:3]}"


def test_seat_maps_have_windows_and_aisles(db):
    for code in ("Q40", "73H", "359"):
        row = q(db, f"""
            select sum(is_window) w, sum(is_aisle) i, count(*) n
            from seat_maps s join aircraft_types a on a.id = s.aircraft_id
            where a.code = '{code}'
        """)[0]
        assert row["n"] > 0 and row["w"] > 0 and row["i"] > 0, f"{code}: {dict(row)}"


def test_no_flight_has_departed_before_the_frozen_clock_reaches_it():
    from datetime import datetime

    from sqlalchemy import select

    from app import create_app
    from app import db as database
    from app.clock import FROZEN_NOW
    from app.models.network import Flight

    app = create_app("en")
    with app.app_context():
        flights = list(database.session().scalars(select(Flight)))
    now = FROZEN_NOW.replace(tzinfo=None)

    too_early = [
        f"{f.flight_no} {f.date} {f.dep_time} is {f.status}"
        for f in flights
        if datetime.combine(f.date, f.dep_time) > now and f.status == "departed"
    ]
    too_late = [
        f"{f.flight_no} {f.date} {f.dep_time} is {f.status}"
        for f in flights
        if datetime.combine(f.date, f.dep_time) <= now and f.status == "scheduled"
    ]
    assert not too_early, f"flights that have not left are marked departed: {too_early[:5]}"
    assert not too_late, f"flights that have left are still scheduled: {too_late[:5]}"


def test_a_delayed_flight_still_lies_ahead_of_the_clock():
    from datetime import datetime

    from sqlalchemy import select

    from app import create_app
    from app import db as database
    from app.clock import FROZEN_NOW
    from app.models.network import Flight

    app = create_app("en")
    with app.app_context():
        flights = list(database.session().scalars(select(Flight)))
    now = FROZEN_NOW.replace(tzinfo=None)
    upcoming = [f for f in flights
                if datetime.combine(f.date, f.dep_time) > now and f.status == "delayed"]
    assert upcoming, "no delayed flight is still ahead of the frozen clock"


def test_a_mismatched_database_is_refused_at_startup(tmp_path):
    import shutil
    import sqlite3

    import pytest

    from app import create_app
    from app.config import Config

    seed = Config.for_language("en").seed_db
    backup = tmp_path / "seed.db"
    shutil.copyfile(seed, backup)
    try:
        connection = sqlite3.connect(seed)
        connection.execute("alter table entertainment_items drop column language_am")
        connection.commit()
        connection.close()

        with pytest.raises(RuntimeError) as raised:
            create_app("am")
        message = str(raised.value)
        assert "entertainment_items.language_am" in message, message
        assert "python seed.py" in message, "the message must name the fix"
    finally:
        shutil.copyfile(backup, seed)

    create_app("am")
