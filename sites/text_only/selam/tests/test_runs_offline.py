from __future__ import annotations

import re
import socket

import pytest

from app import create_app

ROUTES = [
    "/", "/book/search", "/flight-status", "/schedules", "/network",
    "/baggage/allowance", "/baggage/special", "/lounges", "/miles/join",
    "/miles/award-search", "/onboard/wifi", "/onboard/dining", "/stopover",
    "/help", "/help/contact", "/offers", "/travel-requirements", "/vouchers",
    "/cargo", "/onboard/entertainment", "/partners", "/partners/zena-hotel",
    "/checkin", "/manage",
]

EXTERNAL = re.compile(r'(?:href|src|action)\s*=\s*["\'](?:[a-z]+:)?//', re.I)


class _NoNetwork(socket.socket):
    def __init__(self, *args, **kwargs):
        raise AssertionError(
            "the build opened a socket; nothing may touch the network at runtime")


@pytest.mark.parametrize("language", ["en", "am"])
def test_no_route_opens_a_socket(language, monkeypatch):
    app = create_app(language)
    client = app.test_client()
    client.get("/")

    monkeypatch.setattr(socket, "socket", _NoNetwork)
    monkeypatch.setattr(socket, "create_connection", _NoNetwork)

    for url in ROUTES:
        response = client.get(url)
        assert response.status_code < 500, f"{url} -> {response.status_code}"


@pytest.mark.parametrize("language", ["en", "am"])
def test_no_page_references_an_external_url(language):
    app = create_app(language)
    client = app.test_client()

    offenders = []
    for url in ROUTES:
        body = client.get(url).get_data(as_text=True)
        for match in EXTERNAL.finditer(body):
            snippet = body[match.start():match.start() + 90].replace("\n", " ")
            offenders.append(f"{url}: {snippet}")

    assert not offenders, (
        "pages referencing something the browser would fetch from another host; "
        "inline it or bundle it under static/:\n  " + "\n  ".join(offenders[:6]))
