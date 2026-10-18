import pathlib
import random
import sys
from datetime import timedelta

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.clock import FROZEN_TODAY

SEED = 12_2026

PROMOTIONS = [
 ("AFRICA15", ("15% off across Africa", "በአፍሪካ 15% ቅናሽ"),
  ("Fifteen per cent off Economy Standard and above on African routes.",
   "በአፍሪካ መስመሮች በኢኮኖሚ ስታንዳርድና ከዚያ በላይ አሥራ አምስት በመቶ ቅናሽ።"), "africa", 15, -20, 40),
 ("EUROPE10", ("10% off to Europe", "ወደ አውሮፓ 10% ቅናሽ"),
  ("Ten per cent off return fares to Europe, booked at least 21 days ahead.",
   "ቢያንስ ከ21 ቀን በፊት በሚያዙ ወደ አውሮፓ የደርሶ መልስ ታሪፎች ላይ አሥር በመቶ ቅናሽ።"), "europe", 10, -5, 60),
 ("GULF12", ("12% off to the Gulf", "ወደ ባሕረ ሰላጤው 12% ቅናሽ"),
  ("Twelve per cent off Middle East routes in Economy.",
   "በኢኮኖሚ በመካከለኛው ምስራቅ መስመሮች አሥራ ሁለት በመቶ ቅናሽ።"), "middle_east", 12, -40, -5),
 ("ASIA20", ("20% off to Asia", "ወደ እስያ 20% ቅናሽ"),
  ("Twenty per cent off Asian routes, opening next month.",
   "በሚቀጥለው ወር የሚከፈት በእስያ መስመሮች ሃያ በመቶ ቅናሽ።"), "asia", 20, 25, 80),
 ("DOMESTIC08", ("8% off domestic flights", "በአገር ውስጥ በረራዎች 8% ቅናሽ"),
  ("Eight per cent off flights within Ethiopia.",
   "በኢትዮጵያ ውስጥ በሚደረጉ በረራዎች ስምንት በመቶ ቅናሽ።"), "domestic", 8, -60, 90),
 ("HIGHLAND18", ("18% off Highland Class", "በሃይላንድ ክላስ 18% ቅናሽ"),
  ("Eighteen per cent off Highland Class on long-haul routes.",
   "በረጅም ርቀት መስመሮች በሃይላንድ ክላስ አሥራ ስምንት በመቶ ቅናሽ።"), "north_america", 18, -10, 30),
 ("FAMILY10", ("10% off for families", "ለቤተሰቦች 10% ቅናሽ"),
  ("Ten per cent off when two adults travel with a child.",
   "ሁለት አዋቂዎች ከሕፃን ጋር ሲጓዙ አሥር በመቶ ቅናሽ።"), "africa", 10, -15, 45),
 ("STUDENT12", ("12% student fare", "የተማሪ ታሪፍ 12% ቅናሽ"),
  ("Twelve per cent off for students with a valid enrolment letter.",
   "የሚሠራ የምዝገባ ደብዳቤ ላላቸው ተማሪዎች አሥራ ሁለት በመቶ ቅናሽ።"), "europe", 12, -30, 120),
 ("SENIOR10", ("10% for passengers over 60", "ከ60 ዓመት በላይ ለሆኑ 10%"),
  ("Ten per cent off for passengers aged 60 and above.",
   "60 ዓመትና ከዚያ በላይ ለሆኑ ተሳፋሪዎች አሥር በመቶ ቅናሽ።"), "africa", 10, -90, -30),
 ("STOPOVER05", ("5% off with a stopover", "ከማቆያ ጋር 5% ቅናሽ"),
  ("Five per cent off when you add an Addis Ababa stopover.",
   "የአዲስ አበባ ማቆያ ሲጨምሩ አምስት በመቶ ቅናሽ።"), "asia", 5, -25, 55),
 ("SOUTH14", ("14% off to Southern Africa", "ወደ ደቡብ አፍሪካ 14% ቅናሽ"),
  ("Fourteen per cent off routes to Southern Africa.",
   "ወደ ደቡብ አፍሪካ በሚደረጉ መስመሮች አሥራ አራት በመቶ ቅናሽ።"), "africa", 14, -8, 22),
 ("EARLY20", ("20% for booking early", "ቀድሞ ለመያዝ 20%"),
  ("Twenty per cent off when you book 60 days or more ahead.",
   "60 ቀንና ከዚያ በላይ አስቀድመው ሲይዙ ሃያ በመቶ ቅናሽ።"), "europe", 20, -12, 100),
]

