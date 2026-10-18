from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from . import Base, translated


class WifiPackage(Base):

    __tablename__ = "wifi_packages"
    __table_args__ = (UniqueConstraint("flight_id", "position", name="uq_wifi_package"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    flight_id: Mapped[int] = mapped_column(ForeignKey("flights.id"), index=True)
    name_en: Mapped[str] = mapped_column(String(64))
    name_am: Mapped[str] = mapped_column(String(64))
    name_bn: Mapped[str] = mapped_column(String(64))
    name_hi: Mapped[str] = mapped_column(String(64))
    name_ur: Mapped[str] = mapped_column(String(64))
    mb: Mapped[int] = mapped_column(Integer)
    duration_min: Mapped[int] = mapped_column(Integer)
    price_usd: Mapped[float] = mapped_column(Float)
    position: Mapped[int] = mapped_column(Integer, default=0)

    name = translated("name")


class WifiPurchase(Base):
    __tablename__ = "wifi_purchases"

    id: Mapped[int] = mapped_column(primary_key=True)
    package_id: Mapped[int] = mapped_column(ForeignKey("wifi_packages.id"), index=True)
    booking_id: Mapped[int | None] = mapped_column(ForeignKey("bookings.id"), nullable=True)
    reference_no: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime)
    price_usd: Mapped[float] = mapped_column(Float, default=0.0)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)


class SpecialMealCode(Base):

    __tablename__ = "special_meal_codes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    code: Mapped[str] = mapped_column(String(4), unique=True)
    name_en: Mapped[str] = mapped_column(String(80))
    name_am: Mapped[str] = mapped_column(String(80))
    name_bn: Mapped[str] = mapped_column(String(80))
    name_hi: Mapped[str] = mapped_column(String(80))
    name_ur: Mapped[str] = mapped_column(String(80))
    description_en: Mapped[str] = mapped_column(Text)
    description_am: Mapped[str] = mapped_column(Text)
    description_bn: Mapped[str] = mapped_column(Text)
    description_hi: Mapped[str] = mapped_column(Text)
    description_ur: Mapped[str] = mapped_column(Text)
    cutoff_hours: Mapped[int] = mapped_column(Integer, default=24)

    name = translated("name")
    description = translated("description")


class MealMenu(Base):

    __tablename__ = "meal_menus"
    __table_args__ = (UniqueConstraint("band", "cabin", "service", name="uq_menu"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    band: Mapped[str] = mapped_column(String(16))
    cabin: Mapped[str] = mapped_column(String(16))
    service: Mapped[str] = mapped_column(String(16))
    courses_en: Mapped[str] = mapped_column(Text)
    courses_am: Mapped[str] = mapped_column(Text)
    courses_bn: Mapped[str] = mapped_column(Text)
    courses_hi: Mapped[str] = mapped_column(Text)
    courses_ur: Mapped[str] = mapped_column(Text)
    beverages_en: Mapped[str] = mapped_column(Text)
    beverages_am: Mapped[str] = mapped_column(Text)
    beverages_bn: Mapped[str] = mapped_column(Text)
    beverages_hi: Mapped[str] = mapped_column(Text)
    beverages_ur: Mapped[str] = mapped_column(Text)

    courses = translated("courses")
    beverages = translated("beverages")


class MealRequest(Base):

    __tablename__ = "meal_requests"
    __table_args__ = (UniqueConstraint("segment_id", "passenger_id", name="uq_meal_request"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id"), index=True)
    passenger_id: Mapped[int] = mapped_column(ForeignKey("passengers.id"), index=True)
    meal_code: Mapped[str] = mapped_column(String(4))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(16), default="requested")
