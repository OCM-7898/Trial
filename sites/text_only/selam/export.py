from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from bake import bake, remaining_calls
from strip_comments import STRIPPERS

DIST = ROOT / "dist"
STAGE = DIST / "build"
from app.lang import LANGS
from app.config import PORTS, DB_FILES as DB_NAMES


def others(lang: str) -> list[str]:
    return [l for l in LANGS if l != lang]

COPY = ["app", "run.py", "requirements.txt"]
EXCLUDE_DIRS = {"__pycache__", ".venv", "dist", "tests", "tools", "spec", ".git"}


def replaced(source: str, old: str, new: str, what: str) -> str:
    if old not in source:
        raise RuntimeError(
            f"export rewrite no longer matches the source: {what}. "
            f"Update export.py to match app/, or the artifact is built wrong.")
    return source.replace(old, new)


def log(step: str, detail: str = "") -> None:
    print(f"  {step:<44} {detail}")


def stage(lang: str) -> Path:
    target = STAGE / lang
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    for item in COPY:
        source = ROOT / item
        if source.is_dir():
            shutil.copytree(source, target / item,
                            ignore=shutil.ignore_patterns(*EXCLUDE_DIRS, "*.pyc"))
        else:
            shutil.copy2(source, target / item)

    (target / "data").mkdir()
    shutil.copy2(ROOT / "data" / "seed.db", target / "data" / "seed.db")

    if (ROOT / "tasks").exists():
        shutil.copytree(
            ROOT / "tasks", target / "tasks",
            ignore=shutil.ignore_patterns(*EXCLUDE_DIRS, "*.pyc",
                                          *[f"tasks_{o}.json" for o in others(lang)]))
    log("staged", str(target.relative_to(ROOT)))
    return target


def bake_strings(target: Path, lang: str) -> int:
    catalogue = json.loads((ROOT / "app" / "i18n" / f"{lang}.json").read_text("utf-8"))
    from app.brand import BRANDS
    for key, value in BRANDS.items():
        catalogue.setdefault(f"brand.{key}", value[lang])

    total = 0
    for path in sorted(target.rglob("*")):
        if path.suffix not in (".py", ".html") or not path.is_file():
            continue
        if "i18n" in path.parts and path.name in ("__init__.py",):
            continue
        source = path.read_text("utf-8")
        if "t(" not in source:
            continue
        baked, count = bake(source, catalogue, str(path.relative_to(target)))
        if count:
            path.write_text(baked, "utf-8")
            total += count
    log("baked t() calls", f"{total} across templates and python")
    return total


def restructure_i18n(target: Path, lang: str) -> None:
    i18n = target / "app" / "i18n"

    formats = (i18n / "formats.py").read_text("utf-8")
    formats = _keep_one_language_in_maps(formats, lang)
    formats = formats.replace(
        '"""Fixed date and number formats (SPEC.md 11.4).',
        '"""Fixed date and number formats (SPEC.md 11.4).\n\n'
        f'    Baked for the {lang} build by export.py: the other language\'s month\n'
        '    and weekday names are not present in this artifact.')
    (target / "app" / "formats.py").write_text(formats, "utf-8")

    labels = (i18n / "labels.py").read_text("utf-8")
    labels = re.sub(r"^from \. import t\n", "", labels, flags=re.M)
    labels = labels.replace(
        '"""Code -> label lookups, written with literal translation keys.',
        '"""Code -> label lookups.\n\n    Strings were baked by export.py; the'
        ' translation machinery is gone.')
    (target / "app" / "labels.py").write_text(labels, "utf-8")

    shutil.rmtree(i18n)
    rewritten = _rewrite_i18n_imports(target)
    log("removed app/i18n/", "catalogues, t(), glossary, fallback logic")
    log("rewired imports", f"{rewritten} modules no longer reference app.i18n")


IMPORT_REWRITES = (
    (r"^(\s*)from \.\.i18n\.formats import (.+)$",              r"\1from ..formats import \2"),
    (r"^(\s*)from \.\.i18n\.labels import (.+)$",               r"\1from ..labels import \2"),
    (r"^(\s*)from \.i18n\.formats import (.+)$",                 r"\1from .formats import \2"),
)

