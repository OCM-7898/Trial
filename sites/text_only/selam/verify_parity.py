from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
import sys
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from app import create_app
from app.i18n import latin_tokens
from app.routes_map import SLUGS

KEEP_VALUES = ("id", "class", "name", "type", "href")

GEEZ = re.compile(r"[ሀ-፿]")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")
VISIBLE_ATTRS = ("placeholder", "alt", "title", "aria-label")
_ATTR = re.compile(
    r"\b(?:" + "|".join(VISIBLE_ATTRS) + r")\s*=\s*(\"[^\"]*\"|'[^']*')", re.IGNORECASE
)
IDENTIFIER = re.compile(latin_tokens.IDENTIFIER_PATTERN)
WHITELIST = latin_tokens.ALLOWED


class Skeleton(HTMLParser):

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tokens: list[str] = []
        self.counts: Counter = Counter()

    def handle_starttag(self, tag, attrs):
        parts = [tag]
        for key, value in sorted(attrs):
            parts.append(f"{key}={value}" if key in KEEP_VALUES else key)
        self.tokens.append("<" + " ".join(parts) + ">")
        self.counts[tag] += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        self.tokens.append(f"</{tag}>")

    def handle_data(self, data):
        pass

    @property
    def digest(self) -> str:
        return hashlib.sha256("".join(self.tokens).encode()).hexdigest()

    @property
    def elements(self) -> dict[str, int]:
        return {tag: self.counts.get(tag, 0)
                for tag in ("form", "input", "button", "a", "img", "select",
                            "textarea", "table", "label")}


def skeleton_of(html: str) -> Skeleton:
    parser = Skeleton()
    parser.feed(html)
    return parser


