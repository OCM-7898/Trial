from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, translated


class Booking(Base):

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    pnr: Mapped[str] = mapped_column(String(6), unique=True, index=True)
    surname_en: Mapped[str] = mapped_column(String(80), index=True)
    surname_am: Mapped[str] = mapped_column(String(80), index=True)
    surname_bn: Mapped[str] = mapped_column(String(80), index=True)
    surname_hi: Mapped[str] = mapped_column(String(80), index=True)
    surname_ur: Mapped[str] = mapped_column(String(80), index=True)
    email: Mapped[str] = mapped_column(String(160))
    phone: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(16), default="confirmed")
    created_on: Mapped[date] = mapped_column(Date)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    total_paid: Mapped[float] = mapped_column(Float, default=0.0)
    booked_channel: Mapped[str] = mapped_column(String(16), default="website")
    is_group: Mapped[bool] = mapped_column(Boolean, default=False)

    surname = translated("surname")

    passengers: Mapped[list["Passenger"]] = relationship(
        back_populates="booking", order_by="Passenger.id", cascade="all, delete-orphan"
    )
    segments: Mapped[list["Segment"]] = relationship(
        back_populates="booking", order_by="Segment.sequence", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Booking {self.pnr}>"


class Passenger(Base):
    __tablename__ = "passengers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), index=True)
    first_name_en: Mapped[str] = mapped_column(String(80))
    first_name_am: Mapped[str] = mapped_column(String(80))
    first_name_bn: Mapped[str] = mapped_column(String(80))
    first_name_hi: Mapped[str] = mapped_column(String(80))
    first_name_ur: Mapped[str] = mapped_column(String(80))
    last_name_en: Mapped[str] = mapped_column(String(80))
    last_name_am: Mapped[str] = mapped_column(String(80))
    last_name_bn: Mapped[str] = mapped_column(String(80))
    last_name_hi: Mapped[str] = mapped_column(String(80))
    last_name_ur: Mapped[str] = mapped_column(String(80))
    pax_type: Mapped[str] = mapped_column(String(8))
    dob: Mapped[date | None] = mapped_column(Date, nullable=True)
    loyalty_number: Mapped[str | None] = mapped_column(String(12), nullable=True)
    special_meal: Mapped[str | None] = mapped_column(String(8), nullable=True)
    assistance_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    allergy_note_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergy_note_am: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergy_note_bn: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergy_note_hi: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergy_note_ur: Mapped[str | None] = mapped_column(Text, nullable=True)
    passport_number: Mapped[str | None] = mapped_column(String(20), nullable=True)

    booking: Mapped[Booking] = relationship(back_populates="passengers")

    first_name = translated("first_name")
    last_name = translated("last_name")
    allergy_note = translated("allergy_note")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Passenger {self.id}>"


class Segment(Base):

    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), index=True)
    flight_id: Mapped[int] = mapped_column(ForeignKey("flights.id"), index=True)
    fare_class_id: Mapped[int] = mapped_column(ForeignKey("fare_classes.id"))
    sequence: Mapped[int] = mapped_column(Integer, default=1)
    direction: Mapped[str] = mapped_column(String(8), default="outbound")
    checked_in: Mapped[bool] = mapped_column(Boolean, default=False)
    baggage_allowance_kg: Mapped[int] = mapped_column(Integer, default=23)
    extra_baggage_kg: Mapped[int] = mapped_column(Integer, default=0)
    operated_by_en: Mapped[str | None] = mapped_column(String(80), nullable=True)
    operated_by_am: Mapped[str | None] = mapped_column(String(80), nullable=True)
    operated_by_bn: Mapped[str | None] = mapped_column(String(80), nullable=True)
    operated_by_hi: Mapped[str | None] = mapped_column(String(80), nullable=True)
    operated_by_ur: Mapped[str | None] = mapped_column(String(80), nullable=True)

    booking: Mapped[Booking] = relationship(back_populates="segments")

    operated_by = translated("operated_by")

    def __repr__(self) -> str:
        return f"<Segment {self.id}>"


class SeatAssignment(Base):
    __tablename__ = "seat_assignments"
    __table_args__ = (
        UniqueConstraint("segment_id", "seat_no", name="uq_seat_per_segment"),
        UniqueConstraint("segment_id", "passenger_id", name="uq_one_seat_per_pax"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id"), index=True)
    passenger_id: Mapped[int] = mapped_column(ForeignKey("passengers.id"), index=True)
    seat_no: Mapped[str] = mapped_column(String(4))
    paid_amount: Mapped[float] = mapped_column(Float, default=0.0)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<SeatAssignment {self.seat_no}>"
