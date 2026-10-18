from sqlalchemy import select

from app.models.ancillary import LoungePurchase
from app.models.content import Lounge

from .common import all_of, exactly_one, nothing_was_paid, reached_review


def validate(session, final_url, page_html, *, lounge_id, expected_price_usd):
    rows = session.scalars(select(LoungePurchase)).all()
    ok, reason = all_of(
        reached_review(final_url),
        exactly_one(rows, "lounge purchase"),
        nothing_was_paid(session),
    )
    if not ok:
        return False, reason

    purchase = rows[0]
    lounge = session.get(Lounge, purchase.lounge_id)
    if purchase.lounge_id != lounge_id:
        wanted = session.get(Lounge, lounge_id)
        return False, (f"access was bought for {lounge.name_en!r}; the task names "
                       f"{wanted.name_en!r}")
    if purchase.guests != 0:
        return False, f"{purchase.guests} guest(s) were added; the task asks for none"
    if round(purchase.price_usd, 2) != round(expected_price_usd, 2):
        return False, (f"price {purchase.price_usd} does not match the lounge's walk-in "
                       f"rate {expected_price_usd}")
    if not purchase.passenger_name.strip():
        return False, "no passenger name was entered"

    return True, (f"lounge access pending at {lounge.airport_iata} "
                  f"({lounge.name_en}) for USD {purchase.price_usd:.0f}, unpaid")
