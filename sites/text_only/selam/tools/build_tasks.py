from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import task_data as td
from brand_substitutions import TASK_TEXT_SUBSTITUTIONS

BASE = {"en": "http://localhost:7770", "am": "http://localhost:7771"}


def money(value: float) -> str:
    return f"USD {value:,.0f}" if float(value).is_integer() else f"USD {value:,.2f}"


def task_1(conn):
    origin, destination, out, back = "ADD", "NBO", "2026-04-12", "2026-04-19"
    fares = td.cheapest_fares(conn, origin, destination, out)
    if len(fares) < 3:
        raise SystemExit("task 1 needs several fares on the outbound date")
    cheapest = fares[0]
    flight_numbers = sorted({f["flight_no"] for f in fares})
    return (
        {"origin": origin, "destination": destination, "depart": out, "return": back,
         "adults": 1, "cheapest_price": cheapest["price_usd"],
         "flight_numbers": flight_numbers},
        f"Find round-trip flights from Addis Ababa ({origin}) to Nairobi ({destination}) "
        f"departing {out} and returning {back} for one adult. Report the flight numbers "
        f"available on the outbound date and the lowest total price shown.",
        f"ለአንድ አዋቂ በ{out} ተነስቶ በ{back} የሚመለስ ከአዲስ አበባ ({origin}) ወደ ናይሮቢ ({destination}) "
        f"የደርሶ መልስ በረራ ይፈልጉ። በመሄጃው ቀን ያሉትን የበረራ ቁጥሮችና የሚታየውን ዝቅተኛ ጠቅላላ ዋጋ ያቅርቡ።",
        {"eval_types": ["string_match"],
         "reference_answers": {"must_include": flight_numbers + [money(cheapest["price_usd"] + cheapest["taxes_usd"])]}},
        "concrete route and dates; the outbound date has service in both directions",
    )


def task_2(conn):
    picked = td.booking_where(conn, "1=1", "any booking, for the route reference")
    return (
        {"origin": "ADD", "destination": "DXB", "depart": "2026-04-20", "adults": 1},
        "Book a one-way flight from Addis Ababa (ADD) to Dubai (DXB) on 2026-04-20 for "
        "one adult, enter passenger details, and stop at the final payment-review page "
        "without paying.",
        "በ2026-04-20 ለአንድ አዋቂ ከአዲስ አበባ (ADD) ወደ ዱባይ (DXB) የአንድ አቅጣጫ በረራ ይያዙ፤ የተሳፋሪውን "
        "መረጃ ያስገቡ፤ ሳይከፍሉ በመጨረሻው የክፍያ ማጠቃለያ ገጽ ላይ ያቁሙ።",
        {"eval_types": ["program_html", "db_state"],
         "validator": "tasks.validators.task_02_booking_review",
         "validator_args": {"origin": "ADD", "destination": "DXB", "depart": "2026-04-20"}},
        "payment boundary: a draft booking must exist and nothing may be paid",
    )


def task_3(conn):
    flight = td.flight_with_distinct_status(conn, "delayed").value
    return (
        flight,
        f"Check the current status of flight {flight['flight_no']} on {flight['date']}. "
        f"Report its status, scheduled departure and arrival times, and both terminals.",
        f"የበረራ {flight['flight_no']}ን በ{flight['date']} ወቅታዊ ሁኔታ ያረጋግጡ። ሁኔታውን፣ የታቀዱ የመነሻና "
        f"የመድረሻ ሰዓቶችን እንዲሁም ሁለቱንም ተርሚናሎች ያቅርቡ።",
        {"eval_types": ["string_match"],
         "reference_answers": {
             "must_include_en": ["Delayed", str(flight["dep_time"])[:5], str(flight["arr_time"])[:5],
                                 flight["terminal_dep"], flight["terminal_arr"]],
             "must_include_am": ["የዘገየ", str(flight["dep_time"])[:5], str(flight["arr_time"])[:5],
                                 flight["terminal_dep"], flight["terminal_arr"]]}},
        "a delayed flight, so 'scheduled' is not a free correct answer",
    )


def task_4(conn):
    route = td.route_with_partial_week(conn).value
    days = route["operating_days"]
    names_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    names_am = ["ሰኞ", "ማክሰኞ", "ረቡዕ", "ሐሙስ", "ዓርብ", "ቅዳሜ", "እሁድ"]
    operating_en = [names_en[i] for i, c in enumerate(days) if c != "."]
    operating_am = [names_am[i] for i, c in enumerate(days) if c != "."]
    return (
        {**route, "operating_en": operating_en, "operating_am": operating_am},
        f"Find which days of the week flights operate from {route['origin']} to "
        f"{route['destination']}. List every operating day.",
        f"ከ{route['origin']} ወደ {route['destination']} በረራዎች በየትኞቹ የሳምንቱ ቀናት እንደሚሠሩ ያግኙ። "
        f"ሁሉንም የሥራ ቀናት ይዘርዝሩ።",
        {"eval_types": ["string_match"],
         "reference_answers": {"must_include_en": operating_en,
                               "must_include_am": operating_am,
                               "answer_only": True}},
        f"route operates {len(operating_en)} of 7 days, so 'daily' is wrong; scored "
        f"on the reported answer, because the page lists every day either way",
    )


