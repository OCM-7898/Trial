from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Checkin(Base):
    __tablename__ = "checkins"
    __table_args__ = (
        UniqueConstraint("segment_id", "passenger_id", name="uq_checkin_once"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id"), index=True)
    passenger_id: Mapped[int] = mapped_column(ForeignKey("passengers.id"), index=True)
    checked_in_at: Mapped[datetime] = mapped_column(DateTime)
    boarding_pass_id: Mapped[int | None] = mapped_column(
        ForeignKey("boarding_passes.id"), nullable=True
    )
    ineligibility_code: Mapped[str | None] = mapped_column(String(40), nullable=True)


class BoardingPass(Base):
    __tablename__ = "boarding_passes"

    id: Mapped[int] = mapped_column(primary_key=True)
    barcode_payload: Mapped[str] = mapped_column(String(40), unique=True)
    pdf_path: Mapped[str] = mapped_column(String(255))
    gate: Mapped[str | None] = mapped_column(String(6), nullable=True)
    boarding_time: Mapped[str] = mapped_column(String(5))
    sequence_no: Mapped[int] = mapped_column(Integer)
    seat_no: Mapped[str | None] = mapped_column(String(4), nullable=True)
