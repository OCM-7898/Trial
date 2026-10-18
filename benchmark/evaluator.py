import os
import re

import requests

from .harness import headers as harness_headers
from bs4 import BeautifulSoup


def _norm(s):
    import unicodedata
    s = unicodedata.normalize("NFC", str(s))
    for ch in ("‌", "‍", "‎", "‏", "؜", "‪", "‫",
               "‬", "‭", "‮", "⁦", "⁧", "⁨",
               "⁩"):
        s = s.replace(ch, "")
    s = s.translate(_DIGIT_FOLD)
    return " ".join(s.strip().lower().split())


_DIGIT_FOLD = {}
for _block in ("০১২৩৪৫৬৭৮৯", "०१२३४५६७८९", "٠١٢٣٤٥٦٧٨٩", "۰۱۲۳۴۵۶۷۸۹",
               "૦૧૨૩૪૫૬૭૮૯", "੦੧੨੩੪੫੬੭੮੯", "௦௧௨௩௪௫௬௭௮௯", "౦౧౨౩౪౫౬౭౮౯"):
    for _i, _ch in enumerate(_block):
        _DIGIT_FOLD[ord(_ch)] = str(_i)


def _contains(target, answer):
    if not target:
        return False
    pre = r"(?<!\d)(?<!\d\.)(?<!\d,)" if target[0].isdigit() else ""
    suf = r"(?!\d)(?!\.\d)(?!,\d)" if target[-1].isdigit() else ""
    if target[0].isascii() and target[0].isalpha():
        pre += r"(?<![A-Za-z])"
    if target[-1].isascii() and target[-1].isalpha():
        suf += r"(?![A-Za-z])"
    return re.search(pre + re.escape(target) + suf, answer) is not None


def _row_matches(row, match):
    for k, v in match.items():
        have = str(row.get(k, ""))
        if isinstance(v, list):
            if not any(_norm(str(w)) == _norm(have) for w in v):
                return False
            continue
        want = str(v)
        if want.startswith("%") and want.endswith("%") and len(want) > 1:
            if _norm(want.strip("%")) not in _norm(have):
                return False
        elif _norm(want) != _norm(have):
            return False
    return True


def _fetch_state(base_url, table):
    r = requests.get(f"{base_url}/__state__/{table}", timeout=10,
                     headers=harness_headers())
    r.raise_for_status()
    return r.json()


def _mount_artifact(dirname):
    import os
    import sys
    root = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), dirname)
    for mod in list(sys.modules):
        if mod in ("app", "tasks") or mod.startswith(("app.", "tasks.")):
            f = getattr(sys.modules[mod], "__file__", "") or ""
            if f and not f.startswith(root):
                del sys.modules[mod]
    if root in sys.path:
        sys.path.remove(root)
    sys.path.insert(0, root)


def _selam_score(ev, final_answer, final_url, final_html):
    _mount_artifact(os.path.join("sites", "text_only", "selam"))
    from tasks.score import score as selam_score_fn
    return selam_score_fn(ev["lang"], ev["task_id"], final_url or "",
                          final_html or "", final_answer or "")