FLAT_IMPORT = re.compile(
    r"^(?P<indent>[ \t]*)from (?P<dots>\.+)i18n import (?P<names>[A-Za-z_, ]+)$", re.M)

DROPPED_NAMES = frozenset({"t", "latin_tokens"})


def _rewrite_flat_import(match: re.Match) -> str:
    names = [n.strip() for n in match["names"].split(",") if n.strip()]
    kept = [n for n in names if n not in DROPPED_NAMES]
    if not kept:
        return ""
    return f"{match['indent']}from {match['dots']} import {', '.join(kept)}"


def _rewrite_i18n_imports(target: Path) -> int:
    touched = 0
    for path in sorted((target / "app").rglob("*.py")):
        source = path.read_text("utf-8")
        if "i18n" not in source:
            continue
        updated = source
        for pattern, replacement in IMPORT_REWRITES:
            updated = re.sub(pattern, replacement, updated, flags=re.M)
        updated = FLAT_IMPORT.sub(_rewrite_flat_import, updated)
        updated = re.sub(r"\n\n\n+", "\n\n", updated)
        if updated != source:
            path.write_text(updated, "utf-8")
            touched += 1
    leftover = [
        str(p.relative_to(target))
        for p in (target / "app").rglob("*.py")
        if re.search(r"^\s*from [.]+i18n", p.read_text("utf-8"), flags=re.M)
    ]
    if leftover:
        raise RuntimeError(f"imports still pointing at app.i18n: {leftover}")
    return touched


def _keep_one_language_in_maps(source: str, lang: str) -> str:
    for other in others(lang):
        source = re.sub(rf'^\s*"{other}": \[[^\]]*\],\n', "", source, flags=re.M | re.S)
    return source


def bake_language_modules(target: Path, lang: str) -> None:
    lang_py = target / "app" / "lang.py"
    lang_py.write_text(f'''"""The language of this build.

Baked by export.py. This artifact is monolingual by construction: there is no
set_active(), a one-entry LANGS, and no catalogue to switch to. The value exists
only so the paired-column reader in app/models knows which half to read -- and
the other half has been dropped from the database anyway.
"""

ACTIVE = "{lang}"
#: The one language this build has (translated_kwargs iterates it).
LANGS = (ACTIVE,)


def active() -> str:
    return ACTIVE


def col(field: str) -> str:
    return f"{{field}}_{lang}"
''', "utf-8")

    config = (target / "app" / "config.py").read_text("utf-8")
    config = replaced(
        config,
        'PORTS = {"en": 7770, "am": 7771, "bn": 7772, "hi": 7773, "ur": 7774}\n'
        'DB_FILES = {"en": "selam_en.db", "am": "selam_am.db", "bn": "selam_bn.db",\n'
        '            "hi": "selam_hi.db", "ur": "selam_ur.db"}',
        f'PORT = {PORTS[lang]}\nDB_FILE = "{DB_NAMES[lang]}"\nLANGUAGE = "{lang}"',
        "the PORTS/DB_FILES maps in config.py")

    start = config.index("    @classmethod\n    def for_language(")
    end = config.index("\n", config.index("        )", start)) + 1
    config = (config[:start] + '''    @classmethod
    def build(cls) -> "Config":
        """The one configuration this artifact can have."""
        return cls(
            language=LANGUAGE,
            port=PORT,
            db_path=ROOT / "data" / DB_FILE,
            generated_dir=ROOT / "app" / "static" / "generated",
            secret_key=SECRET_KEY,
            session_cookie=SESSION_COOKIE,
        )
''' + config[end:])
    config = replaced(
        config,
        'LANGUAGE = "%s"' % lang,
        'LANGUAGE = "%s"\nSECRET_KEY = "selam-benchmark-fixed-key-%s"\n'
        'SESSION_COOKIE = "selam_session_%s"' % (lang, lang, lang),
        "the baked language constant in config.py")
    (target / "app" / "config.py").write_text(config, "utf-8")

    factory = (target / "app" / "__init__.py").read_text("utf-8")
    factory = factory.replace("from . import i18n\n", "")
    factory = factory.replace("from .i18n import formats, t", "from . import formats")
    factory = factory.replace('def create_app(language: str = "en") -> Flask:\n'
                              "    config = Config.for_language(language)\n"
                              "    i18n.set_language(config.language)\n",
                              "def create_app() -> Flask:\n    config = Config.build()\n")
    factory = re.sub(r"^\s*t=t,\n", "", factory, flags=re.M)
    factory = factory.replace("brand=lambda key: BRANDS[key][lang],",
                              f'brand=lambda key: BRANDS[key]["{lang}"],')

    factory = re.sub(r"    _bind_language\(app, config\)\n", "", factory)
    factory = re.sub(r"def _bind_language.*?\n\ndef _register_error_handlers",
                     "def _register_error_handlers", factory, flags=re.S)
    (target / "app" / "__init__.py").write_text(factory, "utf-8")

    (target / "run.py").write_text(f'''"""Run {"Selam Airways" if lang == "en" else "ሰላም አየር መንገድ"}.

    python run.py

There is no --lang flag: this artifact contains one language and cannot express
the other (SPEC.md 4).
"""
import argparse

from app import create_app
from app.config import PORT


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    create_app().run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
''', "utf-8")
    log("baked language into config", f'{lang}, port {PORTS[lang]}, {DB_NAMES[lang]}')


