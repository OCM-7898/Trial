import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

ROOMS = [
 ("TRANSIT-S", ("Transit single", "የመሸጋገሪያ ነጠላ"),
  ("Airside single room with shower. No visa needed; you stay inside the transit area.",
   "ሻወር ያለው ከደህንነት ፍተሻ በኋላ ያለ ነጠላ ክፍል። ቪዛ አያስፈልግም፤ በመሸጋገሪያ ቀጠናው ውስጥ ይቆያሉ።"), 1, 55.0, 6, 12, True),
 ("TRANSIT-D", ("Transit double", "የመሸጋገሪያ ድርብ"),
  ("Airside room for two with shower and desk.",
   "ሻወርና ጠረጴዛ ያለው ለሁለት ሰው ከደህንነት ፍተሻ በኋላ ያለ ክፍል።"), 2, 78.0, 6, 8, True),
 ("TRANSIT-F", ("Transit family", "የመሸጋገሪያ የቤተሰብ"),
  ("Airside room sleeping four, with two bathrooms.",
   "ሁለት መታጠቢያ ያለው አራት ሰው የሚያድርበት ከደህንነት ፍተሻ በኋላ ያለ ክፍል።"), 4, 120.0, 6, 4, True),
 ("LANDSIDE-S", ("Landside single", "ከደህንነት ፍተሻ ውጭ ነጠላ"),
  ("Single room on the public side of the terminal. Requires a visa, since you pass immigration.",
   "በተርሚናሉ የሕዝብ በኩል ያለ ነጠላ ክፍል። በኢሚግሬሽን ስለሚያልፉ ቪዛ ያስፈልጋል።"), 1, 42.0, 6, 10, False),
 ("SUITE", ("Rest suite", "የማረፊያ ስዊት"),
  ("Suite with a separate lounge area and meal service.",
   "የተለየ የማረፊያ ቦታና የምግብ አገልግሎት ያለው ስዊት።"), 2, 145.0, 6, 3, True),
]

VISAS = [
 ("EV-T30", ("Tourist e-Visa, 30 days", "የቱሪስት ኢ-ቪዛ፣ 30 ቀን"),
  ("Holiday and family visits. Not valid for paid work or study.",
   "ለበዓልና ለቤተሰብ ጉብኝት። ለክፍያ ሥራ ወይም ለትምህርት አይሠራም።"),
  ("Passport valid six months beyond arrival; a recent passport photograph; a confirmed return ticket; proof of accommodation.",
   "ከመድረሻ በኋላ ለስድስት ወር የሚሠራ ፓስፖርት፤ የቅርብ ጊዜ የፓስፖርት ፎቶግራፍ፤ የተረጋገጠ የመመለሻ ትኬት፤ የመኖሪያ ማረጋገጫ።"),
  30, 52.0, 3),
 ("EV-T90", ("Tourist e-Visa, 90 days", "የቱሪስት ኢ-ቪዛ፣ 90 ቀን"),
  ("Longer holiday stays. Single entry only.",
   "ረዘም ያለ የበዓል ቆይታ። አንድ ጊዜ መግቢያ ብቻ።"),
  ("As for the 30-day visa, plus a bank statement covering the last three months.",
   "እንደ 30 ቀኑ ቪዛ፣ በተጨማሪም ያለፉትን ሦስት ወራት የሚሸፍን የባንክ መግለጫ።"),
  90, 82.0, 5),
 ("EV-TR", ("Transit e-Visa", "የመሸጋገሪያ ኢ-ቪዛ"),
  ("For passengers leaving the airport during a connection of up to 72 hours.",
   "እስከ 72 ሰዓት በሚደርስ መሸጋገሪያ ወቅት አየር ማረፊያውን ለሚለቁ ተሳፋሪዎች።"),
  ("Passport; the onward ticket; the booking reference for the connecting flight.",
   "ፓስፖርት፤ የቀጣይ ትኬት፤ የመሸጋገሪያ በረራው የቦታ ማስያዣ ማጣቀሻ።"),
  3, 20.0, 1),
 ("EV-BIZ", ("Business e-Visa", "የንግድ ኢ-ቪዛ"),
  ("Meetings and conferences. Not valid for employment.",
   "ስብሰባዎችና ጉባኤዎች። ለቅጥር አይሠራም።"),
  ("Passport; photograph; an invitation letter from the host organisation; company registration details.",
   "ፓስፖርት፤ ፎቶግራፍ፤ ከአስተናጋጁ ድርጅት የግብዣ ደብዳቤ፤ የኩባንያ ምዝገባ ዝርዝር።"),
  30, 72.0, 5),
]

