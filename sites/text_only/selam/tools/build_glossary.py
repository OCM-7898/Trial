from __future__ import annotations

import json
import pathlib
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

FROM_SPREADSHEET = {
    "round-trip":        "የደርሶ መልስ",
    "booking reference": "የቦታ ማስያዣ ማጣቀሻ",
    "reservation":       "የቦታ ማስያዣ",
    "boarding pass":     "የመሳፈሪያ ፈቃድ",
    "online check-in":   "የመስመር ላይ ቼክ-ኢን",
    "checked baggage":   "የተመዘገበ ሻንጣ",
    "cabin baggage":     "የእጅ ሻንጣ",
    "aisle seat":        "የመተላለፊያ መቀመጫ",
    "extra legroom":     "ተጨማሪ የእግር ቦታ",
    "stopover":          "ማቆያ",
    "lounge":            "ላውንጅ",
    "travel insurance":  "የጉዞ መድን",
    "refund":            "ተመላሽ ክፍያ",
    "cabin class":       "የጉዞ ክፍል",
    "itinerary":         "የጉዞ ዝርዝር",
    "flight status":     "የበረራ ሁኔታ",
    "fare difference":   "የታሪፍ ልዩነት",
    "passenger":         "ተሳፋሪ",
}

FORMS = {
    "upgrade":  ["ማሻሻያ", "ማሻሻል", "ያሻሽሉ", "ሊሻሻል", "ተሻሽሏል"],
    "miles":    ["ማይሎች", "ማይል"],
    "refund":   ["ተመላሽ ክፍያ", "ተመላሽ"],
    "passenger": ["ተሳፋሪ", "ተሳፋሪዎች"],
    "lounge":   ["ላውንጅ", "ላውንጆች"],
    "seat":     ["መቀመጫ", "መቀመጫዎች"],
    "flight":   ["በረራ", "በረራዎች"],
    "date":     ["ቀን", "ቀናት"],
}

EXEMPTIONS = {
    "connection": {
        "partner.no_rail": "a rail link between places, not a transfer between flights",
        "partner.rail_intro": "as above",
    },
    "seat": {
        "partner.car_intro": "'seat' used as a verb -- vehicles that carry a party",
        "partner.car_too_small": "'seat' used as a verb",
    },
    "child": {
        "miles.relationship_hint": "offspring in a family relationship (ልጅ), not the "
                                   "passenger type aged 2-11 (ሕፃን)",
    },
}

ADDITIONAL = {
    "flight":            "በረራ",
    "flight number":     "የበረራ ቁጥር",
    "seat":              "መቀመጫ",
    "gate":              "በር",
    "terminal":          "ተርሚናል",
    "airport":           "አየር ማረፊያ",
    "departure":         "መነሻ",
    "arrival":           "መድረሻ",
    "date":              "ቀን",
    "price":             "ዋጋ",
    "baggage allowance": "የሻንጣ ፈቃድ",
    "excess baggage":    "ትርፍ ሻንጣ",
    "surname":           "የአያት ስም",
    "membership number": "የአባልነት ቁጥር",
    "miles":             "ማይሎች",
    "award ticket":      "የሽልማት ትኬት",
    "upgrade":           "ማሻሻያ",
    "change fee":        "የለውጥ ክፍያ",
    "special meal":      "ልዩ ምግብ",
    "allergy":           "አለርጂ",
    "assistance":        "ድጋፍ",
    "contact office":    "የመገናኛ ቢሮ",
    "opening hours":     "የሥራ ሰዓቶች",
    "adult":             "አዋቂ",
    "child":             "ሕፃን",
    "infant":            "ጨቅላ",
    "economy":           "ኢኮኖሚ",
    "one-way":           "የአንድ አቅጣጫ",
    "connection":        "መሸጋገሪያ",
    "ticket number":     "የትኬት ቁጥር",
}


def vetted_amharic() -> str:
    with zipfile.ZipFile(ROOT / "spec" / "tasks_source.xlsx") as zf:
        shared = ["".join(t.text or "" for t in si.iter(NS + "t"))
                  for si in ET.fromstring(zf.read("xl/sharedStrings.xml")).iter(NS + "si")]
        sheet = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))
    cells = []
    for row in sheet.iter(NS + "row"):
        for cell in row.iter(NS + "c"):
            if "".join(c for c in cell.get("r") if c.isalpha()) != "E":
                continue
            value = cell.find(NS + "v")
            if value is not None and cell.get("t") == "s":
                cells.append(shared[int(value.text)])
    return "\n".join(cells)


def occurs_in(term: str, corpus: str) -> bool:
    tokens = corpus.replace("፣", " ").replace("።", " ").replace("፤", " ").split()
    for word in term.split():
        if not any(token.startswith(word) for token in tokens):
            return False
    return True


def main() -> None:
    corpus = vetted_amharic()

    entries = {}
    unverified = []
    for english, amharic in FROM_SPREADSHEET.items():
        found = occurs_in(amharic, corpus)
        if not found:
            unverified.append((english, amharic))
        entries[english] = {
            "am": amharic,
            "forms": FORMS.get(english, [amharic]),
            "exempt": EXEMPTIONS.get(english, {}),
            "source": "spreadsheet" if found else "claimed",
        }
    for english, amharic in ADDITIONAL.items():
        entries[english] = {
            "am": amharic,
            "forms": FORMS.get(english, [amharic]),
            "exempt": EXEMPTIONS.get(english, {}),
            "source": "generated",
        }

    if unverified:
        print("WARNING -- these are recorded in SPEC.md 11.2 as coming from the")
        print("spreadsheet, but do not appear in its Amharic column:")
        for english, amharic in unverified:
            print(f"    {english:20s} {amharic}")
        print("  They are marked source='claimed' so the reviewer knows they are unvetted.\n")

    path = ROOT / "app" / "i18n" / "glossary.json"
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    "utf-8")

    by_source = {}
    for entry in entries.values():
        by_source[entry["source"]] = by_source.get(entry["source"], 0) + 1
    exemptions = sum(len(e["exempt"]) for e in entries.values())
    print(f"wrote {path.relative_to(ROOT)} -- {len(entries)} terms, "
          f"{exemptions} recorded exemption(s)")
    for source, count in sorted(by_source.items()):
        print(f"  {source:12s} {count}")


if __name__ == "__main__":
    main()
