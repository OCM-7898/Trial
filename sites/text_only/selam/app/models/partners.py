from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from . import Base, translated


class HotelRoom(Base):

    __tablename__ = "hotel_rooms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    code: Mapped[str] = mapped_column(String(12), unique=True)
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
    sleeps: Mapped[int] = mapped_column(Integer, default=1)
    price_per_block_usd: Mapped[float] = mapped_column(Float)
    block_hours: Mapped[int] = mapped_column(Integer, default=6)
    rooms_available: Mapped[int] = mapped_column(Integer, default=0)
    airside: Mapped[bool] = mapped_column(Boolean, default=True)

    name = translated("name")
    description = translated("description")


class HotelBooking(Base):
    __tablename__ = "hotel_bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("hotel_rooms.id"), index=True)
    reference_no: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    guest_name: Mapped[str] = mapped_column(String(160))
    arrival: Mapped[date] = mapped_column(Date)
    hours: Mapped[int] = mapped_column(Integer)
    price_usd: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)


class VisaType(Base):

    __tablename__ = "visa_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    code: Mapped[str] = mapped_column(String(12), unique=True)
    name_en: Mapped[str] = mapped_column(String(80))
    name_am: Mapped[str] = mapped_column(String(80))
    name_bn: Mapped[str] = mapped_column(String(80))
    name_hi: Mapped[str] = mapped_column(String(80))
    name_ur: Mapped[str] = mapped_column(String(80))
    eligibility_en: Mapped[str] = mapped_column(Text)
    eligibility_am: Mapped[str] = mapped_column(Text)
    eligibility_bn: Mapped[str] = mapped_column(Text)
    eligibility_hi: Mapped[str] = mapped_column(Text)
    eligibility_ur: Mapped[str] = mapped_column(Text)
    documents_en: Mapped[str] = mapped_column(Text)
    documents_am: Mapped[str] = mapped_column(Text)
    documents_bn: Mapped[str] = mapped_column(Text)
    documents_hi: Mapped[str] = mapped_column(Text)
    documents_ur: Mapped[str] = mapped_column(Text)
    validity_days: Mapped[int] = mapped_column(Integer)
    fee_usd: Mapped[float] = mapped_column(Float)
    processing_days: Mapped[int] = mapped_column(Integer)

    name = translated("name")
    eligibility = translated("eligibility")
    documents = translated("documents")


class RailConnection(Base):

    __tablename__ = "rail_connections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    arrival_iata: Mapped[str] = mapped_column(String(3), index=True)
    destination_en: Mapped[str] = mapped_column(String(80))
    destination_am: Mapped[str] = mapped_column(String(80))
    destination_bn: Mapped[str] = mapped_column(String(80))
    destination_hi: Mapped[str] = mapped_column(String(80))
    destination_ur: Mapped[str] = mapped_column(String(80))
    operator_en: Mapped[str] = mapped_column(String(60))
    operator_am: Mapped[str] = mapped_column(String(60))
    operator_bn: Mapped[str] = mapped_column(String(60))
    operator_hi: Mapped[str] = mapped_column(String(60))
    operator_ur: Mapped[str] = mapped_column(String(60))
    journey_min: Mapped[int] = mapped_column(Integer)
    changes: Mapped[int] = mapped_column(Integer, default=0)
    ticket_type_en: Mapped[str] = mapped_column(String(80))
    ticket_type_am: Mapped[str] = mapped_column(String(80))
    ticket_type_bn: Mapped[str] = mapped_column(String(80))
    ticket_type_hi: Mapped[str] = mapped_column(String(80))
    ticket_type_ur: Mapped[str] = mapped_column(String(80))
    booking_note_en: Mapped[str] = mapped_column(Text)
    booking_note_am: Mapped[str] = mapped_column(Text)
    booking_note_bn: Mapped[str] = mapped_column(Text)
    booking_note_hi: Mapped[str] = mapped_column(Text)
    booking_note_ur: Mapped[str] = mapped_column(Text)

    destination = translated("destination")
    operator = translated("operator")
    ticket_type = translated("ticket_type")
    booking_note = translated("booking_note")


class CarOffer(Base):

    __tablename__ = "car_offers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    airport_iata: Mapped[str] = mapped_column(String(3), index=True)
    category: Mapped[str] = mapped_column(String(16))
    name_en: Mapped[str] = mapped_column(String(80))
    name_am: Mapped[str] = mapped_column(String(80))
    name_bn: Mapped[str] = mapped_column(String(80))
    name_hi: Mapped[str] = mapped_column(String(80))
    name_ur: Mapped[str] = mapped_column(String(80))
    seats: Mapped[int] = mapped_column(Integer)
    luggage: Mapped[int] = mapped_column(Integer)
    price_usd: Mapped[float] = mapped_column(Float)
    per_day: Mapped[bool] = mapped_column(Boolean, default=False)

    name = translated("name")


class CarBooking(Base):
    __tablename__ = "car_bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    offer_id: Mapped[int] = mapped_column(ForeignKey("car_offers.id"), index=True)
    reference_no: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    passengers: Mapped[int] = mapped_column(Integer, default=1)
    pickup_date: Mapped[date] = mapped_column(Date)
    price_usd: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)


class InsuranceProduct(Base):

    __tablename__ = "insurance_products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    code: Mapped[str] = mapped_column(String(12), unique=True)
    name_en: Mapped[str] = mapped_column(String(80))
    name_am: Mapped[str] = mapped_column(String(80))
    name_bn: Mapped[str] = mapped_column(String(80))
    name_hi: Mapped[str] = mapped_column(String(80))
    name_ur: Mapped[str] = mapped_column(String(80))
    coverage_en: Mapped[str] = mapped_column(Text)
    coverage_am: Mapped[str] = mapped_column(Text)
    coverage_bn: Mapped[str] = mapped_column(Text)
    coverage_hi: Mapped[str] = mapped_column(Text)
    coverage_ur: Mapped[str] = mapped_column(Text)
    medical_limit_usd: Mapped[int] = mapped_column(Integer)
    cancellation_limit_usd: Mapped[int] = mapped_column(Integer)
    baggage_limit_usd: Mapped[int] = mapped_column(Integer)
    price_pct: Mapped[float] = mapped_column(Float)
    price_min_usd: Mapped[float] = mapped_column(Float)

    name = translated("name")
    coverage = translated("coverage")
