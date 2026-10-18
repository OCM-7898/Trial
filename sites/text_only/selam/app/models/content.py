from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from . import Base, translated


class ContentPage(Base):
    __tablename__ = "content_pages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(32), index=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    title_en: Mapped[str] = mapped_column(String(200))
    title_am: Mapped[str] = mapped_column(String(200))
    title_bn: Mapped[str] = mapped_column(String(200))
    title_hi: Mapped[str] = mapped_column(String(200))
    title_ur: Mapped[str] = mapped_column(String(200))
    summary_en: Mapped[str] = mapped_column(Text)
    summary_am: Mapped[str] = mapped_column(Text)
    summary_bn: Mapped[str] = mapped_column(Text)
    summary_hi: Mapped[str] = mapped_column(Text)
    summary_ur: Mapped[str] = mapped_column(Text)
    body_html_en: Mapped[str] = mapped_column(Text)
    body_html_am: Mapped[str] = mapped_column(Text)
    body_html_bn: Mapped[str] = mapped_column(Text)
    body_html_hi: Mapped[str] = mapped_column(Text)
    body_html_ur: Mapped[str] = mapped_column(Text)

    title = translated("title")
    summary = translated("summary")
    body_html = translated("body_html")

    def __repr__(self) -> str:
        return f"<ContentPage {self.slug}>"


class SpecialBaggageItem(Base):

    __tablename__ = "special_baggage_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    category: Mapped[str] = mapped_column(String(32), index=True)
    item_en: Mapped[str] = mapped_column(String(120))
    item_am: Mapped[str] = mapped_column(String(120))
    item_bn: Mapped[str] = mapped_column(String(120))
    item_hi: Mapped[str] = mapped_column(String(120))
    item_ur: Mapped[str] = mapped_column(String(120))
    max_kg: Mapped[int] = mapped_column(Integer)
    max_dims_cm: Mapped[str] = mapped_column(String(32))
    fee_usd: Mapped[float] = mapped_column(Float)
    advance_notice_required: Mapped[bool] = mapped_column(Boolean, default=False)
    notes_en: Mapped[str] = mapped_column(Text)
    notes_am: Mapped[str] = mapped_column(Text)
    notes_bn: Mapped[str] = mapped_column(Text)
    notes_hi: Mapped[str] = mapped_column(Text)
    notes_ur: Mapped[str] = mapped_column(Text)

    item = translated("item")
    notes = translated("notes")


class ContactOffice(Base):

    __tablename__ = "contact_offices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    country_code: Mapped[str] = mapped_column(String(2), index=True)
    country_en: Mapped[str] = mapped_column(String(80))
    country_am: Mapped[str] = mapped_column(String(80))
    country_bn: Mapped[str] = mapped_column(String(80))
    country_hi: Mapped[str] = mapped_column(String(80))
    country_ur: Mapped[str] = mapped_column(String(80))
    city_en: Mapped[str] = mapped_column(String(80))
    city_am: Mapped[str] = mapped_column(String(80))
    city_bn: Mapped[str] = mapped_column(String(80))
    city_hi: Mapped[str] = mapped_column(String(80))
    city_ur: Mapped[str] = mapped_column(String(80))
    phone: Mapped[str] = mapped_column(String(40))
    emergency_phone: Mapped[str] = mapped_column(String(40))
    email: Mapped[str] = mapped_column(String(120))
    hours_en: Mapped[str] = mapped_column(String(160))
    hours_am: Mapped[str] = mapped_column(String(160))
    hours_bn: Mapped[str] = mapped_column(String(160))
    hours_hi: Mapped[str] = mapped_column(String(160))
    hours_ur: Mapped[str] = mapped_column(String(160))
    address_en: Mapped[str] = mapped_column(Text)
    address_am: Mapped[str] = mapped_column(Text)
    address_bn: Mapped[str] = mapped_column(Text)
    address_hi: Mapped[str] = mapped_column(Text)
    address_ur: Mapped[str] = mapped_column(Text)
    has_ticket_desk: Mapped[bool] = mapped_column(Boolean, default=True)

    country = translated("country")
    city = translated("city")
    hours = translated("hours")
    address = translated("address")


class Lounge(Base):

    __tablename__ = "lounges"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    airport_iata: Mapped[str] = mapped_column(String(3), index=True)
    terminal: Mapped[str] = mapped_column(String(8))
    name_en: Mapped[str] = mapped_column(String(120))
    name_am: Mapped[str] = mapped_column(String(120))
    name_bn: Mapped[str] = mapped_column(String(120))
    name_hi: Mapped[str] = mapped_column(String(120))
    name_ur: Mapped[str] = mapped_column(String(120))
    hours_en: Mapped[str] = mapped_column(String(120))
    hours_am: Mapped[str] = mapped_column(String(120))
    hours_bn: Mapped[str] = mapped_column(String(120))
    hours_hi: Mapped[str] = mapped_column(String(120))
    hours_ur: Mapped[str] = mapped_column(String(120))
    location_en: Mapped[str] = mapped_column(Text)
    location_am: Mapped[str] = mapped_column(Text)
    location_bn: Mapped[str] = mapped_column(Text)
    location_hi: Mapped[str] = mapped_column(Text)
    location_ur: Mapped[str] = mapped_column(Text)
    amenities_en: Mapped[str] = mapped_column(Text)
    amenities_am: Mapped[str] = mapped_column(Text)
    amenities_bn: Mapped[str] = mapped_column(Text)
    amenities_hi: Mapped[str] = mapped_column(Text)
    amenities_ur: Mapped[str] = mapped_column(Text)
    access_free_for: Mapped[str] = mapped_column(String(120))
    walk_in_price_usd: Mapped[float] = mapped_column(Float)
    capacity: Mapped[int] = mapped_column(Integer, default=60)

    name = translated("name")
    hours = translated("hours")
    location = translated("location")
    amenities = translated("amenities")


