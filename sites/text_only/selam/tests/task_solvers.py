from __future__ import annotations

import re

from sqlalchemy import select


def _retrieve(client, pnr: str, surname: str):
    return client.post("/manage", data={"pnr": pnr, "surname": surname},
                       follow_redirects=True)


class Trail:

    def __init__(self, client):
        self.client = client
        self.pages: list[str] = []
        self.final_url = "/"

    def visit(self, url: str, **kwargs) -> str:
        response = self.client.get(url, follow_redirects=True, **kwargs)
        body = response.get_data(as_text=True)
        self.pages.append(body)
        self.final_url = url
        return body

    def submit(self, url: str, data: dict, final_url: str | None = None) -> str:
        response = self.client.post(url, data=data, follow_redirects=True)
        body = response.get_data(as_text=True)
        self.pages.append(body)
        self.final_url = final_url or url
        return body

    def result(self):
        return self.final_url, "\n".join(self.pages)


def _page(client, url: str):
    response = client.get(url, follow_redirects=True)
    return url, response.get_data(as_text=True)


def _form_fields(body: str, action: str) -> dict[str, str]:
    start = body.find(f'action="{action}"')
    if start < 0:
        return {}
    end = body.find("</form>", start)
    chunk = body[start:end if end > 0 else len(body)]
    fields = {}
    for match in re.finditer(r'<input[^>]*name="([^"]+)"[^>]*value="([^"]*)"', chunk):
        fields[match.group(1)] = match.group(2)
    return fields


def _free_seats(body: str, characteristic: str) -> list[str]:
    seats = []
    for match in re.finditer(
            r'<button class="seat([^"]*)"[^>]*name="seat_no" value="([0-9]+[A-Z])"',
            body):
        classes, seat = match.group(1), match.group(2)
        if characteristic in classes and "taken" not in classes:
            seats.append(seat)
    return seats


def _surname(app, pnr: str) -> str:
    from app import db as database
    from app.models.booking import Booking

    with app.app_context():
        session = database.session()
        booking = session.scalars(
            select(Booking).where(Booking.pnr == pnr)).one()
        return booking.surname


def task_01(app, client, params):
    return _page(client, "/book/results?origin=ADD&destination=NBO"
                         "&depart=2026-04-12&return=2026-04-19&adults=1")


def task_02(app, client, params):
    body = client.get("/book/results?origin=ADD&destination=DXB"
                      "&depart=2026-04-20&adults=1").get_data(as_text=True)
    itinerary = re.search(r'href="/book/passengers\?itinerary=([^"&]+)"', body)
    assert itinerary, "the results page offered no itinerary to select"

    client.get(f"/book/passengers?itinerary={itinerary.group(1)}")
    client.post("/book/passengers", data={
        "itinerary": itinerary.group(1), "adults": "1",
        "first_name_1": "Test", "last_name_1": "Passenger",
        "contact_email": "test.passenger@example.com",
        "contact_phone": "+251911000000",
    }, follow_redirects=True)
    response = client.get("/book/review", follow_redirects=True)
    return "/book/review", response.get_data(as_text=True)


def task_03(app, client, params):
    return _page(client, "/flight-status?flight_no=SM107&date=2026-03-16")


def task_04(app, client, params):
    url = (f"/schedules?origin={params['origin']}"
           f"&destination={params['destination']}")
    body = client.get(url, follow_redirects=True).get_data(as_text=True)
    rows = re.findall(r"<tr>(.*?)</tr>", body, re.S)
    operating = []
    for row in rows:
        cells = [re.sub(r"<[^>]+>", "", c).strip()
                 for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)]
        if len(cells) >= 5 and cells[-1] not in ("", "--") and "-" not in cells[1]:
            operating.append(cells[0])
    return url, body, ", ".join(operating)


def task_05(app, client, params):
    _retrieve(client, "WGYBNA", _surname(app, "WGYBNA"))
    return _page(client, "/manage/WGYBNA")