def task_5(conn):
    b = td.booking_where(conn, "(select count(*) from segments s2 where s2.booking_id = b.id) > 1",
                         "a round-trip booking, so the itinerary has more than one leg").value
    return (
        b,
        f"Open the booking with reference {b['pnr']} and last name {b['surname_en']}. "
        f"Report the flight numbers on the itinerary and the booking status.",
        f"ማጣቀሻው {b['pnr']} እና የአያት ስሙ {b['surname_am']} የሆነውን የቦታ ማስያዣ ይክፈቱ። በጉዞ ዝርዝሩ ላይ "
        f"ያሉትን የበረራ ቁጥሮችና የቦታ ማስያዣውን ሁኔታ ያቅርቡ።",
        {"eval_types": ["string_match"],
         "reference_answers": {"must_include": [b["flight_no"], b["pnr"]]}},
        "round-trip, so a single flight number is an incomplete answer",
    )


def task_6(conn):
    b = td.booking_where(
        conn,
        "fc.changeable = 1 and b.booked_channel = 'website' "
        "and julianday(f.date) - julianday('2026-03-16') > 4",
        "changeable fare, far enough out that the change flow is open").value
    return (
        b,
        f"Booking {b['pnr']} (last name {b['surname_en']}) needs its outbound flight moved "
        f"to a later date. Select an available alternative, show the fare difference and "
        f"any change fee, and stop before confirming payment.",
        f"የቦታ ማስያዣ {b['pnr']} (የአያት ስም {b['surname_am']}) የመሄጃ በረራው ወደ ሌላ ቀን መዛወር አለበት። "
        f"ያለ አማራጭ ይምረጡ፤ የታሪፍ ልዩነቱንና ካለ የለውጥ ክፍያውን ያሳዩ፤ ክፍያውን ከማረጋገጥዎ በፊት ያቁሙ።",
        {"eval_types": ["program_html", "db_state"],
         "validator": "tasks.validators.task_06_change_request",
         "validator_args": {"pnr": b["pnr"]}},
        f"fare {b['fare_code']} is changeable and the flight is far enough out",
    )


def task_7(conn):
    b = td.booking_where(
        conn, "b.booked_channel = 'agent' and fc.refundable = 1",
        "refundable fare but booked through an agent -- online refund must be refused").value
    return (
        b,
        f"Check whether booking {b['pnr']} (last name {b['surname_en']}) can be refunded "
        f"online. If it can, complete the request up to the final submission step. If it "
        f"cannot, report the reason given.",
        f"የቦታ ማስያዣ {b['pnr']} (የአያት ስም {b['surname_am']}) በመስመር ላይ ተመላሽ ሊደረግ እንደሚችል "
        f"ያረጋግጡ። ከተቻለ እስከ መጨረሻው የማስገቢያ ደረጃ ድረስ ጥያቄውን ይሙሉ። ካልተቻለ የተሰጠውን ምክንያት ያቅርቡ።",
        {"eval_types": ["program_html", "db_state"],
         "validator": "tasks.validators.task_07_refund_blocked",
         "validator_args": {"pnr": b["pnr"], "expected_code": "OFFLINE_CHANNEL_ONLY"}},
        "the fare IS refundable, so the agent-channel rule is what decides -- an agent "
        "that only reads the fare rules gets this wrong",
    )


def task_8(conn):
    b = td.booking_where(
        conn,
        "b.is_group = 0 and (select count(*) from passengers p where p.booking_id = b.id "
        "and p.pax_type != 'adult') = 0 and s.operated_by_en is null "
        "and (julianday(f.date || ' ' || f.dep_time) - julianday('2026-03-16 09:00')) * 24 "
        "between 3 and 47",
        "inside the check-in window with no blocking condition").value
    return (
        b,
        f"Check in for booking {b['pnr']} (last name {b['surname_en']}) and download the "
        f"boarding pass. Report the seat and the gate shown on it.",
        f"ለቦታ ማስያዣ {b['pnr']} (የአያት ስም {b['surname_am']}) ቼክ-ኢን ያድርጉ እና የመሳፈሪያ ፈቃዱን "
        f"ያውርዱ። በላዩ ላይ የሚታየውን መቀመጫና በር ያቅርቡ።",
        {"eval_types": ["url_match", "db_state"],
         "validator": "tasks.validators.task_08_checkin",
         "validator_args": {"pnr": b["pnr"]}},
        "check-in window is open and no refusal code applies",
    )


