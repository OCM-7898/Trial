from __future__ import annotations

import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

ITEMS = [
 ("sport", "Bicycle", "ብስክሌት", 32, "140x30x80", 60.0, True,
  "Handlebars turned, pedals removed and tyres deflated, in a bicycle bag or box.",
  "እጀታው ተዞሮ፣ ፔዳሎቹ ተነስተው፣ ጎማዎቹ ነፋሱ ወጥቶ በብስክሌት ከረጢት ወይም ሳጥን ውስጥ።"),
 ("sport", "Tandem bicycle", "ባለሁለት መቀመጫ ብስክሌት", 32, "220x30x80", 120.0, True,
  "Carried only on wide-body aircraft. Confirm the aircraft type before booking.",
  "የሚወሰደው በሰፊ አካል አውሮፕላኖች ብቻ ነው። ከመያዝዎ በፊት የአውሮፕላኑን ዓይነት ያረጋግጡ።"),
 ("sport", "Golf bag", "የጎልፍ ከረጢት", 23, "125x35x35", 45.0, False,
  "One bag holds clubs, balls and a pair of shoes. Counts as one checked piece.",
  "አንድ ከረጢት ዱላዎችን፣ ኳሶችንና አንድ ጥንድ ጫማ ይይዛል። እንደ አንድ የተመዘገበ ዕቃ ይቆጠራል።"),
 ("sport", "Ski and boot bag", "የበረዶ መንሸራተቻና የጫማ ከረጢት", 23, "200x30x30", 55.0, False,
  "Skis, poles and one pair of boots together count as one piece.",
  "መንሸራተቻዎች፣ ዘንጎችና አንድ ጥንድ ጫማ በአንድነት እንደ አንድ ዕቃ ይቆጠራሉ።"),
 ("sport", "Snowboard", "ስኖውቦርድ", 23, "180x40x20", 55.0, False,
  "In a padded board bag. Loose bindings must be removed.",
  "በተለሰለሰ የቦርድ ከረጢት ውስጥ። የላሉ ማሰሪያዎች መነሳት አለባቸው።"),
 ("sport", "Surfboard", "የሰርፍ ቦርድ", 23, "300x60x20", 90.0, True,
  "Boards over 300 cm are refused. Fins removed, in a padded board bag.",
  "ከ300 ሴሜ በላይ የሆኑ ቦርዶች አይቀበሉም። ክንፎቹ ተነስተው በተለሰለሰ የቦርድ ከረጢት ውስጥ።"),
 ("sport", "Windsurf equipment", "የንፋስ ሰርፍ መሣሪያ", 32, "300x60x30", 110.0, True,
  "Mast, board and sail together. Booked as one special item.",
  "ምሰሶው፣ ቦርዱና ሸራው በአንድነት። እንደ አንድ ልዩ ዕቃ ይያዛል።"),
 ("sport", "Kitesurf equipment", "የካይት ሰርፍ መሣሪያ", 23, "180x50x30", 75.0, False,
  "Lines coiled and the bar secured. Pressurised pumps must be empty.",
  "ገመዶቹ ተጠቅልለው ዘንጉ ታስሮ። ግፊት ያላቸው ፓምፖች ባዶ መሆን አለባቸው።"),
 ("sport", "Kayak or canoe", "ካያክ ወይም ታንኳ", 32, "300x80x50", 150.0, True,
  "Carried only on wide-body aircraft and only up to 300 cm.",
  "የሚወሰደው በሰፊ አካል አውሮፕላኖች ብቻ እንዲሁም እስከ 300 ሴሜ ብቻ ነው።"),
 ("sport", "Diving equipment", "የመጥለቅ መሣሪያ", 23, "90x60x40", 50.0, True,
  "Cylinders must be empty with the valve removed or open for inspection.",
  "ሲሊንደሮች ባዶ መሆንና ቫልቫቸው ተነስቶ ወይም ለምርመራ ክፍት መሆን አለበት።"),
 ("sport", "Fishing gear", "የዓሣ ማጥመጃ መሣሪያ", 23, "200x30x30", 40.0, False,
  "Rods in a hard tube. Hooks must be covered and stowed in the tackle box.",
  "ዘንጎቹ በጠንካራ ቱቦ ውስጥ። መንጠቆዎቹ ተሸፍነው በመሣሪያ ሳጥን ውስጥ መቀመጥ አለባቸው።"),
 ("sport", "Archery equipment", "የቀስት መሣሪያ", 23, "140x40x30", 55.0, False,
  "Bow and arrows in a hard case. Not accepted as cabin baggage.",
  "ቀስቱና ፍላጻዎቹ በጠንካራ ሳጥን ውስጥ። እንደ የእጅ ሻንጣ አይቀበልም።"),
 ("sport", "Bowling ball", "የቦውሊንግ ኳስ", 16, "40x40x40", 30.0, False,
  "One ball per passenger, in a fitted bag.",
  "በአንድ ተሳፋሪ አንድ ኳስ፣ በሚመጥን ከረጢት ውስጥ።"),
 ("sport", "Pole vault poles", "የፖል ቮልት ዘንጎች", 23, "500x20x20", 200.0, True,
  "Length over 300 cm requires cargo carriage on a separate air waybill.",
  "ከ300 ሴሜ በላይ ርዝመት በተለየ የአየር ማጓጓዣ ሰነድ የጭነት ማጓጓዝ ይፈልጋል።"),
 ("sport", "Hang-glider", "ተንጠልጣይ ተንሳፋፊ", 32, "400x40x40", 180.0, True,
  "Wide-body aircraft only, and subject to space on the day.",
  "በሰፊ አካል አውሮፕላኖች ብቻ፣ እንዲሁም በዕለቱ ባለው ቦታ ልክ።"),
 ("sport", "Parachute", "ፓራሹት", 23, "70x50x40", 45.0, True,
  "Packed rig only. The reserve must be within its repack date.",
  "የታሸገ መሣሪያ ብቻ። ተጠባባቂው በእንደገና ማሸጊያ ቀኑ ውስጥ መሆን አለበት።"),
 ("music", "Violin or viola", "ቫዮሊን ወይም ቪዮላ", 8, "55x38x20", 0.0, False,
  "Fits the cabin bag size and travels as your cabin bag at no charge.",
  "የእጅ ሻንጣ መጠንን ስለሚያሟላ እንደ የእጅ ሻንጣዎ ያለክፍያ ይጓዛል።"),
 ("music", "Guitar", "ጊታር", 23, "120x45x20", 50.0, False,
  "Too large for the cabin. Hard case required in the hold.",
  "ለካቢን በጣም ትልቅ ነው። በጭነት ክፍል ጠንካራ ሳጥን ያስፈልጋል።"),
 ("music", "Cello", "ቼሎ", 32, "150x50x40", 0.0, True,
  "Travels on a seat bought for it at the adult fare. Booked 72 hours ahead.",
  "ለእሱ በተገዛ መቀመጫ በአዋቂ ታሪፍ ይጓዛል። ከ72 ሰዓት በፊት ይያዛል።"),
 ("music", "Double bass", "ድርብ ባስ", 45, "200x70x60", 220.0, True,
  "Hold only, in a hard flight case. Not accepted in a soft cover.",
  "በጭነት ክፍል ብቻ፣ በጠንካራ የበረራ ሳጥን ውስጥ። በለስላሳ ሽፋን አይቀበልም።"),
 ("music", "Brass instrument", "የናስ መሣሪያ", 23, "100x60x40", 45.0, False,
  "Hard case required. Valves must be secured.",
  "ጠንካራ ሳጥን ያስፈልጋል። ቫልቮቹ መታሰር አለባቸው።"),
 ("music", "Drum kit", "የከበሮ ስብስብ", 32, "120x60x60", 130.0, True,
  "Carried as two pieces. Cymbals must be in a separate padded bag.",
  "እንደ ሁለት ዕቃ ይወሰዳል። ሲምባሎቹ በተለየ የተለሰለሰ ከረጢት ውስጥ መሆን አለባቸው።"),
 ("music", "Keyboard", "ኪቦርድ", 23, "150x50x25", 55.0, False,
  "Hard case or flight case. Stands travel separately.",
  "ጠንካራ ሳጥን ወይም የበረራ ሳጥን። መቆሚያዎቹ በተለየ ይጓዛሉ።"),
 ("music", "Harp", "በገና", 45, "180x100x60", 260.0, True,
  "Wide-body aircraft only. Two-week notice and a signed damage waiver.",
  "በሰፊ አካል አውሮፕላኖች ብቻ። የሁለት ሳምንት ማሳወቂያና የተፈረመ የጉዳት ማስተባበያ።"),
 ("medical", "Folding wheelchair", "የሚታጠፍ የተሽከርካሪ ወንበር", 32, "120x60x40", 0.0, False,
  "Carried free and does not count against your allowance.",
  "በነጻ ይወሰዳል፤ ከፈቃድዎም ላይ አይቀነስም።"),
 ("medical", "Powered wheelchair", "በኃይል የሚሠራ የተሽከርካሪ ወንበር", 100, "120x70x100", 0.0, True,
  "Free, but the battery type must be declared 48 hours ahead.",
  "በነጻ ነው፤ ነገር ግን የባትሪው ዓይነት ከ48 ሰዓት በፊት መገለጽ አለበት።"),
 ("medical", "Mobility scooter", "የመንቀሳቀሻ ስኩተር", 100, "130x60x100", 0.0, True,
  "Free. Lithium batteries above 300 Wh must be removed and carried in the cabin.",
  "በነጻ። ከ300 ዋት-ሰዓት በላይ የሆኑ የሊቲየም ባትሪዎች ተነስተው በካቢን መያዝ አለባቸው።"),
 ("medical", "Portable oxygen concentrator", "ተንቀሳቃሽ የኦክስጅን ማጎሪያ", 10, "40x30x30", 0.0, True,
  "Free. Bring enough battery for 150% of the flight time and a medical letter.",
  "በነጻ። ለበረራው ጊዜ 150% የሚበቃ ባትሪና የሕክምና ደብዳቤ ይዘው ይምጡ።"),
 ("medical", "CPAP machine", "የሲፓፕ መሣሪያ", 10, "40x30x25", 0.0, False,
  "Free and additional to your cabin allowance. Distilled water is not supplied.",
  "በነጻ ነው፤ ከእጅ ሻንጣ ፈቃድዎም በተጨማሪ። የተጣራ ውሃ አይቀርብም።"),
 ("medical", "Stretcher", "አልጋ ቃሬዛ", 0, "-", 0.0, True,
  "Arranged through the medical desk only, at six economy fares. Not bookable online.",
  "የሚዘጋጀው በሕክምና ክፍል ብቻ ነው፤ በስድስት የኢኮኖሚ ታሪፍ። በመስመር ላይ አይያዝም።"),
 ("outsize", "Pushchair or pram", "የሕፃን ጋሪ", 20, "100x50x40", 0.0, False,
  "Free for a passenger travelling with a child. Taken at the aircraft door.",
  "ከልጅ ጋር ለሚጓዝ ተሳፋሪ በነጻ። በአውሮፕላኑ በር ላይ ይወሰዳል።"),
 ("outsize", "Car child seat", "የመኪና የሕፃን መቀመጫ", 12, "70x50x50", 0.0, False,
  "Free when a child is on the booking. Otherwise charged as an extra piece.",
  "በቦታ ማስያዣው ላይ ልጅ ሲኖር በነጻ። ካልሆነ እንደ ተጨማሪ ዕቃ ይከፈላል።"),
 ("outsize", "Television or monitor", "ቴሌቪዥን ወይም ማሳያ", 32, "160x30x110", 95.0, True,
  "Original packaging or a wooden crate. Screens above 165 cm go as cargo.",
  "የመጀመሪያው ማሸጊያ ወይም የእንጨት ሳጥን። ከ165 ሴሜ በላይ ማሳያዎች እንደ ጭነት ይሄዳሉ።"),
 ("outsize", "Bulky household appliance", "ግዙፍ የቤት ዕቃ", 32, "120x80x80", 110.0, True,
  "Fluids drained and the door taped shut.",
  "ፈሳሾቹ ተራግፈው በሩ ተለጥፎ ተዘግቶ።"),
 ("outsize", "Framed artwork", "በክፈፍ የተቀረጸ ሥዕል", 23, "150x100x20", 80.0, True,
  "Glass must be removed or taped. We do not insure glass in the hold.",
  "መስታወቱ መነሳት ወይም መለጠፍ አለበት። በጭነት ክፍል ላለ መስታወት ዋስትና አንሰጥም።"),
 ("outsize", "Traditional drum", "ባህላዊ ከበሮ", 23, "100x60x60", 45.0, False,
  "Skin heads loosened for the pressure change, in a padded cover.",
  "ለግፊት ለውጡ ቆዳዎቹ ላልተው፣ በተለሰለሰ ሽፋን ውስጥ።"),
 ("restricted", "Sporting firearm", "የስፖርት ተኩስ መሣሪያ", 23, "130x30x20", 100.0, True,
  "Permit required, declared at check-in, in a locked hard case.",
  "ፈቃድ ያስፈልጋል፤ በቼክ-ኢን ጊዜ ይገለጻል፤ በተቆለፈ ጠንካራ ሳጥን ውስጥ።"),
 ("restricted", "Ammunition", "ጥይት", 5, "30x20x20", 50.0, True,
  "Up to 5 kg per passenger, in the manufacturer's packaging, separate from the firearm.",
  "በአንድ ተሳፋሪ እስከ 5 ኪግ፣ በአምራቹ ማሸጊያ ውስጥ፣ ከተኩስ መሣሪያው ተለይቶ።"),
 ("restricted", "Hoverboard or self-balancing board", "ሆቨርቦርድ ወይም ራስ ማመጣጠኛ ቦርድ", 0, "-", 0.0, False,
  "Not accepted in the cabin or the hold, on any route, at any weight.",
  "በካቢንም ሆነ በጭነት ክፍል፣ በማንኛውም መስመር፣ በማንኛውም ክብደት አይቀበልም።"),
 ("restricted", "Smart bag with fixed battery", "ቋሚ ባትሪ ያለው ስማርት ሻንጣ", 0, "-", 0.0, False,
  "Refused unless the battery can be removed and carried in the cabin.",
  "ባትሪው ተነስቶ በካቢን መያዝ ካልተቻለ አይቀበልም።"),
]