RAIL = [
 ("FRA", ("Cologne", "ኮሎኝ"), ("Rheinweg Rail", "ራይንቬግ ሬል"), 62, 0,
  ("Rail & Fly through-ticket", "የባቡርና በረራ ጥምር ትኬት"),
  ("Book the rail leg with your flight in one transaction. The ticket is issued to your booking reference and is valid on any train that day.",
   "የባቡሩን ክፍል ከበረራዎ ጋር በአንድ ግብይት ይያዙ። ትኬቱ በቦታ ማስያዣ ማጣቀሻዎ ይወጣል፤ በዚያ ቀን በማንኛውም ባቡር ላይም ይሠራል።")),
 ("FRA", ("Stuttgart", "ስቱትጋርት"), ("Rheinweg Rail", "ራይንቬግ ሬል"), 78, 0,
  ("Rail & Fly through-ticket", "የባቡርና በረራ ጥምር ትኬት"),
  ("Book with your flight. Valid on any train on the day of travel.",
   "ከበረራዎ ጋር ይያዙ። በጉዞው ቀን በማንኛውም ባቡር ላይ ይሠራል።")),
 ("FRA", ("Munich", "ሙኒክ"), ("Rheinweg Rail", "ራይንቬግ ሬል"), 195, 1,
  ("Rail & Fly through-ticket", "የባቡርና በረራ ጥምር ትኬት"),
  ("One change at Mannheim. Book with your flight; seat reservation is extra.",
   "በማንሃይም አንድ ለውጥ። ከበረራዎ ጋር ይያዙ፤ የመቀመጫ ማስያዣ ተጨማሪ ነው።")),
 ("BRU", ("Antwerp", "አንትወርፕ"), ("Lowlands Rail", "ሎውላንድስ ሬል"), 45, 0,
  ("Airport rail add-on", "የአየር ማረፊያ ባቡር ተጨማሪ"),
  ("Bought as an add-on after ticketing, not with the flight.",
   "ከትኬት በኋላ እንደ ተጨማሪ ይገዛል እንጂ ከበረራው ጋር አይደለም።")),
 ("CDG", ("Lille", "ሊል"), ("Hexagone Rail", "ሄክሳጎን ሬል"), 60, 0,
  ("Rail & Fly through-ticket", "የባቡርና በረራ ጥምር ትኬት"),
  ("Book with your flight. Delays on the rail leg are covered by the airline's connection guarantee.",
   "ከበረራዎ ጋር ይያዙ። በባቡሩ ክፍል ላይ ያሉ መዘግየቶች በአየር መንገዱ የመሸጋገሪያ ዋስትና ይሸፈናሉ።")),
 ("AMS", ("Rotterdam", "ሮተርዳም"), ("Lowlands Rail", "ሎውላንድስ ሬል"), 30, 0,
  ("Airport rail add-on", "የአየር ማረፊያ ባቡር ተጨማሪ"),
  ("Bought at the station or online; not combinable with the flight booking.",
   "በጣቢያው ወይም በመስመር ላይ ይገዛል፤ ከበረራ ቦታ ማስያዣው ጋር አይጣመርም።")),
]

CARS = [
 ("NBO", "transfer", ("Private sedan transfer", "የግል ሴዳን ትራንስፖርት"), 3, 2, 38.0, False),
 ("NBO", "transfer", ("Private van transfer", "የግል ቫን ትራንስፖርት"), 7, 6, 62.0, False),
 ("NBO", "transfer", ("Shared shuttle", "የጋራ ሸተል"), 12, 1, 14.0, False),
 ("NBO", "rental", ("Compact car", "ትንሽ መኪና"), 5, 2, 44.0, True),
 ("NBO", "rental", ("Four-wheel drive", "ባለአራት ጎማ"), 5, 4, 89.0, True),
 ("ADD", "transfer", ("Private sedan transfer", "የግል ሴዳን ትራንስፖርት"), 3, 2, 32.0, False),
 ("ADD", "transfer", ("Private van transfer", "የግል ቫን ትራንስፖርት"), 7, 6, 55.0, False),
 ("ADD", "rental", ("Compact car", "ትንሽ መኪና"), 5, 2, 39.0, True),
 ("JNB", "transfer", ("Private sedan transfer", "የግል ሴዳን ትራንስፖርት"), 3, 2, 41.0, False),
 ("JNB", "rental", ("Estate car", "ሰፊ መኪና"), 5, 4, 58.0, True),
 ("LHR", "transfer", ("Private sedan transfer", "የግል ሴዳን ትራንስፖርት"), 3, 2, 74.0, False),
 ("DXB", "transfer", ("Private sedan transfer", "የግል ሴዳን ትራንስፖርት"), 3, 2, 46.0, False),
]