def task_9(conn):
    b = td.booking_where(
        conn, "b.is_group = 1", "a group booking, refused with GROUP_BOOKING").value
    return (
        b,
        f"Determine whether online check-in is available for booking {b['pnr']} (last name "
        f"{b['surname_en']}). If it is not, explain the reason the website gives.",
        f"ለቦታ ማስያዣ {b['pnr']} (የአያት ስም {b['surname_am']}) የመስመር ላይ ቼክ-ኢን መኖሩን ይወስኑ። "
        f"ካልተቻለ ድረ ገጹ የሚሰጠውን ምክንያት ያብራሩ።",
        {"eval_types": ["string_match"],
         "reference_answers": {"must_include_en": ["Group booking"],
                               "must_include_am": ["የቡድን ቦታ ማስያዣ"]}},
        "the flight is inside the check-in window, so the refusal is the group rule "
        "rather than a timing rule",
    )


def task_10(conn):
    b = td.booking_where(
        conn,
        "not exists (select 1 from seat_assignments sa where sa.segment_id = s.id)",
        "no seats assigned yet, so the selection is a real change").value
    return (
        b,
        f"Open booking {b['pnr']} (last name {b['surname_en']}) and select an available "
        f"aisle seat for the outbound flight. Report the seat number and its price, and "
        f"stop before payment.",
        f"የቦታ ማስያዣ {b['pnr']} (የአያት ስም {b['surname_am']}) ይክፈቱ እና ለመሄጃው በረራ ያለ የመተላለፊያ "
        f"መቀመጫ ይምረጡ። የመቀመጫውን ቁጥርና ዋጋ ያቅርቡ፤ ከክፍያ በፊት ያቁሙ።",
        {"eval_types": ["program_html", "db_state"],
         "validator": "tasks.validators.task_10_aisle_seat",
         "validator_args": {"pnr": b["pnr"]}},
        "booking starts with no seats, so the validator can assert one was added",
    )


def task_11(conn):
    b = td.booking_where(conn, "1=1", "any booking with a seat map").value
    prices = td.seat_prices(conn, b["flight_id"])
    return (
        {**b, **prices},
        f"For booking {b['pnr']} (last name {b['surname_en']}), find the extra-legroom "
        f"seats on the outbound flight and report their price. Do not purchase one.",
        f"ለቦታ ማስያዣ {b['pnr']} (የአያት ስም {b['surname_am']}) በመሄጃው በረራ ላይ ተጨማሪ የእግር ቦታ ያላቸውን "
        f"መቀመጫዎች አግኝተው ዋጋቸውን ያቅርቡ። አይግዙ።",
        {"eval_types": ["string_match"],
         "reference_answers": {"must_include": [money(prices["legroom_high"])]}},
        "extra-legroom seats cost more than standard ones, so the number is specific",
    )


def task_12(conn):
    rule = td.baggage_rule(conn, "north_america", "economy", "adult")
    return (
        {"origin": "ADD", "destination": "JFK", **rule},
        "Report the free checked-baggage and cabin-baggage allowance for an adult "
        "travelling in economy from Addis Ababa (ADD) to New York (JFK).",
        "ከአዲስ አበባ (ADD) ወደ ኒው ዮርክ (JFK) በኢኮኖሚ ለሚጓዝ አዋቂ የነጻ የተመዘገበ ሻንጣና የእጅ ሻንጣ ፈቃድን "
        "ያቅርቡ።",
        {"eval_types": ["string_match"],
         "reference_answers": {"must_include": [str(rule["checked_pieces"]),
                                                str(rule["checked_kg"]),
                                                str(rule["cabin_kg"])]}},
        "a long-haul route, whose allowance differs from the domestic and African "
        "tables shown on neighbouring pages",
    )


def task_13(conn):
    b = td.booking_where(conn, "fc.cabin = 'economy'", "an economy booking with an "
                                                       "excess-baggage rate").value
    return (
        b,
        f"Add 23 kg of extra checked baggage to booking {b['pnr']} (last name "
        f"{b['surname_en']}) for the outbound flight. Report the total charge and stop "
        f"before completing payment.",
        f"ለቦታ ማስያዣ {b['pnr']} (የአያት ስም {b['surname_am']}) ለመሄጃው በረራ 23 ኪግ ተጨማሪ የተመዘገበ "
        f"ሻንጣ ይጨምሩ። ጠቅላላ ክፍያውን ያቅርቡ፤ ክፍያውን ከማጠናቀቅዎ በፊት ያቁሙ።",
        {"eval_types": ["program_html", "db_state"],
         "validator": "tasks.validators.task_13_extra_baggage",
         "validator_args": {"pnr": b["pnr"], "expected_extra_kg": 23}},
        "the per-kg rate is regional, so the total depends on reading the right table",
    )


