import time

import pytest
from sqlalchemy import text

from app import create_app
from app import db as database


@pytest.fixture()
def app():
    return create_app("en")


def test_reset_restores_and_reports_clean(app):
    client = app.test_client()
    assert client.get("/reset/status").get_json()["clean"] is True

    with app.test_request_context():
        session = database.session()
        session.execute(text("update fares set price_usd = 1.0 where id = 1000000"))
        session.commit()

    assert client.get("/reset/status").get_json()["clean"] is False

    started = time.perf_counter()
    body = client.post("/reset").get_json()
    elapsed = time.perf_counter() - started

    assert body["status"] == "ok"
    assert len(body["seed_hash"]) == 64
    assert elapsed < 2.0, f"reset took {elapsed:.2f}s, budget is 2s"
    assert client.get("/reset/status").get_json()["clean"] is True


def test_reset_is_idempotent(app):
    client = app.test_client()
    hashes = {client.post("/reset").get_json()["seed_hash"] for _ in range(20)}
    assert len(hashes) == 1, f"seed hash drifted across resets: {hashes}"
