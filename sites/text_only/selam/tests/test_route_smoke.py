import pytest

from app import create_app

SAMPLES = {
    "pnr": None,
    "checkin_id": "1",
    "fare_class": "EF",
    "iata": "ADD",
    "city": "nairobi",
    "offer_id": "1",
    "lounge_id": "1",
    "flight_no": "SM222",
    "origin": "ADD",
    "destination": "NBO",
    "country": "ET",
    "category": "baggage",
    "slug": "miles-tiers",
}

QUERY = {
    "/book/results": "?origin=ADD&destination=NBO&depart=2026-04-12&adults=1",
}


def _sample_pnr() -> str:
    import sqlite3

    from conftest import ROOT

    with sqlite3.connect(ROOT / "data" / "seed.db") as conn:
        return conn.execute("select pnr from bookings order by id limit 1").fetchone()[0]


def _urls(app) -> list[tuple[str, str]]:
    SAMPLES["pnr"] = _sample_pnr()
    out = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
        if rule.endpoint == "static":
            continue
        path = str(rule)
        missing = [a for a in rule.arguments if SAMPLES.get(a) is None]
        assert not missing, (
            f"{path} takes {missing} but tests/test_route_smoke.py has no sample "
            f"value -- add one so the route is actually exercised"
        )
        for argument in rule.arguments:
            path = path.replace(f"<{argument}>", str(SAMPLES[argument]))
            for converter in ("int:", "string:", "path:"):
                path = path.replace(f"<{converter}{argument}>", str(SAMPLES[argument]))
        method = "GET" if "GET" in rule.methods else "POST"
        out.append((method, path + QUERY.get(str(rule), "")))
    return out


@pytest.mark.slow
@pytest.mark.parametrize("language", ["en", "am"])
def test_no_route_returns_a_server_error(language):
    app = create_app(language)
    client = app.test_client()
    failures = []
    for method, url in _urls(app):
        response = client.open(url, method=method)
        if response.status_code >= 500:
            body = response.get_data(as_text=True)[:300]
            failures.append(f"{method} {url} -> {response.status_code}\n    {body}")
    assert not failures, f"{len(failures)} route(s) failed in {language}:\n" + "\n".join(failures)


@pytest.mark.slow
def test_both_builds_expose_an_identical_route_table():
    def table(language):
        return sorted(
            (str(r), tuple(sorted(r.methods)), r.endpoint)
            for r in create_app(language).url_map.iter_rules()
        )

    assert table("en") == table("am")