INSURANCE = [
 ("SV-BASIC", ("Essential cover", "መሠረታዊ ሽፋን"),
  ("Emergency medical treatment and repatriation. Baggage and cancellation are not covered.",
   "የአስቸኳይ ሕክምናና የመመለስ አገልግሎት። ሻንጣና ስረዛ አይሸፈኑም።"), 100000, 0, 0, 3.5, 18.0),
 ("SV-PLUS", ("Traveller cover", "የተጓዥ ሽፋን"),
  ("Medical, delayed and lost baggage, and cancellation for a covered reason.",
   "ሕክምና፣ የዘገየና የጠፋ ሻንጣ፣ እንዲሁም በተሸፈነ ምክንያት ስረዛ።"), 250000, 3000, 1500, 5.5, 32.0),
 ("SV-MAX", ("Comprehensive cover", "ሁሉን አቀፍ ሽፋን"),
  ("Everything in Traveller cover, plus cancellation for any reason at 60% of the fare.",
   "በተጓዥ ሽፋን ውስጥ ያለው ሁሉ፣ በተጨማሪም በማንኛውም ምክንያት ከታሪፉ 60% ስረዛ።"), 500000, 8000, 3000, 8.5, 55.0),
]


def main() -> None:
    rooms = [{"id": i, "code": c, "name_en": n[0], "name_am": n[1],
              "description_en": d[0], "description_am": d[1], "sleeps": s,
              "price_per_block_usd": p, "block_hours": b, "rooms_available": a,
              "airside": air}
             for i, (c, n, d, s, p, b, a, air) in enumerate(ROOMS, 1)]
    visas = [{"id": i, "code": c, "name_en": n[0], "name_am": n[1],
              "eligibility_en": e[0], "eligibility_am": e[1],
              "documents_en": doc[0], "documents_am": doc[1],
              "validity_days": v, "fee_usd": f, "processing_days": pd}
             for i, (c, n, e, doc, v, f, pd) in enumerate(VISAS, 1)]
    rail = [{"id": i, "arrival_iata": a, "destination_en": d[0], "destination_am": d[1],
             "operator_en": op[0], "operator_am": op[1], "journey_min": j, "changes": ch,
             "ticket_type_en": tt[0], "ticket_type_am": tt[1],
             "booking_note_en": bn[0], "booking_note_am": bn[1]}
            for i, (a, d, op, j, ch, tt, bn) in enumerate(RAIL, 1)]
    cars = [{"id": i, "airport_iata": a, "category": cat, "name_en": n[0],
             "name_am": n[1], "seats": s, "luggage": l, "price_usd": p, "per_day": pd}
            for i, (a, cat, n, s, l, p, pd) in enumerate(CARS, 1)]
    insurance = [{"id": i, "code": c, "name_en": n[0], "name_am": n[1],
                  "coverage_en": cov[0], "coverage_am": cov[1],
                  "medical_limit_usd": m, "cancellation_limit_usd": can,
                  "baggage_limit_usd": bag, "price_pct": pct, "price_min_usd": mn}
                 for i, (c, n, cov, m, can, bag, pct, mn) in enumerate(INSURANCE, 1)]

    nbo = [c for c in cars if c["airport_iata"] == "NBO"]
    assert len({c["seats"] for c in nbo}) >= 3, "NBO options do not differ on capacity"
    assert len({c["luggage"] for c in nbo}) >= 3, "NBO options do not differ on luggage"
    assert any(v["validity_days"] == 3 for v in visas), "no short transit visa to mis-pick"
    assert len({v["fee_usd"] for v in visas}) == len(visas), "visa fees are not distinct"
    assert len({r["ticket_type_en"] for r in rail}) >= 2, "all rail legs book the same way"
    airports = {a["iata"] for a in yaml.safe_load(
        (ROOT / "spec/seed_data/airports.yaml").read_text("utf-8"))["airports"]}
    dangling = sorted({r["arrival_iata"] for r in rail} - airports)
    assert not dangling, f"rail connections start from airports we do not serve: {dangling}"

    out = ROOT / "spec/seed_data/partners.yaml"
    out.write_text("# Generated by tools/make_partners.py -- edit there, not here.\n"
                   + yaml.safe_dump({"hotel_rooms": rooms, "visa_types": visas,
                                     "rail_connections": rail, "car_offers": cars,
                                     "insurance_products": insurance},
                                    sort_keys=False, allow_unicode=True), "utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    for label, rows in (("hotel rooms", rooms), ("visa types", visas),
                        ("rail connections", rail), ("car offers", cars),
                        ("insurance products", insurance)):
        print(f"  {label:20s} {len(rows)}")


if __name__ == "__main__":
    main()