def task_06(app, client, params):
    pnr = "W7JKUF"
    _retrieve(client, pnr, _surname(app, pnr))
    body = client.get(f"/manage/{pnr}/change").get_data(as_text=True)
    segment = re.search(r'name="segment_id"[^>]*value="(\d+)"', body)
    assert segment, "the change page offered no segment to move"
    client.post(f"/manage/{pnr}/change",
                data={"segment_id": segment.group(1), "new_date": "2026-04-26"},
                follow_redirects=True)
    body = client.get(f"/manage/{pnr}/change?segment_id={segment.group(1)}"
                      f"&new_date=2026-04-26").get_data(as_text=True)
    option = re.search(r'name="new_flight_id"[^>]*value="(\d+)"', body)
    assert option, "no replacement flight was offered"
    response = client.post(f"/manage/{pnr}/change", data={
        "segment_id": segment.group(1), "new_date": "2026-04-26",
        "new_flight_id": option.group(1), "confirm": "1",
    }, follow_redirects=True)
    return f"/manage/{pnr}/change/review", response.get_data(as_text=True)


def task_07(app, client, params):
    pnr = "SPMVJC"
    _retrieve(client, pnr, _surname(app, pnr))
    return _page(client, f"/manage/{pnr}/refund")


def task_08(app, client, params):
    pnr = "WGYBNA"
    surname = _surname(app, pnr)
    client.post("/checkin", data={"pnr": pnr, "surname": surname},
                follow_redirects=True)
    body = client.post("/checkin", data={"pnr": pnr, "surname": surname},
                       follow_redirects=True).get_data(as_text=True)
    segment = re.search(r'name="segment_id"[^>]*value="(\d+)"', body)
    assert segment, "check-in offered no segment"
    response = client.post("/checkin", data={
        "pnr": pnr, "surname": surname, "segment_id": segment.group(1),
    }, follow_redirects=True)
    return "/checkin", response.get_data(as_text=True)


def task_09(app, client, params):
    pnr = params["pnr"]
    response = client.post("/checkin",
                           data={"pnr": pnr, "surname": _surname(app, pnr)},
                           follow_redirects=True)
    return "/checkin", response.get_data(as_text=True)


def task_10(app, client, params):
    pnr = "N9JKBF"
    _retrieve(client, pnr, _surname(app, pnr))
    body = client.get(f"/manage/{pnr}/seats").get_data(as_text=True)
    segment = re.search(r'name="segment_id" value="(\d+)"', body)
    passenger = re.search(r'<option value="(\d+)"', body)
    assert segment and passenger, "the seat page offered no segment or passenger"

    aisle = _free_seats(body, "aisle")
    assert aisle, "no free aisle seat on the map"
    response = client.post(f"/manage/{pnr}/seats", data={
        "segment_id": segment.group(1), "passenger_id": passenger.group(1),
        "seat_no": aisle[0],
    }, follow_redirects=True)
    return f"/manage/{pnr}/seats/review", response.get_data(as_text=True)


def task_11(app, client, params):
    _retrieve(client, "WGYBNA", _surname(app, "WGYBNA"))
    return _page(client, "/manage/WGYBNA/seats")


def task_12(app, client, params):
    return _page(client, "/baggage/allowance?origin=ADD&destination=LHR"
                         "&cabin=economy&pax_type=adult")


def task_13(app, client, params):
    pnr = "WGYBNA"
    _retrieve(client, pnr, _surname(app, pnr))
    body = client.get(f"/manage/{pnr}/baggage").get_data(as_text=True)
    segment = re.search(r'name="segment_id"[^>]*value="(\d+)"', body)
    assert segment, "the baggage page offered no segment"
    response = client.post(f"/manage/{pnr}/baggage", data={
        "segment_id": segment.group(1), "extra_kg": "23",
    }, follow_redirects=True)
    return f"/manage/{pnr}/baggage/review", response.get_data(as_text=True)


def task_14(app, client, params):
    return _page(client, "/baggage/special")


def task_15(app, client, params):
    _retrieve(client, "WGYBNA", _surname(app, "WGYBNA"))
    return _page(client, "/manage/WGYBNA/upgrade")


def task_16(app, client, params):
    body = client.get("/lounges/purchase").get_data(as_text=True)
    assert 'name="lounge_id"' in body, "the purchase page offered no lounge"
    response = client.post("/lounges/purchase", data={
        "lounge_id": str(params["id"]), "passenger_name": "Test Passenger",
        "guests": "0",
    }, follow_redirects=True)
    return "/lounges/purchase/review", response.get_data(as_text=True)


