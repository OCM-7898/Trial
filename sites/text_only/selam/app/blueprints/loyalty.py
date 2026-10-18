from __future__ import annotations

from datetime import datetime

from flask import Blueprint, g, redirect, render_template, request, session as flask_session
from sqlalchemy import select

from .. import db as database
from ..clock import WINDOW_END, WINDOW_START, now, today
from ..i18n import labels, t
from ..models import translated_column, translated_kwargs
from ..models.loyalty import LoyaltyMember, MissingMilesClaim
from ..params import bounded_int
from ..routes_map import SLUGS, path
from ..services import loyalty as loyalty_service
from ..services import references

bp = Blueprint("loyalty", __name__)

SESSION_KEY = "member_no"


def _surname_column():
    return translated_column(LoyaltyMember, "last_name")


def _parse_date(raw: str | None):
    if not raw:
        return None
    try:
        parsed = datetime.strptime(raw.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None
    return parsed if WINDOW_START <= parsed <= WINDOW_END else None


@bp.route(SLUGS["miles_join"], methods=["GET", "POST"])
def join():
    g.nav_section = "miles"
    if request.method != "POST":
        return render_template("loyalty/join.html", errors={}, values={})

    values = {k: (request.form.get(k) or "").strip()
              for k in ("first_name", "last_name", "email", "country_code")}
    errors = {}
    if not values["first_name"]:
        errors["first_name"] = t("join.error_required")
    if not values["last_name"]:
        errors["last_name"] = t("join.error_required")
    if "@" not in values["email"] or "." not in values["email"].split("@")[-1]:
        errors["email"] = t("join.error_email")

    db = database.session()
    if not errors and db.scalars(
        select(LoyaltyMember).where(LoyaltyMember.email == values["email"])
    ).one_or_none() is not None:
        errors["email"] = t("join.error_duplicate")

    if errors:
        return render_template("loyalty/join.html", errors=errors, values=values), 400

    member_no = references.membership_number(db, LoyaltyMember.member_no)
    member = LoyaltyMember(
        member_no=member_no,
        **translated_kwargs(LoyaltyMember, "first_name", values["first_name"]),
        **translated_kwargs(LoyaltyMember, "last_name", values["last_name"]),
        email=values["email"], tier="blue", miles_balance=0, qualifying_miles=0,
        joined_on=today(), country_code=(values["country_code"] or "ET")[:2].upper(),
        created_at_runtime=True,
    )
    db.add(member)
    db.commit()

    flask_session[SESSION_KEY] = member_no
    return render_template("loyalty/joined.html", member=member)


@bp.route(SLUGS["miles_account"], methods=["GET", "POST"])
def account():
    g.nav_section = "miles"
    db = database.session()
    member_no = (request.values.get("member_no") or flask_session.get(SESSION_KEY) or "").strip()
    surname = (request.values.get("surname") or "").strip()

    member = None
    if member_no and surname:
        member = loyalty_service.find_member(db, member_no, surname, _surname_column())
        if member is not None:
            flask_session[SESSION_KEY] = member.member_no
    elif member_no and flask_session.get(SESSION_KEY) == member_no:
        member = db.scalars(
            select(LoyaltyMember).where(LoyaltyMember.member_no == member_no)).one_or_none()

    if member is None:
        error = t("miles.not_found") if (member_no and surname) else None
        return render_template("loyalty/signin.html", error=error,
                               member_no=member_no), (404 if error else 200)

    return render_template(
        "loyalty/account.html", member=member,
        progress=loyalty_service.progress(member),
        transactions=loyalty_service.statement(db, member)[:20],
    )


@bp.route(SLUGS["miles_claim"], methods=["GET", "POST"])
def claim():
    g.nav_section = "miles"
    db = database.session()
    if request.method != "POST":
        return render_template("loyalty/claim.html", errors={}, values={}, claim=None)

    values = {k: (request.form.get(k) or "").strip()
              for k in ("member_no", "ticket_no", "flight_no", "flight_date")}
    errors = {}

    member = db.scalars(select(LoyaltyMember).where(
        LoyaltyMember.member_no == values["member_no"].upper())).one_or_none()
    if member is None:
        errors["member_no"] = t("miles.unknown_member")
    if len(values["ticket_no"]) < 6:
        errors["ticket_no"] = t("claim.error_ticket")

    flight_date = _parse_date(values["flight_date"])
    if flight_date is None:
        errors["flight_date"] = t("claim.error_date")
    elif flight_date >= today():
        errors["flight_date"] = t("claim.error_future")

    if errors:
        return render_template("loyalty/claim.html", errors=errors, values=values,
                               claim=None), 400

    record = MissingMilesClaim(
        member_no=member.member_no,
        reference_no=references.next_reference(db, "missing_miles",
                                               MissingMilesClaim.reference_no),
        ticket_no=values["ticket_no"], flight_no=values["flight_no"].upper().replace(" ", ""),
        flight_date=flight_date, status="under_review",
        created_at=now().replace(tzinfo=None),
    )
    db.add(record)
    db.commit()
    return render_template("loyalty/claim.html", errors={}, values=values, claim=record)


@bp.route(SLUGS["award_search"])
def award_search():
    g.nav_section = "miles"
    db = database.session()
    origin = (request.args.get("origin") or "").strip().upper()[:3]
    destination = (request.args.get("destination") or "").strip().upper()[:3]
    day = _parse_date(request.args.get("date"))
    cabin = request.args.get("cabin") if request.args.get("cabin") in ("economy", "business") else None

    options, alternatives = [], []
    if origin and destination and day:
        options = loyalty_service.award_search(db, origin, destination, day, cabin)
        if not options:
            alternatives = loyalty_service.nearby_award_dates(db, origin, destination, day)

    return render_template(
        "loyalty/award_search.html", origin=origin, destination=destination,
        date_value=request.args.get("date", ""), cabin=cabin,
        options=options, alternatives=alternatives,
        searched=bool(origin and destination and day),
        cabin_options=[("", t("search.cabin_any")),
                       ("economy", t("brand.cabin_economy")),
                       ("business", t("brand.cabin_business"))],
    )


def _signed_in_member(db):
    member_no = flask_session.get(SESSION_KEY)
    if not member_no:
        return None
    return db.scalars(
        select(LoyaltyMember).where(LoyaltyMember.member_no == member_no)).one_or_none()


def _require_member():
    db = database.session()
    member = _signed_in_member(db)
    if member is None:
        return None, (render_template("loyalty/signin.html",
                                      error=t("miles.sign_in_first"), member_no=""), 404)
    return member, None


@bp.route(SLUGS["miles_statement"])
def statement():
    g.nav_section = "miles"
    member, refusal = _require_member()
    if refusal:
        return refusal
    db = database.session()
    rows = loyalty_service.statement(db, member)
    earned = sum(r.miles for r in rows if r.miles > 0)
    spent = -sum(r.miles for r in rows if r.miles < 0)
    return render_template("loyalty/statement.html", member=member, rows=rows,
                           earned=earned, spent=spent)


@bp.route(SLUGS["miles_tier"])
def tier_progress():
    g.nav_section = "miles"
    member, refusal = _require_member()
    if refusal:
        return refusal
    progress = loyalty_service.progress(member)
    tiers = [{"name": name, "floor": floor,
              "reached": member.qualifying_miles >= floor,
              "current": member.tier == name}
             for name, floor in loyalty_service.TIERS]
    return render_template("loyalty/tier_progress.html", member=member,
                           progress=progress, tiers=tiers)


@bp.route(SLUGS["miles_nominees"], methods=["GET", "POST"])
def nominees():
    g.nav_section = "miles"
    member, refusal = _require_member()
    if refusal:
        return refusal
    db = database.session()
    from ..models.requests import ServiceRequest

    added = error = None
    if request.method == "POST":
        name = (request.form.get("nominee_name") or "").strip()
        relationship = (request.form.get("relationship") or "").strip()
        if len(name) < 2:
            error = t("miles.nominee_error")
        else:
            import json as _json

            added = ServiceRequest(
                kind="nominee",
                reference_no=references.next_reference(db, "nominee",
                                                       ServiceRequest.reference_no),
                status="active", created_at=now().replace(tzinfo=None),
                payload=_json.dumps({"member_no": member.member_no, "name": name,
                                     "relationship": relationship}, ensure_ascii=False))
            db.add(added)
            db.commit()

    import json as _json

    rows = [_json.loads(r.payload) for r in db.scalars(
        select(ServiceRequest).where(ServiceRequest.kind == "nominee")
        .order_by(ServiceRequest.id))]
    rows = [r for r in rows if r.get("member_no") == member.member_no]
    return render_template("loyalty/nominees.html", member=member, rows=rows,
                           added=added, error=error)


@bp.route(SLUGS["award_chart"])
def award_chart():
    g.nav_section = "miles"
    db = database.session()
    from ..models.loyalty import AwardInventory
    from ..models.network import Airport, Flight, Route

    buckets: dict[tuple[str, str], dict[str, set]] = {}
    for inventory, flight in db.execute(
        select(AwardInventory, Flight).join(Flight, Flight.id == AwardInventory.flight_id)
    ):
        route = db.get(Route, flight.route_id)
        origin = db.get(Airport, route.origin_id)
        destination = db.get(Airport, route.destination_id)
        far = destination if origin.iata == "ADD" else origin
        key = ("ADD", far.region)
        buckets.setdefault(key, {"economy": set(), "business": set()})
        buckets[key][inventory.cabin].add(inventory.miles_required)

    rows = [{
        "region": labels.region_label(region),
        "economy": sorted(values["economy"]),
        "business": sorted(values["business"]),
    } for (_, region), values in sorted(buckets.items(), key=lambda kv: kv[0][1])]
    return render_template("loyalty/award_chart.html", rows=rows)


@bp.route(SLUGS["miles_claim_status"])
def claim_status():
    g.nav_section = "miles"
    db = database.session()
    reference = (request.args.get("reference") or "").strip().upper()
    record = None
    if reference:
        record = db.scalars(select(MissingMilesClaim).where(
            MissingMilesClaim.reference_no == reference)).one_or_none()
    return render_template("loyalty/claim_status.html", reference=reference,
                           record=record, searched=bool(reference))


@bp.route(SLUGS["miles_claim_partner"], methods=["GET", "POST"])
def claim_partner():
    g.nav_section = "miles"
    db = database.session()
    values, errors, record = {}, {}, None

    if request.method == "POST":
        values = {k: (request.form.get(k) or "").strip()
                  for k in ("member_no", "partner", "partner_reference", "flight_date")}
        member = db.scalars(select(LoyaltyMember).where(
            LoyaltyMember.member_no == values["member_no"].upper())).one_or_none()
        if member is None:
            errors["member_no"] = t("miles.unknown_member")
        if len(values["partner_reference"]) < 5:
            errors["partner_reference"] = t("claim.error_ticket")
        day = _parse_date(values["flight_date"])
        if day is None:
            errors["flight_date"] = t("claim.error_date")
        elif day >= today():
            errors["flight_date"] = t("claim.error_future")

        if not errors:
            record = MissingMilesClaim(
                member_no=member.member_no,
                reference_no=references.next_reference(db, "missing_miles",
                                                       MissingMilesClaim.reference_no),
                ticket_no=values["partner_reference"],
                flight_no=values["partner"][:8].upper(),
                flight_date=day, status="under_review",
                created_at=now().replace(tzinfo=None),
                notes="partner claim",
            )
            db.add(record)
            db.commit()

    return render_template("loyalty/claim_partner.html", values=values,
                           errors=errors, record=record,
                           partners=[("SKYVIEW", t("partner_air.skyview")),
                                     ("RIFTAIR", t("partner_air.riftair")),
                                     ("NILEWAYS", t("partner_air.nileways"))])


@bp.route(SLUGS["miles_redeem"])
def redeem():
    g.nav_section = "miles"
    db = database.session()
    member = _signed_in_member(db)
    options = [
        {"key": "award", "title": t("redeem.award_title"), "body": t("redeem.award_body"),
         "url": path("award_search"), "from_miles": 15000},
        {"key": "upgrade", "title": t("redeem.upgrade_title"), "body": t("redeem.upgrade_body"),
         "url": path("manage"), "from_miles": 20000},
        {"key": "voucher", "title": t("redeem.voucher_title"), "body": t("redeem.voucher_body"),
         "url": path("miles_redeem_voucher"), "from_miles": 10000},
    ]
    return render_template("loyalty/redeem.html", member=member, options=options)


@bp.route(SLUGS["miles_redeem_voucher"], methods=["GET", "POST"])
def redeem_voucher():
    g.nav_section = "miles"
    member, refusal = _require_member()
    if refusal:
        return refusal
    db = database.session()
    from ..models.requests import ServiceRequest

    tiers = [(10000, 60.0), (20000, 130.0), (40000, 280.0)]
    record = error = None
    if request.method == "POST":
        miles = bounded_int(request.form.get("miles"), low=0, high=1_000_000, default=0)
        match = next((t for t in tiers if t[0] == miles), None)
        if match is None:
            error = t("redeem.pick_amount")
        elif member.miles_balance < miles:
            error = t("redeem.not_enough", n=member.miles_balance)
        else:
            import json as _json

            record = ServiceRequest(
                kind="voucher",
                reference_no=references.next_reference(db, "voucher",
                                                       ServiceRequest.reference_no),
                status="pending", created_at=now().replace(tzinfo=None),
                payload=_json.dumps({"member_no": member.member_no, "miles": miles,
                                     "value_usd": match[1]}),
                quoted_usd=match[1])
            db.add(record)
            db.commit()

    return render_template("loyalty/redeem_voucher.html", member=member, tiers=tiers,
                           record=record, error=error)


@bp.route(SLUGS["miles_buy"], methods=["GET", "POST"])
def buy_miles():
    g.nav_section = "miles"
    member, refusal = _require_member()
    if refusal:
        return refusal
    db = database.session()
    from ..models.requests import ServiceRequest

    bundles = [(5000, 145.0), (10000, 270.0), (25000, 620.0)]
    record = error = None
    if request.method == "POST":
        miles = bounded_int(request.form.get("miles"), low=0, high=1_000_000, default=0)
        match = next((b for b in bundles if b[0] == miles), None)
        if match is None:
            error = t("redeem.pick_amount")
        else:
            import json as _json

            record = ServiceRequest(
                kind="buy_miles",
                reference_no=references.next_reference(db, "buy_miles",
                                                       ServiceRequest.reference_no),
                status="pending", created_at=now().replace(tzinfo=None),
                payload=_json.dumps({"member_no": member.member_no, "miles": miles}),
                quoted_usd=match[1])
            db.add(record)
            db.commit()

    return render_template("loyalty/buy_miles.html", member=member, bundles=bundles,
                           record=record, error=error)
