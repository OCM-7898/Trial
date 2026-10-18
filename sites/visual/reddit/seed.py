import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = "2026-06-15"

SCHEMA = """
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS forums;
DROP TABLE IF EXISTS forum_rules;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS votes;
DROP TABLE IF EXISTS comment_votes;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS saved;
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS deletions;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    bio TEXT DEFAULT '',
    joined TEXT DEFAULT '',
    about TEXT DEFAULT ''
);
CREATE TABLE forums (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    created_on TEXT,
    members INTEGER,
    mod1 TEXT,
    mod2 TEXT,
    pinned_id INTEGER
);
CREATE TABLE forum_rules (
    forum_id INTEGER NOT NULL,
    pos INTEGER NOT NULL,
    rule TEXT NOT NULL
);
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    forum_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT DEFAULT '',
    score INTEGER DEFAULT 0,
    posted_on TEXT,
    locked INTEGER DEFAULT 0,
    n_images INTEGER DEFAULT 0,
    flair TEXT,
    awards INTEGER DEFAULT 0
);
CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    body TEXT NOT NULL,
    parent_id INTEGER,
    score INTEGER DEFAULT 0
);
CREATE TABLE votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    dir INTEGER NOT NULL
);
CREATE TABLE comment_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    dir INTEGER NOT NULL
);
CREATE TABLE subscriptions (
    user_id INTEGER NOT NULL,
    forum_id INTEGER NOT NULL,
    UNIQUE(user_id, forum_id)
);
CREATE TABLE saved (
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    UNIQUE(user_id, post_id)
);
CREATE TABLE deletions (
    id INTEGER PRIMARY KEY,
    kind TEXT NOT NULL,          -- 'post' | 'comment'
    item_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    title TEXT DEFAULT ''        -- post title / comment body at deletion
);
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    details TEXT DEFAULT ''
);
"""

from .strings import RULES as _RULES
RULES = _RULES["en"]


def content_path(lang="en"):
    return os.path.join(HERE, "content.json" if lang == "en"
                        else f"content_{lang}.json")


def load_content(lang="en"):
    with open(content_path(lang), encoding="utf-8") as f:
        return json.load(f)


def seed(con, lang="en"):
    content = load_content(lang)
    con.executescript(SCHEMA)
    uid = {}
    umeta = content["user_meta"]
    for i, name in enumerate(content["users"], 1):
        uid[name] = i
        pw = "password123" if name == "agent_smith" else f"pw-{name}"
        bio = ("Testing the waters. Bio under construction."
               if name == "agent_smith" else "")
        con.execute("INSERT INTO users (id, username, password, bio,"
                    " joined, about) VALUES (?,?,?,?,?,?)",
                    (i, name, pw, bio, umeta[name]["joined"],
                     umeta[name]["about"]))
    fid = {}
    fmeta = content["forum_meta"]
    for i, f in enumerate(content["forums"], 1):
        fid[f["name"]] = i
        m = fmeta[f["name"]]
        con.execute(
            "INSERT INTO forums (id, name, description, created_on,"
            " members, mod1, mod2, pinned_id) VALUES (?,?,?,?,?,?,?,?)",
            (i, f["name"], f["description"], m["created"], m["members"],
             m["moderators"][0], m["moderators"][1], m["pinned"]))
        con.executemany(
            "INSERT INTO forum_rules (forum_id, pos, rule) VALUES (?,?,?)",
            [(i, pos, rule) for pos, rule in enumerate(m["rules"], 1)])
    con.executemany(
        "INSERT INTO posts (id, forum_id, author_id, title, body, score,"
        " posted_on, locked, n_images, flair, awards)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        [(p["id"], fid[p["forum"]], uid[p["author"]], p["title"], p["body"],
          p["score"], p["posted_on"], p["locked"], p["n_images"],
          p["flair"], p["awards"]) for p in content["posts"]])
    con.executemany(
        "INSERT INTO comments (id, post_id, author_id, body, parent_id,"
        " score) VALUES (?,?,?,?,?,?)",
        [(c["id"], c["post_id"], uid[c["author"]], c["body"],
          c["parent_id"], c["score"]) for c in content["comments"]])
    smith = uid["agent_smith"]
    con.executemany(
        "INSERT INTO subscriptions (user_id, forum_id) VALUES (?,?)",
        [(smith, fid[f]) for f in content["preseed"]["subscriptions"]])
    con.executemany(
        "INSERT INTO saved (user_id, post_id) VALUES (?,?)",
        [(smith, pid) for pid in content["preseed"]["saved"]])
    con.commit()
