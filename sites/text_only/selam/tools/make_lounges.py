import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.brand import BRANDS

HIGHLAND_EN, HIGHLAND_AM = BRANDS["lounge_business"]["en"], BRANDS["lounge_business"]["am"]
SKY_EN, SKY_AM = BRANDS["lounge_premium"]["en"], BRANDS["lounge_premium"]["am"]

AMENITIES = {
    "full": (
        "Hot buffet, barista coffee, full bar, showers, prayer room, quiet zone, "
        "business desks, Wi-Fi, family room",
        "ትኩስ ቡፌ፣ የባሪስታ ቡና፣ ሙሉ መጠጥ ቤት፣ ሻወር፣ የጸሎት ክፍል፣ ጸጥታ ያለው ቀጠና፣ የሥራ ጠረጴዛዎች፣ ዋይ-ፋይ፣ የቤተሰብ ክፍል"),
    "standard": (
        "Hot and cold buffet, coffee bar, Wi-Fi, business desks, newspapers",
        "ትኩስና ቀዝቃዛ ቡፌ፣ የቡና ባር፣ ዋይ-ፋይ፣ የሥራ ጠረጴዛዎች፣ ጋዜጦች"),
    "light": (
        "Light refreshments, coffee, Wi-Fi, seating with power",
        "ቀላል መጠጦች፣ ቡና፣ ዋይ-ፋይ፣ ኃይል ያለው መቀመጫ"),
}

L = [
 ("ADD", "1", (HIGHLAND_EN, HIGHLAND_AM),
  ("04:00-23:30 daily", "በየቀኑ 04:00-23:30"),
  ("Terminal 1, airside, one level above the duty-free hall, opposite Gate A6.",
   "ተርሚናል 1፣ ከደህንነት ፍተሻ በኋላ፣ ከቀረጥ ነጻ አዳራሽ አንድ ፎቅ በላይ፣ ከበር A6 ትይዩ።"),
  "standard", "business,gold,platinum", 55.0, 90),

 ("ADD", "2", (HIGHLAND_EN + " Terminal 2", HIGHLAND_AM + " ተርሚናል 2"),
  ("24 hours", "24 ሰዓት"),
  ("Terminal 2, airside, mezzanine level above Gate B12. Lift and stair access.",
   "ተርሚናል 2፣ ከደህንነት ፍተሻ በኋላ፣ ከበር B12 በላይ ባለው መካከለኛ ፎቅ። በአሳንሰርና በደረጃ ይደረሳል።"),
  "full", "business,gold,platinum", 65.0, 180),

 ("ADD", "2", (SKY_EN, SKY_AM),
  ("05:00-01:00 daily", "በየቀኑ 05:00-01:00"),
  ("Terminal 2, airside, far end of the south concourse past Gate B24.",
   "ተርሚናል 2፣ ከደህንነት ፍተሻ በኋላ፣ ከበር B24 አልፎ በደቡብ አዳራሽ መጨረሻ።"),
  "full", "platinum", 85.0, 70),

 ("ADD", "2", ("Transit Rest Lounge", "የመሸጋገሪያ ማረፊያ ላውንጅ"),
  ("24 hours", "24 ሰዓት"),
  ("Terminal 2, airside, next to the transfer desk between Gates B1 and B4.",
   "ተርሚናል 2፣ ከደህንነት ፍተሻ በኋላ፣ በበሮች B1 እና B4 መካከል ካለው የመሸጋገሪያ ጠረጴዛ አጠገብ።"),
  "light", "", 30.0, 120),

 ("NBO", "1A", (HIGHLAND_EN, HIGHLAND_AM),
  ("05:00-22:00 daily", "በየቀኑ 05:00-22:00"),
  ("Terminal 1A, airside, upper level above the central shopping area.",
   "ተርሚናል 1A፣ ከደህንነት ፍተሻ በኋላ፣ ከመሃል የገበያ ቦታ በላይ ባለው ፎቅ።"),
  "standard", "business,gold,platinum", 48.0, 80),

 ("JNB", "A", (HIGHLAND_EN, HIGHLAND_AM),
  ("06:00-21:00 daily", "በየቀኑ 06:00-21:00"),
  ("Terminal A, international departures, level 3 near Gate A12.",
   "ተርሚናል A፣ ዓለም አቀፍ መነሻ፣ ደረጃ 3 ከበር A12 አጠገብ።"),
  "standard", "business,gold,platinum", 52.0, 75),

 ("LOS", "I", (HIGHLAND_EN, HIGHLAND_AM),
  ("07:00-23:00 daily", "በየቀኑ 07:00-23:00"),
  ("International terminal, airside, first floor above the departure hall.",
   "ዓለም አቀፍ ተርሚናል፣ ከደህንነት ፍተሻ በኋላ፣ ከመነሻ አዳራሽ በላይ ባለው አንደኛ ፎቅ።"),
  "light", "business,platinum", 45.0, 50),

 ("DAR", "3", (HIGHLAND_EN, HIGHLAND_AM),
  ("06:00-20:00 daily", "በየቀኑ 06:00-20:00"),
  ("Terminal 3, airside, adjacent to Gate 7.", "ተርሚናል 3፣ ከደህንነት ፍተሻ በኋላ፣ ከበር 7 አጠገብ።"),
  "light", "business,gold,platinum", 40.0, 45),

 ("LHR", "2", ("Skyview Partner Lounge", "ስካይቪው የአጋር ላውንጅ"),
  ("05:30-22:00 daily", "በየቀኑ 05:30-22:00"),
  ("Terminal 2B, airside, mezzanine above Gate B32. Operated by a partner.",
   "ተርሚናል 2B፣ ከደህንነት ፍተሻ በኋላ፣ ከበር B32 በላይ ባለው መካከለኛ ፎቅ። በአጋር የሚተዳደር።"),
  "standard", "business,platinum", 60.0, 140),

 ("FRA", "1", ("Skyview Partner Lounge", "ስካይቪው የአጋር ላውንጅ"),
  ("05:00-22:30 daily", "በየቀኑ 05:00-22:30"),
  ("Terminal 1, Concourse B, level 2 above Gate B26. Operated by a partner.",
   "ተርሚናል 1፣ አዳራሽ B፣ ደረጃ 2 ከበር B26 በላይ። በአጋር የሚተዳደር።"),
  "standard", "business,gold,platinum", 58.0, 130),

 ("DXB", "1", ("Skyview Partner Lounge", "ስካይቪው የአጋር ላውንጅ"),
  ("24 hours", "24 ሰዓት"),
  ("Terminal 1, Concourse D, level 3. Operated by a partner.",
   "ተርሚናል 1፣ አዳራሽ D፣ ደረጃ 3። በአጋር የሚተዳደር።"),
  "full", "business,gold,platinum", 70.0, 200),

 ("CAI", "3", ("Skyview Partner Lounge", "ስካይቪው የአጋር ላውንጅ"),
  ("06:00-23:00 daily", "በየቀኑ 06:00-23:00"),
  ("Terminal 3, airside, level 4 near Gate F8. Operated by a partner.",
   "ተርሚናል 3፣ ከደህንነት ፍተሻ በኋላ፣ ደረጃ 4 ከበር F8 አጠገብ። በአጋር የሚተዳደር።"),
  "standard", "business,platinum", 50.0, 90),

 ("IAD", "1", ("Skyview Partner Lounge", "ስካይቪው የአጋር ላውንጅ"),
  ("07:00-21:00 daily", "በየቀኑ 07:00-21:00"),
  ("Concourse A, upper level near Gate A6. Operated by a partner.",
   "አዳራሽ A፣ ከበር A6 አጠገብ ባለው የላይኛው ፎቅ። በአጋር የሚተዳደር።"),
  "light", "business,platinum", 55.0, 60),

 ("BOM", "2", ("Skyview Partner Lounge", "ስካይቪው የአጋር ላውንጅ"),
  ("24 hours", "24 ሰዓት"),
  ("Terminal 2, airside, level 4 near Gate 41. Operated by a partner.",
   "ተርሚናል 2፣ ከደህንነት ፍተሻ በኋላ፣ ደረጃ 4 ከበር 41 አጠገብ። በአጋር የሚተዳደር።"),
  "standard", "business,gold,platinum", 46.0, 110),
]