class StopoverPackage(Base):

    __tablename__ = "stopover_packages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    category: Mapped[str] = mapped_column(String(16), index=True)
    name_en: Mapped[str] = mapped_column(String(120))
    name_am: Mapped[str] = mapped_column(String(120))
    name_bn: Mapped[str] = mapped_column(String(120))
    name_hi: Mapped[str] = mapped_column(String(120))
    name_ur: Mapped[str] = mapped_column(String(120))
    description_en: Mapped[str] = mapped_column(Text)
    description_am: Mapped[str] = mapped_column(Text)
    description_bn: Mapped[str] = mapped_column(Text)
    description_hi: Mapped[str] = mapped_column(Text)
    description_ur: Mapped[str] = mapped_column(Text)
    min_layover_h: Mapped[int] = mapped_column(Integer, default=8)
    max_layover_h: Mapped[int] = mapped_column(Integer, default=72)
    cabin_required: Mapped[str | None] = mapped_column(String(16), nullable=True)
    price_usd: Mapped[float] = mapped_column(Float, default=0.0)

    name = translated("name")
    description = translated("description")


class Promotion(Base):

    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    code: Mapped[str] = mapped_column(String(16), unique=True)
    title_en: Mapped[str] = mapped_column(String(120))
    title_am: Mapped[str] = mapped_column(String(120))
    title_bn: Mapped[str] = mapped_column(String(120))
    title_hi: Mapped[str] = mapped_column(String(120))
    title_ur: Mapped[str] = mapped_column(String(120))
    body_en: Mapped[str] = mapped_column(Text)
    body_am: Mapped[str] = mapped_column(Text)
    body_bn: Mapped[str] = mapped_column(Text)
    body_hi: Mapped[str] = mapped_column(Text)
    body_ur: Mapped[str] = mapped_column(Text)
    terms_en: Mapped[str] = mapped_column(Text)
    terms_am: Mapped[str] = mapped_column(Text)
    terms_bn: Mapped[str] = mapped_column(Text)
    terms_hi: Mapped[str] = mapped_column(Text)
    terms_ur: Mapped[str] = mapped_column(Text)
    region: Mapped[str] = mapped_column(String(32))
    discount_pct: Mapped[int] = mapped_column(Integer)
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date] = mapped_column(Date)

    title = translated("title")
    body = translated("body")
    terms = translated("terms")


class EntertainmentItem(Base):

    __tablename__ = "entertainment_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    category: Mapped[str] = mapped_column(String(16), index=True)
    title_en: Mapped[str] = mapped_column(String(160))
    title_am: Mapped[str] = mapped_column(String(160))
    title_bn: Mapped[str] = mapped_column(String(160))
    title_hi: Mapped[str] = mapped_column(String(160))
    title_ur: Mapped[str] = mapped_column(String(160))
    genre_en: Mapped[str] = mapped_column(String(60))
    genre_am: Mapped[str] = mapped_column(String(60))
    genre_bn: Mapped[str] = mapped_column(String(60))
    genre_hi: Mapped[str] = mapped_column(String(60))
    genre_ur: Mapped[str] = mapped_column(String(60))
    minutes: Mapped[int] = mapped_column(Integer)
    language_en: Mapped[str] = mapped_column(String(32))
    language_am: Mapped[str] = mapped_column(String(32))
    language_bn: Mapped[str] = mapped_column(String(32))
    language_hi: Mapped[str] = mapped_column(String(32))
    language_ur: Mapped[str] = mapped_column(String(32))
    year: Mapped[int] = mapped_column(Integer)

    title = translated("title")
    genre = translated("genre")
    language = translated("language")


class TravelRequirement(Base):

    __tablename__ = "travel_requirements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    country_code: Mapped[str] = mapped_column(String(2), index=True)
    passport_months: Mapped[int] = mapped_column(Integer)
    blank_pages: Mapped[int] = mapped_column(Integer)
    visa_required_en: Mapped[str] = mapped_column(String(120))
    visa_required_am: Mapped[str] = mapped_column(String(120))
    visa_required_bn: Mapped[str] = mapped_column(String(120))
    visa_required_hi: Mapped[str] = mapped_column(String(120))
    visa_required_ur: Mapped[str] = mapped_column(String(120))
    health_en: Mapped[str] = mapped_column(Text)
    health_am: Mapped[str] = mapped_column(Text)
    health_bn: Mapped[str] = mapped_column(Text)
    health_hi: Mapped[str] = mapped_column(Text)
    health_ur: Mapped[str] = mapped_column(Text)
    onward_ticket: Mapped[bool] = mapped_column(Boolean, default=True)

    visa_required = translated("visa_required")
    health = translated("health")
