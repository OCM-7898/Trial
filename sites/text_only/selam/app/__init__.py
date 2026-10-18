from __future__ import annotations

from flask import Flask, g, render_template
from markupsafe import Markup

from . import db as database
from . import i18n
from . import lang
from .brand import BRANDS, CURRENCY
from .config import Config
from .i18n import formats, labels, t
from .routes_map import SLUGS, path


def create_app(language: str = "en") -> Flask:
    config = Config.for_language(language)
    i18n.set_language(config.language)

    app = Flask(__name__)
    app.config.update(
        LANGUAGE=config.language,
        SECRET_KEY=config.secret_key,
        SESSION_COOKIE_NAME=config.session_cookie,
        WTF_CSRF_ENABLED=config.wtf_csrf_enabled,
        SELAM=config,
    )
    app.jinja_env.undefined = __import__("jinja2").StrictUndefined

    database.init_app(app)
    _bind_language(app, config)
    _register_error_handlers(app)
    _register_template_globals(app, config)
    _register_blueprints(app)
    return app


def _bind_language(app: Flask, config: Config) -> None:

    @app.before_request
    def _apply_language():
        g.language_token = lang.bind(config.language)
        i18n.set_language(config.language)

    @app.teardown_request
    def _release_language(exc):
        token = g.pop("language_token", None)
        if token is not None:
            lang.unbind(token)


def _register_error_handlers(app: Flask) -> None:

    @app.after_request
    def translate_redirect_body(response):
        if 300 <= response.status_code < 400 and response.mimetype == "text/html":
            target = response.headers.get("Location", "")
            response.set_data(render_template(
                "redirect.html", target=target,
                heading=t("redirect.title"), body=t("redirect.body")))
        return response

    def page(status: int, heading: str, body: str):
        return render_template("error.html", heading=heading, body=body), status

    @app.errorhandler(404)
    def not_found(_error):
        return page(404, t("error.404_title"), t("error.404_body"))

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return page(405, t("error.405_title"), t("error.405_body"))

    @app.errorhandler(409)
    def conflict(_error):
        return page(409, t("error.409_title"), t("error.409_body"))

    @app.errorhandler(500)
    def server_error(_error):
        return page(500, t("error.500_title"), t("error.500_body"))


def _register_blueprints(app: Flask) -> None:
    from .blueprints import (
        booking, checkin, content, extras, flows, harness, home, info, lounges,
        loyalty, manage, onboard, partners, requests, stopover, support,
    )

    app.register_blueprint(home.bp)
    app.register_blueprint(booking.bp)
    app.register_blueprint(manage.bp)
    app.register_blueprint(checkin.bp)
    app.register_blueprint(flows.bp)
    app.register_blueprint(info.bp)
    app.register_blueprint(lounges.bp)
    app.register_blueprint(loyalty.bp)
    app.register_blueprint(onboard.bp)
    app.register_blueprint(stopover.bp)
    app.register_blueprint(partners.bp)
    app.register_blueprint(extras.bp)
    requests.register(app)
    app.register_blueprint(support.bp)
    app.register_blueprint(content.bp)
    content.register(app)
    app.register_blueprint(harness.bp)


def _register_template_globals(app: Flask, config: Config) -> None:
    lang = config.language

    def nav_current(section: str) -> Markup:
        active = getattr(g, "nav_section", None)
        return Markup('aria-current="page"') if active == section else Markup("")

    app.jinja_env.globals.update(
        t=t,
        nav_current=nav_current,
        html_lang=lang,
        path=path,
        slug=SLUGS.__getitem__,
        brand=lambda key: BRANDS[key][lang],
        currency=CURRENCY,
        fmt_date=lambda d: formats.format_date(d, lang),
        fmt_weekday=lambda d: formats.format_weekday(d, lang),
        fmt_time=formats.format_time,
        fmt_money=formats.format_money,
        fmt_money_range=formats.format_money_range,
        special_bag_category=labels.special_baggage_category_label,
        seat_position=labels.seat_position_label,
    )