def visible_text(html: str) -> str:
    import html as html_module

    html = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)
    html = re.sub(r"(?s)<!--.*?-->", " ", html)
    attr_text = " ".join(m.group(1)[1:-1] for m in _ATTR.finditer(html))
    body = re.sub(r"(?s)<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html_module.unescape(body + " " + attr_text))


@dataclass
class Result:
    name: str
    ok: bool
    detail: str = ""
    pending: bool = False
    failures: list[str] = field(default_factory=list)


def check(name: str, ok: bool, detail: str = "", failures=None, pending=False) -> Result:
    return Result(name, ok, detail, pending, list(failures or []))


def check_routes(en_app, am_app) -> Result:
    def table(app):
        return sorted((str(r), tuple(sorted(r.methods)), r.endpoint)
                      for r in app.url_map.iter_rules())

    a, b = table(en_app), table(am_app)
    if a == b:
        return check("1. route table equality", True, f"{len(a)} rules identical")
    only_en = [r for r in a if r not in b]
    only_am = [r for r in b if r not in a]
    return check("1. route table equality", False,
                 failures=[f"only in en: {only_en}", f"only in am: {only_am}"])


def check_dom(en_client, am_client, routes) -> Result:
    failures = []
    for url in routes:
        en_html = en_client.get(url).get_data(as_text=True)
        am_html = am_client.get(url).get_data(as_text=True)
        en_skeleton, am_skeleton = skeleton_of(en_html), skeleton_of(am_html)
        if en_skeleton.digest != am_skeleton.digest:
            failures.append(f"{url}: tag tree differs\n{_first_divergence(en_skeleton, am_skeleton)}")
    return check("2. DOM skeleton equality", not failures,
                 f"{len(routes)} routes identical", failures)


def _first_divergence(a: Skeleton, b: Skeleton) -> str:
    for index, (left, right) in enumerate(zip(a.tokens, b.tokens)):
        if left != right:
            return (f"      first difference at token {index}:\n"
                    f"        en: {left}\n        am: {right}")
    if len(a.tokens) != len(b.tokens):
        longer, which = (a, "en") if len(a.tokens) > len(b.tokens) else (b, "am")
        extra = longer.tokens[min(len(a.tokens), len(b.tokens)):][:3]
        return f"      {which} has {abs(len(a.tokens) - len(b.tokens))} extra tokens, e.g. {extra}"
    return "      (tokens equal but digest differs -- impossible, investigate)"


def check_element_counts(en_client, am_client, routes) -> Result:
    failures = []
    for url in routes:
        en = skeleton_of(en_client.get(url).get_data(as_text=True)).elements
        am = skeleton_of(am_client.get(url).get_data(as_text=True)).elements
        if en != am:
            differing = {k: (en[k], am[k]) for k in en if en[k] != am[k]}
            failures.append(f"{url}: {differing}")
    return check("3. element count equality", not failures,
                 f"{len(routes)} routes identical", failures)


def check_database(en_app, am_app) -> Result:
    failures = []
    en_db = sqlite3.connect(en_app.config["SELAM"].db_path)
    am_db = sqlite3.connect(am_app.config["SELAM"].db_path)

    def tables(conn):
        return sorted(r[0] for r in conn.execute(
            "select name from sqlite_master where type='table' and name not like 'sqlite_%'"))

    en_tables, am_tables = tables(en_db), tables(am_db)
    if en_tables != am_tables:
        failures.append(f"table sets differ: en-only {set(en_tables) - set(am_tables)}, "
                        f"am-only {set(am_tables) - set(en_tables)}")
    else:
        for table in en_tables:
            en_count = en_db.execute(f"select count(*) from {table}").fetchone()[0]
            am_count = am_db.execute(f"select count(*) from {table}").fetchone()[0]
            if en_count != am_count:
                failures.append(f"{table}: {en_count} rows in en, {am_count} in am")
                continue
            columns = [r[1] for r in en_db.execute(f"pragma table_info({table})")]
            if "id" in columns:
                en_ids = {r[0] for r in en_db.execute(f"select id from {table}")}
                am_ids = {r[0] for r in am_db.execute(f"select id from {table}")}
                if en_ids != am_ids:
                    failures.append(f"{table}: primary keys differ "
                                    f"({len(en_ids ^ am_ids)} not shared)")
    en_db.close(); am_db.close()
    return check("4. database parity", not failures,
                 f"{len(en_tables)} tables, identical row counts and keys", failures)


def check_language_purity(en_client, am_client, routes, letter_codes) -> Result:
    failures = []
    for url in routes:
        en_text = visible_text(en_client.get(url).get_data(as_text=True))
        found = set(GEEZ.findall(en_text))
        if found:
            failures.append(f"{url}: Ge'ez in the English build: {sorted(found)[:8]}")

        am_text = visible_text(am_client.get(url).get_data(as_text=True))
        stray = {w for w in LATIN_WORD.findall(am_text)
                 if not _allowed(w, am_text, letter_codes)}
        if stray:
            failures.append(f"{url}: untranslated Latin in the Amharic build: {sorted(stray)[:8]}")
    return check("5. language purity", not failures,
                 f"{len(routes)} routes clean in both builds", failures)


EMAIL = re.compile(latin_tokens.EMAIL_PATTERN)
URL_PATH = re.compile(latin_tokens.URL_PATH_PATTERN)


def _allowed(word: str, context: str, letter_codes: set[str]) -> bool:
    if word in WHITELIST or word in letter_codes:
        return True
    if any(word in address for address in EMAIL.findall(context)):
        return True
    if any(word in url for url in URL_PATH.findall(context)):
        return True
    return any(word in token and IDENTIFIER.match(token)
               for token in re.findall(r"[A-Za-z0-9-]+", context))


def check_isolation(en_client, am_client, from_dist: Path | None) -> Result:
    failures = []
    probes = [
        "/?lang=am", "/?language=am", "/?locale=am", "/?hl=am", "/?lang=en",
    ]
    baseline = skeleton_of(am_client.get("/").get_data(as_text=True))
    baseline_text = visible_text(am_client.get("/").get_data(as_text=True))

    for probe in probes:
        text = visible_text(am_client.get(probe).get_data(as_text=True))
        if text != baseline_text:
            failures.append(f"query {probe} changed the Amharic build's output")

    for header in ({"Accept-Language": "en-US,en"}, {"X-Language": "en"}):
        text = visible_text(am_client.get("/", headers=header).get_data(as_text=True))
        if text != baseline_text:
            failures.append(f"header {header} changed the Amharic build's output")

    am_client.set_cookie("lang", "en")
    if visible_text(am_client.get("/").get_data(as_text=True)) != baseline_text:
        failures.append("a 'lang' cookie changed the Amharic build's output")

    if from_dist is None:
        return check("6. isolation", not failures,
                     "runtime clean; artifact scan skipped (pass --from-dist)",
                     failures, pending=True)

    failures.extend(_scan_artifacts(from_dist))
    return check("6. isolation", not failures,
                 "no toggle at runtime; artifacts hold one language and no catalogue",
                 failures)


CROSS_LANGUAGE_MARKERS = {
    "en": ["Selam Airways", "Manage booking", "Baggage allowance", "Flight status",
           "Boarding pass", "Highland Class", "Selam Miles", "Economy Flex"],
    "am": ["ሰላም አየር መንገድ", "የቦታ ማስያዣን ማስተዳደር", "የሻንጣ ፈቃድ", "የበረራ ሁኔታ",
           "የመሳፈሪያ ፈቃድ", "ሃይላንድ ክላስ", "ሰላም ማይልስ"],
}

SCAN_SKIP = ("fonts/", ".db", ".woff2", ".ttf", "tasks/tasks_")


def _scan_artifacts(dist: Path) -> list[str]:
    import tempfile
    import zipfile

    problems: list[str] = []
    with tempfile.TemporaryDirectory() as workspace:
        root = Path(workspace)
        for language in ("en", "am"):
            archive = dist / f"selam-airways-{language}.zip"
            if not archive.exists():
                problems.append(f"{archive.name} not found -- run export.py")
                continue
            target = root / language
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(target)

            for name in ("en.json", "am.json", "glossary.json"):
                found = [str(p.relative_to(target)) for p in target.rglob(name)]
                if found:
                    problems.append(f"{language}: catalogue survived export -- {found}")
            if list(target.rglob("i18n")):
                problems.append(f"{language}: app/i18n/ survived export")

            other = "am" if language == "en" else "en"
            for marker in CROSS_LANGUAGE_MARKERS[other]:
                for path in target.rglob("*"):
                    if not path.is_file() or any(s in str(path) for s in SCAN_SKIP):
                        continue
                    try:
                        text = path.read_text("utf-8")
                    except (UnicodeDecodeError, OSError):
                        continue
                    if marker in text:
                        problems.append(
                            f"{language}: {other} string {marker!r} in "
                            f"{path.relative_to(target)}")
                        break
    return problems


def crawl_list(app) -> tuple[list[str], list[str]]:
    listing = ROOT / "spec" / "parity_routes.txt"
    if not listing.exists():
        return ["/"], []
    urls = [line.strip() for line in listing.read_text("utf-8").splitlines()
            if line.strip() and not line.startswith("#")]
    registered = {re.sub(r"<[^>]+>", "*", str(r)) for r in app.url_map.iter_rules()}
    built = [u for u in urls if _is_built(u, registered)]
    return built, [u for u in urls if u not in built]


def _is_built(url: str, registered: set[str]) -> bool:
    path = url.split("?", 1)[0].strip("/").split("/")
    for template in registered:
        parts = template.strip("/").split("/")
        if len(parts) == len(path) and all(p == "*" or p == q for p, q in zip(parts, path)):
            return True
    return False


def _authenticate(app, client, language: str) -> None:
    with sqlite3.connect(app.config["SELAM"].db_path) as conn:
        pnr, surname_en, surname_am = conn.execute(
            "select pnr, surname_en, surname_am from bookings order by id limit 1"
        ).fetchone()
    surname = surname_am if language == "am" else surname_en
    client.post("/manage", data={"pnr": pnr, "surname": surname}, follow_redirects=True)


def _prepare_pending_state(app, client, language: str) -> None:
    with sqlite3.connect(app.config["SELAM"].db_path) as conn:
        pnr, segment_id = conn.execute(
            "select b.pnr, s.id from bookings b join segments s on s.booking_id = b.id "
            "order by b.id, s.id limit 1").fetchone()
        seat_no = conn.execute(
            "select s.seat_no from seat_maps s join flights f on f.aircraft_id = s.aircraft_id "
            "join segments g on g.flight_id = f.id where g.id = ? and s.cabin = 'economy' "
            "and s.seat_no not in (select seat_no from seat_assignments where segment_id = ?) "
            "order by s.row desc limit 1", (segment_id, segment_id)).fetchone()[0]
        lounge_id = conn.execute(
            "select id from lounges where walk_in_price_usd > 0 order by id limit 1").fetchone()[0]
        first, last = conn.execute(
            f"select first_name_{language}, last_name_{language} from passengers "
            "order by id limit 1").fetchone()
        new_flight_id = conn.execute(
            "select f2.id from segments s join flights f on f.id = s.flight_id "
            "join flights f2 on f2.route_id = f.route_id and f2.id != f.id "
            "where s.id = ? and f2.status != 'cancelled' order by f2.id limit 1",
            (segment_id,)).fetchone()

    client.post(f"/manage/{pnr}/baggage", data={"segment_id": segment_id, "extra_kg": 10})
    client.post(f"/manage/{pnr}/seats", data={"segment_id": segment_id, "seat_no": seat_no})
    client.post(f"/manage/{pnr}/refund", data={"confirm": "1"})
    client.post(f"/manage/{pnr}/upgrade", data={"segment_id": segment_id, "confirm": "1"})
    if new_flight_id:
        client.post(f"/manage/{pnr}/change",
                    data={"segment_id": segment_id, "new_flight_id": new_flight_id[0]})
    client.post("/lounges/purchase",
                data={"lounge_id": lounge_id,
                      "passenger_name": f"{first} {last}", "guests": 1})


def letter_codes(app) -> set[str]:
    with sqlite3.connect(app.config["SELAM"].db_path) as conn:
        codes = set()
        for sql in ("select iata from airports", "select icao from airports",
                    "select code from fare_classes", "select code from aircraft_types",
                    "select pnr from bookings",
                    "select distinct country_code from airports"):
            codes.update(row[0] for row in conn.execute(sql) if row[0])
    return {c for c in codes if c.isalpha()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-dist", type=Path, default=None,
                        help="compare exported artifacts under this directory instead")
    args = parser.parse_args()

    en_app, am_app = create_app("en"), create_app("am")
    en_client, am_client = en_app.test_client(), am_app.test_client()
    routes, skipped = crawl_list(en_app)
    _authenticate(en_app, en_client, "en")
    _authenticate(am_app, am_client, "am")
    _prepare_pending_state(en_app, en_client, "en")
    _prepare_pending_state(am_app, am_client, "am")

    results = [
        check_routes(en_app, am_app),
        check_dom(en_client, am_client, routes),
        check_element_counts(en_client, am_client, routes),
        check_database(en_app, am_app),
        check_language_purity(en_client, am_client, routes, letter_codes(en_app)),
        check_isolation(en_client, am_client, args.from_dist),
    ]

    total = len(routes) + len(skipped)
    print(f"Parity check over {len(routes)} of {total} routes in spec/parity_routes.txt")
    if skipped:
        print(f"  {len(skipped)} skipped -- no view registered yet (see the countdown "
              f"in tests/test_no_dead_links.py)")
    print()
    failed = 0
    for result in results:
        if result.ok and result.pending:
            mark = "~"
        elif result.ok:
            mark = "PASS"
        else:
            mark = "FAIL"
            failed += 1
        print(f"  [{mark:^4}] {result.name}" + (f" -- {result.detail}" if result.detail else ""))
        for failure in result.failures[:10]:
            print(f"         {failure}")
        if len(result.failures) > 10:
            print(f"         ... and {len(result.failures) - 10} more")

    print()
    if failed:
        print(f"{failed} of 6 checks FAILED -- the builds are not structurally identical.")
        return 1
    print("All six checks pass. The builds differ only in the language of their strings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
