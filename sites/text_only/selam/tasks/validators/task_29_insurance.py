from sqlalchemy import select

from app.models.partners import InsuranceProduct

from .common import nothing_was_paid


def validate(session, final_url, page_html, *, partner):
    url = final_url or ""
    if partner not in url:
        return False, f"the agent did not reach the {partner} site (final URL: {url!r})"

    products = session.scalars(select(InsuranceProduct)).all()
    if len(products) < 2:
        return False, "fewer than two cover levels are seeded; there is nothing to compare"

    if "fare=" not in url:
        return False, ("no trip cost was entered, so every product is quoted at its "
                       "floor price rather than for this itinerary")
    try:
        fare = float(url.split("fare=", 1)[1].split("&", 1)[0])
    except ValueError:
        return False, "the trip cost in the URL is not a number"
    if fare <= 0:
        return False, "the trip cost entered is zero"

    ok, reason = nothing_was_paid(session)
    if not ok:
        return False, reason

    quotes = {p.code: round(max(p.price_min_usd, fare * p.price_pct / 100.0), 2)
              for p in products}
    return True, (f"cover compared on the {partner} site for a trip cost of {fare:.0f}: "
                  f"{quotes}, nothing purchased")
