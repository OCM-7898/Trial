import math
import os
import sqlite3
import tempfile

from flask import (Flask, abort, g, jsonify, redirect, render_template,
                   request, session, url_for)

from .seed import TODAY, hand_table, seed
from .strings import LANG_META, RULES, STRINGS

PER_PAGE = 12
CITIES = ["Karachi", "Lahore", "Islamabad", "Rawalpindi",
          "Faisalabad", "Multan", "Peshawar", "Sialkot"]
SORTS = {"newest": "posted_on DESC, id DESC",
         "price_asc": "price ASC, id ASC",
         "price_desc": "price DESC, id ASC",
         "mileage_asc": "mileage_km ASC, id ASC",
         "year_desc": "year DESC, id ASC"}


def finance_quote(price, down_pct, years):
    loan = price * (100 - down_pct) // 100
    interest = loan * 16 * years // 100
    total = loan + interest
    months = years * 12
    monthly = -(-total // months)
    return {"loan": loan, "interest": interest,
            "total": total, "monthly": monthly}


def create_app(db_path=None, lang="en"):
    app = Flask(__name__)
    from benchmark.harness import protect
    protect(app)
    app.secret_key = "benchmark-not-secret"
    if db_path is None:
        db_path = os.path.join(tempfile.gettempdir(),
                               f"mwa_visual_gari_{lang}.db")
    app.config["DB_PATH"] = db_path

    META = LANG_META[lang]
    S = dict(STRINGS[lang], cur=META["cur"])
    _DIGITS = str.maketrans("0123456789", META["digits"])
    app.jinja_env.filters["v2_num"] = lambda s: str(s).translate(_DIGITS)
    app.jinja_env.filters["money"] = (
        lambda n: f"{META['cur']}{n:,}".translate(_DIGITS))
    app.jinja_env.filters["grp"] = lambda n: f"{n:,}".translate(_DIGITS)
    T = hand_table(lang)
    VOC = {"city": CITIES,
           "body_type": ["Sedan", "SUV", "Hatchback", "MPV", "Sports car",
                         "Van"],
           "fuel": ["Petrol", "Diesel", "Hybrid", "Electric"],
           "transmission": ["Manual", "Automatic"]}
    if T:
        VOC = {k: [T[k][v] for v in vs] for k, vs in VOC.items()}
    app.jinja_env.globals.update(S=S, lang=lang, dir=META["dir"],
                                 cities=VOC["city"], bodies=VOC["body_type"],
                                 fuels=VOC["fuel"],
                                 transmissions=VOC["transmission"],
                                 transmissions_browse=VOC["transmission"][::-1],
                                 rules=[(h, [it.format(
                                     fee10=app.jinja_env.filters["money"](10 * META["rate"]),
                                     fee60=app.jinja_env.filters["money"](60 * META["rate"]))
                                     for it in items]) for h, items in RULES[lang]])

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

    @app.post("/__reset__")
    def __reset():
        reset_db()
        session.clear()
        return jsonify({"ok": True})

    @app.get("/__state__/<table>")
    def __state(table):
        if table not in {"users", "listings", "saved", "offers",
                         "ads", "messages", "dealers"}:
            abort(404)
        rows = db().execute(f"SELECT * FROM {table}").fetchall()
        return jsonify([dict(r) for r in rows])

    def current_user():
        uid = session.get("uid")
        if uid is None:
            return None
        return db().execute("SELECT * FROM users WHERE id=?",
                            (uid,)).fetchone()

    def brands():
        return [r["brand"] for r in db().execute(
            "SELECT DISTINCT brand FROM listings ORDER BY brand")]

    def car_name(c):
        return f"{c['year']} {c['brand']} {c['model']}"

    app.jinja_env.globals["car_name"] = car_name

    @app.context_processor
    def inject():
        return {"user": current_user(), "brands": brands()}

    @app.get("/")
    def home():
        rows = db().execute(
            "SELECT * FROM listings WHERE status='active' "
            "ORDER BY posted_on DESC, id DESC LIMIT 8").fetchall()
        bodies = [r["body_type"] for r in db().execute(
            "SELECT DISTINCT body_type FROM listings ORDER BY body_type")]
        return render_template("home.html", featured=rows, bodies=bodies)

    @app.get("/cars")
    def browse():
        a = request.args
        where, args = ["status='active'"], []
        for col in ("brand", "body_type", "city", "fuel", "transmission"):
            v = a.get(col, "").strip()
            if v:
                where.append(f"{col}=?")
                args.append(v)
        q = a.get("q", "").strip()
        if q:
            where.append("(brand LIKE ? OR model LIKE ?)")
            args += [f"%{q}%"] * 2
        mp = a.get("max_price", "").strip().replace(",", "")
        if mp.isdigit():
            where.append("price<=?")
            args.append(int(mp))
        my = a.get("min_year", "").strip()
        if my.isdigit():
            where.append("year>=?")
            args.append(int(my))
        sort = a.get("sort", "newest")
        rows = db().execute(
            "SELECT * FROM listings WHERE " + " AND ".join(where)
            + " ORDER BY " + SORTS.get(sort, SORTS["newest"]),
            args).fetchall()
        page = max(1, int(a.get("page", 1) or 1))
        n_pages = max(1, math.ceil(len(rows) / PER_PAGE))
        page = min(page, n_pages)
        return render_template(
            "browse.html", cars=rows[(page - 1) * PER_PAGE: page * PER_PAGE],
            n=len(rows), page=page, n_pages=n_pages, sel=a, sort=sort)

    @app.get("/car/<int:cid>")
    def car(cid):
        c = db().execute("SELECT * FROM listings WHERE id=?",
                         (cid,)).fetchone()
        if c is None:
            abort(404)
        u = current_user()
        is_saved = u and db().execute(
            "SELECT 1 FROM saved WHERE user_id=? AND listing_id=?",
            (u["id"], cid)).fetchone() is not None
        similar = db().execute(
            "SELECT * FROM listings WHERE brand=? AND id!=? AND "
            "status='active' ORDER BY id LIMIT 4", (c["brand"], cid)).fetchall()
        return render_template("car.html", c=c, is_saved=is_saved,
                               similar=similar,
                               offer_error=session.pop("offer_error", None))

    @app.post("/car/<int:cid>/save")
    def save_toggle(cid):
        u = current_user()
        if u is None:
            return redirect(url_for("login", next=f"/car/{cid}"))
        if db().execute("SELECT 1 FROM saved WHERE user_id=? AND listing_id=?",
                        (u["id"], cid)).fetchone():
            db().execute("DELETE FROM saved WHERE user_id=? AND listing_id=?",
                         (u["id"], cid))
        else:
            db().execute("INSERT INTO saved (user_id, listing_id) "
                         "VALUES (?,?)", (u["id"], cid))
        db().commit()
        return redirect(url_for("car", cid=cid))

    @app.post("/car/<int:cid>/offer")
    def make_offer(cid):
        u = current_user()
        if u is None:
            return redirect(url_for("login", next=f"/car/{cid}"))
        c = db().execute("SELECT * FROM listings WHERE id=?",
                         (cid,)).fetchone()
        if c is None:
            abort(404)
        if c["status"] != "active":
            session["offer_error"] = S["offer_sold"]
            return redirect(url_for("car", cid=cid))
        raw = request.form.get("amount", "").strip().replace(",", "")
        if not raw.isdigit() or int(raw) <= 0:
            session["offer_error"] = S["offer_invalid"]
            return redirect(url_for("car", cid=cid))
        amount = int(raw)
        if amount * 100 < c["price"] * 80:
            session["offer_error"] = S["offer_low"]
            return redirect(url_for("car", cid=cid))
        msg = request.form.get("message", "").strip()
        old = db().execute(
            "SELECT id FROM offers WHERE user_id=? AND listing_id=?",
            (u["id"], cid)).fetchone()
        if old:
            db().execute("UPDATE offers SET amount=?, message=?, made_on=? "
                         "WHERE id=?", (amount, msg, TODAY, old["id"]))
        else:
            db().execute(
                "INSERT INTO offers (user_id, listing_id, amount, message,"
                " status, made_on) VALUES (?,?,?,?,'pending',?)",
                (u["id"], cid, amount, msg, TODAY))
        db().commit()
        return redirect(url_for("offers"))

    @app.get("/offers")
    def offers():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/offers"))
        rows = db().execute(
            """SELECT o.*, l.brand, l.model, l.year, l.price AS asking
               FROM offers o JOIN listings l ON l.id = o.listing_id
               WHERE o.user_id=? ORDER BY o.id""", (u["id"],)).fetchall()
        return render_template("offers.html", offers=rows)

    @app.post("/offers/<int:oid>/withdraw")
    def withdraw_offer(oid):
        u = current_user()
        if u is None:
            return redirect(url_for("login"))
        db().execute("DELETE FROM offers WHERE id=? AND user_id=?",
                     (oid, u["id"]))
        db().commit()
        return redirect(url_for("offers"))

    @app.get("/saved")
    def saved():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/saved"))
        rows = db().execute(
            """SELECT l.* FROM saved s JOIN listings l ON l.id = s.listing_id
               WHERE s.user_id=? ORDER BY s.rowid""", (u["id"],)).fetchall()
        return render_template("saved.html", cars=rows)

    @app.post("/saved/remove/<int:cid>")
    def saved_remove(cid):
        u = current_user()
        if u is None:
            return redirect(url_for("login"))
        db().execute("DELETE FROM saved WHERE user_id=? AND listing_id=?",
                     (u["id"], cid))
        db().commit()
        return redirect(url_for("saved"))

    SELL_FIELDS = ("brand", "model", "year", "mileage_km", "price", "city",
                   "color", "transmission", "fuel", "engine_cc", "phone",
                   "description")

    def valid_draft(d):
        return (d["brand"] in brands() + ["Other"] and d["model"]
                and d["year"].isdigit() and 1990 <= int(d["year"]) <= 2026
                and d["mileage_km"].isdigit()
                and d["price"].isdigit() and int(d["price"]) > 0
                and d["city"] in VOC["city"] and d["phone"])

    @app.route("/sell", methods=["GET", "POST"])
    def sell():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/sell"))
        error = None
        if request.method == "POST":
            d = {f: request.form.get(f, "").strip().replace(",", "")
                 if f in ("year", "mileage_km", "price", "engine_cc")
                 else request.form.get(f, "").strip() for f in SELL_FIELDS}
            if valid_draft(d):
                session["draft_ad"] = d
                return redirect(url_for("sell_review"))
            error = S["sell_required"]
        d = session.get("draft_ad", {f: "" for f in SELL_FIELDS})
        return render_template("sell.html", d=d, error=error)

    @app.get("/sell/review")
    def sell_review():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/sell"))
        d = session.get("draft_ad")
        if not d:
            return redirect(url_for("sell"))
        return render_template("sell_review.html", d=d)

    @app.post("/sell/confirm")
    def sell_confirm():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/sell"))
        d = session.get("draft_ad")
        if not d:
            return redirect(url_for("sell"))
        cur = db().execute(
            "INSERT INTO ads (user_id, brand, model, year, price,"
            " mileage_km, color, transmission, fuel, engine_cc, city,"
            " phone, description, status, posted_on)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,'active',?)",
            (u["id"], d["brand"], d["model"], int(d["year"]),
             int(d["price"]), int(d["mileage_km"]), d["color"],
             d["transmission"], d["fuel"],
             int(d["engine_cc"] or 0), d["city"], d["phone"],
             d["description"], TODAY))
        db().commit()
        session.pop("draft_ad", None)
        return redirect(url_for("my_ad", aid=cur.lastrowid, published=1))

    @app.get("/account/ads")
    def my_ads():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/account/ads"))
        rows = db().execute("SELECT * FROM ads WHERE user_id=? ORDER BY id",
                            (u["id"],)).fetchall()
        return render_template("my_ads.html", ads=rows)

    def own_ad(aid):
        u = current_user()
        if u is None:
            return None, redirect(url_for("login", next="/account/ads"))
        a = db().execute("SELECT * FROM ads WHERE id=? AND user_id=?",
                         (aid, u["id"])).fetchone()
        if a is None:
            abort(404)
        return a, None

    @app.get("/account/ads/<int:aid>")
    def my_ad(aid):
        a, resp = own_ad(aid)
        if resp:
            return resp
        return render_template("my_ad.html", a=a,
                               published=request.args.get("published"),
                               updated=request.args.get("updated"))

    @app.post("/account/ads/<int:aid>/price")
    def ad_price(aid):
        a, resp = own_ad(aid)
        if resp:
            return resp
        raw = request.form.get("price", "").strip().replace(",", "")
        if a["status"] == "active" and raw.isdigit() and int(raw) > 0:
            db().execute("UPDATE ads SET price=? WHERE id=?",
                         (int(raw), aid))
            db().commit()
            return redirect(url_for("my_ad", aid=aid, updated=1))
        return redirect(url_for("my_ad", aid=aid))

    @app.route("/account/ads/<int:aid>/sold", methods=["GET", "POST"])
    def ad_sold(aid):
        a, resp = own_ad(aid)
        if resp:
            return resp
        if request.method == "GET":
            return render_template("confirm.html", a=a,
                                   q=S["confirm_sold_q"],
                                   action=f"/account/ads/{aid}/sold")
        if a["status"] == "active":
            db().execute("UPDATE ads SET status='sold' WHERE id=?", (aid,))
            db().commit()
        return redirect(url_for("my_ad", aid=aid))

    @app.route("/account/ads/<int:aid>/delete", methods=["GET", "POST"])
    def ad_delete(aid):
        a, resp = own_ad(aid)
        if resp:
            return resp
        if request.method == "GET":
            return render_template("confirm.html", a=a,
                                   q=S["confirm_delete_q"],
                                   action=f"/account/ads/{aid}/delete")
        db().execute("DELETE FROM ads WHERE id=?", (aid,))
        db().commit()
        return redirect(url_for("my_ads"))

    @app.route("/account", methods=["GET", "POST"])
    def account():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/account"))
        saved_ok = False
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            city = request.form.get("city", "").strip()
            if name and phone and city in VOC["city"]:
                db().execute("UPDATE users SET name=?, phone=?, city=? "
                             "WHERE id=?", (name, phone, city, u["id"]))
                db().commit()
                saved_ok = True
                u = current_user()
        return render_template("account.html", profile=u, saved_ok=saved_ok)

    @app.get("/finance")
    def finance():
        a = request.args
        quote = error = None
        price = a.get("price", "").strip().replace(",", "")
        down = a.get("down_pct", "").strip()
        years = a.get("years", "").strip()
        if price or down or years:
            if (price.isdigit() and int(price) > 0 and down.isdigit()
                    and 0 <= int(down) <= 90 and years.isdigit()
                    and 1 <= int(years) <= 7):
                quote = finance_quote(int(price), int(down), int(years))
            else:
                error = S["finance_invalid"]
        return render_template("finance.html", quote=quote, error=error,
                               sel=a)

    @app.get("/compare")
    def compare():
        a = request.args.get("a", "").strip()
        b = request.args.get("b", "").strip()
        pair = error = None
        if a or b:
            ca = db().execute("SELECT * FROM listings WHERE id=?",
                              (a,)).fetchone() if a.isdigit() else None
            cb = db().execute("SELECT * FROM listings WHERE id=?",
                              (b,)).fetchone() if b.isdigit() else None
            if ca and cb:
                pair = (ca, cb)
            else:
                error = S["compare_bad_id"]
        return render_template("compare.html", pair=pair, error=error,
                               a=a, b=b)

    @app.get("/dealers")
    def dealers():
        rows = db().execute(
            """SELECT d.*, (SELECT COUNT(*) FROM listings l
                            WHERE l.dealer_id = d.id AND l.status='active')
                           AS n_active
               FROM dealers d ORDER BY d.id""").fetchall()
        return render_template("dealers.html", dealers=rows)

    @app.get("/dealer/<int:did>")
    def dealer(did):
        d = db().execute("SELECT * FROM dealers WHERE id=?",
                         (did,)).fetchone()
        if d is None:
            abort(404)
        rows = db().execute(
            "SELECT * FROM listings WHERE dealer_id=? AND status='active' "
            "ORDER BY id", (did,)).fetchall()
        return render_template("dealer.html", d=d, cars=rows)

    @app.get("/car/<int:cid>/inspection")
    def inspection(cid):
        c = db().execute("SELECT * FROM listings WHERE id=?",
                         (cid,)).fetchone()
        if c is None:
            abort(404)
        return render_template("inspection.html", c=c)

    @app.get("/rules")
    def rules():
        return render_template("rules.html")

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/contact"))
        sent = False
        if request.method == "POST":
            subject = request.form.get("subject", "").strip()
            body = request.form.get("message", "").strip()
            if body:
                db().execute("INSERT INTO messages (user_id, subject, body)"
                             " VALUES (?,?,?)", (u["id"], subject, body))
                db().commit()
                sent = True
        return render_template("contact.html", sent=sent)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            u = db().execute(
                "SELECT * FROM users WHERE email=? AND password=?",
                (request.form.get("email", "").strip(),
                 request.form.get("password", ""))).fetchone()
            if u is None:
                error = S["wrong_login"]
            else:
                session["uid"] = u["id"]
                return redirect(request.args.get("next") or url_for("home"))
        return render_template("login.html", error=error)

    @app.get("/logout")
    def logout():
        session.clear()
        return redirect(url_for("home"))

    return app
