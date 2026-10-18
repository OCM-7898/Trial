from __future__ import annotations

from flask import Blueprint, abort, g, render_template
from sqlalchemy import select

from .. import db as database
from ..i18n import t
from ..i18n.labels import content_category_label as category_label
from ..models.content import ContentPage
from ..routes_map import SLUGS, path

bp = Blueprint("content", __name__)

CONTENT_ROUTES = {
    "allergies": ("allergies", "help"),
    "bag_special": ("special-baggage", "book"),
    "bag_restricted": ("restricted-items-full", "book"),
    "bag_instruments": ("musical-instruments", "book"),
    "fitness_to_fly": ("fitness-to-fly", "help"),
    "minors": ("unaccompanied-minors", "help"),
    "pets": ("travelling-with-pets", "help"),
    "minors_pets": ("unaccompanied-minors", "help"),
    "corporate": ("corporate-programme", "help"),
}

CATEGORY_ORDER = ("booking-help", "baggage", "travel-info", "health", "onboard",
                  "loyalty", "policies")


PAGE_EXTRAS = {"special-baggage": "content/extras/special_baggage.html",
               "travel-documents": "content/extras/evisa_link.html"}


def _render(page_slug: str, nav_section: str):
    g.nav_section = nav_section
    db = database.session()
    page = db.scalars(
        select(ContentPage).where(ContentPage.slug == page_slug)
    ).one_or_none()
    if page is None:
        abort(404)

    siblings = db.scalars(
        select(ContentPage)
        .where(ContentPage.category == page.category)
        .order_by(ContentPage.position, ContentPage.id)
    ).all()
    return render_template("content/page.html", page=page, siblings=siblings,
                           route_for=_route_for,
                           extra_template=PAGE_EXTRAS.get(page_slug),
                           extra_rows=_extra_rows(db, page_slug),
                           also=_page_links(page_slug))


def _page_links(page_slug: str) -> list[tuple[str, str]]:
    if page_slug == "corporate-programme":
        return [(t("nav.corporate_enroll"), path("corporate_enroll"))]
    return []


def _extra_rows(db, page_slug: str):
    if page_slug != "special-baggage":
        return []
    from ..models.content import SpecialBaggageItem

    return list(db.scalars(
        select(SpecialBaggageItem).order_by(SpecialBaggageItem.id)))


def _route_for(page_slug: str) -> str:
    for name, (slug, _) in CONTENT_ROUTES.items():
        if slug == page_slug:
            return SLUGS[name]
    return SLUGS["help_topic"].replace("<slug>", page_slug)


@bp.route(SLUGS["help_topic"])
def topic(slug: str):
    if any(dedicated == slug for dedicated, _ in CONTENT_ROUTES.values()):
        abort(404)
    return _render(slug, "help")


@bp.route(SLUGS["help"])
def help_centre():
    g.nav_section = "help"
    db = database.session()
    pages = db.scalars(
        select(ContentPage).order_by(ContentPage.category, ContentPage.position,
                                     ContentPage.id)
    ).all()

    grouped = []
    for category in CATEGORY_ORDER:
        rows = [p for p in pages if p.category == category]
        if rows:
            grouped.append({"category": category,
                            "label": category_label(category),
                            "pages": rows})
    for category in sorted({p.category for p in pages} - set(CATEGORY_ORDER)):
        grouped.append({"category": category, "label": category_label(category),
                        "pages": [p for p in pages if p.category == category]})

    return render_template("content/help_centre.html", grouped=grouped,
                           route_for=_route_for)


def register(app) -> None:
    for name, (page_slug, nav_section) in sorted(CONTENT_ROUTES.items()):
        def view(page_slug=page_slug, nav_section=nav_section):
            return _render(page_slug, nav_section)

        app.add_url_rule(SLUGS[name], endpoint=f"content.{name}", view_func=view)