TERMS = (
 "Applies to the base fare only, not to taxes. One promotion per booking. Not "
 "combinable with award tickets or with a corporate discount. Seats are limited.",
 "በመሠረታዊ ታሪፍ ላይ ብቻ ይሠራል እንጂ በግብር ላይ አይደለም። በአንድ የቦታ ማስያዣ አንድ ቅናሽ። ከሽልማት ትኬቶች "
 "ወይም ከድርጅት ቅናሽ ጋር አይጣመርም። መቀመጫዎች ውስን ናቸው።")

FILMS = [
 ("The Long Rains", "ረጅሙ ክረምት", "Drama", "ድራማ", 118, "Amharic", 2024),
 ("Harvest Season", "የመኸር ወቅት", "Drama", "ድራማ", 104, "Amharic", 2023),
 ("Blue Nile", "ጥቁር አባይ", "Documentary", "ዘጋቢ ፊልም", 87, "Amharic", 2025),
 ("City of Salt", "የጨው ከተማ", "Thriller", "አስደንጋጭ", 132, "English", 2024),
 ("Northbound", "ወደ ሰሜን", "Adventure", "ጀብዱ", 96, "English", 2022),
 ("Paper Kites", "የወረቀት ካይት", "Family", "የቤተሰብ", 92, "English", 2025),
 ("The Cartographer", "ካርታ ሠሪው", "Mystery", "ምስጢር", 121, "French", 2023),
 ("Second Monsoon", "ሁለተኛው ዝናብ", "Romance", "የፍቅር", 108, "Hindi", 2024),
]
SERIES = [
 ("Riftline", "ሪፍትላይን", "Drama", "ድራማ", 45, "English", 2025),
 ("Market Days", "የገበያ ቀናት", "Comedy", "ኮሜዲ", 28, "Amharic", 2024),
 ("The Watchtower", "የመጠበቂያ ግንብ", "Thriller", "አስደንጋጭ", 52, "English", 2023),
 ("Highland Kitchen", "የደጋ ወጥ ቤት", "Food", "ምግብ", 24, "Amharic", 2025),
]
MUSIC = [
 ("Azmari Nights", "የአዝማሪ ምሽቶች", "Traditional", "ባህላዊ", 58, "Amharic", 2024),
 ("Addis Jazz Collective", "የአዲስ ጃዝ ስብስብ", "Jazz", "ጃዝ", 64, "Instrumental", 2023),
 ("Rift Valley Sessions", "የስምጥ ሸለቆ ክፍለ ጊዜያት", "World", "ዓለም አቀፍ", 71, "Various", 2025),
 ("Quiet Altitude", "ጸጥ ያለ ከፍታ", "Ambient", "አምቢየንት", 90, "Instrumental", 2024),
]

REQUIREMENTS = [
 ("GB", 6, 2, ("Visa required for most nationalities", "ለአብዛኞቹ ዜግነቶች ቪዛ ያስፈልጋል"),
  ("No vaccinations required.", "ክትባት አያስፈልግም።"), True),
 ("US", 6, 2, ("Visa or ESTA required", "ቪዛ ወይም የኤሌክትሮኒክ የጉዞ ፈቃድ ያስፈልጋል"),
  ("No vaccinations required.", "ክትባት አያስፈልግም።"), True),
 ("AE", 6, 1, ("Visa on arrival for many nationalities", "ለብዙ ዜግነቶች በመድረሻ ቪዛ"),
  ("No vaccinations required.", "ክትባት አያስፈልግም።"), True),
 ("KE", 6, 2, ("Electronic travel authorisation required", "የኤሌክትሮኒክ የጉዞ ፈቃድ ያስፈልጋል"),
  ("Yellow fever certificate required if arriving from an endemic country.",
   "ከበሽታው ከተስፋፋበት አገር ሲመጡ የቢጫ ወባ ምስክር ወረቀት ያስፈልጋል።"), True),
 ("ZA", 6, 2, ("Visa-free for many nationalities for 90 days", "ለብዙ ዜግነቶች ለ90 ቀን ያለ ቪዛ"),
  ("Yellow fever certificate required if arriving from an endemic country.",
   "ከበሽታው ከተስፋፋበት አገር ሲመጡ የቢጫ ወባ ምስክር ወረቀት ያስፈልጋል።"), True),
 ("ET", 6, 1, ("e-Visa available online before travel", "ከጉዞ በፊት በመስመር ላይ ኢ-ቪዛ ይገኛል"),
  ("Yellow fever certificate required if arriving from an endemic country.",
   "ከበሽታው ከተስፋፋበት አገር ሲመጡ የቢጫ ወባ ምስክር ወረቀት ያስፈልጋል።"), True),
 ("IN", 6, 2, ("e-Visa required before travel", "ከጉዞ በፊት ኢ-ቪዛ ያስፈልጋል"),
  ("Yellow fever certificate required if arriving from an endemic country.",
   "ከበሽታው ከተስፋፋበት አገር ሲመጡ የቢጫ ወባ ምስክር ወረቀት ያስፈልጋል።"), True),
 ("CN", 6, 2, ("Visa required in advance", "ቪዛ አስቀድሞ ያስፈልጋል"),
  ("No vaccinations required.", "ክትባት አያስፈልግም።"), True),
 ("DE", 3, 2, ("Schengen visa required for most nationalities", "ለአብዛኞቹ ዜግነቶች የሼንገን ቪዛ ያስፈልጋል"),
  ("No vaccinations required.", "ክትባት አያስፈልግም።"), True),
 ("FR", 3, 2, ("Schengen visa required for most nationalities", "ለአብዛኞቹ ዜግነቶች የሼንገን ቪዛ ያስፈልጋል"),
  ("No vaccinations required.", "ክትባት አያስፈልግም።"), True),
]


