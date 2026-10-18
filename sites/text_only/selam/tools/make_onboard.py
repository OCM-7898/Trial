import pathlib
import sqlite3
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PACKAGES = {
    "short": [
        ("Messaging", "መልእክት", 30, 60, 4.0),
        ("Browse", "አሰሳ", 150, 180, 9.0),
        ("Full flight", "ሙሉ በረራ", 400, 480, 16.0),
    ],
    "medium": [
        ("Messaging", "መልእክት", 50, 120, 6.0),
        ("Browse", "አሰሳ", 250, 300, 14.0),
        ("Full flight", "ሙሉ በረራ", 700, 720, 22.0),
    ],
    "long": [
        ("Messaging", "መልእክት", 80, 180, 8.0),
        ("Browse", "አሰሳ", 400, 480, 19.0),
        ("Full flight", "ሙሉ በረራ", 1500, 1080, 29.0),
    ],
}

MEAL_CODES = [
    ("VGML", "Vegetarian", "ቬጀቴሪያን", "No meat, poultry or fish. Dairy and eggs may be included.",
     "ሥጋ፣ ዶሮ ወይም ዓሣ የለም። የወተት ተዋጽኦና እንቁላል ሊካተቱ ይችላሉ።", 24),
    ("VJML", "Jain vegetarian", "ጃይን ቬጀቴሪያን", "No meat, fish, eggs, dairy or root vegetables.",
     "ሥጋ፣ ዓሣ፣ እንቁላል፣ የወተት ተዋጽኦ ወይም የሥር አትክልት የለም።", 48),
    ("AVML", "Asian vegetarian", "እስያዊ ቬጀቴሪያን", "Spiced Indian-style vegetarian meal.",
     "በቅመም የተዘጋጀ የሕንድ ዓይነት የቬጀቴሪያን ምግብ።", 24),
    ("GFML", "Gluten intolerant", "ግሉተን የማይስማማው",
     "No wheat, rye, barley or oats. Prepared to a dietary specification; it is not an allergy control.",
     "ስንዴ፣ ራይ፣ ገብስ ወይም አጃ የለም። በአመጋገብ መስፈርት ይዘጋጃል፤ የአለርጂ ቁጥጥር አይደለም።", 24),
    ("LFML", "Low fat", "ዝቅተኛ ስብ", "Reduced fat and cholesterol.", "ስብና ኮሌስትሮል የተቀነሰ።", 24),
    ("LSML", "Low salt", "ዝቅተኛ ጨው", "No added salt.", "የተጨመረ ጨው የለም።", 24),
    ("DBML", "Diabetic", "የስኳር በሽተኛ", "Controlled carbohydrate, no added sugar.",
     "ቁጥጥር የተደረገበት ካርቦሃይድሬት፣ የተጨመረ ስኳር የለም።", 24),
    ("HNML", "Hindu", "ሂንዱ", "Non-vegetarian Indian meal without beef or pork.",
     "የበሬና የአሳማ ሥጋ የሌለው የሕንድ ምግብ።", 24),
    ("MOML", "Muslim", "ሙስሊም", "Prepared to halal requirements.", "በሐላል መስፈርት የተዘጋጀ።", 24),
    ("KSML", "Kosher", "ኮሸር", "Sealed kosher meal, loaded from an external supplier.",
     "ከውጭ አቅራቢ የሚጫን የታሸገ የኮሸር ምግብ።", 48),
    ("ORML", "Orthodox fasting", "የኦርቶዶክስ ጾም", "No animal products, for fasting periods.",
     "ለጾም ወቅቶች የእንስሳት ተዋጽኦ የለም።", 24),
    ("CHML", "Child", "የሕፃናት", "Smaller portions for children aged 2 to 11.",
     "ከ2 እስከ 11 ዓመት ለሆኑ ሕፃናት አነስተኛ መጠን።", 24),
    ("BBML", "Infant", "የጨቅላ", "Jarred baby food for infants under two.",
     "ከሁለት ዓመት በታች ለሆኑ ጨቅላዎች በማሰሮ የታሸገ ምግብ።", 24),
    ("FPML", "Fruit platter", "የፍራፍሬ ሳህን", "Fresh seasonal fruit only.",
     "ትኩስ ወቅታዊ ፍራፍሬ ብቻ።", 24),
]