def paired_fields() -> dict[str, list[str]]:
    from app.models import Base

    pairs = {}
    for name, table in sorted(Base.metadata.tables.items()):
        columns = {c.name for c in table.columns}
        fields = sorted({c[:-3] for c in columns if c.endswith("_en")}
                        & {c[:-3] for c in columns if c.endswith("_am")})
        if fields:
            pairs[name] = fields
    return pairs


def drop_other_language(target: Path, lang: str) -> int:
    pairs = paired_fields()

    database = target / "data" / "seed.db"
    dropped = 0
    with sqlite3.connect(database) as conn:
        for table, fields in pairs.items():
            for field in fields:
              for other in others(lang):
                column = f"{field}_{other}"
                for (name, ddl) in conn.execute(
                    "select name, sql from sqlite_master where type='index' and tbl_name=?",
                    (table,),
                ).fetchall():
                    if ddl and re.search(rf"\b{re.escape(column)}\b", ddl):
                        conn.execute(f'drop index "{name}"')
                conn.execute(f'alter table "{table}" drop column "{column}"')
                dropped += 1
        conn.commit()
    with sqlite3.connect(database) as conn:
        conn.execute("vacuum")

    for path in sorted((target / "app" / "models").glob("*.py")):
        source = path.read_text("utf-8")
        cleaned = source
        for other in others(lang):
            cleaned = re.sub(rf"^\s*\w+_{other}: Mapped\[[^\]]*\] = mapped_column\([^\n]*\n",
                             "", cleaned, flags=re.M)
        cleaned = re.sub(rf"(\w+)\.(\w+)_am if active\(\) == \"am\" else \1\.\2_en",
                         rf"\1.\2_{lang}", cleaned)
        if cleaned != source:
            path.write_text(cleaned, "utf-8")

    for path in sorted((target / "app").rglob("*.py")):
        source = path.read_text("utf-8")
        cleaned = re.sub(rf"(\w+)\.(\w+)_am if active\(\) == \"am\" else \1\.\2_en",
                         rf"\1.\2_{lang}", source)
        cleaned = re.sub(rf"f\"(\w+)_\{{language\}}\"", rf'f"\1_{lang}"', cleaned)
        if cleaned != source:
            path.write_text(cleaned, "utf-8")

    log(f"dropped *_{{{','.join(others(lang))}}} columns", f"{dropped} columns across {len(pairs)} tables")
    return dropped


def bake_brands(target: Path, lang: str) -> None:
    from app.brand import BRANDS

    path = target / "app" / "brand.py"
    source = path.read_text("utf-8")
    entries = "\n".join(
        f'    "{key}": {value[lang]!r},' for key, value in BRANDS.items()
    )
    source = re.sub(
        r"BRANDS = \{.*?\n\}",
        "BRANDS = {\n" + entries + "\n}",
        source, flags=re.S,
    )
    source = source.replace("def brand(key: str, lang: str) -> str:\n    return BRANDS[key][lang]",
                            "def brand(key: str) -> str:\n    return BRANDS[key]")
    path.write_text(source, "utf-8")

    factory = target / "app" / "__init__.py"
    text = factory.read_text("utf-8")
    text = text.replace(f'brand=lambda key: BRANDS[key]["{lang}"],', "brand=BRANDS.__getitem__,")
    factory.write_text(text, "utf-8")
    log("baked brand names", f"{len(BRANDS)} marks, {lang} only")


