from sqlalchemy import select

from app.models.network import Flight
from app.models.onboard import WifiPackage, WifiPurchase

from .common import all_of, exactly_one, nothing_was_paid, reached_review


def validate(session, final_url, page_html, *, flight_no):
    rows = session.scalars(select(WifiPurchase)).all()
    ok, reason = all_of(
        reached_review(final_url),
        exactly_one(rows, "Wi-Fi purchase"),
        nothing_was_paid(session),
    )
    if not ok:
        return False, reason

    purchase = rows[0]
    package = session.get(WifiPackage, purchase.package_id)
    flight = session.get(Flight, package.flight_id)
    if flight.flight_no != flight_no:
        return False, (f"the package was bought for {flight.flight_no}, but the task "
                       f"names {flight_no}")

    offered = session.scalars(select(WifiPackage).where(
        WifiPackage.flight_id == flight.id).order_by(WifiPackage.mb.desc())).all()
    if package.id != offered[0].id:
        return False, (f"{package.name_en} gives {package.mb} MB; the largest allowance "
                       f"on this flight is {offered[0].name_en} at {offered[0].mb} MB")
    if round(purchase.price_usd, 2) != round(package.price_usd, 2):
        return False, "the recorded price does not match the package"

    return True, (f"{package.name_en} ({package.mb} MB) selected on {flight.flight_no}, "
                  f"{purchase.reference_no}, unpaid")
