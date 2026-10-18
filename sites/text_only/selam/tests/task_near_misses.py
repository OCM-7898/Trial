from __future__ import annotations

import re

from task_solvers import Trail, _free_seats, _page, _retrieve, _surname


def near_01(app, client, params):
    return _page(client, "/book/search")


def near_02(app, client, params):
    body = client.get(f"/book/results?origin={params['origin']}"
                      f"&destination={params['destination']}"
                      f"&depart={params['depart']}&adults=1").get_data(as_text=True)
    itinerary = re.search(r'href="/book/passengers\?itinerary=([^"&]+)"', body)
    return _page(client, f"/book/passengers?itinerary={itinerary.group(1)}")


def near_03(app, client, params):
    return _page(client, f"/flight-status?flight_no={params['flight_no']}"
                         f"&date=2026-03-17")


def near_04(app, client, params):
    return _page(client, f"/schedules?origin={params['destination']}"
                         f"&destination={params['origin']}")


def near_05(app, client, params):
    return _page(client, "/manage")


def near_06(app, client, params):
    pnr = params["pnr"]
    _retrieve(client, pnr, _surname(app, pnr))
    return _page(client, f"/manage/{pnr}/change")


def near_07(app, client, params):
    return _page(client, "/help/topics/fare-rules-explained")


def near_08(app, client, params):
    pnr = params["pnr"]
    _retrieve(client, pnr, _surname(app, pnr))
    return _page(client, f"/manage/{pnr}")


def near_09(app, client, params):
    other = "WGYBNA"
    response = client.post("/checkin",
                           data={"pnr": other, "surname": _surname(app, other)},
                           follow_redirects=True)
    return "/checkin", response.get_data(as_text=True)


def near_10(app, client, params):
    pnr = params["pnr"]
    _retrieve(client, pnr, _surname(app, pnr))
    body = client.get(f"/manage/{pnr}/seats").get_data(as_text=True)
    segment = re.search(r'name="segment_id" value="(\d+)"', body)
    passenger = re.search(r'<option value="(\d+)"', body)
    window = _free_seats(body, "is-window")
    assert window, "no free window seat to get wrong"
    response = client.post(f"/manage/{pnr}/seats", data={
        "segment_id": segment.group(1), "passenger_id": passenger.group(1),
        "seat_no": window[0],
    }, follow_redirects=True)
    return f"/manage/{pnr}/seats/review", response.get_data(as_text=True)


def near_11(app, client, params):
    return _page(client, "/manage/WGYBNA/seats/legend")


def near_12(app, client, params):
    return _page(client, "/help/topics/checked-baggage-basics")


def near_13(app, client, params):
    pnr = params["pnr"]
    _retrieve(client, pnr, _surname(app, pnr))
    body = client.get(f"/manage/{pnr}/baggage").get_data(as_text=True)
    segment = re.search(r'name="segment_id"[^>]*value="(\d+)"', body)
    response = client.post(f"/manage/{pnr}/baggage", data={
        "segment_id": segment.group(1), "extra_kg": "20",
    }, follow_redirects=True)
    return f"/manage/{pnr}/baggage/review", response.get_data(as_text=True)


def near_14(app, client, params):
    return _page(client, "/help/topics/sports-baggage-quick")


def near_15(app, client, params):
    return _page(client, "/manage/WGYBNA")


def near_16(app, client, params):
    response = client.post("/lounges/purchase", data={
        "lounge_id": "3", "passenger_name": "Test Passenger", "guests": "0",
    }, follow_redirects=True)
    return "/lounges/purchase/review", response.get_data(as_text=True)


def near_17(app, client, params):
    return _page(client, "/lounges/3")


def near_18(app, client, params):
    response = client.post("/miles/join", data={
        "first_name": "Selamawit", "last_name": "Bekele",
        "email": "someone.else@example.com", "country_code": "ET",
        "dob": "1992-05-14",
    }, follow_redirects=True)
    return "/miles/join", response.get_data(as_text=True)


def near_19(app, client, params):
    response = client.post("/miles/claim", data={
        "member_no": params["member_no"], "ticket_no": "0712345678901",
        "flight_no": "SM100", "flight_date": "2026-02-14",
    }, follow_redirects=True)
    return "/miles/claim", response.get_data(as_text=True)


def near_20(app, client, params):
    return _page(client, f"/miles/award-search?origin={params['origin']}"
                         f"&destination={params['destination']}"
                         f"&date={params['date']}&cabin=business")


def near_21(app, client, params):
    body = client.get(f"/onboard/wifi?flight_no={params['flight_no']}"
                      f"&date={params['date']}").get_data(as_text=True)
    package = re.findall(r'name="package_id"[^>]*value="(\d+)"', body)
    response = client.post("/onboard/wifi", data={
        "flight_no": params["flight_no"], "date": params["date"],
        "package_id": package[0],
    }, follow_redirects=True)
    return "/onboard/wifi/review", response.get_data(as_text=True)


def near_22(app, client, params):
    pnr = params["pnr"]
    _retrieve(client, pnr, _surname(app, pnr))
    body = client.get(f"/onboard/dining?pnr={pnr}").get_data(as_text=True)
    passenger = re.search(r'<option value="(\d+)"', body)
    response = client.post("/onboard/dining", data={
        "pnr": pnr, "passenger_id": passenger.group(1) if passenger else "",
        "meal_code": "VGML",
    }, follow_redirects=True)
    return "/onboard/dining", response.get_data(as_text=True)


def near_23(app, client, params):
    return _page(client, "/onboard/dining/special-meals")


def near_24(app, client, params):
    return _page(client, "/stopover")


def near_25(app, client, params):
    return _page(client, "/partners/zena-hotel")


def near_26(app, client, params):
    return _page(client, "/help/topics/visa-transit")


def near_27(app, client, params):
    return _page(client, "/help/topics/codeshare-explained")


def near_28(app, client, params):
    body = client.get("/partners/riftdrive?airport=ADD&passengers=2"
                      "&pickup=2026-04-12").get_data(as_text=True)
    offer = re.search(r'name="offer_id" value="(\d+)"', body)
    response = client.post("/partners/riftdrive", data={
        "offer_id": offer.group(1), "airport": "ADD", "passengers": "2",
        "pickup": "2026-04-12",
    }, follow_redirects=True)
    return "/partners/riftdrive", response.get_data(as_text=True)


def near_29(app, client, params):
    return _page(client, "/partners/safevoyage")


def near_30(app, client, params):
    return _page(client, "/help/contact")


NEAR_MISSES = {number: globals()[f"near_{number:02d}"] for number in range(1, 31)}
