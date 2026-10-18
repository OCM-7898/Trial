from __future__ import annotations

from flask import Blueprint, g, render_template

from ..i18n import t
from ..routes_map import path
from ..routes_map import SLUGS

bp = Blueprint("home", __name__)


def _quick_links() -> list[dict[str, str]]:
    return [
        {"title": t("home.card_baggage_title"), "body": t("home.card_baggage_body"),
         "image": "cards/baggage.svg", "alt": t("home.card_baggage_alt"),
         "href": path("bag_allowance")},
        {"title": t("home.card_checkin_title"), "body": t("home.card_checkin_body"),
         "image": "cards/checkin.svg", "alt": t("home.card_checkin_alt"),
         "href": path("checkin")},
        {"title": t("home.card_miles_title"), "body": t("home.card_miles_body"),
         "image": "cards/miles.svg", "alt": t("home.card_miles_alt"),
         "href": path("miles_join")},
        {"title": t("home.card_lounge_title"), "body": t("home.card_lounge_body"),
         "image": "cards/lounge.svg", "alt": t("home.card_lounge_alt"),
         "href": path("lounges")},
        {"title": t("home.card_stopover_title"), "body": t("home.card_stopover_body"),
         "image": "cards/stopover.svg", "alt": t("home.card_stopover_alt"),
         "href": path("stopover")},
        {"title": t("home.card_status_title"), "body": t("home.card_status_body"),
         "image": "cards/status.svg", "alt": t("home.card_status_alt"),
         "href": path("flight_status")},
    ]


@bp.route(SLUGS["home"])
def index():
    g.nav_section = "home"
    return render_template("home.html", quick_links=_quick_links())