def main() -> None:
    assert len(L) == 14, f"SPEC.md 12 wants 14 lounges, got {len(L)}"
    airports = {row[0] for row in L}
    assert len(airports) >= 8, f"wants 8+ airports, got {len(airports)}"
    add_t2 = [row for row in L if row[0] == "ADD" and row[1] == "2"]
    assert len(add_t2) >= 2, "task 17 needs more than one lounge at Addis Terminal 2"
    assert len({row[7] for row in add_t2}) >= 2, \
        "the Terminal 2 lounges must have different access rules, or there is nothing to choose"

    rows = []
    for index, (iata, terminal, name, hours, location, amenity, access, price, cap) in enumerate(L, 1):
        rows.append({
            "id": index, "airport_iata": iata, "terminal": terminal,
            "name_en": name[0], "name_am": name[1],
            "hours_en": hours[0], "hours_am": hours[1],
            "location_en": location[0], "location_am": location[1],
            "amenities_en": AMENITIES[amenity][0], "amenities_am": AMENITIES[amenity][1],
            "access_free_for": access, "walk_in_price_usd": price, "capacity": cap,
        })

    out = ROOT / "spec/seed_data/lounges.yaml"
    out.write_text("# Generated by tools/make_lounges.py -- edit there, not here.\n"
                   + yaml.safe_dump({"lounges": rows}, sort_keys=False, allow_unicode=True),
                   "utf-8")
    print(f"wrote {out.relative_to(ROOT)} -- {len(rows)} lounges at {len(airports)} airports")
    for row in rows:
        free = row["access_free_for"] or "(paid entry only)"
        print(f"  {row['airport_iata']} T{row['terminal']:<3} {row['name_en'][:34]:36s} free: {free}")


if __name__ == "__main__":
    main()