def task_14(conn):
    return (
        {"item": "bicycle", "route": "ADD-NBO"},
        "Find the rules and any charges for carrying a bicycle as checked baggage from "
        "Addis Ababa to Nairobi. Report how it must be packed and whether advance notice "
        "is required.",
        "ብስክሌትን ከአዲስ አበባ ወደ ናይሮቢ እንደ የተመዘገበ ሻንጣ ለመውሰድ ያሉትን ደንቦችና ክፍያዎች ያግኙ። እንዴት "
        "መታሸግ እንዳለበትና ቅድሚያ ማሳወቅ የሚያስፈልግ መሆኑን ያቅርቡ።",
        {"eval_types": ["string_match"],
         "reference_answers": {"must_include_en": ["handlebars", "pedals", "48"],
                               "must_include_am": ["መሪያቸው", "ፔዳሎቻቸው", "48"]}},
        "the packing detail is only on the special-baggage page, not the allowance page",
    )


def task_15(conn):
    b = td.booking_where(
        conn, "fc.upgrade_eligible = 0",
        "a fare family excluded from upgrade -- the answer is a refusal, not a price").value
    return (
        b,
        f"Check whether the outbound flight on booking {b['pnr']} (last name "
        f"{b['surname_en']}) can be upgraded to Highland Class. Report the outcome and, "
        f"if an upgrade is not possible, the reason.",
        f"በቦታ ማስያዣ {b['pnr']} (የአያት ስም {b['surname_am']}) ላይ ያለው የመሄጃ በረራ ወደ ሃይላንድ ክላስ "
        f"ሊሻሻል እንደሚችል ያረጋግጡ። ውጤቱን፣ ማሻሻል ካልተቻለም ምክንያቱን ያቅርቡ።",
        {"eval_types": ["string_match"],
         "reference_answers": {"must_include_en": ["not eligible"],
                               "must_include_am": ["ብቁ አይደለም"]}},
        f"fare {b['fare_code']} is upgrade-excluded, so the answer is a refusal that "
        f"must be read rather than a price that could be guessed",
    )


def task_16(conn):
    lounge = conn.execute(
        "select id, name_en, name_am, terminal, walk_in_price_usd from lounges "
        "where airport_iata = 'ADD' and walk_in_price_usd > 0 order by id limit 1"
    ).fetchone()
    return (
        dict(lounge),
        f"Buy lounge access at Addis Ababa Bole International Airport for one passenger "
        f"with no guests. Select {lounge['name_en']}, verify the price, and stop at the "
        f"payment page without paying.",
        f"በአዲስ አበባ ቦሌ ዓለም አቀፍ አየር ማረፊያ ለአንድ ተሳፋሪ ያለ እንግዳ የላውንጅ መግቢያ ይግዙ። "
        f"{lounge['name_am']}ን ይምረጡ፣ ዋጋውን ያረጋግጡ፣ ሳይከፍሉ በክፍያ ገጹ ላይ ያቁሙ።",
        {"eval_types": ["program_html", "db_state"],
         "validator": "tasks.validators.task_16_lounge_purchase",
         "validator_args": {"lounge_id": lounge["id"],
                            "expected_price_usd": lounge["walk_in_price_usd"]}},
        "several Addis lounges sell walk-in access at different prices, so the amount "
        "depends on choosing the named one",
    )


def task_17(conn):
    lounge = td.lounge_needing_discrimination(conn)
    v = lounge.value
    return (
        v,
        f"A Selam Miles Gold member is flying in economy from Terminal 2 at Addis Ababa. "
        f"Identify which lounge there they may enter without paying, and report its "
        f"opening hours and location.",
        f"የሰላም ማይልስ ጎልድ አባል በኢኮኖሚ ከአዲስ አበባ ተርሚናል 2 እየተጓዘ ነው። እዚያ ሳይከፍል መግባት የሚችለውን "
        f"ላውንጅ ይለዩ፤ የሥራ ሰዓቱንና ቦታውን ያቅርቡ።",
        {"eval_types": ["string_match"],
         "reference_answers": {"must_include_en": [v["name_en"], v["hours_en"]],
                               "must_include_am": [v["name_am"], v["hours_am"]]}},
        lounge.rationale,
    )


def task_18(conn):
    highest = conn.execute(
        "select member_no from loyalty_members order by member_no desc limit 1").fetchone()[0]
    expected = f"SM{int(highest[2:]) + 1:08d}"
    return (
        {"first_name": "Selamawit", "last_name": "Bekele",
         "first_name_am": "ሰላማዊት", "last_name_am": "በቀለ",
         "email": "selamawit.bekele@example.com", "country_code": "ET",
         "expected_member_no": expected},
        "Enrol a new Selam Miles member with first name Selamawit, last name Bekele, "
        "email selamawit.bekele@example.com and country ET. Report the membership number "
        "you are given.",
        "የመጀመሪያ ስም ሰላማዊት፣ የአያት ስም በቀለ፣ ኢሜይል selamawit.bekele@example.com እና አገር ET ያለው "
        "አዲስ የሰላም ማይልስ አባል ይመዝግቡ። የተሰጠዎትን የአባልነት ቁጥር ያቅርቡ።",
        {"eval_types": ["program_html", "db_state"],
         "validator": "tasks.validators.task_18_enrolment",
         "validator_args": {"email": "selamawit.bekele@example.com",
                            "expected_member_no": expected}},
        f"the sequence is deterministic from the seed high-water mark, so {expected} is "
        f"predictable after a reset",
    )


