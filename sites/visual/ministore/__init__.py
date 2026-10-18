import json
import math
import os
import sqlite3
import tempfile

from flask import (Flask, g, redirect, render_template, request, session,
                   url_for, jsonify, abort)

from .seed import seed
from .strings import LANG_META, STRINGS

PRODUCT_QUERY = """
    SELECT p.*, COUNT(r.id) AS n_reviews, ROUND(AVG(r.stars), 1) AS avg_stars
    FROM products p LEFT JOIN reviews r ON r.product_id = p.id
"""
PER_PAGE = 12


def create_app(db_path=None, lang="en"):
    app = Flask(__name__)
    from benchmark.harness import protect
    protect(app)
    app.secret_key = "benchmark-not-secret"
    if db_path is None:
        db_path = os.path.join(tempfile.gettempdir(),
                               f"mwa_visual_{lang}.db")
    app.config["DB_PATH"] = db_path

    META = LANG_META[lang]
    S = dict(STRINGS[lang], cur=META["cur"])
    _DIGITS = str.maketrans("0123456789", META["digits"])
    app.jinja_env.filters["v2_num"] = lambda s: str(s).translate(_DIGITS)
    _FOLD = {}
    for _block in ("০১২৩৪৫৬৭৮৯", "०१२३४५६७८९", "٠١٢٣٤٥٦٧٨٩", "۰۱۲۳۴۵۶۷۸۹",
                   "૦૧૨૩૪૫૬૭૮૯", "੦੧੨੩੪੫੬੭੮੯", "௦௧௨௩௪௫௬௭௮௯", "౦౧౨౩౪౫౬౭౮౯"):
        for _i, _ch in enumerate(_block):
            _FOLD[ord(_ch)] = str(_i)

    def fold(s):
        return str(s).translate(_FOLD)

    def as_int(raw, default):
        try:
            return int(fold(raw).strip())
        except (TypeError, ValueError):
            return default
    app.jinja_env.globals.update(S=S, lang=lang, dir=META["dir"])

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
            g.db.create_function("fold", 1, fold)
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
        if table not in {"users", "products", "orders", "order_items", "reviews",
                         "wishlist", "coupons", "messages", "qa",
                         "helpful_votes"}:
            abort(404)
        rows = db().execute(f"SELECT * FROM {table}").fetchall()
        return jsonify([dict(r) for r in rows])

    def current_user():
        uid = session.get("uid")
        if uid is None:
            return None
        return db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()

    def cart():
        return session.setdefault("cart", {})

    def cart_items():
        items, total = [], 0.0
        for pid, qty in cart().items():
            p = db().execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
            if p:
                items.append({"p": p, "qty": qty, "subtotal": round(p["price"] * qty, 2)})
                total += p["price"] * qty
        return items, round(total, 2)

    def coupon_discount(total):
        code = session.get("coupon", "")
        if not code:
            return "", 0, total
        c = db().execute("SELECT * FROM coupons WHERE code=? AND active=1", (code,)).fetchone()
        if c is None:
            return "", 0, total
        discounted = round(total * (100 - c["percent_off"]) / 100.0, 2)
        return code, c["percent_off"], discounted

    def categories():
        return [r["category"] for r in db().execute(
            "SELECT DISTINCT category FROM products ORDER BY category")]

    def order_clause(sort):
        return {"price_asc": "p.price ASC", "price_desc": "p.price DESC",
                "rating": "avg_stars DESC NULLS LAST, n_reviews DESC",
                "reviews": "n_reviews DESC"}.get(sort, "p.name ASC")

    @app.context_processor
    def inject():
        return {"user": current_user(), "cart_count": sum(cart().values()),
                "categories": categories()}

    def catalog(where, args, title, sort, q="", cat="", base_path=None):
        page = max(1, as_int(request.args.get("page", 1), 1))
        rows = db().execute(
            PRODUCT_QUERY + " WHERE " + where + " GROUP BY p.id ORDER BY " + order_clause(sort),
            args).fetchall()
        n_pages = max(1, math.ceil(len(rows) / PER_PAGE))
        page = min(page, n_pages)
        window = rows[(page - 1) * PER_PAGE: page * PER_PAGE]
        return render_template("index.html", products=window, title=title, sort=sort,
                               q=q, cat=cat, page=page, n_pages=n_pages,
                               base_path=base_path or "/")

    @app.get("/")
    def index():
        q = request.args.get("q", "").strip()
        sort = request.args.get("sort", "name")
        if q:
            toks = [fold(t) for t in q.split() if any(ch.isalnum() for ch in t)]
            where = " AND ".join(
                ["(fold(p.name) LIKE ? OR fold(p.description) LIKE ? OR p.brand LIKE ?)"] * len(toks)
            ) or "(fold(p.name) LIKE ? OR fold(p.description) LIKE ? OR p.brand LIKE ?)"
            args = [f"%{t}%" for t in (toks or [q]) for _ in range(3)]
            return catalog(where, args, S["results_for"].format(q=q), sort, q=q,
                           base_path=f"/?q={q}")
        return catalog("1=1", [], S["all_products"], sort, base_path="/")

    @app.get("/category/<cat>")
    def category(cat):
        if cat not in categories():
            abort(404)
        sort = request.args.get("sort", "name")
        return catalog("p.category = ?", [cat], cat, sort, cat=cat,
                       base_path=f"/category/{cat}")

    @app.get("/brand/<brand>")
    def brand(brand):
        sort = request.args.get("sort", "name")
        return catalog("p.brand = ?", [brand],
                       S["brand_title"].format(b=brand), sort,
                       base_path=f"/brand/{brand}")

    @app.get("/deals")
    def deals():
        rows = db().execute("SELECT * FROM coupons ORDER BY id").fetchall()
        return render_template("deals.html", coupons=rows)

    @app.get("/product/<int:pid>")
    def product(pid):
        p = db().execute(PRODUCT_QUERY + " WHERE p.id=? GROUP BY p.id", (pid,)).fetchone()
        if p is None or p["id"] is None:
            abort(404)
        reviews = db().execute(
            """SELECT r.*, u.username FROM reviews r JOIN users u ON u.id = r.user_id
               WHERE r.product_id=? ORDER BY r.id""", (pid,)).fetchall()
        qas = db().execute(
            """SELECT q.*, u.username FROM qa q JOIN users u ON u.id = q.user_id
               WHERE q.product_id=? ORDER BY q.id""", (pid,)).fetchall()
        u = current_user()
        in_wishlist = False
        if u:
            in_wishlist = db().execute(
                "SELECT 1 FROM wishlist WHERE user_id=? AND product_id=?",
                (u["id"], pid)).fetchone() is not None
        return render_template("product.html", p=p, reviews=reviews,
                               qas=qas, in_wishlist=in_wishlist)

    @app.get("/shopper/<username>")
    def shopper(username):
        u = db().execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if u is None:
            abort(404)
        rows = db().execute(
            """SELECT r.*, p.name AS product_name, p.id AS pid FROM reviews r
               JOIN products p ON p.id = r.product_id
               WHERE r.user_id=? ORDER BY r.id""", (u["id"],)).fetchall()
        return render_template("shopper.html", profile=u, reviews=rows)

    @app.post("/product/<int:pid>/ask")
    def ask_question(pid):
        u = current_user()
        if u is None:
            return redirect(url_for("login", next=f"/product/{pid}"))
        if db().execute("SELECT 1 FROM products WHERE id=?",
                        (pid,)).fetchone() is None:
            abort(404)
        question = request.form.get("question", "").strip()
        if question:
            db().execute("INSERT INTO qa (product_id, user_id, question,"
                         " answer) VALUES (?,?,?,'')", (pid, u["id"],
                                                        question))
            db().commit()
        return redirect(url_for("product", pid=pid))

    @app.post("/review/<int:rid>/helpful")
    def mark_helpful(rid):
        u = current_user()
        r = db().execute("SELECT * FROM reviews WHERE id=?",
                         (rid,)).fetchone()
        if r is None:
            abort(404)
        if u is None:
            return redirect(url_for("login",
                                    next=f"/product/{r['product_id']}"))
        cur = db().execute(
            "INSERT OR IGNORE INTO helpful_votes (review_id, user_id)"
            " VALUES (?,?)", (rid, u["id"]))
        if cur.rowcount:
            db().execute("UPDATE reviews SET helpful = helpful + 1 "
                         "WHERE id=?", (rid,))
        db().commit()
        return redirect(url_for("product", pid=r["product_id"]))

    @app.get("/brands")
    def brands():
        rows = db().execute(
            """SELECT p.brand, COUNT(DISTINCT p.id) AS n_products,
                      ROUND(AVG(r.stars), 1) AS avg_stars
               FROM products p LEFT JOIN reviews r ON r.product_id = p.id
               GROUP BY p.brand ORDER BY p.brand""").fetchall()
        return render_template("brands.html", rows=rows)

    @app.post("/product/<int:pid>/review")
    def add_review(pid):
        u = current_user()
        if u is None:
            return redirect(url_for("login", next=f"/product/{pid}"))
        stars = min(5, max(1, as_int(request.form.get("stars", 5), 5)))
        body = request.form.get("body", "").strip()
        if body:
            db().execute("INSERT INTO reviews (product_id, user_id, stars, body) VALUES (?,?,?,?)",
                         (pid, u["id"], stars, body))
            db().commit()
        return redirect(url_for("product", pid=pid))

    @app.post("/cart/add/<int:pid>")
    def cart_add(pid):
        p = db().execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
        if p is None:
            abort(404)
        if p["stock"] <= 0:
            return render_template("product_error.html", p=p,
                                   error=S["oos_cart_error"])
        qty = max(1, as_int(request.form.get("qty", 1), 1))
        c = cart()
        c[str(pid)] = c.get(str(pid), 0) + qty
        session.modified = True
        return redirect(url_for("view_cart"))

    @app.post("/cart/update/<int:pid>")
    def cart_update(pid):
        c = cart()
        qty = as_int(request.form.get("qty", 0), c.get(str(pid), 0))
        if qty <= 0:
            c.pop(str(pid), None)
        else:
            c[str(pid)] = qty
        session.modified = True
        return redirect(url_for("view_cart"))

    @app.post("/cart/remove/<int:pid>")
    def cart_remove(pid):
        cart().pop(str(pid), None)
        session.modified = True
        return redirect(url_for("view_cart"))

    @app.post("/cart/clear")
    def cart_clear():
        session["cart"] = {}
        return redirect(url_for("view_cart"))

    @app.get("/cart")
    def view_cart():
        items, total = cart_items()
        return render_template("cart.html", items=items, total=total)

    @app.route("/checkout", methods=["GET", "POST"])
    def checkout():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/checkout"))
        items, total = cart_items()
        error = None
        if request.method == "POST":
            address = request.form.get("address", "").strip()
            if not items:
                error = S["cart_empty"]
            elif not address:
                error = S["addr_required"]
            else:
                session["ship_address"] = address
                session.modified = True
                return redirect(url_for("checkout_review"))
        return render_template("checkout_address.html", items=items, total=total,
                               error=error, saved_address=u["default_address"])

    @app.post("/checkout/coupon")
    def checkout_coupon():
        code = request.form.get("code", "").strip().upper()
        c = db().execute("SELECT * FROM coupons WHERE code=?", (code,)).fetchone()
        if c is None:
            session["coupon_error"] = S["unknown_coupon"]
            session.pop("coupon", None)
        elif not c["active"]:
            session["coupon_error"] = S["coupon_expired"]
            session.pop("coupon", None)
        else:
            session["coupon"] = code
            session.pop("coupon_error", None)
        session.modified = True
        return redirect(url_for("checkout_review"))

    @app.get("/checkout/review")
    def checkout_review():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/checkout"))
        if not session.get("ship_address"):
            return redirect(url_for("checkout"))
        items, total = cart_items()
        code, pct, discounted = coupon_discount(total)
        coupon_error = session.pop("coupon_error", None)
        return render_template("checkout_review.html", items=items, total=total,
                               address=session["ship_address"], coupon_code=code,
                               coupon_pct=pct, final_total=discounted,
                               coupon_error=coupon_error)

    @app.post("/checkout/confirm")
    def checkout_confirm():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/checkout"))
        items, total = cart_items()
        address = session.get("ship_address", "")
        if not items or not address:
            return redirect(url_for("checkout"))
        code, pct, discounted = coupon_discount(total)
        cur = db().execute(
            "INSERT INTO orders (user_id, address, total, status, placed_on, coupon_code)"
            " VALUES (?,?,?,'placed','2026-08-31',?)", (u["id"], address, discounted, code))
        oid = cur.lastrowid
        for it in items:
            db().execute(
                "INSERT INTO order_items (order_id, product_id, qty, price) VALUES (?,?,?,?)",
                (oid, it["p"]["id"], it["qty"], it["p"]["price"]))
        db().commit()
        session["cart"] = {}
        session.pop("ship_address", None)
        session.pop("coupon", None)
        return redirect(url_for("order_detail", oid=oid))

    @app.get("/orders")
    def orders():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/orders"))
        rows = db().execute(
            """SELECT o.*, (SELECT SUM(qty) FROM order_items oi WHERE oi.order_id = o.id) AS n_items
               FROM orders o WHERE o.user_id=? ORDER BY o.id DESC""", (u["id"],)).fetchall()
        return render_template("orders.html", orders=rows)

    @app.get("/order/<int:oid>")
    def order_detail(oid):
        u = current_user()
        if u is None:
            return redirect(url_for("login", next=f"/order/{oid}"))
        o = db().execute("SELECT * FROM orders WHERE id=? AND user_id=?", (oid, u["id"])).fetchone()
        if o is None:
            abort(404)
        items = db().execute(
            """SELECT oi.*, p.name FROM order_items oi JOIN products p ON p.id = oi.product_id
               WHERE oi.order_id=?""", (oid,)).fetchall()
        return render_template("order.html", o=o, items=items)

    @app.route("/order/<int:oid>/cancel", methods=["GET", "POST"])
    def cancel_order(oid):
        u = current_user()
        if u is None:
            return redirect(url_for("login"))
        o = db().execute("SELECT * FROM orders WHERE id=? AND user_id=?", (oid, u["id"])).fetchone()
        if o is None:
            abort(404)
        if request.method == "GET":
            return render_template("confirm_cancel.html", o=o)
        if o["status"] in ("placed", "shipped"):
            db().execute("UPDATE orders SET status='cancelled' WHERE id=?", (oid,))
            db().commit()
        return redirect(url_for("order_detail", oid=oid))

    @app.route("/order/<int:oid>/address", methods=["GET", "POST"])
    def edit_order_address(oid):
        u = current_user()
        if u is None:
            return redirect(url_for("login", next=f"/order/{oid}"))
        o = db().execute("SELECT * FROM orders WHERE id=? AND user_id=?", (oid, u["id"])).fetchone()
        if o is None:
            abort(404)
        error = None
        if o["status"] not in ("placed", "shipped"):
            error = S["addr_no_change"]
        elif request.method == "POST":
            addr = request.form.get("address", "").strip()
            if addr:
                db().execute("UPDATE orders SET address=? WHERE id=?", (addr, oid))
                db().commit()
                return redirect(url_for("order_detail", oid=oid))
            error = S["addr_required2"]
        return render_template("edit_address.html", o=o, error=error)

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/contact"))
        sent = False
        if request.method == "POST":
            body = request.form.get("message", "").strip()
            order_ref = request.form.get("order_ref", "").strip()
            if body:
                db().execute("INSERT INTO messages (user_id, order_ref, body) VALUES (?,?,?)",
                             (u["id"], order_ref, body))
                db().commit()
                sent = True
        return render_template("contact.html", sent=sent)

    @app.route("/settings", methods=["GET", "POST"])
    def settings():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/settings"))
        saved = False
        if request.method == "POST":
            addr = request.form.get("default_address", "").strip()
            db().execute("UPDATE users SET default_address=? WHERE id=?", (addr, u["id"]))
            db().commit()
            saved = True
            u = current_user()
        return render_template("settings.html", profile=u, saved=saved)

    @app.get("/wishlist")
    def wishlist():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/wishlist"))
        rows = db().execute(
            """SELECT p.* FROM wishlist w JOIN products p ON p.id = w.product_id
               WHERE w.user_id=? ORDER BY w.id""", (u["id"],)).fetchall()
        return render_template("wishlist.html", products=rows)

    @app.post("/wishlist/add/<int:pid>")
    def wishlist_add(pid):
        u = current_user()
        if u is None:
            return redirect(url_for("login", next=f"/product/{pid}"))
        db().execute("INSERT OR IGNORE INTO wishlist (user_id, product_id) VALUES (?,?)",
                     (u["id"], pid))
        db().commit()
        return redirect(url_for("wishlist"))

    @app.post("/wishlist/remove/<int:pid>")
    def wishlist_remove(pid):
        u = current_user()
        if u is None:
            return redirect(url_for("login"))
        db().execute("DELETE FROM wishlist WHERE user_id=? AND product_id=?", (u["id"], pid))
        db().commit()
        return redirect(url_for("wishlist"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            u = db().execute("SELECT * FROM users WHERE username=? AND password=?",
                             (request.form.get("username", ""),
                              request.form.get("password", ""))).fetchone()
            if u is None:
                error = S["wrong_login"]
            else:
                session["uid"] = u["id"]
                return redirect(request.args.get("next") or url_for("index"))
        return render_template("login.html", error=error)

    @app.get("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    return app
