from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, translated


class LoyaltyMember(Base):
    __tablename__ = "loyalty_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_no: Mapped[str] = mapped_column(String(12), unique=True, index=True)
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
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    tier: Mapped[str] = mapped_column(String(12))
    miles_balance: Mapped[int] = mapped_column(Integer, default=0)
    qualifying_miles: Mapped[int] = mapped_column(Integer, default=0)
    joined_on: Mapped[date] = mapped_column(Date)
    country_code: Mapped[str] = mapped_column(String(2))
    created_at_runtime: Mapped[bool] = mapped_column(Boolean, default=False)

    first_name = translated("first_name")
    last_name = translated("last_name")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class MilesTransaction(Base):
    __tablename__ = "miles_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("loyalty_members.id"), index=True)
    posted_on: Mapped[date] = mapped_column(Date, index=True)
    kind: Mapped[str] = mapped_column(String(16))
    description_en: Mapped[str] = mapped_column(String(160))
    description_am: Mapped[str] = mapped_column(String(160))
    description_bn: Mapped[str] = mapped_column(String(160))
    description_hi: Mapped[str] = mapped_column(String(160))
    description_ur: Mapped[str] = mapped_column(String(160))
    flight_no: Mapped[str | None] = mapped_column(String(8), nullable=True)
    miles: Mapped[int] = mapped_column(Integer)
    qualifying_miles: Mapped[int] = mapped_column(Integer, default=0)

    description = translated("description")


class AwardInventory(Base):

    __tablename__ = "award_inventory"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    flight_id: Mapped[int] = mapped_column(ForeignKey("flights.id"), index=True)
    cabin: Mapped[str] = mapped_column(String(16), index=True)
    miles_required: Mapped[int] = mapped_column(Integer)
    taxes_usd: Mapped[float] = mapped_column(Float)
    seats: Mapped[int] = mapped_column(Integer)


class MissingMilesClaim(Base):

    __tablename__ = "missing_miles_claims"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_no: Mapped[str] = mapped_column(String(12), index=True)
    reference_no: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    ticket_no: Mapped[str] = mapped_column(String(20))
    flight_no: Mapped[str] = mapped_column(String(8))
    flight_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(16), default="under_review")
    created_at: Mapped[datetime] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
