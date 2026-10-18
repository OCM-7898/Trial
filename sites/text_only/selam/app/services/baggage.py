from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.ancillary import BaggageRule
from ..models.network import Airport, Route

DOMESTIC_COUNTRY = "ET"


def region_for(origin: Airport, destination: Airport) -> str:
    if origin.country_code == DOMESTIC_COUNTRY and destination.country_code == DOMESTIC_COUNTRY:
        return "domestic"
    return destination.region if origin.region == "africa" else origin.region


def rule_for(session: Session, region: str, cabin: str, pax_type: str) -> BaggageRule | None:
    return session.scalars(
        select(BaggageRule).where(
            BaggageRule.region == region,
            BaggageRule.cabin == cabin,
            BaggageRule.pax_type == pax_type,
        )
    ).one_or_none()


def rule_for_route(session: Session, route: Route, cabin: str, pax_type: str) -> BaggageRule | None:
    origin = session.get(Airport, route.origin_id)
    destination = session.get(Airport, route.destination_id)
    return rule_for(session, region_for(origin, destination), cabin, pax_type)


def quote_extra(rule: BaggageRule, extra_kg: int, extra_pieces: int = 0) -> float:
    return round(extra_kg * rule.extra_kg_price_usd + extra_pieces * rule.extra_piece_price_usd, 2)
