import math
import os
import sqlite3
import tempfile

from flask import (Flask, abort, g, jsonify, redirect, render_template,
                   request, session, url_for)

from .seed import seed
from .strings import RULES
from .strings import LANG_META, STRINGS

POST_QUERY = """
    SELECT p.*, u.username, f.name AS forum_name,
           (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS n_comments
    FROM posts p JOIN users u ON u.id = p.author_id
                 JOIN forums f ON f.id = p.forum_id
"""
PER_PAGE = 15


def create_app(db_path=None, lang="en"):
    app = Flask(__name__)
    from benchmark.harness import protect
    protect(app)
    app.secret_key = "benchmark-not-secret"
    if db_path is None:
        db_path = os.path.join(tempfile.gettempdir(),
                               f"mwa_visual_reddit_{lang}.db")
    app.config["DB_PATH"] = db_path

    META = LANG_META[lang]
    S = dict(STRINGS[lang])
    _DIGITS = str.maketrans("0123456789", META["digits"])
    app.jinja_env.filters["v2_num"] = lambda s: str(s).translate(_DIGITS)
    app.jinja_env.globals.update(S=S, lang=lang, dir=META["dir"])

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
        if table not in {"users", "forums", "posts", "comments", "votes",
                         "comment_votes", "subscriptions", "saved",
                         "reports", "forum_rules", "deletions"}:
            abort(404)
        rows = db().execute(f"SELECT * FROM {table}").fetchall()
        return jsonify([dict(r) for r in rows])

    def current_user():
        uid = session.get("uid")
        if uid is None:
            return None
        return db().execute("SELECT * FROM users WHERE id=?",
                            (uid,)).fetchone()

    def order_clause(sort):
        return {"new": "p.id DESC", "old": "p.id ASC",
                "comments": "n_comments DESC, p.id DESC"
                }.get(sort, "p.score DESC, p.id DESC")

    def all_forums():
        return db().execute("SELECT * FROM forums ORDER BY name").fetchall()

    def paginate(rows):
        page = max(1, int(request.args.get("page", 1) or 1))
        n_pages = max(1, math.ceil(len(rows) / PER_PAGE))
        page = min(page, n_pages)
        return rows[(page - 1) * PER_PAGE: page * PER_PAGE], page, n_pages

    @app.context_processor
    def inject_user():
        return {"user": current_user()}

    @app.get("/")
    def index():
        sort = request.args.get("sort", "top")
        rows = db().execute(
            POST_QUERY + " ORDER BY " + order_clause(sort)).fetchall()
        posts, page, n_pages = paginate(rows)
        return render_template("index.html", posts=posts, forums=all_forums(),
                               title=S["frontpage"], sort=sort, base_path="/",
                               page=page, n_pages=n_pages)

    @app.get("/communities")
    def communities():
        return render_template("communities.html", forums=all_forums())

    @app.get("/rules")
    def rules():
        return render_template("rules.html", rules=RULES[lang])

    @app.get("/f/<forum_name>")
    def forum(forum_name):
        f = db().execute("SELECT * FROM forums WHERE name=?",
                         (forum_name,)).fetchone()
        if f is None:
            abort(404)
        sort = request.args.get("sort", "top")
        flair = request.args.get("flair", "").strip()
        where, args = ["p.forum_id = ?"], [f["id"]]
        if flair:
            where.append("p.flair = ?")
            args.append(flair)
        rows = db().execute(
            POST_QUERY + " WHERE " + " AND ".join(where) +
            " ORDER BY " + order_clause(sort), args).fetchall()
        posts, page, n_pages = paginate(rows)
        u = current_user()
        subscribed = False
        if u:
            subscribed = db().execute(
                "SELECT 1 FROM subscriptions WHERE user_id=? AND forum_id=?",
                (u["id"], f["id"])).fetchone() is not None
        base = f"/f/{forum_name}" + (f"?flair={flair}" if flair else "")
        return render_template("index.html", posts=posts, forums=all_forums(),
                               title=f"f/{forum_name}", active_forum=f,
                               sort=sort, base_path=base,
                               page=page, n_pages=n_pages,
                               subscribed=subscribed,
                               flair=flair, n_results=len(rows))

    @app.get("/f/<forum_name>/about")
    def forum_about(forum_name):
        f = db().execute("SELECT * FROM forums WHERE name=?",
                         (forum_name,)).fetchone()
        if f is None:
            abort(404)
        frules = [r["rule"] for r in db().execute(
            "SELECT rule FROM forum_rules WHERE forum_id=? ORDER BY pos",
            (f["id"],))]
        pinned = None
        if f["pinned_id"]:
            pinned = db().execute(POST_QUERY + " WHERE p.id=?",
                                  (f["pinned_id"],)).fetchone()
        return render_template("about.html", f=f, frules=frules,
                               pinned=pinned)

    @app.post("/f/<forum_name>/subscribe")
    def subscribe(forum_name):
        u = current_user()
        f = db().execute("SELECT * FROM forums WHERE name=?",
                         (forum_name,)).fetchone()
        if u is None or f is None:
            return redirect(url_for("login", next=f"/f/{forum_name}"))
        db().execute("INSERT OR IGNORE INTO subscriptions (user_id,"
                     " forum_id) VALUES (?,?)", (u["id"], f["id"]))
        db().commit()
        return redirect(url_for("forum", forum_name=forum_name))

    @app.post("/f/<forum_name>/unsubscribe")
    def unsubscribe(forum_name):
        u = current_user()
        f = db().execute("SELECT * FROM forums WHERE name=?",
                         (forum_name,)).fetchone()
        if u is None or f is None:
            return redirect(url_for("login", next=f"/f/{forum_name}"))
        db().execute("DELETE FROM subscriptions WHERE user_id=? AND "
                     "forum_id=?", (u["id"], f["id"]))
        db().commit()
        return redirect(url_for("forum", forum_name=forum_name))

    @app.route("/create_community", methods=["GET", "POST"])
    def create_community():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/create_community"))
        error = None
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()
            if not name or not description:
                error = S["cc_required"]
            elif db().execute("SELECT 1 FROM forums WHERE name=?",
                              (name,)).fetchone():
                error = S["cc_exists"]
            else:
                db().execute("INSERT INTO forums (name, description) "
                             "VALUES (?,?)", (name, description))
                db().commit()
                return redirect(url_for("forum", forum_name=name))
        return render_template("create_community.html", error=error)

    @app.route("/settings", methods=["GET", "POST"])
    def settings():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/settings"))
        saved_ok = False
        if request.method == "POST":
            bio = request.form.get("bio", "").strip()
            db().execute("UPDATE users SET bio=? WHERE id=?", (bio, u["id"]))
            db().commit()
            saved_ok = True
            u = current_user()
        return render_template("settings.html", profile=u, saved_ok=saved_ok)

    @app.get("/search")
    def search():
        q = request.args.get("q", "").strip()
        posts, page, n_pages = [], 1, 1
        if q:
            rows = db().execute(
                POST_QUERY + " WHERE p.title LIKE ? OR p.body LIKE ? "
                "ORDER BY p.score DESC, p.id DESC",
                (f"%{q}%", f"%{q}%")).fetchall()
            posts, page, n_pages = paginate(rows)
        return render_template("search.html", posts=posts, q=q,
                               page=page, n_pages=n_pages)

    @app.get("/post/<int:post_id>")
    def post(post_id):
        p = db().execute(POST_QUERY + " WHERE p.id=?",
                         (post_id,)).fetchone()
        if p is None:
            abort(404)
        rows = db().execute(
            """SELECT c.*, u.username FROM comments c
               JOIN users u ON u.id = c.author_id
               WHERE c.post_id=? ORDER BY c.id""", (post_id,)).fetchall()
        top = [c for c in rows if c["parent_id"] is None]
        replies = {}
        for c in rows:
            if c["parent_id"] is not None:
                replies.setdefault(c["parent_id"], []).append(c)
        u = current_user()
        my_vote = None
        is_saved = False
        if u:
            v = db().execute("SELECT dir FROM votes WHERE post_id=? AND "
                             "user_id=?", (post_id, u["id"])).fetchone()
            my_vote = v["dir"] if v else None
            is_saved = db().execute(
                "SELECT 1 FROM saved WHERE user_id=? AND post_id=?",
                (u["id"], post_id)).fetchone() is not None
        return render_template("post.html", p=p, comments=top,
                               replies=replies, my_vote=my_vote,
                               is_saved=is_saved)

    @app.post("/post/<int:post_id>/vote")
    def vote(post_id):
        u = current_user()
        p = db().execute("SELECT * FROM posts WHERE id=?",
                         (post_id,)).fetchone()
        if p is None:
            abort(404)
        if u is None:
            return redirect(url_for("login", next=f"/post/{post_id}"))
        if p["locked"]:
            return redirect(url_for("post", post_id=post_id))
        direction = 1 if request.form.get("dir") == "up" else -1
        existing = db().execute(
            "SELECT * FROM votes WHERE post_id=? AND user_id=?",
            (post_id, u["id"])).fetchone()
        if existing is None:
            db().execute("INSERT INTO votes (post_id, user_id, dir) "
                         "VALUES (?,?,?)", (post_id, u["id"], direction))
            db().execute("UPDATE posts SET score = score + ? WHERE id=?",
                         (direction, post_id))
        elif existing["dir"] != direction:
            db().execute("UPDATE votes SET dir=? WHERE id=?",
                         (direction, existing["id"]))
            db().execute("UPDATE posts SET score = score + ? WHERE id=?",
                         (2 * direction, post_id))
        db().commit()
        return redirect(url_for("post", post_id=post_id))

    @app.post("/post/<int:post_id>/save")
    def save_toggle(post_id):
        u = current_user()
        if u is None:
            return redirect(url_for("login", next=f"/post/{post_id}"))
        if db().execute("SELECT 1 FROM saved WHERE user_id=? AND post_id=?",
                        (u["id"], post_id)).fetchone():
            db().execute("DELETE FROM saved WHERE user_id=? AND post_id=?",
                         (u["id"], post_id))
        else:
            db().execute("INSERT INTO saved (user_id, post_id) VALUES "
                         "(?,?)", (u["id"], post_id))
        db().commit()
        return redirect(url_for("post", post_id=post_id))

    @app.get("/saved")
    def saved_posts():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/saved"))
        rows = db().execute(
            POST_QUERY + " JOIN saved s ON s.post_id = p.id "
            "WHERE s.user_id=? ORDER BY s.rowid", (u["id"],)).fetchall()
        return render_template("saved.html", posts=rows)

    @app.post("/saved/remove/<int:post_id>")
    def saved_remove(post_id):
        u = current_user()
        if u is None:
            return redirect(url_for("login"))
        db().execute("DELETE FROM saved WHERE user_id=? AND post_id=?",
                     (u["id"], post_id))
        db().commit()
        return redirect(url_for("saved_posts"))

    @app.route("/post/<int:post_id>/report", methods=["GET", "POST"])
    def report_post(post_id):
        u = current_user()
        if u is None:
            return redirect(url_for("login", next=f"/post/{post_id}/report"))
        p = db().execute(POST_QUERY + " WHERE p.id=?",
                         (post_id,)).fetchone()
        if p is None:
            abort(404)
        sent = False
        if request.method == "POST":
            reason = request.form.get("reason", "").strip()
            details = request.form.get("details", "").strip()
            if reason:
                db().execute(
                    "INSERT INTO reports (post_id, user_id, reason,"
                    " details) VALUES (?,?,?,?)",
                    (post_id, u["id"], reason, details))
                db().commit()
                sent = True
        return render_template("report.html", p=p, sent=sent)

    @app.post("/post/<int:post_id>/comment")
    def add_comment(post_id):
        u = current_user()
        p = db().execute("SELECT * FROM posts WHERE id=?",
                         (post_id,)).fetchone()
        if p is None:
            abort(404)
        if u is None:
            return redirect(url_for("login", next=f"/post/{post_id}"))
        body = request.form.get("body", "").strip()
        if body and not p["locked"]:
            db().execute(
                "INSERT INTO comments (post_id, author_id, body, parent_id)"
                " VALUES (?,?,?,NULL)", (post_id, u["id"], body))
            db().commit()
        return redirect(url_for("post", post_id=post_id))

    @app.post("/comment/<int:comment_id>/reply")
    def reply_comment(comment_id):
        u = current_user()
        if u is None:
            return redirect(url_for("login"))
        parent = db().execute(
            """SELECT c.*, p.locked FROM comments c
               JOIN posts p ON p.id = c.post_id WHERE c.id=?""",
            (comment_id,)).fetchone()
        if parent is None:
            abort(404)
        body = request.form.get("body", "").strip()
        if body and not parent["locked"]:
            db().execute(
                "INSERT INTO comments (post_id, author_id, body, parent_id)"
                " VALUES (?,?,?,?)",
                (parent["post_id"], u["id"], body, comment_id))
            db().commit()
        return redirect(url_for("post", post_id=parent["post_id"]))

    @app.post("/comment/<int:comment_id>/vote")
    def vote_comment(comment_id):
        u = current_user()
        c = db().execute(
            """SELECT c.*, p.locked FROM comments c
               JOIN posts p ON p.id = c.post_id WHERE c.id=?""",
            (comment_id,)).fetchone()
        if c is None:
            abort(404)
        if u is None:
            return redirect(url_for("login", next=f"/post/{c['post_id']}"))
        existing = db().execute(
            "SELECT 1 FROM comment_votes WHERE comment_id=? AND user_id=?",
            (comment_id, u["id"])).fetchone()
        if existing is None and not c["locked"]:
            db().execute("INSERT INTO comment_votes (comment_id, user_id,"
                         " dir) VALUES (?,?,1)", (comment_id, u["id"]))
            db().execute("UPDATE comments SET score = score + 1 WHERE "
                         "id=?", (comment_id,))
            db().commit()
        return redirect(url_for("post", post_id=c["post_id"]))

    @app.route("/comment/<int:comment_id>/delete", methods=["GET", "POST"])
    def delete_comment(comment_id):
        u = current_user()
        if u is None:
            return redirect(url_for("login"))
        c = db().execute(
            """SELECT c.*, p.title AS post_title FROM comments c
               JOIN posts p ON p.id = c.post_id WHERE c.id=?""",
            (comment_id,)).fetchone()
        if c is None:
            abort(404)
        if c["author_id"] != u["id"]:
            return redirect(url_for("post", post_id=c["post_id"]))
        if request.method == "GET":
            return render_template("confirm_delete.html", kind="comment",
                                   item=c, q=S["confirm_delete_comment"],
                                   action=f"/comment/{comment_id}/delete")
        db().execute("DELETE FROM comments WHERE parent_id=?", (comment_id,))
        db().execute("DELETE FROM comments WHERE id=?", (comment_id,))
        db().commit()
        return redirect(url_for("post", post_id=c["post_id"]))

    @app.route("/comment/<int:comment_id>/edit", methods=["GET", "POST"])
    def edit_comment(comment_id):
        u = current_user()
        if u is None:
            return redirect(url_for("login"))
        c = db().execute(
            """SELECT c.*, p.title AS post_title FROM comments c
               JOIN posts p ON p.id = c.post_id WHERE c.id=?""",
            (comment_id,)).fetchone()
        if c is None:
            abort(404)
        if c["author_id"] != u["id"]:
            return redirect(url_for("post", post_id=c["post_id"]))
        if request.method == "POST":
            body = request.form.get("body", "").strip()
            if body:
                db().execute("UPDATE comments SET body=? WHERE id=?",
                             (body, comment_id))
                db().commit()
            return redirect(url_for("post", post_id=c["post_id"]))
        return render_template("edit_comment.html", c=c)

    @app.route("/post/<int:post_id>/delete", methods=["GET", "POST"])
    def delete_post(post_id):
        u = current_user()
        if u is None:
            return redirect(url_for("login"))
        p = db().execute("SELECT * FROM posts WHERE id=?",
                         (post_id,)).fetchone()
        if p is None:
            abort(404)
        if p["author_id"] != u["id"]:
            return redirect(url_for("post", post_id=post_id))
        if request.method == "GET":
            return render_template("confirm_delete.html", kind="post",
                                   item=p, q=S["confirm_delete_post"],
                                   action=f"/post/{post_id}/delete")
        db().execute("INSERT INTO deletions (kind, item_id, author_id, "
                     "title) VALUES ('post', ?, ?, ?)",
                     (post_id, p["author_id"], p["title"]))
        db().execute("DELETE FROM votes WHERE post_id=?", (post_id,))
        db().execute("DELETE FROM comments WHERE post_id=?", (post_id,))
        db().execute("DELETE FROM saved WHERE post_id=?", (post_id,))
        db().execute("DELETE FROM posts WHERE id=?", (post_id,))
        db().commit()
        return redirect(url_for("profile", username=u["username"]))

    @app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
    def edit_post(post_id):
        u = current_user()
        if u is None:
            return redirect(url_for("login", next=f"/post/{post_id}"))
        p = db().execute("SELECT * FROM posts WHERE id=?",
                         (post_id,)).fetchone()
        if p is None:
            abort(404)
        if p["author_id"] != u["id"]:
            return redirect(url_for("post", post_id=post_id))
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            body = request.form.get("body", "").strip()
            if title:
                db().execute("UPDATE posts SET title=?, body=? WHERE id=?",
                             (title, body, post_id))
                db().commit()
            return redirect(url_for("post", post_id=post_id))
        return render_template("edit_post.html", p=p)

    @app.route("/submit", methods=["GET", "POST"])
    def submit():
        u = current_user()
        if u is None:
            return redirect(url_for("login", next="/submit"))
        error = None
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            body = request.form.get("body", "").strip()
            f = db().execute("SELECT * FROM forums WHERE name=?",
                             (request.form.get("forum", ""),)).fetchone()
            if not title or f is None:
                error = S["submit_required"]
            else:
                cur = db().execute(
                    "INSERT INTO posts (forum_id, author_id, title, body,"
                    " score, posted_on) VALUES (?,?,?,?,0,?)",
                    (f["id"], u["id"], title, body, "2026-06-15"))
                db().commit()
                return redirect(url_for("post", post_id=cur.lastrowid))
        return render_template("submit.html", forums=all_forums(),
                               error=error,
                               preselect=request.args.get("forum", ""))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            u = db().execute(
                "SELECT * FROM users WHERE username=? AND password=?",
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

    @app.get("/u/<username>")
    def profile(username):
        u = db().execute("SELECT * FROM users WHERE username=?",
                         (username,)).fetchone()
        if u is None:
            abort(404)
        rows = db().execute(POST_QUERY + " WHERE p.author_id=? ORDER BY "
                            "p.id DESC", (u["id"],)).fetchall()
        posts, page, n_pages = paginate(rows)
        comments = db().execute(
            """SELECT c.*, p.title AS post_title FROM comments c
               JOIN posts p ON p.id = c.post_id
               WHERE c.author_id=? ORDER BY c.id DESC""",
            (u["id"],)).fetchall()
        karma = sum(p["score"] for p in rows)
        ckarma = sum(c["score"] for c in comments)
        top_comments = sorted(comments,
                              key=lambda c: (-c["score"], c["id"]))[:20]
        return render_template("profile.html", profile_user=u, posts=posts,
                               comments=top_comments,
                               n_all_comments=len(comments), karma=karma,
                               ckarma=ckarma, page=page, n_pages=n_pages)

    return app
