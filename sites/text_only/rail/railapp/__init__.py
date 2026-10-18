from urllib.parse import quote
import datetime
import os
import sqlite3
import tempfile

from flask import (Flask, abort, g, jsonify, redirect, render_template,
                   request, session)

from . import seed as S_
from .seed import (BOOKINGS, CLASSES, DIGITS, LANG_META, STATIONS, TRAINS,
                   TRAIN_BY_NO, days_at, fare, money, resolve_station,
                   runs_on, search, seed, seg, serves, station_name,
                   train_name)
from .strings import STRINGS

STATE_TABLES = {"users", "bookings", "messages"}


def create_app(db_path=None, lang="en"):
    app = Flask(__name__)
    from benchmark.harness import protect
    protect(app)
    app.secret_key = "benchmark-not-secret"
    if db_path is None:
        db_path = os.path.join(tempfile.gettempdir(),
                               f"mwa_rail_{lang}.db")
    app.config["DB_PATH"] = db_path
    META = LANG_META[lang]
    CUR = META["cur"]
    _ND0 = str.maketrans("0123456789", DIGITS[lang])
    MONEY = {f"c{v}": f"{CUR}{str(money(v, lang)).translate(_ND0)}"
             for v in (240, 120, 60, 20)}
    S = {k: (v.format(**MONEY) if k.startswith("rules_") else v)
         for k, v in STRINGS[lang].items()}

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        d = g.pop("db", None)
        if d is not None:
            d.close()

    def reset_db():
        con = sqlite3.connect(app.config["DB_PATH"])
        seed(con, lang)
        con.close()

    reset_db()

    _ND = str.maketrans("0123456789", DIGITS[lang])
    _FOLD = str.maketrans(DIGITS[lang], "0123456789")

    def nd(x):
        return str(x).translate(_ND)

    if DIGITS[lang] != "0123456789":
        from werkzeug.datastructures import ImmutableMultiDict

        def _fold_md(md):
            return ImmutableMultiDict(
                [(k, v.translate(_FOLD) if isinstance(v, str) else v)
                 for k, v in md.items(multi=True)])

        @app.before_request
        def _fold_digits():
            if request.form:
                request.form = _fold_md(request.form)
            if request.args:
                request.args = _fold_md(request.args)

    def lfare(no, cls, a=None, b=None):
        return fare(no, cls, a, b, lang)

    def sname(code):
        return station_name(code, lang)

    def tname(no):
        return train_name(no, lang)

    def current_user():
        uid = session.get("uid")
        if uid is None:
            return None
        return db().execute("SELECT * FROM users WHERE id=?",
                            (uid,)).fetchone()

    def require_login():
        if current_user() is None:
            return redirect("/login?next=" + quote(request.full_path.rstrip("?"), safe="/"))
        return None

    def classes_of(no):
        t = TRAIN_BY_NO[no]
        return [(c, t["classes"][c]) for c in CLASSES
                if c in t["classes"]]

    def wl_of(no):
        return TRAIN_BY_NO[no]["wl"]

    app.jinja_env.globals.update(
        S=S, lang=lang, nd=nd, sname=sname, tname=tname, CUR=CUR,
        DIR=META["dir"], CLASSES=CLASSES, fare=lfare, seg=seg,
        user=current_user, classes_of=classes_of, wl_of=wl_of)

    @app.post("/__reset__")
    def __reset():
        reset_db()
        session.clear()
        return jsonify({"ok": True})

    @app.get("/__state__/<table>")
    def __state(table):
        if table not in STATE_TABLES:
            abort(404)
        rows = db().execute(f"SELECT * FROM {table}").fetchall()
        return jsonify([dict(r) for r in rows])

    @app.get("/")
    def home():
        return render_template("home.html")

    @app.get("/search")
    def do_search():
        a = resolve_station(request.args.get("from", ""), lang)
        b = resolve_station(request.args.get("to", ""), lang)
        date = (request.args.get("date") or "").strip()
        err = None
        if a is None or b is None or a == b:
            err = S["bad_station"]
        else:
            try:
                datetime.date.fromisoformat(date)
            except ValueError:
                err = S["bad_date"]
        if err:
            return render_template("home.html", error=err)
        nos = search(a, b, date)
        return render_template("results.html", a=a, b=b, date=date,
                               nos=nos)

    @app.get("/trains")
    def trains():
        return render_template("trains.html", trains=TRAINS)

    @app.get("/station/<code>")
    def station_board(code):
        code = code.upper()
        if code not in STATIONS:
            abort(404)
        rows = []
        for t in TRAINS:
            stop = next((s for s in t["stops"] if s[0] == code), None)
            if stop is None:
                continue
            rows.append(dict(no=t["no"], arr=stop[1], dep=stop[2],
                             day=stop[3], origin=t["stops"][0][0],
                             terminus=t["stops"][-1][0],
                             days=days_at(t["no"], code)))
        rows.sort(key=lambda r: r["dep"] or r["arr"])
        return render_template("station.html", code=code, rows=rows)

    @app.get("/train/<no>")
    def train(no):
        t = TRAIN_BY_NO.get(no)
        if t is None:
            abort(404)
        a = request.args.get("from")
        b = request.args.get("to")
        date = request.args.get("date")
        segment = None
        if a and b and date and serves(t, a, b):
            segment = dict(a=a, b=b, date=date,
                           running=runs_on(no, date, a))
        return render_template("train.html", t=t, segment=segment)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            row = db().execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (request.form.get("username", "").strip(),
                 request.form.get("password", ""))).fetchone()
            if row:
                session["uid"] = row["id"]
                return redirect(request.form.get("next") or
                                "/account/bookings")
            error = S["bad_login"]
        return render_template("login.html", error=error,
                               next=request.args.get("next", ""))

    @app.get("/logout")
    def logout():
        session.pop("uid", None)
        return redirect("/")

    @app.get("/book/<no>")
    def book(no):
        r = require_login()
        if r:
            return r
        t = TRAIN_BY_NO.get(no)
        a, b = request.args.get("from"), request.args.get("to")
        date = request.args.get("date")
        cls = request.args.get("class")
        if (t is None or not a or not b or not serves(t, a, b)
                or cls not in t["classes"]):
            abort(404)
        try:
            datetime.date.fromisoformat(date or "")
        except ValueError:
            abort(404)
        if not runs_on(no, date, a):
            return render_template("train.html", t=t,
                                   segment=dict(a=a, b=b, date=date,
                                                running=False))
        session["bctx"] = dict(no=no, a=a, b=b, date=date, cls=cls)
        return render_template("book.html", ctx=session["bctx"])

    @app.post("/book/passenger")
    def book_passenger():
        r = require_login()
        if r:
            return r
        ctx = session.get("bctx")
        if not ctx:
            return redirect("/")
        ctx["passenger"] = dict(
            name=request.form.get("name", "").strip(),
            age=request.form.get("age", "").strip(),
            gender=request.form.get("gender", "M"),
            berth=request.form.get("berth", "No Preference"),
            meal=request.form.get("meal", "No meal"))
        session["bctx"] = ctx
        f = lfare(ctx["no"], ctx["cls"], ctx["a"], ctx["b"])
        return render_template("review.html", ctx=ctx, amount=f)

    @app.post("/book/confirm")
    def book_confirm():
        r = require_login()
        if r:
            return r
        ctx = session.pop("bctx", None)
        if not ctx or "passenger" not in ctx:
            return redirect("/")
        n = db().execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        pnr = str(6210000000 + n + 1)
        t = TRAIN_BY_NO[ctx["no"]]
        status = "CNF" if t["classes"][ctx["cls"]] > 0 else "WL"
        p = ctx["passenger"]
        db().execute(
            "INSERT INTO bookings (pnr, user_id, train_no, from_code,"
            " to_code, date, class_code, passenger, age, gender, berth,"
            " fare, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (pnr, session["uid"], ctx["no"], ctx["a"], ctx["b"],
             ctx["date"], ctx["cls"], p["name"], p["age"] or 0,
             p["gender"], p["berth"],
             lfare(ctx["no"], ctx["cls"], ctx["a"], ctx["b"]), status))
        db().commit()
        return redirect(f"/booking/{pnr}")

    @app.get("/booking/<pnr>")
    def booking(pnr):
        r = require_login()
        if r:
            return r
        row = db().execute("SELECT * FROM bookings WHERE pnr=?",
                           (pnr,)).fetchone()
        if row is None:
            abort(404)
        return render_template("booked.html", b=row)

    @app.route("/pnr", methods=["GET", "POST"])
    def pnr():
        row = None
        searched = False
        if request.method == "POST":
            searched = True
            row = db().execute(
                "SELECT * FROM bookings WHERE pnr=?",
                (request.form.get("pnr", "").strip(),)).fetchone()
        return render_template("pnr.html", b=row, searched=searched)

    @app.get("/account/bookings")
    def my_bookings():
        r = require_login()
        if r:
            return r
        rows = db().execute(
            "SELECT * FROM bookings WHERE user_id=? ORDER BY id",
            (session["uid"],)).fetchall()
        msg = session.pop("flash", None)
        return render_template("bookings.html", rows=rows, msg=msg)

    @app.route("/cancel/<pnr>", methods=["GET", "POST"])
    def cancel(pnr):
        r = require_login()
        if r:
            return r
        row = db().execute("SELECT * FROM bookings WHERE pnr=?",
                           (pnr,)).fetchone()
        if row is None:
            abort(404)
        if request.method == "POST":
            if row["status"] != "CAN":
                db().execute(
                    "UPDATE bookings SET status='CAN' WHERE pnr=?",
                    (pnr,))
                db().commit()
                session["flash"] = S["cancelled_ok"].format(pnr=pnr)
            else:
                session["flash"] = S["already_cancelled"]
            return redirect("/account/bookings")
        return render_template("cancel.html", b=row)

    @app.route("/account/profile", methods=["GET", "POST"])
    def profile():
        r = require_login()
        if r:
            return r
        saved = False
        if request.method == "POST":
            db().execute(
                "UPDATE users SET full_name=?, email=?, mobile=?"
                " WHERE id=?",
                (request.form.get("full_name", "").strip(),
                 request.form.get("email", "").strip(),
                 request.form.get("mobile", "").strip(),
                 session["uid"]))
            db().commit()
            saved = True
        return render_template("profile.html", u=current_user(),
                               saved=saved)

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        sent = False
        if request.method == "POST":
            db().execute(
                "INSERT INTO messages (name, email, subject, message,"
                " created_date) VALUES (?,?,?,?,?)",
                (request.form.get("name", "").strip(),
                 request.form.get("email", "").strip(),
                 request.form.get("subject", "").strip(),
                 request.form.get("message", "").strip(), S_.TODAY))
            db().commit()
            sent = True
        return render_template("contact.html", sent=sent)

    @app.get("/rules")
    def rules():
        return render_template("rules.html")

    return app