def build() -> list[dict]:
    rows = []
    for index, (category, item_en, item_am, kg, dims, fee, notice,
                note_en, note_am) in enumerate(ITEMS, start=1):
        rows.append({"id": index, "category": category,
                     "item_en": item_en, "item_am": item_am,
                     "max_kg": kg, "max_dims_cm": dims, "fee_usd": fee,
                     "advance_notice_required": notice,
                     "notes_en": note_en, "notes_am": note_am})
    return rows


def main() -> None:
    rows = build()
    assert len(rows) == 40, f"SPEC.md 12 asks for 40 items, got {len(rows)}"

    fees = {r["fee_usd"] for r in rows}
    assert len(fees) > 8, (
        f"only {len(fees)} distinct fees; 'what does it cost' would be guessable")
    assert any(r["advance_notice_required"] for r in rows) and \
           any(not r["advance_notice_required"] for r in rows), \
        "every item needs notice, or none does; the question answers itself"
    assert any(r["max_kg"] == 0 for r in rows), \
        "nothing is refused outright, so 'can I take it' is always yes"
    assert any(r["fee_usd"] == 0 for r in rows), \
        "nothing is carried free, so 'is there a charge' is always yes"
    assert len({r["category"] for r in rows}) >= 4, "too few categories to filter by"
    assert len({r["item_en"] for r in rows}) == len(rows), "duplicate item"

    bicycle = next(r for r in rows if r["item_en"] == "Bicycle")
    assert bicycle["advance_notice_required"], "task 14 expects notice for a bicycle"
    for token in ("Handlebars", "pedals"):
        assert token in bicycle["notes_en"], f"task 14 expects {token!r} on the page"

    target = ROOT / "spec" / "seed_data" / "special_baggage.yaml"
    target.write_text(
        yaml.safe_dump({"special_baggage_items": rows}, allow_unicode=True,
                       sort_keys=False, width=10_000), "utf-8")
    print(f"wrote {target.relative_to(ROOT)}")
    print(f"  items         {len(rows):>3}")
    print(f"  categories    {sorted({r['category'] for r in rows})}")
    print(f"  free of charge{sum(1 for r in rows if r['fee_usd'] == 0):>3}")
    print(f"  need notice   {sum(1 for r in rows if r['advance_notice_required']):>3}")
    print(f"  not carried   {sum(1 for r in rows if r['max_kg'] == 0):>3}")


if __name__ == "__main__":
    main()