def task_19(conn):
    member = conn.execute(
        "select member_no, last_name_en, last_name_am from loyalty_members order by id limit 1"
    ).fetchone()
    flight = conn.execute(
        "select flight_no, date from flights where status = 'departed' "
        "and date < '2026-03-16' order by date desc limit 1").fetchone()
    return (
        {**dict(member), **dict(flight), "ticket_no": "0712345678901"},
        f"Member {member['member_no']} did not receive miles for flight "
        f"{flight['flight_no']} on {flight['date']}, ticket 0712345678901. Submit a "
        f"missing-miles claim and report the claim reference number.",
        f"አባል {member['member_no']} በ{flight['date']} ለበረራ {flight['flight_no']}፣ ትኬት "
        f"0712345678901 ማይሎችን አላገኘም። ያልተመዘገቡ ማይሎች ጥያቄ ያስገቡ እና የጥያቄውን ማጣቀሻ ቁጥር ያቅርቡ።",
        {"eval_types": ["program_html", "db_state"],
         "validator": "tasks.validators.task_19_missing_miles",
         "validator_args": {"member_no": member["member_no"],
                            "flight_no": flight["flight_no"]}},
        "the flight is in the past, which the form requires -- a future date is rejected",
    )


def task_20(conn):
    award = td.award_with_seats(conn).value
    return (
        award,
        f"Search for award seats bookable with miles from {award['origin']} to "
        f"{award['destination']} on {award['date']} in economy. Report the miles required "
        f"and the taxes payable.",
        f"በ{award['date']} ከ{award['origin']} ወደ {award['destination']} በኢኮኖሚ በማይል ሊያዙ "
        f"የሚችሉ የሽልማት መቀመጫዎችን ይፈልጉ። የሚያስፈልጉትን ማይሎችና የሚከፈለውን ግብር ያቅርቡ።",
        {"eval_types": ["string_match"],
         "reference_answers": {"must_include": [str(award["miles_required"]),
                                                money(award["taxes_usd"])]}},
        "a date with seats remaining; sold-out rows are not listed, so the figure is real",
    )


def task_21(conn):
    flight = conn.execute(
        "select flight_no, date from flights where wifi_equipped = 1 "
        "and date > '2026-03-16' order by date, id limit 1").fetchone()
    return (
        dict(flight),
        f"Flight {flight['flight_no']} on {flight['date']} has Wi-Fi. Compare the "
        f"available internet packages, select the largest data allowance, and stop before "
        f"payment.",
        f"በ{flight['date']} በረራ {flight['flight_no']} ዋይ-ፋይ አለው። ያሉትን የኢንተርኔት ፓኬጆች "
        f"ያወዳድሩ፤ ትልቁን የዳታ መጠን ይምረጡ፤ ከክፍያ በፊት ያቁሙ።",
        {"eval_types": ["program_html", "db_state"],
         "validator": "tasks.validators.task_21_wifi",
         "validator_args": {"flight_no": flight["flight_no"]}},
        "only some aircraft are equipped, so the flight must be one that is",
    )


def task_22(conn):
    b = td.booking_where(conn, "1=1", "any booking, for the meal request").value
    return (
        b,
        f"Check the meal options for the outbound flight on booking {b['pnr']} (last name "
        f"{b['surname_en']}), then request a gluten-free meal for the passenger.",
        f"በቦታ ማስያዣ {b['pnr']} (የአያት ስም {b['surname_am']}) ላይ ላለው የመሄጃ በረራ የምግብ አማራጮችን "
        f"ያረጋግጡ፤ ከዚያም ለተሳፋሪው ግሉተን-አልባ ምግብ ይጠይቁ።",
        {"eval_types": ["db_state"],
         "validator": "tasks.validators.task_22_special_meal",
         "validator_args": {"pnr": b["pnr"], "expected_code": "GFML"}},
        "GFML is one of fourteen codes, so the right one must be looked up",
    )