def task_17(app, client, params):
    trail = Trail(client)
    body = trail.visit(f"/lounges/eligibility?airport={params['airport_iata']}"
                       f"&cabin=economy&tier=gold")
    free = re.findall(r'href="/lounges/(\d+)"', body)
    assert free, "the eligibility check listed no lounge"
    trail.visit(f"/lounges/{params['id']}")
    return trail.result()


def task_18(app, client, params):
    response = client.post("/miles/join", data={
        "first_name": "Selamawit", "last_name": "Bekele",
        "email": "selamawit.bekele@example.com", "country_code": "ET",
        "dob": "1992-05-14",
    }, follow_redirects=True)
    return "/miles/join", response.get_data(as_text=True)


def task_19(app, client, params):
    response = client.post("/miles/claim", data={
        "member_no": "SM00000001", "ticket_no": "0712345678901",
        "flight_no": "SM246", "flight_date": "2026-02-14",
    }, follow_redirects=True)
    return "/miles/claim", response.get_data(as_text=True)


def task_20(app, client, params):
    return _page(client, f"/miles/award-search?origin={params['origin']}"
                         f"&destination={params['destination']}"
                         f"&date={params['date']}&cabin={params['cabin']}")


def task_21(app, client, params):
    body = client.get("/onboard/wifi?flight_no=SM106&date=2026-03-19"
                      ).get_data(as_text=True)
    package = re.findall(r'name="package_id"[^>]*value="(\d+)"', body)
    assert package, "no Wi-Fi package was offered for this flight"
    response = client.post("/onboard/wifi", data={
        "flight_no": "SM106", "date": "2026-03-19", "package_id": package[-1],
    }, follow_redirects=True)
    return "/onboard/wifi/review", response.get_data(as_text=True)


def task_22(app, client, params):
    pnr = "WGYBNA"
    _retrieve(client, pnr, _surname(app, pnr))
    body = client.get(f"/onboard/dining?pnr={pnr}").get_data(as_text=True)
    assert "GFML" in body, "the special-meal codes are not on the dining page"
    passenger = re.search(r'<option value="(\d+)"', body)
    response = client.post("/onboard/dining", data={
        "pnr": pnr, "passenger_id": passenger.group(1) if passenger else "",
        "meal_code": "GFML",
    }, follow_redirects=True)
    return "/onboard/dining", response.get_data(as_text=True)


def task_23(app, client, params):
    return _page(client, "/help/allergies")


def task_24(app, client, params):
    return _page(client, "/stopover?origin=NBO&destination=LHR&date=2026-04-12")


def task_25(app, client, params):
    body = client.get("/partners/zena-hotel").get_data(as_text=True)
    room = re.search(r'<option value="(\d+)"', body)
    assert room, "the hotel offered no room"
    response = client.post("/partners/zena-hotel", data={
        "room_id": room.group(1), "arrival": "2026-04-12", "hours": "12",
        "guest_name": "Test Passenger",
    }, follow_redirects=True)
    return "/partners/zena-hotel", response.get_data(as_text=True)


def task_26(app, client, params):
    body = client.get("/partners/evisa").get_data(as_text=True)
    code = re.search(r'href="/partners/evisa\?code=([A-Z0-9-]+)"', body)
    assert code, "the eVisa portal listed no visa type"
    return _page(client, f"/partners/evisa?code={code.group(1)}")


def task_27(app, client, params):
    return _page(client, "/partners/eurorail?arrival=FRA")


def task_28(app, client, params):
    body = client.get("/partners/riftdrive?airport=NBO&passengers=2"
                      "&pickup=2026-04-12").get_data(as_text=True)
    offer = re.search(r'name="offer_id" value="(\d+)"', body)
    assert offer, "RiftDrive offered no vehicle for two passengers"
    response = client.post("/partners/riftdrive", data={
        "offer_id": offer.group(1), "airport": "NBO", "passengers": "2",
        "pickup": "2026-04-12",
    }, follow_redirects=True)
    return "/partners/riftdrive", response.get_data(as_text=True)


def task_29(app, client, params):
    return _page(client, "/partners/safevoyage?fare=900")


def task_30(app, client, params):
    trail = Trail(client)
    trail.visit("/help/contact")
    trail.visit(f"/help/contact/{params['country_code']}")
    return trail.result()


SOLVERS = {number: globals()[f"task_{number:02d}"] for number in range(1, 31)}
