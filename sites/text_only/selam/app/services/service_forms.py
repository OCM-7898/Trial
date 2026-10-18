from __future__ import annotations

from dataclasses import dataclass, field

from ..i18n import t


@dataclass(frozen=True)
class Field:
    name: str
    label: str
    kind: str = "text"
    required: bool = True
    hint: str = ""
    choices: tuple = ()
    min_length: int = 0


@dataclass(frozen=True)
class Form:
    kind: str
    slug: str
    title: str
    intro: str
    submit: str
    done_title: str
    done_body: str
    reference_kind: str
    fields: tuple[Field, ...] = field(default_factory=tuple)
    status_slug: str | None = None


def _contact_fields() -> tuple[Field, ...]:
    return (
        Field("full_name", t("form.full_name")),
        Field("email", t("form.email"), hint=t("form.email_hint")),
    )


def all_forms() -> dict[str, Form]:
    forms = [
        Form("feedback", "feedback", t("form.feedback_title"), t("form.feedback_intro"),
             t("form.submit_feedback"), t("form.feedback_done"), t("form.feedback_done_body"),
             "feedback", _contact_fields() + (
                 Field("category", t("form.category"), "select", choices=(
                     ("complaint", t("form.cat_complaint")),
                     ("compliment", t("form.cat_compliment")),
                     ("suggestion", t("form.cat_suggestion")),
                 )),
                 Field("booking_reference", t("manage.pnr"), required=False),
                 Field("message", t("form.message"), "textarea", min_length=20),
             ), status_slug="feedback_status"),

        Form("baggage_report", "baggage-report", t("form.bagrep_title"),
             t("form.bagrep_intro"), t("form.submit_report"), t("form.bagrep_done"),
             t("form.bagrep_done_body"), "baggage_report", _contact_fields() + (
                 Field("booking_reference", t("manage.pnr")),
                 Field("flight_no", t("status.flight_no")),
                 Field("tag_number", t("form.tag_number"), hint=t("form.tag_hint")),
                 Field("problem", t("form.problem"), "select", choices=(
                     ("delayed", t("form.bag_delayed")),
                     ("damaged", t("form.bag_damaged")),
                     ("missing_items", t("form.bag_missing")),
                 )),
                 Field("description", t("form.description"), "textarea", min_length=20),
             ), status_slug="bag_report_status"),

        Form("assistance", "assistance", t("form.assistance_title"),
             t("form.assistance_intro"), t("form.submit_request"),
             t("form.assistance_done"), t("form.assistance_done_body"),
             "assistance", _contact_fields() + (
                 Field("booking_reference", t("manage.pnr")),
                 Field("service_code", t("form.service_code"), "select", choices=(
                     ("WCHR", t("form.wchr")), ("WCHS", t("form.wchs")),
                     ("WCHC", t("form.wchc")), ("DEAF", t("form.deaf")),
                     ("BLND", t("form.blnd")), ("DPNA", t("form.dpna")),
                 )),
                 Field("notes", t("form.notes"), "textarea", required=False),
             ), status_slug="assistance_status"),

        Form("group", "groups", t("form.group_title"), t("form.group_intro"),
             t("form.submit_enquiry"), t("form.group_done"), t("form.group_done_body"),
             "group", _contact_fields() + (
                 Field("organisation", t("form.organisation")),
                 Field("group_size", t("form.group_size"), "number", hint=t("form.group_min")),
                 Field("origin", t("search.origin")),
                 Field("destination", t("search.destination")),
                 Field("travel_date", t("form.travel_date"), "date"),
             ), status_slug="groups_status"),

        Form("corporate", "corporate-enrol", t("form.corporate_title"),
             t("form.corporate_intro"), t("form.submit_enrolment"),
             t("form.corporate_done"), t("form.corporate_done_body"),
             "corporate", _contact_fields() + (
                 Field("organisation", t("form.organisation")),
                 Field("annual_spend", t("form.annual_spend"), "number",
                       hint=t("form.annual_spend_hint")),
                 Field("country_code", t("join.country"), hint=t("join.country_hint")),
             )),

        Form("cargo", "cargo-quote", t("form.cargo_title"), t("form.cargo_intro"),
             t("form.submit_quote"), t("form.cargo_done"), t("form.cargo_done_body"),
             "cargo", _contact_fields() + (
                 Field("origin", t("search.origin")),
                 Field("destination", t("search.destination")),
                 Field("weight_kg", t("form.weight_kg"), "number"),
                 Field("commodity", t("form.commodity")),
             ), status_slug="cargo_track"),

        Form("compensation", "compensation", t("form.comp_title"), t("form.comp_intro"),
             t("form.submit_claim"), t("form.comp_done"), t("form.comp_done_body"),
             "compensation", _contact_fields() + (
                 Field("booking_reference", t("manage.pnr")),
                 Field("flight_no", t("status.flight_no")),
                 Field("flight_date", t("claim.flight_date"), "date"),
                 Field("delay_hours", t("form.delay_hours"), "number",
                       hint=t("form.delay_hint")),
             )),

        Form("medical", "medical-clearance", t("form.medical_title"),
             t("form.medical_intro"), t("form.submit_request"), t("form.medical_done"),
             t("form.medical_done_body"), "medical", _contact_fields() + (
                 Field("booking_reference", t("manage.pnr")),
                 Field("condition", t("form.condition"), "textarea", min_length=20),
                 Field("oxygen_required", t("form.oxygen"), "select", choices=(
                     ("no", t("schedules.no")), ("yes", t("schedules.yes")))),
             )),
    ]
    return {form.slug: form for form in forms}


def validate(form: Form, values: dict) -> dict:
    errors = {}
    for entry in form.fields:
        raw = (values.get(entry.name) or "").strip()
        if entry.required and not raw:
            errors[entry.name] = t("form.error_required")
            continue
        if not raw:
            continue
        if entry.kind == "number" and not raw.lstrip("-").isdigit():
            errors[entry.name] = t("form.error_number")
        elif entry.kind == "date" and not _is_iso_date(raw):
            errors[entry.name] = t("form.error_date")
        elif entry.name == "email" and ("@" not in raw or "." not in raw.split("@")[-1]):
            errors[entry.name] = t("form.error_email")
        elif entry.min_length and len(raw) < entry.min_length:
            errors[entry.name] = t("form.error_too_short", n=entry.min_length)
        elif entry.kind == "select" and raw not in {c[0] for c in entry.choices}:
            errors[entry.name] = t("form.error_choice")
    return errors


def _is_iso_date(raw: str) -> bool:
    from datetime import datetime

    try:
        datetime.strptime(raw, "%Y-%m-%d")
    except ValueError:
        return False
    return True