def task_23(conn):
    return (
        {"allergy": "peanut"},
        "A passenger with a severe peanut allergy is travelling next week. Find the "
        "airline's allergy guidance and summarise what they must do before travel and "
        "what the airline will and will not guarantee on board.",
        "ከባድ የለውዝ አለርጂ ያለው ተሳፋሪ በሚቀጥለው ሳምንት ይጓዛል። የአየር መንገዱን የአለርጂ መመሪያ ያግኙ፤ ከጉዞ በፊት "
        "ማድረግ ያለበትንና አየር መንገዱ በበረራ ላይ የሚያረጋግጠውንና የማያረጋግጠውን ያጠቃልሉ።",
        {"eval_types": ["string_match"],
         "reference_answers": {
             "must_include_en": ["48 hours", "24 hours", "allergen-free"],
             "must_include_am": ["48 ሰዓት", "24 ሰዓት", "አለርጂ-ነጻ"]}},
        "the page states two different cut-offs and an explicit non-guarantee; a summary "
        "that omits the non-guarantee is wrong. The strings were bare numerals and "
        "'cannot' until a near-miss run showed the special-meals page satisfying all "
        "three",
    )


def task_24(conn):
    return (
        {"origin": "NBO", "destination": "LHR", "date": "2026-04-12"},
        "A passenger is connecting from Nairobi (NBO) to London (LHR) through Addis Ababa "
        "on 2026-04-12, on a single booking. Determine whether they qualify for the "
        "stopover programme and list the services available.",
        "ተሳፋሪ በ2026-04-12 በአንድ የቦታ ማስያዣ ከናይሮቢ (NBO) ወደ ለንደን (LHR) በአዲስ አበባ በኩል "
        "ይሸጋገራል። ለማቆያ መርሐ ግብሩ ብቁ መሆኑን ይወስኑ እና ያሉትን አገልግሎቶች ይዘርዝሩ።",
        {"eval_types": ["string_match", "db_state"],
         "reference_answers": {"must_include_en": ["Eligible for a stopover"],
                               "must_include_am": ["ለማቆያ ብቁ"]},
         "validator": "tasks.validators.task_24_stopover",
         "validator_args": {"origin": "NBO", "destination": "LHR", "day": "2026-04-12"}},
        "the connection is 21 hours, inside the 8-72 hour window, so eligibility turns "
        "on reading the layover rather than assuming",
    )


def _partner_task(number, slug, name_en, name_am, intent_en, intent_am, validator, why):
    def build(conn):
        return ({"partner": slug}, intent_en, intent_am,
                {"eval_types": ["url_match", "db_state"],
                 "validator": f"tasks.validators.{validator}",
                 "validator_args": {"partner": slug}}, why)
    return build


task_25 = _partner_task(
    25, "zena-hotel", "Zena Transit Hotel", "ዜና ትራንዚት ሆቴል",
    "Check room availability at the Zena Transit Hotel inside Addis Ababa airport for a "
    "layover on 2026-04-12 and proceed to the booking review page without paying.",
    "በ2026-04-12 ለሚኖር የመሸጋገሪያ ጊዜ በአዲስ አበባ አየር ማረፊያ ውስጥ ባለው ዜና ትራንዚት ሆቴል የክፍል መኖርን "
    "ያረጋግጡ እና ሳይከፍሉ እስከ ቦታ ማስያዣ ማጠቃለያ ገጽ ይቀጥሉ።",
    "task_25_hotel", "the hotel is a partner site with its own layout; leaving the "
                     "airline site is part of what is measured")

task_26 = _partner_task(
    26, "evisa", "National eVisa Service", "ብሔራዊ ኢ-ቪዛ አገልግሎት",
    "From the airline website, open the National eVisa Service, select the visa type for "
    "a seven-day tourist visit, and report the documents required before applying.",
    "ከአየር መንገዱ ድረ ገጽ ብሔራዊ ኢ-ቪዛ አገልግሎትን ይክፈቱ፤ ለሰባት ቀን የቱሪስት ጉብኝት የቪዛ ዓይነቱን ይምረጡ፤ "
    "ከማመልከትዎ በፊት የሚያስፈልጉትን ሰነዶች ያቅርቡ።",
    "task_26_evisa", "requires navigating off the airline site, which the URL check verifies")

task_27 = _partner_task(
    27, "eurorail", "EuroRail Connect", "ዩሮሬል ኮኔክት",
    "Find a combined flight-and-rail connection from Frankfurt (FRA) onward to Cologne by "
    "train, and report how it can be booked.",
    "ከፍራንክፈርት (FRA) ወደ ኮሎኝ በባቡር የሚቀጥል የበረራና የባቡር ጥምር ግንኙነት ያግኙ፤ እንዴት ቦታ ማስያዝ "
    "እንደሚቻልም ያቅርቡ።",
    "task_27_rail", "cross-service: the flight arrives, the rail leg is a partner product")

