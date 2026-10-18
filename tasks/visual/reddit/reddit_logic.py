import json
import re as _re
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "sites", "visual"))
from reddit_i18n import I18N, LIT
from build_reddit_content import load_pack

CRED = {l: p["cred"] for l, p in I18N.items()}
NA_SUFFIX = {l: p["na"] for l, p in I18N.items()}

LOGIN = ["goto /login", "fill 0 username=agent_smith; password=password123"]


def load_content(lang="en"):
    p = os.path.join(ROOT, "sites", "visual", "reddit",
                     "content.json" if lang == "en" else f"content_{lang}.json")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def build(lang="en"):
    C = load_content(lang)
    posts = C["posts"]
    comments = C["comments"]
    by_id = {p["id"]: p for p in posts}
    forum_id = {f["name"]: i + 1 for i, f in enumerate(C["forums"])}
    cred = CRED[lang]
    na = NA_SUFFIX[lang]
    TPL = I18N[lang]
    L = LIT[lang]
    P = load_pack(lang)
    P_EN = load_pack("en")

    def flair_l(forum, en_name):
        return P["FLAIRS"][forum][P_EN["FLAIRS"][forum].index(en_name)]

    witt_pre, witt_suf = P["WITT_ID"].split("{name}")

    def I(key, **kw):
        return TPL[key].format(cred=cred, na=na, **kw)

    assert max(p["id"] for p in posts) == 2000
    def clean_title(start):
        return next(p for p in unlocked[start:]
                    if sum(1 for q in posts
                           if q["title"].startswith(p["title"])) == 1)
    own_posts = sorted(p["id"] for p in posts
                       if p["author"] == "agent_smith")
    own_a, own_b = own_posts
    own_cids = sorted(c["id"] for c in comments
                      if c["author"] == "agent_smith")

    n_comments = {}
    for c in comments:
        n_comments[c["post_id"]] = n_comments.get(c["post_id"], 0) + 1

    def tops(pid):
        return [c for c in comments
                if c["post_id"] == pid and c["parent_id"] is None]

    def cvote_form(pid, cid):
        pos = [c["id"] for c in tops(pid)].index(cid)
        return 4 + 2 * pos

    def creply_form(pid, cid):
        return cvote_form(pid, cid) + 1

    def feed(forum=None, sort="top"):
        pool = [p for p in posts if forum is None or p["forum"] == forum]
        key = {"top": lambda p: (-p["score"], -p["id"]),
               "new": lambda p: -p["id"],
               "old": lambda p: p["id"],
               "comments": lambda p: (-n_comments.get(p["id"], 0),
                                      -p["id"])}[sort]
        return sorted(pool, key=key)

    def uniq_max(pool, val):
        pool = list(pool)
        assert pool
        best = max(val(p) for p in pool)
        hits = [p for p in pool if val(p) == best]
        assert len(hits) == 1, [h["id"] for h in hits]
        return hits[0]

    T = []

    def add(diff, intent, eval_, solution, start="/", steps=30, tags=None):
        for ev in eval_:
            if "any_of" in ev:
                ev["any_of"] = list(dict.fromkeys(ev["any_of"]))
        T.append({"id": f"visualreddit-{len(T) + 1:03d}", "site": "reddit",
                  "difficulty": diff, "intent": intent, "start_path": start,
                  "eval": eval_, "solution": solution, "max_steps": steps})
        if tags:
            T[-1]["tags"] = list(tags)

    locked_ids = [p["id"] for p in posts if p["locked"]]
    unlocked = [p for p in posts if not p["locked"]
                and p["author"] != "agent_smith"]

    add("hard",
        I("a1", t=L['a1_title'], b=L['a1_body'], new=L['a1_new']),
        [{"type": "db_record_exists", "table": "posts",
          "match": {"title": L["a1_new"], "body": L["a1_body"],
                    "forum_id": forum_id["technology"],
                    "author_id": 1}},
         {"type": "db_record_absent", "table": "posts",
          "match": {"title": L["a1_title"]}}],
        LOGIN + ["goto /submit",
                 f"fill 0 forum=technology; title={L['a1_title']}; "
                 f"body={L['a1_body']}",
                 "goto /post/2001/edit",
                 f"fill 0 title={L['a1_new']}"])

    add("hard",
        I("a2", t=L['a2_title'], b=L['a2_body']),
        [{"type": "db_record_exists", "table": "deletions",
          "match": {"kind": "post", "title": L["a2_title"],
                    "author_id": 1}},
         {"type": "db_record_absent", "table": "posts",
          "match": {"title": L["a2_title"]}}],
        LOGIN + ["goto /submit",
                 f"fill 0 forum=movies; title={L['a2_title']}; "
                 f"body={L['a2_body']}",
                 "goto /post/2001/delete", "fill 0"])

    add("hard",
        I("a3", t=L['a3_title'], b=L['a3_body'], c=L['a3_comment']),
        [{"type": "db_record_exists", "table": "posts",
          "match": {"title": L["a3_title"], "body": L["a3_body"],
                    "forum_id": forum_id["askanything"], "author_id": 1}},
         {"type": "db_record_exists", "table": "comments",
          "match": {"post_id": 2001, "author_id": 1,
                    "body": L["a3_comment"]}}],
        LOGIN + ["goto /submit",
                 f"fill 0 forum=askanything; title={L['a3_title']}; "
                 f"body={L['a3_body']}",
                 f"fill 3 body={L['a3_comment']}"])

    add("hard",
        I("a4", name=L['a4_name'], desc=L['a4_desc'], t=L['a4_title'], b=L['a4_body']),
        [{"type": "db_record_exists", "table": "forums",
          "match": {"name": L["a4_name"], "description": L["a4_desc"]}},
         {"type": "db_record_exists", "table": "posts",
          "match": {"title": L["a4_title"], "body": L["a4_body"],
                    "forum_id": 13, "author_id": 1}}],
        LOGIN + ["goto /create_community",
                 f"fill 0 name={L['a4_name']}; description={L['a4_desc']}",
                 "goto /submit",
                 f"fill 0 forum={L['a4_name']}; title={L['a4_title']}; "
                 f"body={L['a4_body']}"])

    l7 = by_id[feed("technology", "top")[0]["id"]]
    add("hard",
        I("a5", re=L['re_prefix'], b=L['a5_body']),
        [{"type": "db_record_exists", "table": "posts",
          "match": {"title": "%" + L["re_prefix"]
                    + _re.sub(r" \(\d+\)$", "", l7["title"]) + "%",
                    "body": L["a5_body"],
                    "forum_id": forum_id["technology"], "author_id": 1}}],
        LOGIN + [f"goto /post/{l7['id']}", "goto /submit",
                 f"fill 0 forum=technology; title={L['re_prefix']}"
                 f"{l7['title']}; body={L['a5_body']}"])

    add("hard",
        I("a6", t=L['a6_title'], b=L['a6_body']),
        [{"type": "db_record_exists", "table": "posts",
          "match": {"title": L["a6_title"], "body": L["a6_body"],
                    "forum_id": forum_id["personalfinance"],
                    "author_id": 1}},
         {"type": "db_record_exists", "table": "saved",
          "match": {"user_id": 1, "post_id": 2001}}],
        LOGIN + ["goto /submit",
                 f"fill 0 forum=personalfinance; title={L['a6_title']}; "
                 f"body={L['a6_body']}",
                 "fill 2"])

    b3 = unlocked[30]
    add("hard",
        I("b3", id=b3['id']),
        [{"type": "db_record_exists", "table": "votes",
          "match": {"post_id": b3["id"], "user_id": 1, "dir": -1}},
         {"type": "db_field_equals", "table": "posts",
          "match": {"id": b3["id"]}, "field": "score",
          "value": b3["score"] - 1}],
        LOGIN + [f"goto /post/{b3['id']}", "fill 0", "fill 1"])

    b4 = next(p for p in unlocked if len(tops(p["id"])) >= 4)
    b4top = uniq_max(tops(b4["id"]), lambda c: c["score"])
    add("hard",
        I("b4", id=b4['id']),
        [{"type": "db_record_exists", "table": "comment_votes",
          "match": {"comment_id": b4top["id"], "user_id": 1}}],
        LOGIN + [f"goto /post/{b4['id']}",
                 f"fill {cvote_form(b4['id'], b4top['id'])}"])

    tech2 = feed("technology", "top")[1]
    assert not tech2["locked"]
    add("hard",
        I("b5"),
        [{"type": "db_record_exists", "table": "votes",
          "match": {"post_id": tech2["id"], "user_id": 1, "dir": -1}}],
        LOGIN + [f"goto /post/{tech2['id']}", "fill 1"])

    b6 = clean_title(40)
    add("hard",
        I("b6", title=b6['title']),
        [{"type": "db_record_exists", "table": "votes",
          "match": {"post_id": b6["id"], "user_id": 1, "dir": 1}}],
        LOGIN + [f"goto /post/{b6['id']}", "fill 0"])

    b7 = [unlocked[50], unlocked[60], unlocked[70]]
    add("hard",
        I("b7", a=b7[0]['id'], b=b7[1]['id'], c=b7[2]['id']),
        [{"type": "db_record_exists", "table": "votes",
          "match": {"post_id": p["id"], "user_id": 1, "dir": 1}}
         for p in b7],
        LOGIN + sum([[f"goto /post/{p['id']}", "fill 0"] for p in b7], []))

    c1 = unlocked[80]
    add("hard",
        I("c1", id=c1['id'], c=L['c1']),
        [{"type": "db_record_exists", "table": "comments",
          "match": {"post_id": c1["id"], "author_id": 1,
                    "body": L["c1"]}}],
        LOGIN + [f"goto /post/{c1['id']}",
                 f"fill 3 body={L['c1']}"])

    c2 = next(p for p in unlocked if len(tops(p["id"])) >= 3
              and len({t["author"] for t in tops(p["id"])})
              == len(tops(p["id"])))
    c2target = tops(c2["id"])[1]
    add("hard",
        I("c2", id=c2['id'], u=c2target['author'], c=L['c2']),
        [{"type": "db_record_exists", "table": "comments",
          "match": {"post_id": c2["id"], "author_id": 1,
                    "parent_id": c2target["id"],
                    "body": L["c2"]}}],
        LOGIN + [f"goto /post/{c2['id']}",
                 f"fill {creply_form(c2['id'], c2target['id'])} "
                 f"body={L['c2']}"])

    c3 = next(p for p in unlocked[5:] if len(tops(p["id"])) >= 5)
    c3top = uniq_max(tops(c3["id"]), lambda c: c["score"])
    add("hard",
        I("c3", id=c3['id'], c=L['c3']),
        [{"type": "db_record_exists", "table": "comments",
          "match": {"parent_id": c3top["id"], "author_id": 1,
                    "body": L["c3"]}}],
        LOGIN + [f"goto /post/{c3['id']}",
                 f"fill {creply_form(c3['id'], c3top['id'])} "
                 f"body={L['c3']}"])

    c5 = unlocked[90]
    c5_n_top = len(tops(c5["id"]))
    add("hard",
        I("c5", id=c5['id'], c1=L['c5a'], c2=L['c5b']),
        [{"type": "db_record_exists", "table": "comments",
          "match": {"post_id": c5["id"], "author_id": 1,
                    "body": L["c5a"]}},
         {"type": "db_reply_to", "author_id": 1, "post_id": c5["id"],
          "parent_body": L["c5a"],
          "child_body": L["c5b"]}],
        LOGIN + [f"goto /post/{c5['id']}",
                 f"fill 3 body={L['c5a']}",
                 f"fill {5 + 2 * c5_n_top} body={L['c5b']}"])

    witt = next(p for p in posts if p["forum"] == "whatisthisthing"
                and not p["locked"])
    witt_c = min(tops(witt["id"]), key=lambda c: c["id"])
    assert witt_c["body"].startswith(witt_pre)
    add("hard",
        I("c6", id=witt['id'], c=L['c6']),
        [{"type": "db_record_exists", "table": "comments",
          "match": {"parent_id": witt_c["id"], "author_id": 1,
                    "body": L["c6"]}}],
        LOGIN + [f"goto /post/{witt['id']}",
                 f"fill {creply_form(witt['id'], witt_c['id'])} "
                 f"body={L['c6']}"])

    busy_ask = feed("askanything", "comments")[0]
    assert not busy_ask["locked"]
    n_top_busy = len(tops(busy_ask["id"]))
    assert feed("askanything", "comments")[1]["id"] != busy_ask["id"]
    add("hard",
        I("c7", c=L['c7']),
        [{"type": "db_record_exists", "table": "comments",
          "match": {"post_id": busy_ask["id"], "author_id": 1,
                    "body": L["c7"]}}],
        LOGIN + [f"goto /post/{busy_ask['id']}",
                 f"fill 3 body={L['c7']}"])

    add("hard",
        I("d1"),
        [{"type": "db_record_absent", "table": "subscriptions",
          "match": {"user_id": 1, "forum_id": forum_id["carspotting"]}},
         {"type": "db_record_exists", "table": "subscriptions",
          "match": {"user_id": 1, "forum_id": forum_id["cooking"]}},
         {"type": "db_record_exists", "table": "subscriptions",
          "match": {"user_id": 1, "forum_id": forum_id["technology"]}}],
        LOGIN + ["goto /f/carspotting", "fill 0"])

    add("hard",
        I("d2"),
        [{"type": "db_record_exists", "table": "subscriptions",
          "match": {"user_id": 1, "forum_id": forum_id["cooking"]}},
         {"type": "db_record_absent", "table": "subscriptions",
          "match": {"user_id": 1, "forum_id": forum_id["technology"]}},
         {"type": "db_record_absent", "table": "subscriptions",
          "match": {"user_id": 1, "forum_id": forum_id["carspotting"]}}],
        LOGIN + ["goto /f/technology", "fill 0", "goto /f/carspotting",
                 "fill 0"])

    d4 = [unlocked[110]["id"], unlocked[120]["id"], unlocked[130]["id"]]
    add("hard",
        I("d4", a=d4[0], b=d4[1], c=d4[2]),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"user_id": 1, "post_id": i}} for i in d4],
        LOGIN + sum([[f"goto /post/{i}", "fill 2"] for i in d4], []))

    pre = C["preseed"]["saved"]
    pre_forums = [by_id[i]["forum"] for i in pre]
    target_forum = next(f for f in pre_forums if pre_forums.count(f) == 1)
    d5_pid = pre[pre_forums.index(target_forum)]
    d5_row = pre.index(d5_pid)
    add("hard",
        I("d5", forum=target_forum),
        [{"type": "db_record_absent", "table": "saved",
          "match": {"user_id": 1, "post_id": d5_pid}}] +
        [{"type": "db_record_exists", "table": "saved",
          "match": {"user_id": 1, "post_id": i}}
         for i in pre if i != d5_pid],
        LOGIN + ["goto /saved", f"fill {d5_row}"])

    d6_keep = unlocked[140]["id"]
    add("hard",
        I("d6", id=d6_keep),
        [{"type": "db_record_absent", "table": "saved",
          "match": {"user_id": 1, "post_id": i}} for i in pre] +
        [{"type": "db_record_exists", "table": "saved",
          "match": {"user_id": 1, "post_id": d6_keep}}],
        LOGIN + ["goto /saved", "fill 0", "fill 0", "fill 0", "fill 0",
                 f"goto /post/{d6_keep}", "fill 2"])

    d8a, d8b = unlocked[160]["id"], unlocked[170]["id"]
    add("hard",
        I("d8", a=d8a, b=d8b),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"user_id": 1, "post_id": d8a}},
         {"type": "db_record_exists", "table": "saved",
          "match": {"user_id": 1, "post_id": d8b}},
         {"type": "db_record_absent", "table": "subscriptions",
          "match": {"user_id": 1, "forum_id": forum_id["technology"]}}],
        LOGIN + [f"goto /post/{d8a}", "fill 2", f"goto /post/{d8b}",
                 "fill 2", "goto /f/technology", "fill 0"])

    e1 = uniq_max((by_id[i] for i in pre),
                  lambda p: n_comments.get(p["id"], 0))
    assert not e1["locked"]
    add("hard",
        I("e1"),
        [{"type": "db_record_exists", "table": "votes",
          "match": {"post_id": e1["id"], "user_id": 1, "dir": 1}}],
        LOGIN + [f"goto /post/{e1['id']}", "fill 0"])

    from collections import Counter
    author_posts = Counter(p["author"] for p in posts)
    e2u = min((u for u in set(p["author"] for p in posts)
               if any(p["author"] == u and p["n_images"] for p in posts)),
              key=lambda u: (author_posts[u], u))
    assert author_posts[e2u] <= 30
    e2n = sum(1 for p in posts if p["author"] == e2u and p["n_images"])
    add("hard",
        I("e2", u=e2u),
        [{"type": "answer_match", "answer": str(e2n)}],
        [f"goto /u/{e2u}", f"stop {e2n}"])

    locked_per_forum = Counter(p["forum"] for p in posts if p["locked"])
    e3f, e3n = max(sorted(locked_per_forum.items()),
                   key=lambda kv: kv[1])
    add("hard",
        I("e3", forum=e3f),
        [{"type": "answer_match", "answer": str(e3n)}],
        [f"goto /f/{e3f}?sort=new", f"stop {e3n}"],
        tags=["memory"])

    car5 = feed("carspotting", "top")[:5]
    e4 = uniq_max(car5, lambda p: n_comments.get(p["id"], 0))
    assert not e4["locked"]
    add("hard",
        I("e4"),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"user_id": 1, "post_id": e4["id"]}}],
        LOGIN + [f"goto /post/{e4['id']}", "fill 2"])

    bifl_top = feed("buyitforlife", "top")[0]
    assert not bifl_top["locked"]
    e5c = uniq_max(tops(bifl_top["id"]), lambda c: c["score"])
    add("hard",
        I("e5"),
        [{"type": "db_record_exists", "table": "comment_votes",
          "match": {"comment_id": e5c["id"], "user_id": 1}}],
        LOGIN + [f"goto /post/{bifl_top['id']}",
                 f"fill {cvote_form(bifl_top['id'], e5c['id'])}"])

    witt2 = next(p for p in posts if p["forum"] == "whatisthisthing"
                 and not p["locked"] and p["id"] != witt["id"])
    witt2_c = min(tops(witt2["id"]), key=lambda c: c["id"])
    witt2_name = witt2_c["body"][len(witt_pre):len(witt2_c["body"]) - len(witt_suf)]
    add("hard",
        I("e6", id=witt2['id']),
        [{"type": "answer_match", "answer": witt2_name}],
        [f"goto /post/{witt2['id']}", f"stop {witt2_name}"])

    e8pool = [p for p in posts if p["author"] == e2u and not p["locked"]]
    e8 = uniq_max(e8pool, lambda p: p["score"])
    add("hard",
        I("e8", u=e2u),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"user_id": 1, "post_id": e8["id"]}}],
        LOGIN + [f"goto /u/{e2u}", f"goto /post/{e8['id']}", "fill 2"])

    def no_collide(*vals):
        ss = [str(v) for v in vals]
        return all(a not in b for a in ss for b in ss if a is not b)

    f1 = next(p for p in unlocked[180:]
              if no_collide(p["score"], n_comments.get(p["id"], 0)))
    add("hard",
        I("f1", id=f1['id']),
        [{"type": "answer_match", "answer": str(f1["score"])},
         {"type": "answer_match",
          "answer": str(n_comments.get(f1["id"], 0))}],
        [f"goto /post/{f1['id']}",
         f"stop score {f1['score']}, {n_comments.get(f1['id'], 0)} "
         f"comments"])

    fa = unlocked[200]
    fb = next(p for p in unlocked[210:] if p["score"] != fa["score"]
              and no_collide(
                  (fa if fa["score"] > p["score"] else p)["id"],
                  abs(fa["score"] - p["score"])))
    hi = fa if fa["score"] > fb["score"] else fb
    diff = abs(fa["score"] - fb["score"])
    add("hard",
        I("f2", a=fa['id'], b=fb['id']),
        [{"type": "answer_match", "answer": str(hi["id"]),
          "none_of": [str(fb["id"] if hi is fa else fa["id"])]},
         {"type": "answer_match", "answer": str(diff)}],
        [f"goto /post/{fa['id']}", f"goto /post/{fb['id']}",
         f"stop {hi['id']} is higher by {diff}"])

    f4u = "gearhead_gia"
    f4k = sum(p["score"] for p in posts if p["author"] == f4u)
    add("hard",
        I("f4", u=f4u),
        [{"type": "answer_match",
          "any_of": [f"{f4k:,}", str(f4k)]}],
        [f"goto /u/{f4u}", f"stop {f4k}"])

    f5 = clean_title(220)
    add("hard",
        I("f5", title=f5['title']),
        [{"type": "answer_match", "answer": str(f5["score"])},
         {"type": "answer_match", "answer": f5["forum"]}],
        [f"goto /post/{f5['id']}",
         f"stop {f5['score']}, f/{f5['forum']}"])

    f6 = next(p for p in unlocked if p["forum"] == "projectcars"
              and p["n_images"] == 3
              and "3" not in p["posted_on"])
    add("hard",
        I("f6", id=f6['id']),
        [{"type": "answer_match", "answer": str(f6["n_images"])},
         {"type": "answer_match", "answer": f6["posted_on"]}],
        [f"goto /post/{f6['id']}",
         f"stop {f6['n_images']} photos, posted {f6['posted_on']}"])

    n_hg = sum(1 for p in posts if p["forum"] == "homegadgets")
    add("hard",
        I("g1"),
        [{"type": "answer_match", "answer": str(n_hg)}],
        ["goto /f/homegadgets", f"stop {n_hg}"])

    n_ask = sum(1 for p in posts if p["forum"] == "askanything")
    pages_ask = -(-n_ask // 15)
    add("hard",
        I("g2"),
        [{"type": "answer_match", "answer": str(pages_ask)}],
        ["goto /f/askanything", f"stop {pages_ask}"])

    ga, gb = unlocked[230], unlocked[240]
    gsum = ga["score"] + gb["score"]
    add("hard",
        I("g3", a=ga['id'], b=gb['id']),
        [{"type": "answer_match", "any_of": [f"{gsum:,}", str(gsum)]}],
        [f"goto /post/{ga['id']}", f"goto /post/{gb['id']}",
         f"stop {gsum}"])

    gc, gd = unlocked[250], unlocked[260]
    csum = n_comments.get(gc["id"], 0) + n_comments.get(gd["id"], 0)
    add("hard",
        I("g4", a=gc['id'], b=gd['id']),
        [{"type": "answer_match", "answer": str(csum)}],
        [f"goto /post/{gc['id']}", f"goto /post/{gd['id']}",
         f"stop {csum}"])

    h1 = unlocked[270]
    add("hard",
        I("h1", id=h1['id'], d=L['h1_details']),
        [{"type": "db_record_exists", "table": "reports",
          "match": {"post_id": h1["id"], "user_id": 1, "reason": "Spam",
                    "details": L["h1_details"]}}],
        LOGIN + [f"goto /post/{h1['id']}/report",
                 f"fill 0 reason=Spam; details={L['h1_details']}"])

    h3 = unlocked[280]
    add("hard",
        I("h3", id=h3['id'], d=L['h3_details']),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"user_id": 1, "post_id": h3["id"]}},
         {"type": "db_record_exists", "table": "reports",
          "match": {"post_id": h3["id"], "user_id": 1,
                    "reason": "Misinformation",
                    "details": L["h3_details"]}}],
        LOGIN + [f"goto /post/{h3['id']}", "fill 2",
                 f"goto /post/{h3['id']}/report",
                 f"fill 0 reason=Misinformation; details={L['h3_details']}"])

    add("hard",
        I("i1", bio=L['i1_bio']),
        [{"type": "db_field_equals", "table": "users", "match": {"id": 1},
          "field": "bio",
          "value": L["i1_bio"]}],
        LOGIN + ["goto /settings",
                 f"fill 0 bio={L['i1_bio']}"])

    add("hard",
        I("i2"),
        [{"type": "db_field_equals", "table": "users", "match": {"id": 1},
          "field": "bio", "value": ""}],
        LOGIN + ["goto /settings", "fill 0 bio="])

    j1 = by_id[locked_ids[0]]
    add("hard",
        I("j1", c=L['j1'], id=j1['id']),
        [{"type": "answer_match", "answer": "N/A"},
         {"type": "db_record_absent", "table": "comments",
          "match": {"post_id": j1["id"], "author_id": 1}}],
        LOGIN + [f"goto /post/{j1['id']}", "stop N/A"])

    j2 = by_id[locked_ids[1]]
    add("hard",
        I("j2", id=j2['id']),
        [{"type": "answer_match", "answer": "N/A"},
         {"type": "db_record_absent", "table": "votes",
          "match": {"post_id": j2["id"], "user_id": 1}}],
        LOGIN + [f"goto /post/{j2['id']}", "stop N/A"])

    add("hard",
        I("j3"),
        [{"type": "answer_match", "answer": "N/A"}],
        ["goto /post/2001", "stop N/A"])

    add("hard",
        I("j4"),
        [{"type": "answer_match", "answer": "N/A"}],
        LOGIN + ["goto /communities", "stop N/A"])

    j5 = unlocked[290]
    add("hard",
        I("j5", id=j5['id'], u=j5['author']),
        [{"type": "answer_match", "answer": "N/A"},
         {"type": "db_record_exists", "table": "posts",
          "match": {"id": j5["id"]}}],
        LOGIN + [f"goto /post/{j5['id']}", "stop N/A"])

    own2 = by_id[own_a]
    add("hard",
        I("k1", title=own2['title'], new=L['k1_prefix'] + own2['title']),
        [{"type": "db_record_exists", "table": "posts",
          "match": {"id": own_a, "title": L["k1_prefix"] + own2["title"],
                    "body": own2["body"]}}],
        LOGIN + [f"goto /post/{own_a}/edit",
                 f"fill 0 title={L['k1_prefix']}{own2['title']}"])

    add("hard",
        I("k2", title=by_id[own_b]['title']),
        [{"type": "db_record_absent", "table": "posts",
          "match": {"id": own_b}},
         {"type": "db_record_exists", "table": "posts",
          "match": {"id": own_a}}],
        LOGIN + [f"goto /post/{own_b}/delete", "fill 0"])

    k3 = next(c for c in comments if c["id"] == own_cids[1])
    add("hard",
        I("k3", body=k3['body'], title=by_id[k3['post_id']]['title'], new=L['k3_new']),
        [{"type": "db_record_exists", "table": "comments",
          "match": {"id": k3["id"],
                    "body": L["k3_new"]}}],
        LOGIN + [f"goto /comment/{k3['id']}/edit",
                 f"fill 0 body={L['k3_new']}"])

    k4 = next(c for c in comments if c["id"] == own_cids[2])
    add("hard",
        I("k4", body=k4['body'], title=by_id[k4['post_id']]['title']),
        [{"type": "db_record_absent", "table": "comments",
          "match": {"id": k4["id"]}}] +
        [{"type": "db_record_exists", "table": "comments",
          "match": {"id": i}} for i in own_cids if i != k4["id"]],
        LOGIN + [f"goto /comment/{k4['id']}/delete", "fill 0"])

    umeta = C["user_meta"]
    ckarma, pkarma = {}, {}
    for c in comments:
        ckarma[c["author"]] = ckarma.get(c["author"], 0) + c["score"]
    for p in posts:
        pkarma[p["author"]] = pkarma.get(p["author"], 0) + p["score"]

    ua, ub = "chai_addict", "midnight_owl"
    assert ckarma[ua] != ckarma[ub]
    pwin = ua if ckarma[ua] > ckarma[ub] else ub
    add("hard",
        I("p1", a=ua, b=ub),
        [{"type": "answer_match", "answer": pwin,
          "none_of": [ub if pwin == ua else ua]}],
        [f"goto /u/{ua}", f"goto /u/{ub}", f"stop {pwin}"])

    p2 = unlocked[95]
    p2j = umeta[p2["author"]]["joined"]
    add("hard",
        I("p2", id=p2['id']),
        [{"type": "answer_match", "answer": p2j}],
        [f"goto /post/{p2['id']}", f"goto /u/{p2['author']}",
         f"stop {p2j}"])

    uc, ud = "salty_sailor", "quiet_quokka"
    assert umeta[uc]["joined"] != umeta[ud]["joined"]
    p3win = uc if umeta[uc]["joined"] < umeta[ud]["joined"] else ud
    add("hard",
        I("p3", a=uc, b=ud),
        [{"type": "answer_match", "answer": p3win,
          "none_of": [ud if p3win == uc else uc]}],
        [f"goto /u/{uc}", f"goto /u/{ud}", f"stop {p3win}"])

    def p4_pick(u):
        cs = [c for c in comments if c["author"] == u]
        if not cs:
            return None
        best = max(c["score"] for c in cs)
        hits = [c for c in cs if c["score"] == best]
        if len(hits) != 1:
            return None
        c = hits[0]
        if c["parent_id"] is not None or by_id[c["post_id"]]["locked"]:
            return None
        return c

    p4u = next(u for u in C["users"][1:] if p4_pick(u))
    p4c = p4_pick(p4u)
    add("hard",
        I("p4", u=p4u),
        [{"type": "db_record_exists", "table": "comment_votes",
          "match": {"comment_id": p4c["id"], "user_id": 1}}],
        LOGIN + [f"goto /u/{p4u}", f"goto /post/{p4c['post_id']}",
                 f"fill {cvote_form(p4c['post_id'], p4c['id'])}"])

    fmeta = C["forum_meta"]

    q1rule = fmeta["cooking"]["rules"][1]
    add("hard",
        I("q1"),
        [{"type": "answer_match", "answer": q1rule}],
        ["goto /f/cooking/about", f"stop {q1rule}"])

    fa2, fb2 = "travel", "movies"
    assert fmeta[fa2]["members"] != fmeta[fb2]["members"]
    q2win = fa2 if fmeta[fa2]["members"] > fmeta[fb2]["members"] else fb2
    add("hard",
        I("q2", a=fa2, b=fb2),
        [{"type": "answer_match", "answer": q2win,
          "none_of": [fb2 if q2win == fa2 else fa2]}],
        [f"goto /f/{fa2}/about", f"goto /f/{fb2}/about",
         f"stop f/{q2win}"])

    q3mod = fmeta["personalfinance"]["moderators"][0]
    q3k = pkarma.get(q3mod, 0)
    add("hard",
        I("q3"),
        [{"type": "answer_match", "any_of": [f"{q3k:,}", str(q3k)]}],
        ["goto /f/personalfinance/about", f"goto /u/{q3mod}",
         f"stop {q3k}"])

    modded = {}
    for fname, m in fmeta.items():
        for u in m["moderators"]:
            modded.setdefault(u, []).append(fname)
    q4u, q4f = next((u, fs[0]) for u, fs in sorted(modded.items())
                    if len(fs) == 1
                    and fs[0] not in C["preseed"]["subscriptions"])
    add("hard",
        I("q4", u=q4u),
        [{"type": "db_record_exists", "table": "subscriptions",
          "match": {"user_id": 1, "forum_id": forum_id[q4f]}}] +
        [{"type": "db_record_absent", "table": "subscriptions",
          "match": {"user_id": 1, "forum_id": forum_id[f]}}
         for f in sorted(forum_id) if f != q4f
         and f not in C["preseed"]["subscriptions"]],
        LOGIN + [f"goto /f/{q4f}/about", f"goto /f/{q4f}", "fill 0"])

    q5f = next(f for f in ("technology", "askanything", "travel",
                           "movies", "gardening")
               if no_collide(str(fmeta[f]["members"]), fmeta[f]["created"])
               and no_collide(f"{fmeta[f]['members']:,}",
                              fmeta[f]["created"]))
    q5m, q5c = fmeta[q5f]["members"], fmeta[q5f]["created"]
    add("hard",
        I("q5", forum=q5f),
        [{"type": "answer_match", "any_of": [f"{q5m:,}", str(q5m)]},
         {"type": "answer_match", "answer": q5c}],
        [f"goto /f/{q5f}/about",
         f"stop {q5m:,} members, created {q5c}"])

    r1f = "travel"
    r1p = fmeta[r1f]["pinned"]
    assert not by_id[r1p]["locked"]
    add("hard",
        I("r1", forum=r1f),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"user_id": 1, "post_id": r1p}}],
        LOGIN + [f"goto /f/{r1f}/about", f"goto /post/{r1p}", "fill 2"])

    r2n = sum(1 for p in posts if p["forum"] == "cooking"
              and p["flair"] == flair_l("cooking", "Recipe"))
    add("hard",
        I("r2", flair=flair_l('cooking', 'Recipe')),
        [{"type": "answer_match", "answer": str(r2n)}],
        [f"goto /f/cooking?flair={flair_l('cooking', 'Recipe')}", f"stop {r2n}"])

    def r3_pick(fname):
        pool = feed(fname, "top")[:15]
        best = max(p["awards"] for p in pool)
        hits = [p for p in pool if p["awards"] == best]
        return hits[0] if best > 0 and len(hits) == 1 else None

    r3f = next(f["name"] for f in C["forums"] if r3_pick(f["name"]))
    r3 = r3_pick(r3f)
    add("hard",
        I("r3", forum=r3f),
        [{"type": "answer_match", "answer": str(r3["id"])}],
        [f"goto /f/{r3f}?sort=top", f"stop {r3['id']}"])

    def r4_pick(fname, flair):
        pool = feed(fname, "top")[:5]
        hits = [p for p in pool if p["flair"] == flair]
        if len(hits) == 1 and not hits[0]["locked"]:
            return hits[0]
        return None

    r4 = r4f = r4fl = None
    for fname in ("personalfinance", "gardening", "technology",
                  "movies", "travel", "cooking", "askanything"):
        for fl in sorted({p["flair"] for p in posts
                          if p["forum"] == fname and p["flair"]}):
            r4 = r4_pick(fname, fl)
            if r4:
                r4f, r4fl = fname, fl
                break
        if r4:
            break
    assert r4 is not None
    add("hard",
        I("r4", forum=r4f, flair=r4fl),
        [{"type": "db_record_exists", "table": "votes",
          "match": {"post_id": r4["id"], "user_id": 1, "dir": 1}}] +
        [{"type": "db_record_absent", "table": "votes",
          "match": {"post_id": q["id"], "user_id": 1}}
         for q in feed(r4f, "top")[:5] if q["id"] != r4["id"]],
        LOGIN + [f"goto /post/{r4['id']}", "fill 0"])

    m1 = next(p for p in unlocked[300:] if p["flair"])
    add("easy",
        I("m1", id=m1['id']),
        [{"type": "answer_match", "answer": m1["flair"],
          "none_of": [f for f in P["FLAIRS"][m1["forum"]]
                      if f != m1["flair"]]}],
        [f"goto /post/{m1['id']}", f"stop {m1['flair']}"])

    m2 = unlocked[310]
    add("easy",
        I("m2", id=m2['id']),
        [{"type": "answer_match",
          "answer": str(n_comments.get(m2["id"], 0))}],
        [f"goto /post/{m2['id']}",
         f"stop {n_comments.get(m2['id'], 0)}"])

    m3m = fmeta["movies"]["members"]
    add("medium",
        I("m3"),
        [{"type": "answer_match", "any_of": [f"{m3m:,}", str(m3m)]}],
        ["goto /f/movies/about", f"stop {m3m:,}"])

    add("easy",
        I("m4"),
        [{"type": "db_record_exists", "table": "subscriptions",
          "match": {"user_id": 1, "forum_id": forum_id["movies"]}}],
        LOGIN + ["goto /f/movies", "fill 0"])

    m5 = unlocked[330]
    add("easy",
        I("m5", id=m5['id']),
        [{"type": "db_record_exists", "table": "saved",
          "match": {"user_id": 1, "post_id": m5["id"]}}],
        LOGIN + [f"goto /post/{m5['id']}", "fill 2"])

    m6 = unlocked[340]
    add("medium",
        I("m6", c=L['m6'], id=m6['id']),
        [{"type": "db_record_exists", "table": "comments",
          "match": {"post_id": m6["id"], "author_id": 1,
                    "body": L["m6"]}}],
        LOGIN + [f"goto /post/{m6['id']}", f"fill 3 body={L['m6']}"])

    add("easy",
        I("m7"),
        [{"type": "answer_match", "answer": "48"}],
        ["goto /rules", "stop 48 hours"])

    n_cook = sum(1 for p in posts if p["forum"] == "cooking")
    pages_cook = -(-n_cook // 15)
    add("medium",
        I("m8"),
        [{"type": "answer_match", "answer": str(pages_cook)}],
        ["goto /f/cooking", f"stop {pages_cook}"])

    m9 = clean_title(350)
    add("medium",
        I("m9", title=m9['title']),
        [{"type": "final_url", "path": f"/post/{m9['id']}"}],
        [f"goto /post/{m9['id']}"])

    m10 = unlocked[360]
    add("medium",
        I("m10", id=m10['id']),
        [{"type": "db_record_exists", "table": "votes",
          "match": {"post_id": m10["id"], "user_id": 1, "dir": 1}}],
        LOGIN + [f"goto /post/{m10['id']}", "fill 0"])

    assert len(T) == 75, len(T)
    n_hard = sum(1 for t in T if t["difficulty"] == "hard")
    assert n_hard == 65, n_hard
    return T


def write(lang, out_dir):
    tasks = build(lang)
    out = os.path.join(out_dir, "visual_reddit_tasks.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=1, ensure_ascii=False)
    n_hard = sum(1 for t in tasks if t["difficulty"] == "hard")
    print(f"wrote {len(tasks)} tasks ({n_hard} hard) to {out}")
