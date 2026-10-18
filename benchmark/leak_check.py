import json
import sys

import requests

from .env import BrowserEnv
from .harness import TOKEN_HEADER, headers as harness_headers

LOGIN = {
    "ministore": {"username": "agent_smith", "password": "password123"},
    "reddit": {"username": "agent_smith", "password": "password123"},
    "gari": {"email": "ahmed.raza@garibazaar.test",
             "password": "garibazaar2026"},
    "portal": {"citizen_id": "9999708182203", "password": "citizen1234"},
    "rail": {"username": "priya_sharma", "password": "travel123"},
}
PORT_SITE = {8015: "portal", 8016: "portal", 8046: "portal",
             8047: "portal", 8048: "portal", 8017: "selam", 8053: "selam",
             8054: "selam", 8055: "selam", 8056: "selam", 8021: "rail", 8049: "rail",
             8050: "rail", 8051: "rail", 8052: "rail",
             8031: "ministore", 8032: "ministore", 8033: "ministore",
             8034: "ministore", 8035: "ministore", 8036: "gari",
             8037: "reddit", 8038: "reddit", 8039: "reddit",
             8040: "reddit", 8041: "reddit", 8042: "gari", 8043: "gari", 8044: "gari", 8045: "gari"}

SPELLINGS = [
    "/__state__/users", "/__state__/bookings", "/__reset__",
    "/%5F%5Fstate%5F%5F/users", "/%255F%255Fstate%255F%255F/users",
    "//__state__/users", "/./__state__/users", "/x/../__state__/users",
    "/__state__/users/", "/__state__/users?x=1", "/__STATE__/users",
    "/__state__%2Fusers", "/reset", "/reset/status",
]


def _leaked(r):
    if r.status_code != 200:
        return False
    try:
        body = r.json()
    except ValueError:
        return False
    return isinstance(body, (list, dict))


def check_site(base_url, site):
    open_doors = []
    r = requests.post(base_url + "/__reset__", headers=harness_headers(),
                      timeout=10)
    if not _leaked(r):
        open_doors.append(f"token REFUSED: POST /__reset__ with "
                          f"{TOKEN_HEADER} -> {r.status_code}")
    for sp in SPELLINGS:
        for m in ("get", "post"):
            r = getattr(requests, m)(base_url + sp, timeout=10)
            if _leaked(r):
                open_doors.append(f"raw {m.upper()} {sp} -> {r.status_code}")
    creds = LOGIN.get(site)
    if creds:
        for target in ("/__state__/users", "/__state__/bookings",
                       "/__state__/ads", "/__state__/posts"):
            s = requests.Session()
            s.get(base_url + "/login?next=" + target, timeout=10)
            r = s.post(base_url + "/login", data={**creds, "next": target},
                       timeout=10)
            if _leaked(r):
                open_doors.append(f"raw login next={target} -> JSON")
    env = BrowserEnv(base_url)
    for sp in SPELLINGS:
        if sp in ("/reset", "/reset/status"):
            continue
        try:
            env.goto(sp)
        except ValueError:
            continue
        except requests.RequestException:
            continue
        if _leaked_env(env):
            open_doors.append(f"env goto {sp} -> JSON")
    if creds:
        for target in ("/__state__/users", "/__state__/bookings"):
            env = BrowserEnv(base_url)
            try:
                obs = env.goto("/login?next=" + target)
                idx = next(i for i, _, _, f in obs.forms
                           if any(x.startswith("password") for x in f))
                env.submit_form(idx, creds)
            except (ValueError, StopIteration, requests.RequestException):
                continue
            if _leaked_env(env):
                open_doors.append(f"env login next={target} -> JSON")
            env = BrowserEnv(base_url)
            try:
                obs = env.goto("/login")
                idx = next(i for i, _, _, f in obs.forms
                           if any(x.startswith("password") for x in f))
                env.submit_form(idx, {**creds, "next": target})
            except (ValueError, StopIteration, requests.RequestException):
                continue
            if _leaked_env(env):
                open_doors.append(f"env login fill next={target} -> JSON")
    return open_doors


def _leaked_env(env):
    try:
        body = json.loads(env.last_html)
    except ValueError:
        return False
    return isinstance(body, (list, dict))


def check_all(site_urls):
    bad = {}
    for site, url in site_urls.items():
        try:
            doors = check_site(url, site)
        except requests.RequestException as e:
            doors = [f"site unreachable: {e}"]
        n = len(SPELLINGS) * 2 + 1
        print(f"leak check {site} {url}: "
              + ("closed" if not doors else "OPEN -> " + "; ".join(doors)))
        if doors:
            bad[site] = doors
    return bad


def main(argv):
    ports = [int(a) for a in argv] or sorted(PORT_SITE)
    urls = {}
    for p in ports:
        urls[f"{PORT_SITE.get(p, 'site')}:{p}"] = f"http://127.0.0.1:{p}"
    bad = {}
    for key, url in urls.items():
        site = key.split(":")[0]
        try:
            doors = check_site(url, site)
        except requests.RequestException as e:
            doors = [f"site unreachable: {e}"]
        print(f"leak check {key}: "
              + ("closed" if not doors else "OPEN -> " + "; ".join(doors)))
        if doors:
            bad[key] = doors
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