def strip_commentary(target: Path) -> int:
    stripped = 0
    for path in sorted(target.rglob("*")):
        if not path.is_file() or path.suffix not in STRIPPERS:
            continue
        source = path.read_text("utf-8")
        cleaned = STRIPPERS[path.suffix](source)
        if cleaned != source:
            path.write_text(cleaned, "utf-8")
            stripped += 1
    log("stripped commentary", f"{stripped} files (source repo keeps it)")
    return stripped


READMES = {
 "en": """# Selam Airways

A self-contained, offline benchmark environment. Fictional airline; no real
trademarks; no network access required.

## Quickstart

```bash
pip install -r requirements.txt
python run.py
# open http://localhost:7770
```

## Notes

- Every date derives from a frozen clock set to 16 March 2026.
- `POST /reset` restores the seeded database and returns its hash.
- No payment is ever processed; purchase flows stop at a review page.
""",
 "am": """# ሰላም አየር መንገድ

ራሱን የቻለ፣ ከመስመር ውጭ የሚሠራ የሙከራ አካባቢ። ምናባዊ አየር መንገድ፤ እውነተኛ የንግድ ምልክቶች የሉም፤
የኢንተርኔት ግንኙነት አያስፈልገውም።

## በፍጥነት ለመጀመር

```bash
pip install -r requirements.txt
python run.py
# http://localhost:7771 ን ይክፈቱ
```

## ማስታወሻዎች

- ሁሉም ቀኖች መጋቢት 16፣ 2026 ላይ ከቆመ ሰዓት ይመነጫሉ።
- `POST /reset` የተዘራውን ዳታቤዝ ይመልሳል፤ ሃሹንም ይመልሳል።
- ምንም ክፍያ አይከናወንም፤ የግዢ ሂደቶች በማጠቃለያ ገጽ ላይ ይቆማሉ።
""",
 "bn": """# সেলাম এয়ারওয়েজ

একটি স্বয়ংসম্পূর্ণ, অফলাইন বেঞ্চমার্ক পরিবেশ। কাল্পনিক এয়ারলাইন; কোনো বাস্তব ট্রেডমার্ক নেই;
ইন্টারনেট সংযোগ প্রয়োজন নেই।

## দ্রুত শুরু

```bash
pip install -r requirements.txt
python run.py
# http://localhost:7772 খুলুন
```

## নোট

- প্রতিটি তারিখ 16 মার্চ 2026-এ স্থির একটি ঘড়ি থেকে আসে।
- `POST /reset` সিড করা ডেটাবেস পুনরুদ্ধার করে এবং তার হ্যাশ ফেরত দেয়।
- কোনো পরিশোধ কখনও প্রক্রিয়া করা হয় না; ক্রয় প্রবাহ একটি পর্যালোচনা পৃষ্ঠায় থামে।
""",
 "hi": """# सेलाम एयरवेज़

एक स्वतंत्र, ऑफ़लाइन बेंचमार्क वातावरण। काल्पनिक एयरलाइन; कोई वास्तविक ट्रेडमार्क नहीं;
इंटरनेट कनेक्शन की आवश्यकता नहीं।

## त्वरित शुरुआत

```bash
pip install -r requirements.txt
python run.py
# http://localhost:7773 खोलें
```

## टिप्पणियाँ

- हर तिथि 16 मार्च 2026 पर स्थिर घड़ी से आती है।
- `POST /reset` सीड किया गया डेटाबेस बहाल करता है और उसका हैश लौटाता है।
- कोई भुगतान कभी संसाधित नहीं होता; खरीद प्रवाह समीक्षा पृष्ठ पर रुकते हैं।
""",
 "ur": """# سلام ایئرویز

ایک خود مکتفی، آف لائن بینچ مارک ماحول۔ فرضی ایئرلائن؛ کوئی حقیقی ٹریڈ مارک نہیں؛
انٹرنیٹ کنکشن درکار نہیں۔

## فوری آغاز

```bash
pip install -r requirements.txt
python run.py
# http://localhost:7774 کھولیں
```

## نوٹس

- ہر تاریخ 16 مارچ 2026 پر منجمد گھڑی سے آتی ہے۔
- `POST /reset` سیڈ شدہ ڈیٹا بیس بحال کرتا ہے اور اس کا ہیش واپس کرتا ہے۔
- کوئی ادائیگی کبھی پروسیس نہیں ہوتی؛ خریداری کے مراحل جائزہ صفحے پر رکتے ہیں۔
""",
}


