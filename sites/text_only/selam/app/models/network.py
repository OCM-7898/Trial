from __future__ import annotations

from datetime import date, time

from sqlalchemy import (
    Boolean, Date, Float, ForeignKey, Integer, String, Time, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, translated


class Airport(Base):

    __tablename__ = "airports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    iata: Mapped[str] = mapped_column(String(3), unique=True, index=True)
    icao: Mapped[str] = mapped_column(String(4), unique=True)
    city_en: Mapped[str] = mapped_column(String(80))
    city_am: Mapped[str] = mapped_column(String(80))
    city_bn: Mapped[str] = mapped_column(String(80))
    city_hi: Mapped[str] = mapped_column(String(80))
    city_ur: Mapped[str] = mapped_column(String(80))
    name_en: Mapped[str] = mapped_column(String(160))
    name_am: Mapped[str] = mapped_column(String(160))
    name_bn: Mapped[str] = mapped_column(String(160))
    name_hi: Mapped[str] = mapped_column(String(160))
    name_ur: Mapped[str] = mapped_column(String(160))
    country_en: Mapped[str] = mapped_column(String(80))
    country_am: Mapped[str] = mapped_column(String(80))
    country_bn: Mapped[str] = mapped_column(String(80))
    country_hi: Mapped[str] = mapped_column(String(80))
    country_ur: Mapped[str] = mapped_column(String(80))
    country_code: Mapped[str] = mapped_column(String(2))
    region: Mapped[str] = mapped_column(String(32))
    timezone: Mapped[str] = mapped_column(String(48))
    terminal_count: Mapped[int] = mapped_column(Integer, default=1)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    city = translated("city")
    name = translated("name")
    country = translated("country")

    def __repr__(self) -> str:
        return f"<Airport {self.iata}>"


class Route(Base):
    __tablename__ = "routes"
    __table_args__ = (UniqueConstraint("origin_id", "destination_id", name="uq_route_pair"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    origin_id: Mapped[int] = mapped_column(ForeignKey("airports.id"), index=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("airports.id"), index=True)
    distance_km: Mapped[int] = mapped_column(Integer)
    block_time_min: Mapped[int] = mapped_column(Integer)
    operating_days: Mapped[str] = mapped_column(String(7))
    seasonal_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    seasonal_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    origin: Mapped[Airport] = relationship(foreign_keys=[origin_id])
    destination: Mapped[Airport] = relationship(foreign_keys=[destination_id])

    def operates_on(self, day: date) -> bool:
        if self.seasonal_from and day < self.seasonal_from:
            return False
        if self.seasonal_to and day > self.seasonal_to:
            return False
        return self.operating_days[day.weekday()] != "."

    def __repr__(self) -> str:
        return f"<Route {self.id}>"


class Aircraft(Base):
    __tablename__ = "aircraft_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    code: Mapped[str] = mapped_column(String(8), unique=True)
    name_en: Mapped[str] = mapped_column(String(80))
    name_am: Mapped[str] = mapped_column(String(80))
    name_bn: Mapped[str] = mapped_column(String(80))
    name_hi: Mapped[str] = mapped_column(String(80))
    name_ur: Mapped[str] = mapped_column(String(80))
    rows_business: Mapped[int] = mapped_column(Integer)
    rows_economy: Mapped[int] = mapped_column(Integer)
    business_layout: Mapped[str] = mapped_column(String(16))
    economy_layout: Mapped[str] = mapped_column(String(16))
    has_wifi: Mapped[bool] = mapped_column(Boolean, default=False)

    name = translated("name")

    def __repr__(self) -> str:
        return f"<Aircraft {self.code}>"


class SeatMapSeat(Base):

    __tablename__ = "seat_maps"
    __table_args__ = (UniqueConstraint("aircraft_id", "seat_no", name="uq_seat"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    aircraft_id: Mapped[int] = mapped_column(ForeignKey("aircraft_types.id"), index=True)
    seat_no: Mapped[str] = mapped_column(String(4))
    row: Mapped[int] = mapped_column(Integer)
    col: Mapped[str] = mapped_column(String(1))
    cabin: Mapped[str] = mapped_column(String(16))
    is_exit: Mapped[bool] = mapped_column(Boolean, default=False)
    is_aisle: Mapped[bool] = mapped_column(Boolean, default=False)
    is_window: Mapped[bool] = mapped_column(Boolean, default=False)
    is_bassinet: Mapped[bool] = mapped_column(Boolean, default=False)
    extra_legroom: Mapped[bool] = mapped_column(Boolean, default=False)
    price_usd: Mapped[float] = mapped_column(Float, default=0.0)

    aircraft: Mapped[Aircraft] = relationship()

    def __repr__(self) -> str:
        return f"<Seat {self.seat_no}>"


class Flight(Base):
    __tablename__ = "flights"
    __table_args__ = (UniqueConstraint("flight_no", "date", name="uq_flight_date"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    flight_no: Mapped[str] = mapped_column(String(8), index=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    dep_time: Mapped[time] = mapped_column(Time)
    arr_time: Mapped[time] = mapped_column(Time)
    arr_day_offset: Mapped[int] = mapped_column(Integer, default=0)
    aircraft_id: Mapped[int] = mapped_column(ForeignKey("aircraft_types.id"))
    status: Mapped[str] = mapped_column(String(16), default="scheduled")
    gate: Mapped[str | None] = mapped_column(String(6), nullable=True)
    terminal_dep: Mapped[str | None] = mapped_column(String(4), nullable=True)
    terminal_arr: Mapped[str | None] = mapped_column(String(4), nullable=True)
    wifi_equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    has_lounge_access: Mapped[bool] = mapped_column(Boolean, default=False)
    delay_minutes: Mapped[int] = mapped_column(Integer, default=0)

    route: Mapped[Route] = relationship()
    aircraft: Mapped[Aircraft] = relationship()

    def __repr__(self) -> str:
        return f"<Flight {self.flight_no} {self.date}>"


class FareClass(Base):
    __tablename__ = "fare_classes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    code: Mapped[str] = mapped_column(String(2), unique=True)
    cabin: Mapped[str] = mapped_column(String(16))
    name_en: Mapped[str] = mapped_column(String(64))
    name_am: Mapped[str] = mapped_column(String(64))
    name_bn: Mapped[str] = mapped_column(String(64))
    name_hi: Mapped[str] = mapped_column(String(64))
    name_ur: Mapped[str] = mapped_column(String(64))
    refundable: Mapped[bool] = mapped_column(Boolean, default=False)
    refund_pct: Mapped[int] = mapped_column(Integer, default=0)
    refund_fee_usd: Mapped[float] = mapped_column(Float, default=0.0)
    changeable: Mapped[bool] = mapped_column(Boolean, default=True)
    change_fee_usd: Mapped[float] = mapped_column(Float, default=0.0)
    baggage_rule_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    miles_earn_pct: Mapped[int] = mapped_column(Integer, default=100)
    upgrade_eligible: Mapped[bool] = mapped_column(Boolean, default=True)
    seat_selection_free: Mapped[bool] = mapped_column(Boolean, default=False)

    name = translated("name")

    def __repr__(self) -> str:
        return f"<FareClass {self.code}>"


class Fare(Base):

    __tablename__ = "fares"
    __table_args__ = (UniqueConstraint("flight_id", "fare_class_id", name="uq_fare"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    flight_id: Mapped[int] = mapped_column(ForeignKey("flights.id"), index=True)
    fare_class_id: Mapped[int] = mapped_column(ForeignKey("fare_classes.id"), index=True)
    price_usd: Mapped[float] = mapped_column(Float)
    taxes_usd: Mapped[float] = mapped_column(Float, default=0.0)
    seats_available: Mapped[int] = mapped_column(Integer, default=0)

    flight: Mapped[Flight] = relationship()
    fare_class: Mapped[FareClass] = relationship()

    def __repr__(self) -> str:
        return f"<Fare {self.flight_id}/{self.fare_class_id}>"
