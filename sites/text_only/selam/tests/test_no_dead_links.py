import re
import sqlite3

import pytest
from werkzeug.routing import RequestRedirect
from werkzeug.exceptions import MethodNotAllowed, NotFound

from app import create_app
from conftest import ROOT

HREF = re.compile(r"""(?:href|action)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)

def _pages():
    with sqlite3.connect(ROOT / "data" / "seed.db") as conn:
        pnr, surname = conn.execute(
            "select pnr, surname_en from bookings order by id limit 1").fetchone()
    return pnr, surname, [
        "/",
        "/book/search",
        "/book/results?origin=ADD&destination=NBO&depart=2026-04-12&adults=1",
        "/manage",
        "/checkin",
        "/flight-status?flight_no=SM222&date=2026-04-12",
        "/schedules?origin=ADD&destination=NBO",
        "/baggage/allowance?origin=ADD&destination=LHR&cabin=economy&pax_type=adult",
        "/baggage/fees",
        f"/manage/{pnr}",
        f"/manage/{pnr}/seats",
        f"/manage/{pnr}/refund",
        f"/manage/{pnr}/upgrade",
        f"/manage/{pnr}/baggage",
        f"/manage/{pnr}/change",
    ]


def _resolvable(adapter, url: str) -> bool:
    path = url.split("#", 1)[0].split("?", 1)[0]
    try:
        adapter.match(path, method="GET")
    except RequestRedirect:
        return True
    except MethodNotAllowed:
        return True
    except NotFound:
        return False
    return True


@pytest.mark.slow
@pytest.mark.parametrize("language", ["en", "am"])
def test_no_dead_links(language):
    app = create_app(language)
    adapter = app.url_map.bind("localhost")
    pnr, surname, pages = _pages()

    dead: dict[str, set[str]] = {}
    with app.test_client() as client:
        client.post("/manage", data={"pnr": pnr, "surname": surname},
                    follow_redirects=True)
        for page in pages:
            response = client.get(page)
            assert response.status_code < 500, f"{page} -> {response.status_code}"
            for link in HREF.findall(response.get_data(as_text=True)):
                if link.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                    continue
                if link.startswith("/static/"):
                    continue
                if not _resolvable(adapter, link):
                    dead.setdefault(link, set()).add(page)

    unplanned = {link for link in dead if not _matches_planned(_strip(link))}
    assert not unplanned, (
        "links pointing at paths that are not in app/routes_map.py -- these are "
        "typos or hand-written URLs, not unbuilt pages:\n"
        + "\n".join(f"  {link}  (from {sorted(dead[link])})" for link in sorted(unplanned))
    )


def _strip(url: str) -> str:
    return url.split("#", 1)[0].split("?", 1)[0]


def _planned_paths() -> set[str]:
    from app.routes_map import SLUGS

    out = set()
    for template in SLUGS.values():
        out.add(re.sub(r"<[^>]+>", "*", template))
    return out


PLANNED_PATHS = _planned_paths()


def _matches_planned(path: str) -> bool:
    if path in PLANNED_PATHS:
        return True
    parts = path.strip("/").split("/")
    for template in PLANNED_PATHS:
        candidate = template.strip("/").split("/")
        if len(candidate) != len(parts):
            continue
        if all(c == "*" or c == p for c, p in zip(candidate, parts)):
            return True
    return False


@pytest.mark.slow
def test_unbuilt_areas_are_tracked():
    app = create_app("en")
    registered = {re.sub(r"<[^>]+>", "*", str(rule)) for rule in app.url_map.iter_rules()}
    missing = sorted(PLANNED_PATHS - registered)
    print(f"\n{len(missing)} of {len(PLANNED_PATHS)} planned routes still unbuilt:")
    for path in missing:
        print(f"    {path}")
    assert len(missing) <= UNBUILT_CEILING, (
        f"{len(missing)} unbuilt routes exceeds the recorded ceiling of "
        f"{UNBUILT_CEILING}; lower the ceiling as areas are completed, never raise it"
    )


UNBUILT_CEILING = 0
