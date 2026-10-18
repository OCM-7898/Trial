from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "spec" / "seed_data"
HAND = ROOT / "spec" / "hand_translations"
I18N = ROOT / "app" / "i18n"
TASKS = ROOT / "tasks"

LISTS = {
    "aircraft": [("aircraft", "code")],
    "airports": [("airports", "iata")],
    "bookings": [("bookings", "pnr"), ("bookings.passengers", "id"),
                 ("bookings.segments", "id")],
    "contact_offices": [("contact_offices", "country_code")],
    "content_pages": [("content_pages", "slug")],
    "extras": [("promotions", "code"), ("entertainment_items", "id"),
               ("travel_requirements", "country_code")],
    "fare_classes": [("fare_classes", "code")],
    "lounges": [("lounges", "id")],
    "loyalty": [("loyalty_members", "member_no"), ("miles_transactions", "id")],
    "onboard": [("wifi_packages", "name_en"), ("special_meal_codes", "code"),
                ("meal_menus", "id")],
    "partners": [("hotel_rooms", "id"), ("visa_types", "code"),
                 ("rail_connections", "id"), ("car_offers", "id"),
                 ("insurance_products", "code")],
    "special_baggage": [("special_baggage_items", "id")],
    "stopover": [("stopover_packages", "id")],
}


def _load(name):
    return yaml.safe_load((SEED / f"{name}.yaml").read_text("utf-8"))


def _rows(doc, list_key):
    if "." in list_key:
        parent, child = list_key.split(".", 1)
        return [r for prow in doc[parent] for r in prow.get(child, [])]
    rows = doc[list_key]
    if not isinstance(rows, list):
        raise SystemExit(f"{list_key} is not a list")
    return rows


def extract():
    src = {}
    for fname, lists in LISTS.items():
        doc = _load(fname)
        for list_key, key_field in lists:
            for row in _rows(doc, list_key):
                rk = str(row[key_field])
                for k, v in row.items():
                    if k.endswith("_en") and v not in (None, ""):
                        src[f"{list_key}|{rk}|{k[:-3]}"] = v
    HAND.mkdir(exist_ok=True)
    (HAND / "_source_en.json").write_text(
        json.dumps(src, ensure_ascii=False, indent=1), "utf-8")
    ui = json.loads((I18N / "en.json").read_text("utf-8"))
    (HAND / "_source_ui_en.json").write_text(
        json.dumps(ui, ensure_ascii=False, indent=1), "utf-8")
    tasks = json.loads((TASKS / "tasks_en.json").read_text("utf-8"))
    (HAND / "_source_tasks_en.json").write_text(
        json.dumps({str(t["task_id"]): t["intent"] for t in tasks},
                   ensure_ascii=False, indent=1), "utf-8")
    print(f"seeded strings: {len(src)} ({sum(len(v) for v in src.values()):,} chars)")
    print(f"ui strings:     {len(ui)}")
    print(f"task intents:   {len(tasks)}")


