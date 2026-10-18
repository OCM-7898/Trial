import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from l10n import (CATEGORY_AM, CATEGORY_BN, CATEGORY_HI, CATEGORY_UR,
                  COLOUR_LABEL, DESC_PHRASES_AM, DESC_PHRASES_BN,
                  DESC_PHRASES_HI, DESC_PHRASES_UR, MATERIAL_LABEL,
                  translate_name)

CATEGORY = {"hi": CATEGORY_HI, "bn": CATEGORY_BN,
            "ur": CATEGORY_UR, "am": CATEGORY_AM}
DESC_PHRASES = {"hi": DESC_PHRASES_HI, "bn": DESC_PHRASES_BN,
                "ur": DESC_PHRASES_UR, "am": DESC_PHRASES_AM}


HAND_DIR = os.path.join(HERE, "hand_names")
VARIANTS = (" Twin Pack", " Classic")


def load_hand(lang):
    p = os.path.join(HAND_DIR, f"{lang}.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def hand_name(lang, hand, name):
    if not hand:
        return None
    for v in VARIANTS:
        if name.endswith(v) and name[:-len(v)] in hand["names"]:
            suf = hand.get("variant_suffixes", {}).get(v) or translate_name(lang, v)
            return hand["names"][name[:-len(v)]] + suf
    return hand["names"].get(name)


def _attr(lang, hand, table, value):
    if hand and value in hand.get(table, {}):
        return hand[table][value]
    return translate_name(lang, value)


def translate_description(lang, desc, hand=None):
    out = []
    end = {"hi": "।", "bn": "।", "ur": "۔", "am": "።"}.get(lang, ".")
    m = re.search(r"Colour: ([^.]+)\.", desc)
    if m:
        out.append(f"{COLOUR_LABEL[lang]}: "
                   f"{_attr(lang, hand, 'colours', m.group(1))}{end}")
    m = re.search(r"Material: ([^.]+)\.", desc)
    if m:
        out.append(f"{MATERIAL_LABEL[lang]}: "
                   f"{_attr(lang, hand, 'materials', m.group(1))}{end}")
    for en_phrase, tr in DESC_PHRASES[lang].items():
        if en_phrase in desc:
            out.append(tr)
    assert out, desc
    return " ".join(out)


def main(lang):
    src = os.path.join(HERE, "ministore", "catalog.json")
    with open(src, encoding="utf-8") as f:
        catalog = json.load(f)
    hand = load_hand(lang)
    overlay = {}
    fallback = 0
    for c in catalog:
        name = hand_name(lang, hand, c["name"])
        if name is None:
            name = translate_name(lang, c["name"])
            fallback += 1
        overlay[str(c["id"])] = {
            "name": name,
            "description": translate_description(lang, c["description"], hand),
            "category": CATEGORY[lang][c["category"]],
        }
    out = os.path.join(HERE, "ministore", f"catalog_{lang}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(overlay, f, indent=1, ensure_ascii=False)
    print(f"wrote {len(overlay)} entries to {out}"
          + (f" ({fallback} names from the rule engine, no hand table)"
             if hand is None else f" ({fallback} names fell back to the rule engine)"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "hi")