def evaluate(task, base_url, final_answer, final_url=None, final_html=None):
    details = []
    ok_all = True
    for ev in task["eval"]:
        etype = ev["type"]
        ok = False

        if etype == "selam_score":
            ok, reason = _selam_score(ev, final_answer, final_url,
                                      final_html)
            details.append(f"selam_score task {ev['task_id']} -> {ok} "
                           f"({reason})")

        elif etype == "final_url":
            from urllib.parse import urlparse
            got = urlparse(final_url or "").path.rstrip("/")
            want = ev["path"].rstrip("/")
            ok = got == want
            details.append(f"final_url {ev['path']} -> {ok} (got: {got!r})")

        elif etype == "answer_match":
            ans = _norm(final_answer or "")
            targets = list(dict.fromkeys(ev.get("any_of")
                                         or [ev["answer"]]))
            mode = ev.get("mode", "contains")
            for t in targets:
                t = _norm(t)
                ok = (t == ans) if mode == "exact" else _contains(t, ans)
                if ok:
                    break
            all_targets = [t for e2 in task["eval"]
                           if e2["type"] == "answer_match"
                           for t in (e2.get("any_of") or [e2["answer"]])]
            hedged = [n for n in ev.get("none_of", [])
                      if _contains(_norm(n), ans)
                      and not any(_contains(_norm(n), _norm(t))
                                  for t in all_targets)]
            if ok and hedged:
                ok = False
            details.append(f"answer_match -> {ok} (got: {final_answer!r})"
                           + (f" HEDGED: also names {hedged[:3]}"
                              if hedged else ""))

        elif etype == "final_page_contains":
            text = _norm(BeautifulSoup(final_html or "", "html.parser")
                         .get_text(" ", strip=True))
            missing = [s for s in ev["strings"] if _norm(s) not in text]
            ok = not missing
            details.append(f"final_page_contains -> {ok}"
                           + (f" | missing {missing[:4]}" if missing else ""))

        elif etype == "page_contains":
            r = requests.get(base_url + ev["path"], timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            text = _norm(soup.get_text(" ", strip=True))
            ok = all(_norm(s) in text for s in ev["strings"])
            details.append(f"page_contains {ev['path']} -> {ok}")

        elif etype in ("db_record_exists", "db_record_absent"):
            rows = _fetch_state(base_url, ev["table"])
            found = any(_row_matches(r, ev["match"]) for r in rows)
            ok = found if etype == "db_record_exists" else not found
            detail = f"{etype} {ev['table']} {ev['match']} -> {ok}"
            if not ok and etype == "db_record_exists" and rows:
                def n_hits(r):
                    return sum(_row_matches(r, {k: v})
                               for k, v in ev["match"].items())
                best = max(rows, key=n_hits)
                if n_hits(best) > 0:
                    diff = {k: best.get(k) for k, v in ev["match"].items()
                            if not _row_matches(best, {k: v})}
                    detail += (f" | closest row id={best.get('id')} "
                               f"differs on {diff}")
                else:
                    detail += " | no row matches any field"
            details.append(detail)

        elif etype == "db_reply_to":
            rows = _fetch_state(base_url, ev.get("table", "comments"))
            if ev.get("post_id") is not None:
                rows = [r for r in rows
                        if str(r.get("post_id")) == str(ev["post_id"])]
            parents = [r["id"] for r in rows
                       if _norm(r.get("body", "")) ==
                       _norm(ev["parent_body"])]
            ok = any(r.get("parent_id") in parents
                     and _norm(r.get("body", "")) == _norm(ev["child_body"])
                     and str(r.get("author_id")) == str(ev["author_id"])
                     for r in rows)
            details.append(f"db_reply_to {ev['child_body'][:30]!r} -> "
                           f"parent {ev['parent_body'][:30]!r}"
                           + (f" on post {ev['post_id']}"
                              if ev.get("post_id") is not None else "")
                           + f" -> {ok}")

        elif etype == "db_field_equals":
            rows = _fetch_state(base_url, ev["table"])
            hits = [r for r in rows if _row_matches(r, ev.get("match", {}))]
            ok = any(_norm(r.get(ev["field"], "")) == _norm(ev["value"])
                     for r in hits)
            details.append(
                f"db_field_equals {ev['table']}.{ev['field']}=={ev['value']} -> {ok}")

        elif etype == "order_contains":
            orders = [o for o in _fetch_state(base_url, "orders")
                      if _row_matches(o, {"user_id": ev.get("user_id", 1),
                                          "address": ev["address"]})]
            items = _fetch_state(base_url, "order_items")
            want = {str(k): int(v) for k, v in ev["items"].items()}
            for o in orders:
                got = {str(i["product_id"]): int(i["qty"]) for i in items
                       if i["order_id"] == o["id"]}
                if got == want and ("total" not in ev or
                                    abs(float(o["total"]) - float(ev["total"])) < 0.01):
                    ok = True
                    break
            detail = f"order_contains {ev['address']} {want} -> {ok}"
            if not ok:
                if not orders:
                    others = [o for o in _fetch_state(base_url, "orders")
                              if str(o.get("user_id")) ==
                              str(ev.get("user_id", 1))]
                    seeded = 4
                    new = [o for o in others if int(o["id"]) > seeded]
                    if new:
                        detail += " | no order to that address; orders placed elsewhere: " + "; ".join(
                            f"id={o['id']} to {o['address']!r} total={o['total']}"
                            for o in new[-3:])
                    else:
                        detail += " | no order placed at all"
                else:
                    for o in orders[-2:]:
                        got = {str(i["product_id"]): int(i["qty"])
                               for i in items if i["order_id"] == o["id"]}
                        detail += (f" | order id={o['id']} items={got} "
                                   f"total={o['total']}")
            details.append(detail)

        else:
            details.append(f"unknown eval type {etype} -> False")

        ok_all = ok_all and ok
    return ok_all, details
