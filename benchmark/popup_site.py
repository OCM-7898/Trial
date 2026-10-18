import os
import re
import secrets
import threading
from html import escape

from .harness import TOKEN_HEADER, token
from .popup_text import POPUP_TEXT, RTL

COOKIE = "mwa_popup"
ROUTE = "/-/popup/"
FORWARDED = "X-MWA-Forwarded"
LEFT_MARK = '<meta name="mwa-popup" content="left-site">'

_lock = threading.Lock()
_state = {}


def enabled():
    return os.environ.get("MWA_POPUPS") == "1"


def maybe_install(app):
    if enabled():
        install(app)
    return app


_CSS = """
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{background:#eef1f5;color:#1b2330;font-family:Roboto,"Segoe UI","Noto Sans",
 "Noto Sans Bengali","Noto Sans Devanagari","Noto Nastaliq Urdu","Noto Sans Ethiopic",Arial,sans-serif;
 display:grid;place-items:center;padding:24px}
.card{background:#fff;border-radius:14px;box-shadow:0 18px 50px rgba(0,0,0,.18);max-width:460px;width:100%;
 padding:30px 30px 24px;display:grid;gap:18px;position:relative}
.card p{margin:0;font-size:17px;line-height:1.55}
.cookie{padding-inline-end:58px}
.cookie a{position:absolute;top:10px;inset-inline-end:12px;font-size:28px;line-height:1;color:#555;
 text-decoration:none;padding:4px 9px;border-radius:6px}
.cookie a:hover{background:#eef1f5}
.offer a[data-kind=offer]{background:#0b6b3a;color:#fff;border-radius:9px;padding:13px 18px;font-size:17px;
 font-weight:600;text-align:center;text-decoration:none}
.offer a[data-kind=decline]{color:#5b6678;font-size:15px;justify-self:center}
[dir=rtl] body{font-family:"Noto Nastaliq Urdu",serif}
"""


def _page(lang, title, body, extra_head=""):
    d = "rtl" if lang in RTL else "ltr"
    return (f'<!doctype html><html lang="{lang}" dir="{d}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{escape(title)}</title>{extra_head}<style>{_CSS}</style></head>'
            f'<body>{body}</body></html>')


def _popup_html(st, name):
    t = POPUP_TEXT[st["lang"]][name]
    links = "".join(f'<a href="{ROUTE}{st["tokens"][kind]}" data-kind="{kind}">{escape(label)}</a>'
                    for kind, label in t["links"])
    body = (f'<div class="card {name}" role="dialog" aria-modal="true" data-mwa-popup="{name}">'
            f'<p>{escape(t["message"])}</p>{links}</div>')
    return _page(st["lang"], st["title"], body)


def _left_html(st):
    body = '<div class="card"><p>↗</p></div>'
    return _page(st["lang"], st["title"], body, LEFT_MARK)


def _raw_url(request):
    env = request.environ
    raw = env.get("RAW_URI") or env.get("REQUEST_URI")
    if not raw:
        from urllib.parse import quote
        qs = env.get("QUERY_STRING", "")
        raw = quote(env.get("PATH_INFO", "")) + ("?" + qs if qs else "")
    return request.host_url.rstrip("/") + raw


def _lang_title(html):
    m = re.search(r'<html[^>]*\blang="([a-z]{2})"', html)
    lang = m.group(1) if m and m.group(1) in POPUP_TEXT else "en"
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    return lang, (t.group(1).strip() if t else "")


def install(app):
    from flask import Response, g, make_response, redirect, request

    def skip():
        if (request.headers.get(TOKEN_HEADER) == token()
                or request.path.startswith("/static/") or request.endpoint == "static"):
            return True
        dest = request.headers.get("Sec-Fetch-Dest")
        if dest and dest not in ("document", "iframe"):
            return True
        if (request.path in ("/favicon.ico", "/robots.txt")
                or request.path.startswith("/apple-touch-icon")):
            return request.headers.get("Accept", "").startswith("image/")
        return False

    def respond(st, html, status=200):
        r = make_response(html, status)
        r.headers[FORWARDED] = str(st["forwarded"])
        return r

    @app.before_request
    def _popup_before():
        g.mwa_popup_done = False
        if skip():
            return None
        sid = request.cookies.get(COOKIE)
        with _lock:
            st = _state.get(sid)
        if st is None:
            return None
        if request.path.startswith(ROUTE):
            g.mwa_popup_done = True
            kind = next((k for k, v in st["tokens"].items()
                         if request.path == ROUTE + v), None)
            if kind is None or st["stage"] not in ("cookie", "offer"):
                return respond(st, "not found", 404)
            if kind == "offer":
                st["stage"] = "left"
                return respond(st, _left_html(st))
            st["stage"] = "restore_" + st["stage"]
            return redirect(st["held_url"], code=303)
        if st["stage"] in ("cookie", "offer"):
            g.mwa_popup_done = True
            return respond(st, _popup_html(st, st["stage"]))
        if st["stage"] == "left":
            g.mwa_popup_done = True
            return respond(st, _left_html(st))
        if st["stage"].startswith("restore_") and _raw_url(request) == st["held_url"]:
            g.mwa_popup_done = True
            body, status, headers = st["held"]
            st["stage"] = "await_offer" if st["stage"] == "restore_cookie" else "done"
            st["held"] = None
            r = Response(body, status=status, headers=headers)
            r.headers[FORWARDED] = str(st["forwarded"])
            return r
        return None

    @app.after_request
    def _popup_after(resp):
        if getattr(g, "mwa_popup_done", False) or skip():
            return resp
        sid = request.cookies.get(COOKIE)
        with _lock:
            st = _state.get(sid)
            new = st is None
            if new:
                sid = secrets.token_hex(12)
                st = _state[sid] = {"stage": "new", "forwarded": 0, "held": None,
                                    "tokens": {k: secrets.token_hex(6)
                                               for k in ("close", "offer", "decline")}}
        st["forwarded"] += 1
        html_ok = resp.mimetype == "text/html" and not 300 <= resp.status_code < 400
        name = {"new": "cookie", "await_offer": "offer"}.get(st["stage"]) if html_ok else None
        if name is None:
            resp.headers[FORWARDED] = str(st["forwarded"])
            if new:
                resp.set_cookie(COOKIE, sid, httponly=True, samesite="Lax")
            return resp
        held_body = resp.get_data()
        st["lang"], st["title"] = _lang_title(held_body.decode("utf-8", "replace"))
        st["held"] = (held_body, resp.status_code,
                      [(k, v) for k, v in resp.headers if k.lower() not in ("content-length", "set-cookie")])
        st["held_url"] = _raw_url(request)
        st["stage"] = name
        out = respond(st, _popup_html(st, name))
        for k, v in resp.headers:
            if k.lower() == "set-cookie":
                out.headers.add(k, v)
        if new:
            out.set_cookie(COOKIE, sid, httponly=True, samesite="Lax")
        return out

    return app