def merge(lang):
    src = json.loads((HAND / "_source_en.json").read_text("utf-8"))
    by_value = {}
    for k, v in src.items():
        by_value.setdefault(v, []).append(k)
    out, vmap = {}, {}
    for f in sorted((HAND / "chunks" / lang).glob("*.json")):
        if f.name == "tasks.json":
            continue
        for k, v in json.loads(f.read_text("utf-8")).items():
            if k.startswith("="):
                vmap[k[1:]] = v
            else:
                out[k] = v
    for value, keys in by_value.items():
        if value in vmap:
            for k in keys:
                out.setdefault(k, vmap[value])
    unknown = [v for v in vmap if v not in by_value]
    if unknown:
        print(f"  ! {len(unknown)} value-map entries match no source value, e.g. {unknown[:4]}")
    (HAND / f"{lang}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), "utf-8")
    ui_parts = sorted((HAND / "chunks" / lang / "ui").glob("*.json"))
    if ui_parts:
        ui = {}
        for f in ui_parts:
            ui.update(json.loads(f.read_text("utf-8")))
        (HAND / f"ui_{lang}.json").write_text(json.dumps(ui, ensure_ascii=False, indent=1), "utf-8")
        print(f"[{lang}] ui: {len(ui)} keys from {len(ui_parts)} part(s)")
    tpath = HAND / "chunks" / lang / "tasks.json"
    if tpath.exists():
        (HAND / f"tasks_{lang}.json").write_text(tpath.read_text("utf-8"), "utf-8")
    missing = [k for k in src if k not in out]
    print(f"[{lang}] merged {len(out)}/{len(src)} seeded keys; missing {len(missing)}")
    if missing:
        import collections
        c = collections.Counter(k.split("|")[0] + "." + k.split("|")[2] for k in missing)
        for t, n in sorted(c.items()):
            print(f"    {t}: {n}")


def _hand(lang):
    seeded = json.loads((HAND / f"{lang}.json").read_text("utf-8"))
    ui = json.loads((HAND / f"ui_{lang}.json").read_text("utf-8"))
    tasks = json.loads((HAND / f"tasks_{lang}.json").read_text("utf-8"))
    return seeded, ui, tasks


def check(lang, strict=True):
    src = json.loads((HAND / "_source_en.json").read_text("utf-8"))
    ui_src = json.loads((HAND / "_source_ui_en.json").read_text("utf-8"))
    tasks_src = json.loads((HAND / "_source_tasks_en.json").read_text("utf-8"))
    seeded, ui, tasks = _hand(lang)
    problems = []
    miss = [k for k in src if k not in seeded]
    extra = [k for k in seeded if k not in src]
    if miss:
        problems.append(f"seeded: {len(miss)} missing, e.g. {miss[:5]}")
    if extra:
        problems.append(f"seeded: {len(extra)} unknown keys, e.g. {extra[:5]}")
    umiss = [k for k in ui_src if k not in ui]
    uextra = [k for k in ui if k not in ui_src]
    if umiss:
        problems.append(f"ui: {len(umiss)} missing, e.g. {umiss[:5]}")
    if uextra:
        problems.append(f"ui: {len(uextra)} unknown keys, e.g. {uextra[:5]}")
    import re
    for k, v in ui_src.items():
        if k in ui:
            a = set(re.findall(r"\{(\w+)\}", v))
            b = set(re.findall(r"\{(\w+)\}", ui[k]))
            if a != b:
                problems.append(f"ui placeholder mismatch {k}: {a} vs {b}")
    tmiss = [k for k in tasks_src if k not in tasks]
    if tmiss:
        problems.append(f"tasks: {len(tmiss)} missing: {tmiss}")
    empty = [k for k, v in list(seeded.items()) + list(ui.items()) + list(tasks.items())
             if not str(v).strip()]
    if empty:
        problems.append(f"{len(empty)} empty values, e.g. {empty[:5]}")
    print(f"[{lang}] seeded {len(seeded)}/{len(src)}  ui {len(ui)}/{len(ui_src)}  "
          f"tasks {len(tasks)}/{len(tasks_src)}")
    for p in problems:
        print("  !", p)
    if strict and problems:
        raise SystemExit(f"{lang}: pack incomplete")
    return not problems


def apply(langs):
    for lang in langs:
        check(lang, strict=True)
    packs = {lang: _hand(lang) for lang in langs}
    for fname, lists in LISTS.items():
        path = SEED / f"{fname}.yaml"
        doc = _load(fname)
        header = "".join(l for l in path.read_text("utf-8").splitlines(keepends=True)
                         if l.startswith("#"))
        for list_key, key_field in lists:
            for row in _rows(doc, list_key):
                rk = str(row[key_field])
                for k in list(row.keys()):
                    if not k.endswith("_en"):
                        continue
                    field = k[:-3]
                    for lang in langs:
                        seeded = packs[lang][0]
                        if row[k] in (None, ""):
                            row[f"{field}_{lang}"] = row[k]
                        else:
                            row[f"{field}_{lang}"] = seeded[f"{list_key}|{rk}|{field}"]
        path.write_text(header + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False,
                                                width=88), "utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    for lang in langs:
        _, ui, tasks = packs[lang]
        (I18N / f"{lang}.json").write_text(
            json.dumps(ui, ensure_ascii=False, indent=2) + "\n", "utf-8")
        en_tasks = json.loads((TASKS / "tasks_en.json").read_text("utf-8"))
        seeded = packs[lang][0]
        out = []
        for t in en_tasks:
            t = json.loads(json.dumps(t))
            t["intent"] = tasks[str(t["task_id"])]
            params = t.get("instantiation", {}).get("parameters", {})
            if "surname" in params and "pnr" in params:
                params["surname"] = seeded[f"bookings|{params['pnr']}|surname"]
            out.append(t)
        (TASKS / f"tasks_{lang}.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2) + "\n", "utf-8")
        print(f"wrote app/i18n/{lang}.json and tasks/tasks_{lang}.json")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "extract":
        extract()
    elif cmd == "merge":
        for lang in sys.argv[2:]:
            merge(lang)
    elif cmd == "check":
        check(sys.argv[2], strict=False)
    elif cmd == "apply":
        apply(sys.argv[2:])
    else:
        raise SystemExit("usage: python tools/apply_hand_languages.py extract | check <lang> | apply <lang> [<lang> ...]")
