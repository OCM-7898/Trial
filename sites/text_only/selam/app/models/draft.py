from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class DraftBooking(Base):
    __tablename__ = "draft_bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(String(6), unique=True, index=True)
    flight_id: Mapped[int] = mapped_column(ForeignKey("flights.id"), index=True)
    fare_class_id: Mapped[int] = mapped_column(ForeignKey("fare_classes.id"))
    return_flight_id: Mapped[int | None] = mapped_column(
        ForeignKey("flights.id"), nullable=True)
    adults: Mapped[int] = mapped_column(Integer, default=1)
    contact_email: Mapped[str] = mapped_column(String(160), default="")
    contact_phone: Mapped[str] = mapped_column(String(40), default="")
    price_usd: Mapped[float] = mapped_column(Float, default=0.0)
    taxes_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)

    passengers: Mapped[list["DraftPassenger"]] = relationship(
        back_populates="draft", order_by="DraftPassenger.id",
        cascade="all, delete-orphan")

    @property
    def total_usd(self) -> float:
        return round(self.price_usd + self.taxes_usd, 2)


class DraftPassenger(Base):
    __tablename__ = "draft_passengers"

    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("draft_bookings.id"), index=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    pax_type: Mapped[str] = mapped_column(String(8), default="adult")
    dob: Mapped[date | None] = mapped_column(Date, nullable=True)

    draft: Mapped[DraftBooking] = relationship(back_populates="passengers")
