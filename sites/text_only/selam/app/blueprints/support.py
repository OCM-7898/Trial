from __future__ import annotations

from flask import Blueprint, abort, g, render_template, request
from sqlalchemy import func, select

from .. import db as database
from ..i18n import t
from ..models import translated_column
from ..models.content import ContactOffice
from ..routes_map import SLUGS

bp = Blueprint("support", __name__)


@bp.route(SLUGS["help_contact"])
def contact():
    g.nav_section = "help"
    db = database.session()
    query = (request.args.get("country") or "").strip()

    offices = list(db.scalars(
        select(ContactOffice).order_by(ContactOffice.country_code)))
    if query:
        needle = query.lower()
        offices = [o for o in offices
                   if needle in o.country.lower()
                   or needle in o.country_code.lower()
                   or needle in o.city.lower()]

    return render_template("support/contact.html", offices=offices, query=query,
                           total=db.scalar(select(func.count(ContactOffice.id))))


@bp.route(SLUGS["help_contact_country"])
def contact_country(country: str):
    g.nav_section = "help"
    db = database.session()
    office = db.scalars(
        select(ContactOffice).where(
            func.upper(ContactOffice.country_code) == country.upper())
    ).one_or_none()
    if office is None:
        abort(404)

    channels = [
        {"label": t("contact.local_line"), "value": office.phone,
         "availability": office.hours, "urgent": False},
        {"label": t("contact.urgent_line"), "value": office.emergency_phone,
         "availability": t("contact.always_open"), "urgent": True},
        {"label": t("contact.email"), "value": office.email,
         "availability": t("contact.email_response"), "urgent": False},
    ]
    return render_template("support/office.html", office=office, channels=channels)