NOTICES = {
 "en": """# Notice

**Selam Airways** is a fictional airline created for academic benchmarking. It is not a real
company. The name, the `SM` airline code, the flight numbers, the loyalty programme, the cabin
names, the partner brands, and every logo and wordmark in this artifact are original and
invented for this project.

No trademark of any real airline appears here.

Geography is real: city names, airport names and IATA/ICAO codes are factual public
information, retained because realistic content depends on it.

All imagery is original flat-colour SVG. No photography has been retrieved from any
third-party website. The bundled typeface is Noto Sans Ethiopic, used under the SIL Open
Font License 1.1; its licence travels with it in `app/static/fonts/OFL.txt`.

This environment exists to measure web-agent performance. It is not a booking system: no
payment is ever processed, and every purchase flow terminates at a review page.
""",
 "am": """# ማስታወቂያ

**ሰላም አየር መንገድ** ለአካዳሚክ ሙከራ የተፈጠረ ምናባዊ አየር መንገድ ነው። እውነተኛ ኩባንያ አይደለም። ስሙ፣ የ`SM`
የአየር መንገድ ኮድ፣ የበረራ ቁጥሮች፣ የታማኝነት መርሐ ግብሩ፣ የጉዞ ክፍል ስሞች፣ የአጋር ምልክቶች፣ እንዲሁም በዚህ ውጤት
ውስጥ ያሉ ሁሉም አርማዎችና ጽሑፋዊ ምልክቶች ለዚህ ፕሮጀክት የተፈጠሩ ኦሪጅናል ሥራዎች ናቸው።

የማንኛውም እውነተኛ አየር መንገድ የንግድ ምልክት እዚህ አይገኝም።

ጂኦግራፊው እውነተኛ ነው፦ የከተማ ስሞች፣ የአየር ማረፊያ ስሞችና የIATA/ICAO ኮዶች ተጨባጭ የሕዝብ መረጃ ናቸው፤
ተጨባጭ ይዘት ስለሚያስፈልጋቸውም ተይዘዋል።

ሁሉም ምስሎች ኦሪጅናል ነጠላ-ቀለም SVG ናቸው። ከሦስተኛ ወገን ድረ ገጽ ምንም ፎቶግራፍ አልተወሰደም። አብሮ የቀረበው
ፊደል ኖቶ ሳንስ ኢትዮፒክ ሲሆን በSIL Open Font License 1.1 ይጠቀማል፤ ፈቃዱም በ`app/static/fonts/OFL.txt`
ውስጥ አብሮ ይገኛል።

ይህ አካባቢ የድር ወኪሎችን አፈጻጸም ለመለካት የተፈጠረ ነው። የቦታ ማስያዣ ሥርዓት አይደለም፦ ምንም ክፍያ አይከናወንም፤
እያንዳንዱም የግዢ ሂደት በማጠቃለያ ገጽ ላይ ይቆማል።
""",
 "bn": """# বিজ্ঞপ্তি

**সেলাম এয়ারওয়েজ** একাডেমিক বেঞ্চমার্কিংয়ের জন্য তৈরি একটি কাল্পনিক এয়ারলাইন। এটি কোনো বাস্তব কোম্পানি
নয়। নাম, `SM` এয়ারলাইন কোড, ফ্লাইট নম্বর, লয়্যালটি প্রোগ্রাম, কেবিনের নাম, পার্টনার ব্র্যান্ড এবং এই
আর্টিফ্যাক্টের প্রতিটি লোগো ও ওয়ার্ডমার্ক মৌলিক এবং এই প্রকল্পের জন্য উদ্ভাবিত।

কোনো বাস্তব এয়ারলাইনের ট্রেডমার্ক এখানে নেই।

ভূগোল বাস্তব: শহরের নাম, বিমানবন্দরের নাম এবং IATA/ICAO কোড প্রকাশ্য তথ্য, বাস্তবসম্মত বিষয়বস্তুর জন্য রাখা।

সব ছবি মৌলিক ফ্ল্যাট-কালার SVG। কোনো তৃতীয় পক্ষের ওয়েবসাইট থেকে কোনো ফটোগ্রাফ নেওয়া হয়নি। সংযুক্ত
টাইপফেস Noto Sans Ethiopic, SIL Open Font License 1.1-এর অধীনে; এর লাইসেন্স `app/static/fonts/OFL.txt`-এ
সঙ্গে থাকে।

এই পরিবেশ ওয়েব-এজেন্টের কর্মক্ষমতা মাপার জন্য। এটি কোনো বুকিং সিস্টেম নয়: কোনো পরিশোধ কখনও প্রক্রিয়া
করা হয় না, এবং প্রতিটি ক্রয় প্রবাহ একটি পর্যালোচনা পৃষ্ঠায় শেষ হয়।
""",
 "hi": """# सूचना

**सेलाम एयरवेज़** अकादमिक बेंचमार्किंग के लिए बनाई गई एक काल्पनिक एयरलाइन है। यह वास्तविक कंपनी नहीं है।
नाम, `SM` एयरलाइन कोड, उड़ान संख्याएँ, लॉयल्टी कार्यक्रम, केबिन के नाम, पार्टनर ब्रांड और इस आर्टिफ़ैक्ट का
हर लोगो और वर्डमार्क मौलिक हैं और इस परियोजना के लिए गढ़े गए हैं।

किसी वास्तविक एयरलाइन का कोई ट्रेडमार्क यहाँ नहीं है।

भूगोल वास्तविक है: शहरों के नाम, हवाई अड्डों के नाम और IATA/ICAO कोड सार्वजनिक तथ्य हैं, यथार्थवादी
सामग्री के लिए रखे गए हैं।

सभी चित्र मौलिक फ़्लैट-कलर SVG हैं। किसी तीसरे पक्ष की वेबसाइट से कोई फ़ोटो नहीं ली गई। बंडल किया गया
टाइपफ़ेस Noto Sans Ethiopic है, SIL Open Font License 1.1 के तहत; इसका लाइसेंस `app/static/fonts/OFL.txt`
में साथ है।

यह वातावरण वेब-एजेंट प्रदर्शन मापने के लिए है। यह बुकिंग सिस्टम नहीं है: कोई भुगतान कभी संसाधित नहीं होता,
और हर खरीद प्रवाह समीक्षा पृष्ठ पर समाप्त होता है।
""",
 "ur": """# اطلاع

**سلام ایئرویز** علمی بینچ مارکنگ کے لیے بنائی گئی ایک فرضی ایئرلائن ہے۔ یہ حقیقی کمپنی نہیں ہے۔ نام،
`SM` ایئرلائن کوڈ، پرواز نمبر، لائلٹی پروگرام، کیبن کے نام، پارٹنر برانڈ اور اس آرٹیفیکٹ کا ہر لوگو اور
ورڈ مارک اصل ہیں اور اس منصوبے کے لیے ایجاد کیے گئے ہیں۔

کسی حقیقی ایئرلائن کا کوئی ٹریڈ مارک یہاں نہیں ہے۔

جغرافیہ حقیقی ہے: شہروں کے نام، ہوائی اڈوں کے نام اور IATA/ICAO کوڈ عوامی حقائق ہیں، حقیقت پسندانہ مواد کے
لیے رکھے گئے ہیں۔

تمام تصاویر اصل فلیٹ کلر SVG ہیں۔ کسی تیسرے فریق کی ویب سائٹ سے کوئی تصویر نہیں لی گئی۔ شامل کردہ
ٹائپ فیس Noto Sans Ethiopic ہے، SIL Open Font License 1.1 کے تحت؛ اس کا لائسنس `app/static/fonts/OFL.txt`
میں ساتھ ہے۔

یہ ماحول ویب ایجنٹ کی کارکردگی ناپنے کے لیے ہے۔ یہ بکنگ سسٹم نہیں ہے: کوئی ادائیگی کبھی پروسیس نہیں ہوتی،
اور ہر خریداری کا مرحلہ جائزہ صفحے پر ختم ہوتا ہے۔
""",
}


