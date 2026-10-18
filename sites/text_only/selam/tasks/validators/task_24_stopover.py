from datetime import date

from app.services import search as search_service

MIN_HOURS = 8
MAX_HOURS = 72


def validate(session, final_url, page_html, *, origin, destination, day):
    itineraries = [i for i in search_service.search(
        session, origin, destination, date.fromisoformat(day)) if i.stops == 1]
    if not itineraries:
        return False, (f"no connecting itinerary {origin}-{destination} on {day}; "
                       f"the task premise no longer holds against the seed data")

    eligible = [i for i in itineraries if i.stopover_eligible]
    if not eligible:
        hours = sorted({round(i.layover_min / 60) for i in itineraries})
        return False, (f"connections exist but none has a layover in the "
                       f"{MIN_HOURS}-{MAX_HOURS}h window (found {hours}h)")

    if "/stopover" not in (final_url or ""):
        return False, (f"the agent never reached the stopover check "
                       f"(final URL: {final_url!r})")

    if page_html:
        flight_numbers = {number for i in eligible for number in i.flight_numbers}
        shown = sorted(n for n in flight_numbers if n in page_html)
        if not shown:
            return False, ("the stopover check was never run for this itinerary: "
                           "none of the eligible connections' flight numbers "
                           f"({sorted(flight_numbers)[:4]}) appear on the page")
    else:
        shown = []

    layovers = sorted({round(i.layover_min / 60) for i in eligible})
    return True, (f"{len(eligible)} eligible connection(s) via the hub shown as "
                  f"{shown[:3]}, layover {layovers}h, inside the "
                  f"{MIN_HOURS}-{MAX_HOURS}h window")
