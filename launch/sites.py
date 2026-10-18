import logging
import os
import sqlite3
import sys
import tempfile
import threading
import time

from werkzeug.serving import make_server

logging.getLogger("werkzeug").setLevel(logging.WARNING)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ("en", "bn", "hi", "ur", "am")

PORTS = {
    "portal":    {"en": 8015, "bn": 8016, "hi": 8046, "ur": 8047, "am": 8048},
    "selam":     {"en": 8017, "bn": 8054, "hi": 8055, "ur": 8056, "am": 8053},
    "rail":      {"en": 8021, "bn": 8049, "hi": 8050, "ur": 8051, "am": 8052},
    "ministore": {"en": 8031, "bn": 8032, "hi": 8033, "ur": 8034, "am": 8035},
    "gari":      {"en": 8036, "bn": 8042, "hi": 8043, "ur": 8044, "am": 8045},
    "reddit":    {"en": 8037, "bn": 8038, "hi": 8039, "ur": 8040, "am": 8041},
}

PREFIX = {"portal": "portal", "selam": "selam", "rail": "rail",
          "ministore": "visual", "gari": "visualgari", "reddit": "visualreddit"}

SELAM_STATE_TABLES = {
    "bookings", "segments", "passengers", "checkins", "boarding_passes",
    "seat_assignments", "baggage_purchases", "meal_requests",
    "wifi_purchases", "lounge_purchases", "upgrade_purchases",
    "loyalty_members", "miles_transactions", "missing_miles_claims",
    "change_requests", "refund_requests", "service_requests",
    "hotel_bookings", "car_bookings", "draft_bookings",
}


def suite_name(site, lang):
    return PREFIX[site] + ("" if lang == "en" else lang)


def parse_suite(suite):
    for site, pre in sorted(PREFIX.items(), key=lambda kv: -len(kv[1])):
        if suite.startswith(pre):
            lang = suite[len(pre):] or "en"
            if lang in LANGS:
                return site, lang
    raise ValueError(f"unknown suite {suite!r} (e.g. rail, railbn, visual, visualgariur)")


def url(site, lang):
    return f"http://127.0.0.1:{PORTS[site][lang]}"


def site_urls(suite):
    site, lang = parse_suite(suite)
    return {site: url(site, lang)}


def _db(site, lang):
    return os.path.join(tempfile.gettempdir(), f"mwa_{site}_{lang}.db")


def _selam_app(lang):
    selam_root = os.path.join(ROOT, "sites", "text_only", "selam")
    if selam_root not in sys.path:
        sys.path.insert(0, selam_root)
    from app import create_app
    from flask import abort, jsonify

    from benchmark.harness import protect

    flask_app = create_app(lang)
    flask_app.add_url_rule("/__reset__", endpoint="harness_reset_alias",
                           view_func=flask_app.view_functions["harness.reset"], methods=["POST"])
    db_path = str(flask_app.config["SELAM"].db_path)

    def harness_state(table):
        if table not in SELAM_STATE_TABLES:
            abort(404)
        con = sqlite3.connect(db_path)
        con.row_factory = sqlite3.Row
        rows = [dict(r) for r in con.execute(f"SELECT * FROM {table}").fetchall()]
        con.close()
        return jsonify(rows)

    flask_app.add_url_rule("/__state__/<table>", endpoint="harness_state",
                           view_func=harness_state, methods=["GET"])
    protect(flask_app, endpoint_prefixes=("harness.", "harness_"))
    return flask_app


def make_app(site, lang):
    if site == "selam":
        return _selam_app(lang)
    if site == "portal":
        from sites.text_only.portal.portal_clone import create_app
    elif site == "rail":
        from sites.text_only.rail.railapp import create_app
    else:
        sites_dir = os.path.join(ROOT, "sites")
        if sites_dir not in sys.path:
            sys.path.insert(1, sites_dir)
        if site == "ministore":
            from visual.ministore import create_app
        elif site == "gari":
            from visual.gari import create_app
        else:
            from visual.reddit import create_app
    return create_app(_db(site, lang), lang=lang)


class SiteServer(threading.Thread):
    def __init__(self, site, lang):
        super().__init__(daemon=True)
        self.name = f"{site}_{lang}"
        self.port = PORTS[site][lang]
        self.srv = make_server("127.0.0.1", self.port, make_app(site, lang), threaded=True)

    def run(self):
        self.srv.serve_forever()

    def stop(self):
        self.srv.shutdown()


def start(site, lang):
    s = SiteServer(site, lang)
    s.start()
    print(f"[{site}_{lang}] running at {url(site, lang)}")
    return s


def start_suite(suite):
    return start(*parse_suite(suite))


if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        servers = [start(sys.argv[1], sys.argv[2])]
    elif len(sys.argv) == 2:
        servers = [start_suite(sys.argv[1])]
    else:
        raise SystemExit("usage: python -m launch.sites <site> <lang>   "
                         "(sites: portal selam rail ministore gari reddit; langs: en bn hi ur am)")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for s in servers:
            s.stop()