def write_readme(target: Path, lang: str) -> None:
    (target / "README.md").write_text(READMES[lang], "utf-8")
    (target / "NOTICE.md").write_text(NOTICES[lang], "utf-8")


def make_zip(target: Path, lang: str) -> Path:
    DIST.mkdir(exist_ok=True)
    archive = DIST / f"selam-airways-{lang}.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(target.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(target))
    log("wrote archive", f"{archive.relative_to(ROOT)} "
                         f"({archive.stat().st_size / 1_000_000:.1f} MB)")
    return archive


def verify(target: Path, lang: str) -> list[str]:
    problems: list[str] = []

    for path in sorted(target.rglob("*")):
        if path.suffix not in (".py", ".html") or not path.is_file():
            continue
        leftovers = remaining_calls(path.read_text("utf-8"), path.suffix == ".py")
        if leftovers:
            problems.append(f"{path.relative_to(target)}: unbaked t() -- {leftovers[:2]}")

    LICENCE_FILES = {"app/static/fonts/OFL.txt"}

    prose_in_static = sorted(
        str(p.relative_to(target))
        for p in (target / "app" / "static").rglob("*")
        if p.is_file() and p.suffix.lower() in (".md", ".txt", ".rst")
        and str(p.relative_to(target)) not in LICENCE_FILES)
    if prose_in_static:
        problems.append(
            f"prose files under static/ ship in both builds: {prose_in_static}")

    for name in (*[f"{o}.json" for o in others(lang)], f"{lang}.json", "glossary.json"):
        found = list(target.rglob(name))
        if found:
            problems.append(f"catalogue survived export: {[str(f.relative_to(target)) for f in found]}")
    if (target / "app" / "i18n").exists():
        problems.append("app/i18n/ still present")

    checker = target / "_export_check.py"
    checker.write_text('''
import json, re, socket, sys
sys.path.insert(0, ".")
from app import create_app

app = create_app()

# The artifact must run on an air-gapped machine (SPEC.md 2, 17). Everything
# below this line runs with sockets that raise, so anything reaching for the
# network fails here rather than in someone's evaluation run. The app is created
# first: SQLite goes through the filesystem, but the font registration and the
# catalogue load happen on the first request and a failure there would be
# reported as a network error it is not.


class _NoNetwork(socket.socket):
    def __init__(self, *args, **kwargs):
        raise AssertionError("the exported build opened a socket")


app.test_client().get("/")
socket.socket = _NoNetwork
socket.create_connection = _NoNetwork
client = app.test_client()
registered = {re.sub(r"<[^>]+>", "*", str(r)) for r in app.url_map.iter_rules()}


def is_built(url):
    parts = url.split("?")[0].strip("/").split("/")
    for template in registered:
        candidate = template.strip("/").split("/")
        if len(candidate) == len(parts) and all(
            a == "*" or a == b for a, b in zip(candidate, parts)
        ):
            return True
    return False


urls = [line.strip() for line in open("parity_routes.txt", encoding="utf-8")
        if line.strip() and not line.startswith("#")]
checked, bad = 0, []
for url in urls:
    if not is_built(url):
        continue
    checked += 1
    response = client.get(url)
    if response.status_code >= 500:
        bad.append([url, response.status_code])


# ---------------------------------------------------------------- write paths
# The GET crawl above cannot reach a POST handler, and two of the bugs that
# reached a shipped zip were on POST paths that named a dropped language column:
# enrollment (TypeError) and manage-booking retrieval (AttributeError, via the
# check-in eligibility rules). Both were invisible to a GET-only crawl.
#
# So: log in to a booking, walk the flows behind that session, and submit the
# forms an agent submits. Nothing here needs to *succeed* -- a 400 on a rejected
# form is a working validator. Only 5xx counts as a failure.
from sqlalchemy import select
from app import db as database
from app.models.booking import Booking
from app.models.network import Flight

with app.app_context():
    session = database.session()
    booking = session.scalars(select(Booking).order_by(Booking.id)).first()
    pnr, surname = booking.pnr, booking.surname
    flight_no = session.scalars(select(Flight.flight_no).order_by(Flight.id)).first()

posts = [
    ("/manage", {"pnr": pnr, "surname": surname}),
    ("/miles/join", {"first_name": "Test", "last_name": "Person",
                     "email": "export.check@example.com", "country_code": "ET",
                     "dob": "1990-01-01"}),
    ("/miles/claim", {"member_no": "SM1000001", "ticket_no": "0712345678901",
                      "flight_no": flight_no, "date": "2026-02-02"}),
    ("/help/feedback", {"category": "baggage", "name": "Test Person",
                        "email": "export.check@example.com", "message": "Check."}),
    ("/services/assistance", {"pnr": pnr, "assistance_code": "WCHR",
                              "name": "Test Person"}),
    ("/vouchers/buy", {"recipient": "Test Person", "amount": "100"}),
    ("/flight-status/subscribe", {"flight_no": flight_no,
                                  "email": "export.check@example.com"}),
    ("/stopover/book", {"pnr": pnr, "package_id": "1"}),
    ("/cargo/quote", {"origin": "ADD", "destination": "NBO", "weight_kg": "40",
                      "length_cm": "50", "width_cm": "40", "height_cm": "30"}),
]

posted = 0
for url, data in posts:
    if not is_built(url):
        continue
    posted += 1
    response = client.post(url, data=data, follow_redirects=True)
    if response.status_code >= 500:
        bad.append([f"POST {url}", response.status_code])

# Pages behind the retrieval session, unreachable in the crawl above because it
# uses a fresh client per URL and never authenticates.
for url in (f"/manage/{pnr}", f"/manage/{pnr}/seats", f"/manage/{pnr}/change",
            f"/manage/{pnr}/refund", f"/manage/{pnr}/baggage",
            f"/manage/{pnr}/upgrade", f"/manage/{pnr}/itinerary.pdf",
            f"/checkin?pnr={pnr}&surname={surname}"):
    if not is_built(url.split("?")[0]):
        continue
    checked += 1
    response = client.get(url)
    if response.status_code >= 500:
        bad.append([url, response.status_code])

print(json.dumps({"checked": checked, "posted": posted, "bad": bad}))
''', "utf-8")

    shutil.copy2(ROOT / "spec" / "parity_routes.txt", target / "parity_routes.txt")
    result = subprocess.run([sys.executable, "_export_check.py"], cwd=target,
                            capture_output=True, text=True)
    (target / "parity_routes.txt").unlink()
    checker.unlink()

    if result.returncode != 0:
        problems.append("the exported build failed to boot:\n" + result.stderr[-1500:])
    else:
        report = json.loads(result.stdout.strip().splitlines()[-1])
        if report["bad"]:
            problems.append(f"routes returning 5xx: {report['bad'][:5]}")
        log("crawled exported build",
            f"{report['checked']} routes + {report['posted']} form submissions, "
            f"{len(report['bad'])} server errors")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", choices=LANGS, default=None,
                        help="export only one build (default: all)")
    parser.add_argument("--keep-stage", action="store_true",
                        help="leave dist/build/ in place for inspection")
    args = parser.parse_args()

    if not (ROOT / "data" / "seed.db").exists():
        sys.exit("data/seed.db is missing -- run `python seed.py` first")

    failed = False
    for lang in ([args.lang] if args.lang else LANGS):
        print(f"\n{lang} build")
        target = stage(lang)
        bake_strings(target, lang)
        restructure_i18n(target, lang)
        bake_language_modules(target, lang)
        drop_other_language(target, lang)
        bake_brands(target, lang)
        strip_commentary(target)
        write_readme(target, lang)

        problems = verify(target, lang)
        if problems:
            failed = True
            print("  FAILED:")
            for problem in problems:
                print(f"    {problem}")
            continue
        make_zip(target, lang)

    if not args.keep_stage and STAGE.exists():
        shutil.rmtree(STAGE)

    if failed:
        print("\nExport failed. No usable artifact was produced.")
        return 1
    print("\nBoth artifacts built and verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