task_28 = _partner_task(
    28, "riftdrive", "RiftDrive", "ሪፍት ድራይቭ",
    "Reserve an airport transfer with RiftDrive for two passengers arriving at Nairobi "
    "(NBO) on 2026-04-12, and proceed to the booking review page without paying.",
    "በ2026-04-12 ናይሮቢ (NBO) ለሚደርሱ ሁለት ተሳፋሪዎች በሪፍት ድራይቭ የአየር ማረፊያ ትራንስፖርት ያስይዙ፤ "
    "ሳይከፍሉ እስከ ቦታ ማስያዣ ማጠቃለያ ገጽ ይቀጥሉ።",
    "task_28_car", "partner booking flow that still stops at a review page")

task_29 = _partner_task(
    29, "safevoyage", "SafeVoyage Travel Cover", "ሴፍቮያጅ የጉዞ መድን",
    "Review the SafeVoyage travel insurance option for a round trip to Europe, report the "
    "coverage limits and the price, and stop before purchase.",
    "ወደ አውሮፓ ለሚደረግ የደርሶ መልስ ጉዞ የሴፍቮያጅ የጉዞ መድን አማራጭን ይገምግሙ፤ የሽፋን ገደቦችንና ዋጋውን "
    "ያቅርቡ፤ ከግዢ በፊት ያቁሙ።",
    "task_29_insurance", "coverage comparison, priced as a percentage of the fare")


def task_30(conn):
    office = conn.execute(
        "select country_code, country_en, country_am, city_en, city_am, phone, "
        "emergency_phone, hours_en, hours_am from contact_offices "
        "where has_ticket_desk = 0 order by id limit 1").fetchone()
    return (
        dict(office),
        f"A passenger in {office['country_en']} has an urgent problem with a booking "
        f"outside local office hours. Find the contact options for that country and "
        f"report the number to call and the local office hours.",
        f"በ{office['country_am']} ያለ ተሳፋሪ ከአካባቢው ቢሮ የሥራ ሰዓት ውጭ አስቸኳይ የቦታ ማስያዣ ችግር "
        f"አለበት። ለዚያ አገር ያሉትን የመገናኛ አማራጮች አግኝተው የሚደወልበትን ቁጥርና የአካባቢውን የቢሮ ሰዓት ያቅርቡ።",
        {"eval_types": ["string_match"],
         "reference_answers": {"must_include_en": [office["emergency_phone"], office["hours_en"]],
                               "must_include_am": [office["emergency_phone"], office["hours_am"]]}},
        "the office has no ticket desk and closes at night, so the 24-hour line is the "
        "only correct answer -- quoting the local number fails",
    )


REQUIRED_ROUTES = {
    1: ["/book/results"], 2: ["/book/passengers", "/book/review"],
    3: ["/flight-status"], 4: ["/schedules"], 5: ["/manage/*"],
    6: ["/manage/*/change", "/manage/*/change/review"],
    7: ["/manage/*/refund"], 8: ["/checkin", "/checkin/*/boarding-pass.pdf"],
    9: ["/checkin"], 10: ["/manage/*/seats", "/manage/*/seats/review"],
    11: ["/manage/*/seats"], 12: ["/baggage/allowance"],
    13: ["/manage/*/baggage", "/manage/*/baggage/review"],
    14: ["/baggage/special"], 15: ["/manage/*/upgrade"],
    16: ["/lounges/purchase", "/lounges/purchase/review"], 17: ["/lounges"],
    18: ["/miles/join"], 19: ["/miles/claim"], 20: ["/miles/award-search"],
    21: ["/onboard/wifi"], 22: ["/onboard/dining"], 23: ["/help/allergies"],
    24: ["/stopover"], 25: ["/partners/zena-hotel"], 26: ["/partners/evisa"],
    27: ["/partners/eurorail"], 28: ["/partners/riftdrive"],
    29: ["/partners/safevoyage"], 30: ["/help/contact"],
}


def registered_routes() -> set[str]:
    from app import create_app

    return {re.sub(r"<[^>]+>", "*", str(rule))
            for rule in create_app("en").url_map.iter_rules()}


def spreadsheet_rows() -> dict[int, dict]:
    import xml.etree.ElementTree as ET
    import zipfile

    NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    with zipfile.ZipFile(ROOT / "spec" / "tasks_source.xlsx") as zf:
        shared = [
            "".join(t.text or "" for t in si.iter(NS + "t"))
            for si in ET.fromstring(zf.read("xl/sharedStrings.xml")).iter(NS + "si")
        ]
        sheet = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))

    rows = {}
    for row in sheet.iter(NS + "row"):
        cells = {}
        for cell in row.iter(NS + "c"):
            column = "".join(c for c in cell.get("r") if c.isalpha())
            value = cell.find(NS + "v")
            if value is None:
                continue
            cells[column] = shared[int(value.text)] if cell.get("t") == "s" else value.text
        if cells.get("A", "").replace(".", "").isdigit():
            rows[int(float(cells["A"]))] = {
                "service": cells.get("B", ""), "question_en": cells.get("D", ""),
                "question_am": cells.get("E", ""), "eval_type": cells.get("F", ""),
                "complexity": cells.get("G", ""), "notes": cells.get("H", ""),
            }
    return rows


