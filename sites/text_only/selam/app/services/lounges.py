from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.content import Lounge

TIERS = ("blue", "silver", "gold", "platinum")


@dataclass(frozen=True)
class Access:
    lounge: Lounge
    free: bool
    reason: str
    price_usd: float


def at_airport(session: Session, iata: str, terminal: str | None = None) -> list[Lounge]:
    stmt = select(Lounge).where(Lounge.airport_iata == iata.upper())
    if terminal:
        stmt = stmt.where(Lounge.terminal == terminal)
    return list(session.scalars(stmt.order_by(Lounge.terminal, Lounge.id)))


def access_for(lounge: Lounge, cabin: str | None, tier: str | None) -> Access:
    admitted = {token.strip() for token in (lounge.access_free_for or "").split(",") if token.strip()}

    if cabin == "business" and "business" in admitted:
        return Access(lounge, True, "cabin", 0.0)
    if tier and tier.lower() in admitted:
        return Access(lounge, True, "tier", 0.0)
    if lounge.walk_in_price_usd > 0:
        return Access(lounge, False, "paid", lounge.walk_in_price_usd)
    return Access(lounge, False, "none", 0.0)