MENUS = [
    ("short", "economy", "snack",
     "Hot sandwich or savoury pastry", "ትኩስ ሳንድዊች ወይም ጣፋጭ ዳቦ",
     "Tea, coffee, water, soft drinks", "ሻይ፣ ቡና፣ ውሃ፣ ለስላሳ መጠጦች"),
    ("short", "business", "snack",
     "Hot plate with salad and dessert", "ከሰላጣና ከጣፋጭ ጋር ትኩስ ሳህን",
     "Tea, coffee, water, soft drinks, wine", "ሻይ፣ ቡና፣ ውሃ፣ ለስላሳ መጠጦች፣ ወይን"),
    ("medium", "economy", "meal",
     "Main course with bread, salad and dessert", "ከዳቦ፣ ከሰላጣና ከጣፋጭ ጋር ዋና ምግብ",
     "Tea, coffee, water, soft drinks, beer", "ሻይ፣ ቡና፣ ውሃ፣ ለስላሳ መጠጦች፣ ቢራ"),
    ("medium", "business", "meal",
     "Starter, choice of two main courses, cheese and dessert",
     "መክፈቻ፣ ከሁለት ዋና ምግቦች ምርጫ፣ አይብና ጣፋጭ",
     "Full bar, wine list, barista coffee", "ሙሉ መጠጥ ቤት፣ የወይን ዝርዝር፣ የባሪስታ ቡና"),
    ("long", "economy", "dinner",
     "Dinner with a choice of two main courses, plus a light breakfast before landing",
     "ከሁለት ዋና ምግቦች ምርጫ ያለው እራት፣ እንዲሁም ከማረፍ በፊት ቀላል ቁርስ",
     "Tea, coffee, water, soft drinks, beer, wine", "ሻይ፣ ቡና፣ ውሃ፣ ለስላሳ መጠጦች፣ ቢራ፣ ወይን"),
    ("long", "business", "dinner",
     "Four-course dinner served on request, plus a full breakfast before landing",
     "በጥያቄ የሚቀርብ ባለ አራት ኮርስ እራት፣ እንዲሁም ከማረፍ በፊት ሙሉ ቁርስ",
     "Full bar, sommelier wine list, espresso", "ሙሉ መጠጥ ቤት፣ የሶመሊየር የወይን ዝርዝር፣ ኤስፕሬሶ"),
]


def band_for(distance_km: int) -> str:
    if distance_km < 1500:
        return "short"
    if distance_km < 4500:
        return "medium"
    return "long"


def main() -> None:
    conn = sqlite3.connect(ROOT / "data" / "seed.db")
    flights = conn.execute("""
        select f.id, r.distance_km from flights f
        join routes r on r.id = f.route_id
        where f.wifi_equipped = 1 order by f.id
    """).fetchall()

    packages, package_id = [], 1
    for flight_id, distance in flights:
        for position, (name_en, name_am, mb, minutes, price) in enumerate(
                PACKAGES[band_for(distance)]):
            packages.append({
                "id": package_id, "flight_id": flight_id,
                "name_en": name_en, "name_am": name_am,
                "mb": mb, "duration_min": minutes, "price_usd": price,
                "position": position,
            })
            package_id += 1

    for band, options in PACKAGES.items():
        prices = [price for *_, price in options]
        sizes = [mb for _, _, mb, _, _ in options]
        durations = [minutes for _, _, _, minutes, _ in options]
        assert prices == sorted(prices) and len(set(prices)) == 3, f"{band}: prices tie"
        assert sizes == sorted(sizes) and len(set(sizes)) == 3, f"{band}: sizes tie"
        assert durations == sorted(durations), f"{band}: durations are not ordered"
        per_mb = [price / mb for _, _, mb, _, price in options]
        assert per_mb[0] == max(per_mb), (
            f"{band}: the cheapest package is also the best value per MB, so an "
            f"agent can pick correctly without comparing anything")

    codes = [{"id": i, "code": c, "name_en": ne, "name_am": na,
              "description_en": de, "description_am": da, "cutoff_hours": h}
             for i, (c, ne, na, de, da, h) in enumerate(MEAL_CODES, 1)]
    assert len(codes) == 14, f"SPEC.md 12 wants 14 meal codes, got {len(codes)}"
    assert len({c["cutoff_hours"] for c in codes}) > 1, \
        "all codes share one cut-off; the deadline question would be free"

    menus = [{"id": i, "band": b, "cabin": cab, "service": s,
              "courses_en": ce, "courses_am": ca,
              "beverages_en": be, "beverages_am": ba}
             for i, (b, cab, s, ce, ca, be, ba) in enumerate(MENUS, 1)]

    out = ROOT / "spec/seed_data/onboard.yaml"
    out.write_text("# Generated by tools/make_onboard.py -- edit there, not here.\n"
                   + yaml.safe_dump({"wifi_packages": packages,
                                     "special_meal_codes": codes,
                                     "meal_menus": menus},
                                    sort_keys=False, allow_unicode=True), "utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    print(f"  wifi packages   {len(packages):,} across {len(flights):,} equipped flights")
    print(f"  meal codes      {len(codes)} ({len({c['cutoff_hours'] for c in codes})} distinct cut-offs)")
    print(f"  menus           {len(menus)}")
    for band, options in PACKAGES.items():
        rates = ", ".join(f"{price/mb*1000:.0f}c/GB" for _, _, mb, _, price in options)
        print(f"    {band:7s} value per MB: {rates}")


if __name__ == "__main__":
    main()
