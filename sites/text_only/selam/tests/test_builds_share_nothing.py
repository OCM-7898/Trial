from __future__ import annotations

import io
import re

import pytest
from pypdf import PdfReader
from sqlalchemy import select

from app import create_app
from app import db as database
from app import lang
from app.config import Config
from app.models.booking import Booking
from app.models.checkin import BoardingPass

GEEZ = range(0x1200, 0x1380)


def _has_geez(text: str) -> bool:
    return any(ord(ch) in GEEZ for ch in text)


def _surname(app, pnr: str) -> str:
    with app.app_context():
        return database.session().scalars(
            select(Booking).where(Booking.pnr == pnr)).one().surname


def _check_in(app, pnr: str):
    client = app.test_client()
    surname = _surname(app, pnr)
    client.post("/checkin", data={"pnr": pnr, "surname": surname},
                follow_redirects=True)
    body = client.post("/checkin", data={"pnr": pnr, "surname": surname},
                       follow_redirects=True).get_data(as_text=True)
    segment = re.search(r'name="segment_id"[^>]*value="(\d+)"', body)
    assert segment, "check-in offered no segment"
    client.post("/checkin", data={"pnr": pnr, "surname": surname,
                                  "segment_id": segment.group(1)},
                follow_redirects=True)
    return client


def _boarding_pass_text(app, client) -> str:
    with app.app_context():
        record = database.session().scalars(
            select(BoardingPass).order_by(BoardingPass.id)).first()
    assert record is not None, "no boarding pass was created"
    data = client.get(f"/checkin/{record.id}/boarding-pass.pdf").data
    return "\n".join(page.extract_text() or ""
                     for page in PdfReader(io.BytesIO(data)).pages)


def test_no_writable_path_is_shared_between_the_builds():
    english, amharic = Config.for_language("en"), Config.for_language("am")
    shared = [
        name for name in ("db_path", "generated_dir", "secret_key", "session_cookie")
        if getattr(english, name) == getattr(amharic, name)
    ]
    assert not shared, f"both builds write to or authenticate with: {shared}"
    assert english.seed_db == amharic.seed_db


def test_a_boarding_pass_stays_in_its_own_language():
    english, amharic = create_app("en"), create_app("am")

    english_client = _check_in(english, "WGYBNA")
    before = _boarding_pass_text(english, english_client)
    assert not _has_geez(before), "the English pass was never in English"

    _check_in(amharic, "WGYBNA")
    after = _boarding_pass_text(english, english_client)

    assert not _has_geez(after), (
        "the English build served a Ge'ez boarding pass after the same booking "
        "was checked in on the Amharic build")
    assert after == before, "the English pass changed when the Amharic build ran"


def test_a_reset_leaves_the_other_builds_files_alone():
    english, amharic = create_app("en"), create_app("am")
    _check_in(english, "WGYBNA")
    _check_in(amharic, "WGYBNA")

    amharic_dir = amharic.config["SELAM"].generated_dir
    before = sorted(p.name for p in amharic_dir.glob("*.pdf"))
    assert before, "the Amharic build produced no PDFs to protect"

    english.test_client().post("/reset")

    after = sorted(p.name for p in amharic_dir.glob("*.pdf"))
    assert after == before, (
        "resetting the English build deleted the Amharic build's boarding passes")


def test_a_session_from_one_build_does_not_authenticate_on_the_other():
    english, amharic = create_app("en"), create_app("am")
    english_client = english.test_client()
    english_client.post("/manage", data={"pnr": "WGYBNA",
                                         "surname": _surname(english, "WGYBNA")},
                        follow_redirects=True)
    cookies = {key[-1]: morsel.value for key, morsel in english_client._cookies.items()}
    assert cookies, "the English build set no session cookie"

    amharic_client = amharic.test_client()
    for name, value in cookies.items():
        amharic_client.set_cookie(name, value, domain="localhost")

    response = amharic_client.get("/manage/WGYBNA", follow_redirects=True)
    assert "SM111" not in response.get_data(as_text=True), (
        "the Amharic build honoured a session established on the English build; "
        "cookies are not scoped by port, so the two must not share a name or key")


@pytest.mark.parametrize("built_last", ["en", "am"])
def test_an_app_context_reads_its_own_language(built_last):
    first = "am" if built_last == "en" else "en"
    apps = {first: create_app(first), built_last: create_app(built_last)}

    for language, app in apps.items():
        with app.app_context():
            surname = database.session().scalars(
                select(Booking).where(Booking.pnr == "WGYBNA")).one().surname
        if language == "am":
            assert _has_geez(surname), f"the Amharic app read {surname!r}"
        else:
            assert not _has_geez(surname), f"the English app read {surname!r}"
            assert surname == "Assefa", surname


def test_the_process_default_still_applies_with_no_app():
    lang.set_active("en")
    assert lang.active() == "en"
    lang.set_active("am")
    assert lang.active() == "am"
    lang.set_active("en")
