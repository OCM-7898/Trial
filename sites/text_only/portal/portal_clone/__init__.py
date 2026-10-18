import json
import os
import sqlite3
import tempfile

from flask import (Flask, abort, g, jsonify, redirect, render_template,
                   request, session)

from .seed import seed, TODAY

STATE_TABLES = {"submissions", "appointments", "payments", "record_overrides",
                "bills"}

SLOTS = {
    2: {"dates": ["2026-06-21", "2026-06-22", "2026-06-24", "2026-06-25"],
        "times": ["09:30", "10:30", "11:30", "15:00"]},
    7: {"dates": ["2026-06-23", "2026-06-25", "2026-06-26", "2026-06-29"],
        "times": ["09:00", "11:00", "14:30"]},
}


def create_app(db_path=None, lang="en"):
    app = Flask(__name__)
    from benchmark.harness import protect
    protect(app)
    app.secret_key = "benchmark-not-secret"
    if db_path is None:
        db_path = os.path.join(tempfile.gettempdir(),
                               f"mwa_portal_{lang}.db")
    app.config["DB_PATH"] = db_path

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

    from .content import DIGITS, panel_items, STRINGS
    PANEL_ITEMS = panel_items(lang)
    S = STRINGS[lang]
    _DIGITS = str.maketrans("0123456789", DIGITS.get(lang, "0123456789"))
    app.jinja_env.filters["v2_num"] = lambda x: str(x).translate(_DIGITS)
    if lang in DIGITS:
        from werkzeug.datastructures import ImmutableMultiDict
        _FOLD = str.maketrans(DIGITS[lang], "0123456789")

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

    def current_account():
        aid = session.get("aid")
        if aid is None:
            return None
        return db().execute("SELECT * FROM accounts WHERE id=?",
                            (aid,)).fetchone()

    def current_citizen():
        acc = current_account()
        if acc is None:
            return None
        return db().execute("SELECT * FROM citizens WHERE id=?",
                            (acc["citizen_ref"],)).fetchone()

    def svc(slug):
        s = db().execute("SELECT * FROM services WHERE slug=?",
                         (slug,)).fetchone()
        if s is None:
            abort(404)
        return s

    def new_ref(prefix, table):
        n = db().execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        return f"{prefix}{n + 1:06d}"

    def add_submission(kind, payload, prefix):
        ref = new_ref(prefix, "submissions")
        cz = current_citizen()
        db().execute(
            "INSERT INTO submissions (kind, citizen_ref, ref_no, payload,"
            " created_date) VALUES (?,?,?,?,?)",
            (kind, cz["id"] if cz else None, ref,
             json.dumps(payload, ensure_ascii=False), TODAY))
        db().commit()
        return ref

    def add_payment(service_id, target_kind, ref, amount, method):
        db().execute(
            "INSERT INTO payments (service_id, target_kind, ref, amount,"
            " method, created_date) VALUES (?,?,?,?,?,?)",
            (service_id, target_kind, ref, amount, method or "counter",
             TODAY))
        db().commit()
        return new_ref("PMT", "payments")

    def add_override(table_name, field_name, record_id, new_value, document):
        db().execute(
            "INSERT INTO record_overrides (table_name, field_name,"
            " record_id, new_value, document, created_date)"
            " VALUES (?,?,?,?,?,?)",
            (table_name, field_name, record_id, new_value, document or "",
             TODAY))
        db().commit()

    def locker_docs():
        acc = current_account()
        if acc is None:
            return []
        return db().execute(
            "SELECT * FROM locker_documents WHERE account_id=?"
            " ORDER BY id", (acc["id"],)).fetchall()

    def result_page(title, rows, back):
        return render_template("result.html", title=title, rows=rows,
                               back=back)

    def no_record(title, back):
        return render_template("result.html", title=title, rows=None,
                               back=back)

    @app.context_processor
    def inject():
        return {"account": current_account(), "S": S,
                "nav_services": db().execute(
                    "SELECT * FROM services ORDER BY id").fetchall()}

    @app.get("/")
    def home():
        services = db().execute(
            "SELECT * FROM services ORDER BY id").fetchall()
        notices = db().execute(
            "SELECT * FROM notices ORDER BY date DESC, id LIMIT 8").fetchall()
        by = {s["slug"]: s for s in services}
        sectors = [
            ("sector_identity",
             ["national-id", "civil-registration", "passport"]),
            ("sector_land", ["land", "electricity"]),
            ("sector_edu", ["exam-results", "health", "pilgrimage"]),
            ("sector_tax", ["tax", "driving-licence", "police-clearance",
                            "trade-licence", "pension"]),
        ]
        sectors = [(key, [by[sl] for sl in slugs]) for key, slugs in sectors]
        stats = {
            "services": db().execute(
                "SELECT COUNT(*) FROM services").fetchone()[0],
            "offices": db().execute(
                "SELECT COUNT(*) FROM offices").fetchone()[0],
            "notices": db().execute(
                "SELECT COUNT(*) FROM notices").fetchone()[0],
            "fees": db().execute(
                "SELECT COUNT(*) FROM fee_schedules").fetchone()[0],
        }
        return render_template("home.html", services=services,
                               notices=notices, sectors=sectors,
                               stats=stats)

    @app.get("/search")
    def search():
        q = (request.args.get("q") or "").strip()
        hits = []
        if q:
            like = f"%{q}%"
            hits = db().execute(
                "SELECT slug, name, summary FROM services WHERE name LIKE ?"
                " OR summary LIKE ? ORDER BY id", (like, like)).fetchall()
        return render_template("search.html", q=q, hits=hits)

    @app.get("/notices/")
    def notices_index():
        period = (request.args.get("period") or "").strip()
        category = (request.args.get("category") or "").strip().lower()
        service = (request.args.get("service") or "").strip()
        q = ("SELECT n.*, s.name AS service_name FROM notices n JOIN"
             " services s ON s.id = n.service_id")
        where, args = [], []
        if period:
            where.append("n.date LIKE ?")
            args.append(period + "%")
        if category:
            where.append("lower(n.category)=?")
            args.append(category)
        if service:
            where.append("s.name LIKE ?")
            args.append(f"%{service}%")
        if where:
            q += " WHERE " + " AND ".join(where)
        q += " ORDER BY n.date DESC, n.id"
        rows = db().execute(q, args).fetchall()
        per = 20
        page = max(1, int(request.args.get("page", 1) or 1))
        n_pages = max(1, (len(rows) + per - 1) // per)
        page = min(page, n_pages)
        return render_template(
            "notices.html", rows=rows[(page - 1) * per: page * per],
            total=len(rows), page=page, n_pages=n_pages,
            period=period, category=category, service=service)

    @app.get("/services/")
    def services_index():
        services = db().execute(
            "SELECT * FROM services ORDER BY id").fetchall()
        return render_template("services_index.html", services=services)

    @app.get("/accounts")
    def accounts():
        rows = db().execute(
            "SELECT username, display_name FROM accounts ORDER BY id"
            " LIMIT 10").fetchall()
        return render_template("accounts.html", rows=rows)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            acc = db().execute(
                "SELECT * FROM accounts WHERE username=? AND password=?",
                (request.form.get("citizen_id", "").strip(),
                 request.form.get("password", ""))).fetchone()
            if acc:
                session["aid"] = acc["id"]
                return redirect(request.args.get("next") or "/")
            error = S["bad_login"]
        return render_template("login.html", error=error)

    @app.route("/logout", methods=["GET", "POST"])
    def logout():
        session.clear()
        return redirect("/")

    @app.get("/services/<slug>/")
    def service_landing(slug):
        s = svc(slug)
        notices = db().execute(
            "SELECT * FROM notices WHERE service_id=? ORDER BY date DESC,"
            " id", (s["id"],)).fetchall()
        return render_template("service_landing.html", s=s, notices=notices)

    @app.get("/services/<slug>/guide/")
    def service_guide(slug):
        s = svc(slug)
        from .seed import content
        c = content(lang)[slug]
        return render_template("static_page.html", s=s,
                               title=c["guide_title"], body=c["guide_body"])

    @app.get("/services/<slug>/fees/")
    def service_fees(slug):
        s = svc(slug)
        from .seed import content
        c = content(lang)[slug]
        fees = db().execute(
            "SELECT * FROM fee_schedules WHERE service_id=? ORDER BY id",
            (s["id"],)).fetchall()
        return render_template("fees.html", s=s, fees=fees,
                               intro=c["fees_intro"])

    @app.get("/services/<slug>/offices/")
    def service_offices(slug):
        s = svc(slug)
        rows = db().execute(
            "SELECT * FROM offices WHERE service_id=? ORDER BY id LIMIT 25",
            (s["id"],)).fetchall()
        return render_template("offices.html", s=s, rows=rows)

    @app.get("/services/<slug>/panel/")
    def panel(slug):
        s = svc(slug)
        if s["requires_login"] and current_account() is None:
            return redirect(f"/login?next=/services/{slug}/panel/")
        return render_template("panel.html", s=s,
                               items=PANEL_ITEMS.get(slug, []))

    @app.route("/services/<slug>/panel/<item>/", methods=["GET", "POST"])
    def panel_item(slug, item):
        s = svc(slug)
        items = {i["slug"]: i for i in PANEL_ITEMS.get(slug, [])}
        if item not in items:
            abort(404)
        if s["requires_login"] and current_account() is None:
            return redirect(f"/login?next=/services/{slug}/panel/{item}/")
        handler = HANDLERS.get((slug, item))
        meta = items[item]
        if handler:
            return handler(s, meta)
        if meta.get("lookup"):
            ref = (request.args.get("ref_no") or "").strip()
            if ref:
                return no_record(meta["title"], panel_path(slug, item))
            return render_template(
                "lookup.html", s=s, title=meta["title"],
                intro=meta["summary"],
                fields=[("ref_no", S["f_ref_no"])], method="get")
        return render_template("static_page.html", s=s, title=meta["title"],
                               body=meta["summary"])

    def panel_path(slug, item):
        return f"/services/{slug}/panel/{item}/"

    def lookup_handler(s, meta, field, label, query, present):
        val = (request.args.get(field) or "").strip()
        if val:
            row = query(val)
            if row is None:
                return no_record(meta["title"],
                                 panel_path(s["slug"], meta["slug"]))
            return result_page(meta["title"], present(row),
                               panel_path(s["slug"], meta["slug"]))
        return render_template("lookup.html", s=s, title=meta["title"],
                               intro=meta["summary"],
                               fields=[(field, label)], method="get")

    def h_correction_status(s, meta):
        return lookup_handler(
            s, meta, "slip_no", S["f_slip_no"],
            lambda v: db().execute(
                "SELECT * FROM applications WHERE slip_no=? AND service_id=1",
                (v,)).fetchone(),
            lambda r: [(S["f_slip_no"], r["slip_no"]),
                       (S["r_kind"], r["kind"]),
                       (S["r_submitted"], r["submitted_date"]),
                       (S["r_status"], r["status"])])

    def h_passport_status(s, meta):
        return lookup_handler(
            s, meta, "application_id", S["f_application_id"],
            lambda v: db().execute(
                "SELECT * FROM passports WHERE application_id=?",
                (v,)).fetchone(),
            lambda r: [(S["f_application_id"], r["application_id"]),
                       (S["r_pages"], r["pages"]),
                       (S["r_validity"], f"{r['validity_years']}"),
                       (S["r_applied"], r["applied_date"]),
                       (S["r_status"], r["status"])])

    def h_delivery_status(s, meta):
        return lookup_handler(
            s, meta, "passport_no", S["f_passport_no"],
            lambda v: db().execute(
                "SELECT * FROM passports WHERE passport_no=?",
                (v,)).fetchone(),
            lambda r: [(S["f_passport_no"], r["passport_no"]),
                       (S["r_status"], r["status"])])

    def h_birth_status(s, meta):
        return lookup_handler(
            s, meta, "registration_no", S["f_registration_no"],
            lambda v: db().execute(
                "SELECT * FROM civil_records WHERE registration_no=?"
                " AND record_type='birth'", (v,)).fetchone(),
            lambda r: [(S["f_registration_no"], r["registration_no"]),
                       (S["r_name"], r["person_name"]),
                       (S["r_father"], r["father_name"]),
                       (S["r_mother"], r["mother_name"]),
                       (S["r_event_date"], r["event_date"]),
                       (S["f_registered_date"], r["registered_date"]),
                       (S["r_place"], r["place"])])

    def h_death_status(s, meta):
        return lookup_handler(
            s, meta, "registration_no", S["f_registration_no"],
            lambda v: db().execute(
                "SELECT * FROM civil_records WHERE registration_no=?"
                " AND record_type='death'", (v,)).fetchone(),
            lambda r: [(S["f_registration_no"], r["registration_no"]),
                       (S["r_name"], r["person_name"])])

    def h_licence_status(s, meta):
        return lookup_handler(
            s, meta, "reference_no", S["f_reference_no"],
            lambda v: db().execute(
                "SELECT * FROM licences WHERE reference_no=?",
                (v,)).fetchone(),
            lambda r: [(S["f_reference_no"], r["reference_no"]),
                       (S["r_class"], r["licence_class"]),
                       (S["r_expiry"], r["expiry_date"]),
                       (S["r_status"], r["status"])])

    def h_tin_verify(s, meta):
        return lookup_handler(
            s, meta, "tin_no", S["f_tin_no"],
            lambda v: db().execute(
                "SELECT * FROM tins WHERE tin_no=?", (v,)).fetchone(),
            lambda r: [(S["f_tin_no"], r["tin_no"]),
                       (S["r_registered_name"], r["registered_name"]),
                       (S["r_circle"], r["circle"]),
                       (S["r_zone"], r["zone"]),
                       (S["r_valid"], S["yes"] if r["is_active"]
                        else S["no"])])

    def h_vaccine_certificate(s, meta):
        idn = (request.args.get("identity_no") or "").strip()
        rdate = (request.args.get("registered_date") or "").strip()
        if idn:
            row = db().execute(
                "SELECT v.* FROM vaccine_records v JOIN citizens c ON"
                " c.id = v.citizen_ref WHERE c.citizen_id=? AND"
                " v.registered_date=?", (idn, rdate)).fetchone()
            if row is None:
                return no_record(meta["title"],
                                 panel_path(s["slug"], meta["slug"]))
            return result_page(meta["title"], [
                (S["r_certificate_no"], row["certificate_no"]),
                (S["r_vaccine"], row["vaccine_name"]),
                (S["r_doses"], row["doses"]),
                (S["r_centre"], row["centre_name"])],
                panel_path(s["slug"], meta["slug"]))
        return render_template(
            "lookup.html", s=s, title=meta["title"], intro=meta["summary"],
            fields=[("identity_no", S["f_identity_no"]),
                    ("registered_date", S["f_registered_date"])],
            method="get")

    def h_result_lookup(s, meta):
        boards = db().execute(
            "SELECT name FROM exam_boards ORDER BY id").fetchall()
        roll = (request.args.get("roll_no") or "").strip()
        if roll:
            board = (request.args.get("board") or "").strip().lower()
            year = (request.args.get("year") or "").strip()
            exam = (request.args.get("exam") or "secondary").strip().lower()
            row = db().execute(
                "SELECT r.*, b.name AS board_name FROM exam_results r"
                " JOIN exam_boards b ON b.id = r.board_id"
                " WHERE r.roll_no=? AND lower(b.name)=? AND r.exam_year=?"
                " AND lower(r.exam)=?", (roll, board, year, exam)).fetchone()
            if row is None:
                return no_record(meta["title"],
                                 panel_path(s["slug"], meta["slug"]))
            return result_page(meta["title"], [
                (S["f_roll_no"], row["roll_no"]),
                (S["r_board"], row["board_name"]),
                (S["r_candidate"], row["candidate_name"]),
                (S["r_institution"], row["institution"]),
                (S["f_registration_no"], row["registration_no"]),
                (S["r_gpa"], row["gpa"]),
                (S["r_status"], row["result_status"])],
                panel_path(s["slug"], meta["slug"]))
        return render_template(
            "lookup.html", s=s, title=meta["title"],
            intro=meta["summary"] + " " + S["boards_are"] + " " +
            ", ".join(b["name"] for b in boards) + ".",
            fields=[("exam", S["f_exam"]), ("board", S["r_board"]),
                    ("year", S["f_year"]), ("roll_no", S["f_roll_no"])],
            method="get")

    def h_due_check(s, meta):
        cn = (request.args.get("consumer_no") or "").strip()
        if cn:
            meter = db().execute(
                "SELECT * FROM meters WHERE consumer_no=?", (cn,)).fetchone()
            if meter is None:
                return no_record(meta["title"],
                                 panel_path(s["slug"], meta["slug"]))
            unpaid = db().execute(
                "SELECT * FROM bills WHERE meter_id=? AND is_paid=0"
                " ORDER BY period", (meter["id"],)).fetchall()
            total = sum(b["amount"] for b in unpaid)
            rows = [(S["f_consumer_no"], meter["consumer_no"]),
                    (S["r_tariff"], meter["tariff"])]
            for b in unpaid:
                rows.append((f"{S['r_bill']} {b['bill_no']} ({b['period']})",
                             b["amount"]))
            rows.append((S["r_total_outstanding"], total))
            return result_page(meta["title"], rows,
                               panel_path(s["slug"], meta["slug"]))
        return render_template("lookup.html", s=s, title=meta["title"],
                               intro=meta["summary"],
                               fields=[("consumer_no", S["f_consumer_no"])],
                               method="get")

    def h_bill_payment(s, meta):
        if request.method == "POST" and request.form.get("bill_no"):
            bill = db().execute(
                "SELECT b.*, m.consumer_no FROM bills b JOIN meters m ON"
                " m.id = b.meter_id WHERE b.bill_no=? AND b.is_paid=0",
                (request.form["bill_no"].strip(),)).fetchone()
            if bill is None:
                return no_record(meta["title"],
                                 panel_path(s["slug"], meta["slug"]))
            add_payment(s["id"], "bill", bill["bill_no"], bill["amount"],
                        request.form.get("method"))
            db().execute("UPDATE bills SET is_paid=1 WHERE id=?",
                         (bill["id"],))
            db().commit()
            return render_template("confirm.html", s=s, title=meta["title"],
                                   message=S["paid_ok"].format(
                                       ref=bill["bill_no"],
                                       amount=bill["amount"]))
        cn = (request.values.get("consumer_no") or "").strip()
        if cn:
            meter = db().execute(
                "SELECT * FROM meters WHERE consumer_no=?", (cn,)).fetchone()
            if meter is None:
                return no_record(meta["title"],
                                 panel_path(s["slug"], meta["slug"]))
            unpaid = db().execute(
                "SELECT * FROM bills WHERE meter_id=? AND is_paid=0"
                " ORDER BY period", (meter["id"],)).fetchall()
            return render_template("bill_pay.html", s=s, title=meta["title"],
                                   meter=meter, bills=unpaid)
        return render_template("lookup.html", s=s, title=meta["title"],
                               intro=meta["summary"],
                               fields=[("consumer_no", S["f_consumer_no"])],
                               method="get")

    def h_prepaid_recharge(s, meta):
        error = None
        if request.method == "POST":
            mn = (request.form.get("meter_no") or "").strip()
            amount = (request.form.get("amount") or "").strip()
            meter = db().execute(
                "SELECT * FROM meters WHERE meter_no=? AND"
                " meter_type='prepaid'", (mn,)).fetchone()
            if meter is None:
                error = S["no_prepaid_meter"]
            elif not amount.isdigit():
                error = S["bad_amount"]
            else:
                add_payment(s["id"], "recharge", mn, int(amount),
                            request.form.get("method"))
                return render_template(
                    "confirm.html", s=s, title=meta["title"],
                    message=S["paid_ok"].format(ref=mn, amount=amount))
        return render_template(
            "lookup.html", s=s, title=meta["title"], intro=meta["summary"],
            fields=[("meter_no", S["f_meter_no"]),
                    ("amount", S["f_amount"]), ("method", S["f_method"])],
            method="post", error=error)

    def h_tax_payment(s, meta):
        if request.method == "POST" and request.form.get("due_id"):
            due = db().execute(
                "SELECT d.*, h.holding_no FROM land_tax_dues d JOIN"
                " land_holdings h ON h.id = d.holding_id WHERE d.id=? AND"
                " d.is_paid=0", (request.form["due_id"],)).fetchone()
            if due is None:
                return no_record(meta["title"],
                                 panel_path(s["slug"], meta["slug"]))
            add_payment(s["id"], "tax", due["holding_no"], due["amount"],
                        request.form.get("method"))
            db().execute("UPDATE land_tax_dues SET is_paid=1 WHERE id=?",
                         (due["id"],))
            db().commit()
            return render_template("confirm.html", s=s, title=meta["title"],
                                   message=S["paid_ok"].format(
                                       ref=due["holding_no"],
                                       amount=due["amount"]))
        hn = (request.values.get("holding_no") or "").strip()
        if hn:
            holding = db().execute(
                "SELECT * FROM land_holdings WHERE holding_no=?",
                (hn,)).fetchone()
            if holding is None:
                return no_record(meta["title"],
                                 panel_path(s["slug"], meta["slug"]))
            dues = db().execute(
                "SELECT * FROM land_tax_dues WHERE holding_id=? AND"
                " is_paid=0 ORDER BY fiscal_year",
                (holding["id"],)).fetchall()
            return render_template("tax_pay.html", s=s, title=meta["title"],
                                   holding=holding, dues=dues)
        return render_template("lookup.html", s=s, title=meta["title"],
                               intro=meta["summary"],
                               fields=[("holding_no", S["f_holding_no"])],
                               method="get")

    def h_fee_challan(s, meta):
        fees = db().execute(
            "SELECT * FROM fee_schedules WHERE service_id=? ORDER BY id",
            (s["id"],)).fetchall()
        error = None
        if request.method == "POST":
            cat = (request.form.get("category") or "").strip().lower()
            var = (request.form.get("variant") or "").strip().lower()
            row = next((f for f in fees
                        if f["category"].lower() == cat
                        and f["variant"].lower() == var), None)
            if row is None:
                error = S["no_fee_row"]
            else:
                add_payment(s["id"], "fee",
                            f"{row['category']}/{row['variant']}",
                            row["amount"], request.form.get("method"))
                return render_template(
                    "confirm.html", s=s, title=meta["title"],
                    message=S["paid_ok"].format(
                        ref=f"{row['category']} / {row['variant']}",
                        amount=row["amount"]))
        return render_template("fee_challan.html", s=s, title=meta["title"],
                               fees=fees, error=error)

    def h_booking(s, meta):
        cal = SLOTS[s["id"]]
        offices = db().execute(
            "SELECT name FROM offices WHERE service_id=? ORDER BY id"
            " LIMIT 6", (s["id"],)).fetchall()
        error = None
        if request.method == "POST":
            d = (request.form.get("slot_date") or "").strip()
            t = (request.form.get("slot_time") or "").strip()
            office = (request.form.get("office") or "").strip()
            if d not in cal["dates"] or t not in cal["times"]:
                error = S["bad_slot"]
            else:
                cz = current_citizen()
                db().execute(
                    "INSERT INTO appointments (service_id, citizen_ref,"
                    " office, slot_date, slot_time, created_date)"
                    " VALUES (?,?,?,?,?,?)",
                    (s["id"], cz["id"] if cz else None, office, d, t, TODAY))
                db().commit()
                return render_template(
                    "confirm.html", s=s, title=meta["title"],
                    message=S["booked_ok"].format(date=d, time=t,
                                                  office=office))
        return render_template("booking.html", s=s, title=meta["title"],
                               intro=meta["summary"], offices=offices,
                               dates=cal["dates"], times=cal["times"],
                               error=error)

    def h_citizen_correction(field_name):
        def handler(s, meta):
            cz = current_citizen()
            if request.method == "POST" and request.form.get("new_value"):
                add_override("citizens", field_name, cz["id"],
                             request.form["new_value"].strip(),
                             request.form.get("document"))
                return render_template(
                    "confirm.html", s=s, title=meta["title"],
                    message=S["correction_ok"])
            docs = locker_docs()
            return render_template(
                "correction.html", s=s, title=meta["title"],
                intro=meta["summary"],
                current_value=cz[field_name] if cz else "",
                docs=docs)
        return handler

    def h_birth_correction(s, meta):
        cz = current_citizen()
        rec = db().execute(
            "SELECT * FROM civil_records WHERE citizen_ref=? AND"
            " record_type='birth'", (cz["id"],)).fetchone() if cz else None
        if rec is None:
            return render_template("static_page.html", s=s,
                                   title=meta["title"],
                                   body=S["no_linked_record"])
        if request.method == "POST" and request.form.get("new_value"):
            add_override("civil_records", "person_name", rec["id"],
                         request.form["new_value"].strip(),
                         request.form.get("document"))
            return render_template("confirm.html", s=s, title=meta["title"],
                                   message=S["correction_ok"])
        return render_template("correction.html", s=s, title=meta["title"],
                               intro=meta["summary"],
                               current_value=rec["person_name"],
                               docs=locker_docs())

    def h_death_correction(s, meta):
        return render_template("static_page.html", s=s, title=meta["title"],
                               body=S["no_linked_record"])

    def flow_handler(kind, prefix, steps):
        def handler(s, meta):
            step = int(request.form.get("_step", 0)) \
                if request.method == "POST" else 0
            carried = {}
            if request.method == "POST":
                for i in range(step):
                    for name, _label in steps[i]:
                        carried[name] = request.form.get(name, "")
                if step > 0:
                    for name, _label in steps[step - 1]:
                        carried[name] = request.form.get(name, "")
            if request.method == "POST" and step >= len(steps):
                ref = add_submission(kind, carried, prefix)
                return render_template(
                    "confirm.html", s=s, title=meta["title"],
                    message=S["submitted_ok"].format(ref=ref))
            return render_template(
                "flow.html", s=s, title=meta["title"], intro=meta["summary"],
                step=step + 1, n_steps=len(steps), fields=steps[step],
                carried=carried, next_step=step + 1)
        return handler

    HANDLERS = {
        ("national-id", "correction-status"): h_correction_status,
        ("national-id", "name-correction"): h_citizen_correction("name"),
        ("national-id", "address-correction"):
            h_citizen_correction("present_addr"),
        ("national-id", "dob-correction"): h_citizen_correction("dob"),
        ("national-id", "id-card-copy"): lambda s, meta: render_template(
            "id_card.html", s=s, title=meta["title"],
            citizen=current_citizen()),
        ("national-id", "voter-registration"): flow_handler(
            "nid-voter-registration", "VR", [[
                ("name", S["f_name"]), ("father_name", S["f_father_name"]),
                ("dob", S["f_dob"]),
                ("present_addr", S["f_present_addr"]),
                ("perm_addr", S["f_perm_addr"]),
                ("centre", S["f_centre"])]]),
        ("passport", "application-status"): h_passport_status,
        ("passport", "delivery-status"): h_delivery_status,
        ("passport", "new-application"): flow_handler(
            "passport-new", "PN",
            [[("name", S["f_name"]), ("dob", S["f_dob"]),
              ("father_name", S["f_father_name"])],
             [("present_addr", S["f_present_addr"]),
              ("perm_addr", S["f_perm_addr"])],
             [("pages", S["f_pages"]), ("validity", S["f_validity"]),
              ("delivery", S["f_delivery"])]]),
        ("passport", "reissue-application"): flow_handler(
            "passport-reissue", "PR",
            [[("passport_no", S["f_passport_no"]),
              ("reason", S["f_reason"])]]),
        ("passport", "appointment-booking"): h_booking,
        ("civil-registration", "birth-apply"): flow_handler(
            "birth-registration", "BR", [[
                ("child_name", S["f_child_name"]), ("dob", S["f_dob"]),
                ("place", S["f_place"]),
                ("father_name", S["f_father_name"]),
                ("mother_name", S["f_mother_name"])]]),
        ("civil-registration", "birth-status"): h_birth_status,
        ("civil-registration", "death-status"): h_death_status,
        ("civil-registration", "birth-correction"): h_birth_correction,
        ("civil-registration", "death-correction"): h_death_correction,
        ("land", "record-search"): None,
        ("land", "mutation-apply"): flow_handler(
            "land-mutation", "MU", [[
                ("buyer_name", S["f_buyer_name"]),
                ("buyer_id", S["f_buyer_id"]),
                ("seller_name", S["f_seller_name"]),
                ("seller_id", S["f_seller_id"]),
                ("khatian_no", S["f_khatian_no"]),
                ("plot_no", S["f_plot_no"]), ("area", S["f_area"])]]),
        ("land", "tax-payment"): h_tax_payment,
        ("land", "certified-copy"): lambda s, meta: render_template(
            "certified_copy.html", s=s, title=meta["title"],
            khatians=db().execute(
                "SELECT k.* FROM land_khatians k JOIN land_holdings h ON"
                " h.khatian_id = k.id WHERE h.owner_ref=?",
                ((current_citizen() or {"id": -1})["id"],)).fetchall()),
        ("electricity", "bill-payment"): h_bill_payment,
        ("electricity", "due-check"): h_due_check,
        ("electricity", "prepaid-recharge"): h_prepaid_recharge,
        ("electricity", "bill-history"): lambda s, meta: render_template(
            "bill_history.html", s=s, title=meta["title"],
            bills=db().execute(
                "SELECT b.*, m.consumer_no FROM bills b JOIN meters m ON"
                " m.id = b.meter_id WHERE m.account_id=? AND"
                " m.meter_type='postpaid' ORDER BY b.period DESC",
                ((current_account() or {"id": -1})["id"],)).fetchall()),
        ("exam-results", "result-lookup"): h_result_lookup,
        ("exam-results", "rescrutiny-apply"): flow_handler(
            "exam-rescrutiny", "RS", [[
                ("roll_no", S["f_roll_no"]),
                ("registration_no", S["f_registration_no"]),
                ("board", S["r_board"]), ("year", S["f_year"]),
                ("subjects", S["f_subjects"])]]),
        ("driving-licence", "licence-status"): h_licence_status,
        ("driving-licence", "fee-challan"): h_fee_challan,
        ("driving-licence", "test-booking"): h_booking,
        ("tax", "tin-registration"): flow_handler(
            "tin-registration", "TR",
            [[("name", S["f_name"]), ("father_name", S["f_father_name"]),
              ("dob", S["f_dob"]), ("address", S["f_address"])],
             [("circle", S["r_circle"]),
              ("income_source", S["f_income_source"])]]),
        ("tax", "tin-verify"): h_tin_verify,
        ("tax", "ereturn-submit"): flow_handler(
            "individual-return", "ER", [[
                ("assessment_year", S["f_assessment_year"]),
                ("tin_no", S["f_tin_no"]),
                ("total_income", S["f_total_income"]),
                ("deductions", S["f_deductions"]),
                ("tax_payable", S["f_tax_payable"]),
                ("declaration", S["f_declaration"])]]),
        ("pilgrimage", "pre-registration"): flow_handler(
            "pilgrimage-pre-registration", "PG", [[
                ("name", S["f_name"]), ("father_name", S["f_father_name"]),
                ("passport_no", S["f_passport_no"]),
                ("address", S["f_address"]), ("mobile", S["f_mobile"]),
                ("next_of_kin", S["f_next_of_kin"]),
                ("package", S["f_package"])]]),
        ("health", "vaccine-certificate"): h_vaccine_certificate,
        ("police-clearance", "clearance-apply"): flow_handler(
            "police-clearance", "PC", [[
                ("name", S["f_name"]), ("father_name", S["f_father_name"]),
                ("dob", S["f_dob"]),
                ("present_addr", S["f_present_addr"]),
                ("perm_addr", S["f_perm_addr"]),
                ("purpose", S["f_purpose"])]]),
    }

    def h_record_search(s, meta):
        args = request.args
        base = panel_path("land", "record-search")

        def sel(table, parent_col, parent_val):
            q = f"SELECT * FROM {table}"
            p = ()
            if parent_col:
                q += f" WHERE {parent_col}=?"
                p = (parent_val,)
            return db().execute(q + " ORDER BY name", p).fetchall()

        div = args.get("division")
        dist = args.get("district")
        upz = args.get("upazila")
        mouza = args.get("mouza")
        if not div:
            return render_template(
                "cascade.html", s=s, title=meta["title"],
                intro=meta["summary"], level=S["l_division"],
                links=[(r["name"], f"{base}?division={r['id']}")
                       for r in sel("geo_divisions", None, None)])
        if not dist:
            return render_template(
                "cascade.html", s=s, title=meta["title"], intro="",
                level=S["l_district"],
                links=[(r["name"], f"{base}?division={div}&district={r['id']}")
                       for r in sel("geo_districts", "division_id", div)])
        if not upz:
            return render_template(
                "cascade.html", s=s, title=meta["title"], intro="",
                level=S["l_upazila"],
                links=[(r["name"],
                        f"{base}?division={div}&district={dist}&upazila={r['id']}")
                       for r in sel("geo_upazilas", "district_id", dist)])
        if not mouza:
            return render_template(
                "cascade.html", s=s, title=meta["title"], intro="",
                level=S["l_mouza"],
                links=[(f"{r['name']} (JL {r['jl_no']})",
                        f"{base}?division={div}&district={dist}"
                        f"&upazila={upz}&mouza={r['id']}")
                       for r in sel("land_mouzas", "upazila_id", upz)])
        kn = (args.get("khatian_no") or "").strip()
        if kn:
            row = db().execute(
                "SELECT * FROM land_khatians WHERE mouza_id=? AND"
                " khatian_no=?", (mouza, kn)).fetchone()
            if row is None:
                return no_record(meta["title"], base)
            return result_page(meta["title"], [
                (S["f_khatian_no"], row["khatian_no"]),
                (S["r_khatian_type"], row["khatian_type"]),
                (S["r_owner"], row["owner_name"]),
                (S["r_father"], row["father_name"]),
                (S["f_plot_no"], row["plot_no"]),
                (S["r_land_type"], row["land_type"]),
                (S["f_area"], row["area_decimal"]),
                (S["r_share"], row["share"])], base)
        m = db().execute("SELECT * FROM land_mouzas WHERE id=?",
                         (mouza,)).fetchone()
        return render_template(
            "lookup.html", s=s, title=meta["title"],
            intro=S["in_mouza"].format(mouza=m["name"] if m else ""),
            fields=[("khatian_no", S["f_khatian_no"])], method="get",
            hidden={"division": div, "district": dist, "upazila": upz,
                    "mouza": mouza})

    HANDLERS[("land", "record-search")] = h_record_search

    return app