LANGUAGE_NAMES = {
    "Amharic": "አማርኛ", "English": "እንግሊዝኛ", "French": "ፈረንሳይኛ",
    "Hindi": "ሒንዲ", "Arabic": "ዓረብኛ", "Swahili": "ስዋሂሊ",
    "Portuguese": "ፖርቱጋልኛ", "Instrumental": "የመሣሪያ ሙዚቃ", "Various": "የተለያዩ",
}


def main() -> None:
    rng = random.Random(SEED)
    promotions = [{
        "id": i, "code": code, "title_en": title[0], "title_am": title[1],
        "body_en": body[0], "body_am": body[1],
        "terms_en": TERMS[0], "terms_am": TERMS[1],
        "region": region, "discount_pct": pct,
        "valid_from": (FROZEN_TODAY + timedelta(days=lo)).isoformat(),
        "valid_to": (FROZEN_TODAY + timedelta(days=hi)).isoformat(),
    } for i, (code, title, body, region, pct, lo, hi) in enumerate(PROMOTIONS, 1)]

    live = [p for p in promotions
            if p["valid_from"] <= FROZEN_TODAY.isoformat() <= p["valid_to"]]
    expired = [p for p in promotions if p["valid_to"] < FROZEN_TODAY.isoformat()]
    future = [p for p in promotions if p["valid_from"] > FROZEN_TODAY.isoformat()]
    assert live and expired and future, (
        f"promotions must span live ({len(live)}), expired ({len(expired)}) and "
        f"not-yet-open ({len(future)}), or 'which offers apply' is not a question")

    items, item_id = [], 1
    for category, rows in (("film", FILMS), ("series", SERIES), ("music", MUSIC)):
        for title_en, title_am, genre_en, genre_am, minutes, language, year in rows:
            if language not in LANGUAGE_NAMES:
                raise KeyError(f"no Amharic for the audio language {language!r}; "
                               f"an untranslated one leaks Latin into the Amharic build")
            items.append({"id": item_id, "category": category,
                          "title_en": title_en, "title_am": title_am,
                          "genre_en": genre_en, "genre_am": genre_am,
                          "minutes": minutes, "language_en": language,
                          "language_am": LANGUAGE_NAMES[language], "year": year})
            item_id += 1

    requirements = [{
        "id": i, "country_code": code, "passport_months": months,
        "blank_pages": pages, "visa_required_en": visa[0], "visa_required_am": visa[1],
        "health_en": health[0], "health_am": health[1], "onward_ticket": onward,
    } for i, (code, months, pages, visa, health, onward) in enumerate(REQUIREMENTS, 1)]

    assert len({r["passport_months"] for r in requirements}) > 1, \
        "every destination wants the same passport validity; the answer would be free"

    out = ROOT / "spec/seed_data/extras.yaml"
    out.write_text("# Generated by tools/make_extras.py -- edit there, not here.\n"
                   + yaml.safe_dump({"promotions": promotions,
                                     "entertainment_items": items,
                                     "travel_requirements": requirements},
                                    sort_keys=False, allow_unicode=True), "utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    print(f"  promotions       {len(promotions)} ({len(live)} live, {len(expired)} expired, "
          f"{len(future)} not yet open)")
    print(f"  entertainment    {len(items)}")
    print(f"  entry rules      {len(requirements)} countries")


if __name__ == "__main__":
    main()
