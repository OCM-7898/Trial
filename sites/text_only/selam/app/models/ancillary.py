from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class _Request:

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int | None] = mapped_column(
        ForeignKey("bookings.id"), index=True, nullable=True
    )
    reference_no: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)


class ChangeRequest(_Request, Base):
    __tablename__ = "change_requests"

    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id"), index=True)
    new_flight_id: Mapped[int] = mapped_column(ForeignKey("flights.id"))
    eligibility_reason: Mapped[str | None] = mapped_column(String(40), nullable=True)
    fare_difference_usd: Mapped[float] = mapped_column(Float, default=0.0)
    change_fee_usd: Mapped[float] = mapped_column(Float, default=0.0)
    total_due_usd: Mapped[float] = mapped_column(Float, default=0.0)


class RefundRequest(_Request, Base):
    __tablename__ = "refund_requests"

    eligibility_reason: Mapped[str | None] = mapped_column(String(40), nullable=True)
    refund_pct: Mapped[int] = mapped_column(Integer, default=0)
    gross_usd: Mapped[float] = mapped_column(Float, default=0.0)
    fee_usd: Mapped[float] = mapped_column(Float, default=0.0)
    quoted_amount_usd: Mapped[float] = mapped_column(Float, default=0.0)


class BaggagePurchase(_Request, Base):
    __tablename__ = "baggage_purchases"

    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id"), index=True)
    extra_kg: Mapped[int] = mapped_column(Integer, default=0)
    extra_pieces: Mapped[int] = mapped_column(Integer, default=0)
    price_usd: Mapped[float] = mapped_column(Float, default=0.0)


class UpgradePurchase(_Request, Base):
    __tablename__ = "upgrade_purchases"

    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id"), index=True)
    target_fare_class_id: Mapped[int] = mapped_column(ForeignKey("fare_classes.id"))
    price_usd: Mapped[float] = mapped_column(Float, default=0.0)
    benefits_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class LoungePurchase(_Request, Base):

    __tablename__ = "lounge_purchases"

    lounge_id: Mapped[int] = mapped_column(ForeignKey("lounges.id"), index=True)
    flight_id: Mapped[int | None] = mapped_column(ForeignKey("flights.id"), nullable=True)
    passenger_name: Mapped[str] = mapped_column(String(160))
    guests: Mapped[int] = mapped_column(Integer, default=0)
    price_usd: Mapped[float] = mapped_column(Float, default=0.0)


class BaggageRule(Base):

    __tablename__ = "baggage_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    region: Mapped[str] = mapped_column(String(32), index=True)
    cabin: Mapped[str] = mapped_column(String(16), index=True)
    pax_type: Mapped[str] = mapped_column(String(8), index=True)
    checked_pieces: Mapped[int] = mapped_column(Integer)
    checked_kg: Mapped[int] = mapped_column(Integer)
    cabin_kg: Mapped[int] = mapped_column(Integer)
    cabin_dims_cm: Mapped[str] = mapped_column(String(24))
    extra_kg_price_usd: Mapped[float] = mapped_column(Float, default=0.0)
    extra_piece_price_usd: Mapped[float] = mapped_column(Float, default=0.0)