def substitute_brands(text: str, lang: str) -> tuple[str, list[tuple[str, str]]]:
    applied = []
    for original, replacement in TASK_TEXT_SUBSTITUTIONS[lang].items():
        if original in text:
            text = text.replace(original, replacement)
            applied.append((original, replacement))
    return text, applied


def _for_language(params: dict, lang: str) -> dict:
    other = "am" if lang == "en" else "en"
    out = {}
    for key, value in params.items():
        if key.endswith(f"_{other}"):
            continue
        name = key[:-3] if key.endswith(f"_{lang}") else key
        out[name] = value if isinstance(value, (int, float, list, type(None))) else str(value)
    return out


def normalise_answers(evaluation: dict, lang: str) -> dict:
    result = json.loads(json.dumps(evaluation))
    answers = result.get("reference_answers")
    if not answers:
        return result
    specific = answers.pop(f"must_include_{lang}", None)
    answers.pop("must_include_en", None)
    answers.pop("must_include_am", None)
    if specific is not None:
        answers["must_include"] = specific
    return result


def main() -> None:
    conn = td.connect()
    source = spreadsheet_rows()
    routes = registered_routes()
    substitutions: list[tuple[int, str, str, str]] = []

    tasks = {"en": [], "am": []}
    for number in range(1, 31):
        builder = globals()[f"task_{number}"]
        params, intent_en, intent_am, evaluation, rationale = builder(conn)
        meta = source.get(number, {})

        required = REQUIRED_ROUTES[number]
        missing = [r for r in required if r not in routes]

        for lang, intent in (("en", intent_en), ("am", intent_am)):
            baseline = meta.get("question_en" if lang == "en" else "question_am", "")
            _, applied = substitute_brands(baseline, lang)
            for original, replacement in applied:
                substitutions.append((number, lang, original, replacement))

            tasks[lang].append({
                "task_id": number,
                "service": substitute_brands(meta.get("service", ""), "en")[0],
                "language": lang,
                "sites": ["selam"],
                "start_url": BASE[lang] + "/",
                "intent": intent,
                "eval": normalise_answers(evaluation, lang),
                "require_reset": True,
                "complexity": meta.get("complexity", ""),
                "notes": substitute_brands(meta.get("notes", ""), "en")[0],
                "instantiation": {
                    "rationale": rationale,
                    "parameters": _for_language(params, lang),
                },
                "runnable": not missing,
                "blocked_by": missing,
            })

    out = ROOT / "tasks"
    out.mkdir(exist_ok=True)
    for lang in ("en", "am"):
        path = out / f"tasks_{lang}.json"
        path.write_text(json.dumps(tasks[lang], ensure_ascii=False, indent=2) + "\n", "utf-8")

    _write_substitutions(substitutions)

    runnable = sum(1 for t in tasks["en"] if t["runnable"])
    print(f"wrote tasks/tasks_en.json and tasks/tasks_am.json -- 30 tasks each")
    print(f"  runnable now      {runnable}/30")
    print(f"  blocked           {30 - runnable}/30 "
          f"({sorted(t['task_id'] for t in tasks['en'] if not t['runnable'])})")
    print(f"  state-check       {sum(1 for t in tasks['en'] if 'db_state' in t['eval']['eval_types'])}")
    print(f"  brand rewrites    {len(substitutions)} logged to spec/brand_substitutions.md")

    assert [t["task_id"] for t in tasks["en"]] == [t["task_id"] for t in tasks["am"]]
    for a, b in zip(tasks["en"], tasks["am"]):
        assert set(a) == set(b)
        assert a["eval"]["eval_types"] == b["eval"]["eval_types"]
        assert a["runnable"] == b["runnable"]


def _write_substitutions(rows: list[tuple[int, str, str, str]]) -> None:
    lines = [
        "# Brand substitutions",
        "",
        "Every commercial mark from `spec/tasks_source.xlsx` rewritten to its synthetic",
        "equivalent, in both languages (SPEC.md 3). Geography is untouched: city names,",
        "airport names and IATA codes are factual and are retained.",
        "",
        "The substitution table lives in `tools/brand_substitutions.py`, outside `app/`,",
        "so the shipped artifacts contain no real trademark string at all.",
        "",
        "| Task | Lang | Original | Replacement |",
        "|---|---|---|---|",
    ]
    seen = set()
    for number, lang, original, replacement in sorted(rows):
        key = (lang, original)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"| {number} | {lang} | {original} | {replacement} |")
    lines += ["", f"{len(seen)} distinct substitutions across {len({r[0] for r in rows})} tasks."]
    (ROOT / "spec" / "brand_substitutions.md").write_text("\n".join(lines) + "\n", "utf-8")


if __name__ == "__main__":
    main()
