from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.network import Flight, Route
from ..models.onboard import MealMenu, SpecialMealCode, WifiPackage


def band_for(distance_km: int) -> str:
    if distance_km < 1500:
        return "short"
    if distance_km < 4500:
        return "medium"
    return "long"


def packages_for(session: Session, flight: Flight) -> list[WifiPackage]:
    if not flight.wifi_equipped:
        return []
    return list(session.scalars(
        select(WifiPackage).where(WifiPackage.flight_id == flight.id)
        .order_by(WifiPackage.position)))


def menu_for(session: Session, flight: Flight, cabin: str) -> MealMenu | None:
    route = session.get(Route, flight.route_id)
    band = band_for(route.distance_km)
    service = {"short": "snack", "medium": "meal", "long": "dinner"}[band]
    return session.scalars(
        select(MealMenu).where(MealMenu.band == band, MealMenu.cabin == cabin,
                               MealMenu.service == service)).one_or_none()


def meal_codes(session: Session) -> list[SpecialMealCode]:
    return list(session.scalars(select(SpecialMealCode).order_by(SpecialMealCode.id)))


def meal_code(session: Session, code: str) -> SpecialMealCode | None:
    return session.scalars(
        select(SpecialMealCode).where(SpecialMealCode.code == code.upper())).one_or_none()
