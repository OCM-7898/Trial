from __future__ import annotations

import json

from flask import Blueprint, g, render_template, request
from sqlalchemy import func, select

from .. import db as database
from ..clock import now
from ..i18n import t
from ..models.requests import ServiceRequest
from ..routes_map import SLUGS, path
from ..services import references
from ..services import service_forms

bp = Blueprint("requests", __name__)

FORM_ROUTES = {
    "feedback": ("feedback", "help"),
    "bag_report": ("baggage-report", "book"),
    "assistance": ("assistance", "help"),
    "assistance_wchr": ("assistance", "help"),
    "groups": ("groups", "help"),
    "corporate_enroll": ("corporate-enrol", "help"),
    "cargo_quote": ("cargo-quote", "help"),
    "compensation": ("compensation", "help"),
    "medical_clearance": ("medical-clearance", "help"),
}

STATUS_ROUTES = {
    "feedback_status": "feedback",
    "bag_report_status": "baggage_report",
    "assistance_status": "assistance",
    "groups_status": "group",
    "cargo_track": "cargo",
}


def _render_form(form_slug: str, nav_section: str):
    g.nav_section = nav_section
    form = service_forms.all_forms()[form_slug]
    db = database.session()

    if request.method != "POST":
        return render_template("requests/form.html", form=form, errors={}, values={},
                               record=None, also=_related(form_slug))

    values = {entry.name: (request.form.get(entry.name) or "").strip()
              for entry in form.fields}
    errors = service_forms.validate(form, values)
    if errors:
        return render_template("requests/form.html", form=form, errors=errors,
                               also=_related(form_slug),
                               values=values, record=None), 400

    record = ServiceRequest(
        kind=form.kind,
        reference_no=references.next_reference(db, form.reference_kind,
                                               ServiceRequest.reference_no),
        status="received", created_at=now().replace(tzinfo=None),
        payload=json.dumps(values, ensure_ascii=False),
        quoted_usd=_quote_for(form.kind, values),
    )
    db.add(record)
    db.commit()
    return render_template("requests/form.html", form=form, errors={}, values=values,
                           record=record)


def _quote_for(kind: str, values: dict) -> float | None:
    if kind != "cargo":
        return None
    try:
        weight = max(1, int(values.get("weight_kg", 0)))
    except ValueError:
        return None
    return round(45.0 + weight * 3.75, 2)


def _render_status(kind: str):
    g.nav_section = "help"
    db = database.session()
    reference = (request.args.get("reference") or "").strip().upper()
    record = None
    if reference:
        record = db.scalars(select(ServiceRequest).where(
            func.upper(ServiceRequest.reference_no) == reference,
            ServiceRequest.kind == kind)).one_or_none()
    return render_template("requests/status.html", kind_label=_kind_label(kind),
                           reference=reference, record=record,
                           searched=bool(reference),
                           payload=json.loads(record.payload) if record else {})


def _kind_label(kind: str) -> str:
    return {
        "feedback": t("form.feedback_title"),
        "baggage_report": t("form.bagrep_title"),
        "assistance": t("form.assistance_title"),
        "group": t("form.group_title"),
        "cargo": t("form.cargo_title"),
    }[kind]


def register(app) -> None:
    for slug, (form_slug, nav_section) in sorted(FORM_ROUTES.items()):
        def view(form_slug=form_slug, nav_section=nav_section):
            return _render_form(form_slug, nav_section)

        app.add_url_rule(SLUGS[slug], endpoint=f"requests.{slug}", view_func=view,
                         methods=["GET", "POST"])

    for slug, kind in sorted(STATUS_ROUTES.items()):
        def status_view(kind=kind):
            return _render_status(kind)

        app.add_url_rule(SLUGS[slug], endpoint=f"requests.{slug}",
                         view_func=status_view)


def _related(form_slug: str) -> list[tuple[str, str]]:
    if form_slug == "assistance":
        return [(t("nav.wheelchair"), path("assistance_wchr")),
                (t("nav.medical_clearance"), path("medical_clearance"))]
    if form_slug == "feedback":
        return [(t("nav.compensation"), path("compensation"))]
    return []
