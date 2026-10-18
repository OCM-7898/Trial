from __future__ import annotations

import html
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.brand import BRANDS
from tools.content_pages_extra import EXTRA

AIRLINE_EN, AIRLINE_AM = BRANDS["airline"]["en"], BRANDS["airline"]["am"]
BIZ_EN, BIZ_AM = BRANDS["cabin_business"]["en"], BRANDS["cabin_business"]["am"]
MILES_EN, MILES_AM = BRANDS["loyalty"]["en"], BRANDS["loyalty"]["am"]


def brief(slug, category, position, title, summary, sections):
    return page(slug, category, position, title, summary, sections)


def page(slug, category, position, title, summary, sections):
    return {
        "slug": slug, "category": category, "position": position,
        "title_en": title[0], "title_am": title[1],
        "summary_en": summary[0], "summary_am": summary[1],
        "body_html_en": _render(sections, 0),
        "body_html_am": _render(sections, 1),
    }


def _render(sections, index: int) -> str:
    parts = []
    for heading, blocks in sections:
        parts.append(f"<h2>{html.escape(heading[index])}</h2>")
        for block in blocks:
            if isinstance(block, tuple):
                parts.append(f"<p>{html.escape(block[index])}</p>")
            else:
                items = "".join(f"<li>{html.escape(b[index])}</li>" for b in block)
                parts.append(f"<ul>{items}</ul>")
    return "".join(parts)


PAGES = [
    page("allergies", "health", 1,
         ("Allergies on board", "በበረራ ላይ አለርጂዎች"),
         ("What we can and cannot do for passengers with food allergies.",
          "የምግብ አለርጂ ላላቸው ተሳፋሪዎች ምን ማድረግ እንደምንችልና እንደማንችል።"),
         [
          (("We cannot guarantee an allergen-free cabin", "አለርጂ-ነጻ ካቢን ዋስትና መስጠት አንችልም"),
           [("Our aircraft are not free of nuts, dairy, gluten, sesame or shellfish. "
             "Other passengers may bring food on board, and cabins are not deep-cleaned "
             "between every sector. We therefore cannot describe any flight as allergen-free.",
             "አውሮፕላኖቻችን ከለውዝ፣ ከወተት ተዋጽኦ፣ ከግሉተን፣ ከሰሊጥ ወይም ከሼልፊሽ ነጻ አይደሉም። ሌሎች ተሳፋሪዎች ምግብ "
             "ይዘው ሊገቡ ይችላሉ፤ ካቢኖችም በእያንዳንዱ ክፍል መካከል በጥልቀት አይጸዱም። ስለዚህ ማንኛውንም በረራ አለርጂ-ነጻ ብለን "
             "መግለጽ አንችልም።")]),
          (("Before you travel", "ከመጓዝዎ በፊት"),
           [[("Tell us at least 48 hours before departure by adding a note to your booking "
              "or calling the contact office for your country.",
              "ከመነሻው ቢያንስ 48 ሰዓት በፊት በቦታ ማስያዣዎ ላይ ማስታወሻ በመጨመር ወይም የአገርዎን የመገናኛ ቢሮ በመደወል ያሳውቁን።"),
             ("Order a special meal that excludes your allergen. Special meals close 24 hours "
              "before departure and cannot be arranged at the airport.",
              "አለርጂዎን የማያካትት ልዩ ምግብ ያዙ። ልዩ ምግቦች ከመነሻው 24 ሰዓት በፊት ይዘጋሉ፤ በአየር ማረፊያም ሊዘጋጁ አይችሉም።"),
             ("Carry your own antihistamines and adrenaline auto-injector in your cabin "
              "baggage, not in the hold. Cabin crew carry a medical kit but it is not a "
              "substitute for your own medication.",
              "የራስዎን ፀረ-ሂስታሚንና የአድሬናሊን መርፌ በእጅ ሻንጣዎ ውስጥ ይያዙ፤ በጭነት ክፍል ውስጥ አይደለም። የካቢን ሠራተኞች "
              "የሕክምና ቁሳቁስ ይይዛሉ፤ ነገር ግን ለራስዎ መድኃኒት ምትክ አይደለም።"),
             ("Bring a doctor's letter if you carry injectable medication, so it is not "
              "questioned at security.",
              "የመርፌ መድኃኒት የሚይዙ ከሆነ በደህንነት ፍተሻ ጥያቄ እንዳይነሳ የሐኪም ደብዳቤ ይዘው ይምጡ።")]]),
          (("On board", "በበረራ ላይ"),
           [("Tell the cabin crew when you board. They can make an announcement asking other "
             "passengers not to open nut products, and they will note your seat. "
             "The announcement is a request, not an enforceable rule.",
             "በሚሳፈሩበት ጊዜ ለካቢን ሠራተኞች ይንገሩ። ሌሎች ተሳፋሪዎች የለውዝ ምርቶችን እንዳይከፍቱ ማስታወቂያ ማድረግ ይችላሉ፤ "
             "መቀመጫዎንም ይመዘግባሉ። ማስታወቂያው ጥያቄ እንጂ የሚያስገድድ ደንብ አይደለም።"),
            ("You may bring your own sealed food on board for your own consumption.",
             "ለራስዎ ፍጆታ የታሸገ የራስዎን ምግብ ይዘው መሳፈር ይችላሉ።")]),
          (("Buffer zones", "የመከላከያ ቀጠናዎች"),
           [("On request we will seat you away from the galley and note a buffer of one row "
             "in front and behind. Buffer zones cannot be guaranteed on a full flight.",
             "በጥያቄዎ መሠረት ከጋሊው ራቅ ብለን እናስቀምጥዎታለን፤ ከፊትና ከኋላ የአንድ ረድፍ መከላከያም እንመዘግባለን። በሙሉ በረራ ላይ "
             "የመከላከያ ቀጠናዎች ዋስትና ሊሰጣቸው አይችልም።")]),
         ]),

    page("special-baggage", "baggage", 1,
         ("Special and sports baggage", "ልዩና የስፖርት ሻንጣ"),
         ("Rules, weight limits and charges for sports equipment and outsize items.",
          "ለስፖርት መሣሪያዎችና ለትልልቅ ዕቃዎች ደንቦች፣ የክብደት ገደቦችና ክፍያዎች።"),
         [
          (("How special baggage is charged", "ልዩ ሻንጣ እንዴት እንደሚከፈል"),
           [("Sports equipment counts as one checked bag if it is within your free allowance "
             "and under the weight limit for the item. Anything above that is charged at the "
             "fixed item fee below, which replaces the normal excess-weight rate.",
             "የስፖርት መሣሪያ በነጻ ፈቃድዎ ውስጥ ከሆነና ከዕቃው የክብደት ገደብ በታች ከሆነ እንደ አንድ የተመዘገበ ሻንጣ ይቆጠራል። "
             "ከዚያ በላይ የሆነው ከታች ባለው ቋሚ የዕቃ ክፍያ ይከፈላል፤ ይህም መደበኛውን የትርፍ ክብደት ተመን ይተካል።"),
            ("Items marked as requiring advance notice must be declared at least 48 hours "
             "before departure. We cannot accept them at the airport without a booking.",
             "ቅድሚያ ማሳወቅ የሚያስፈልጋቸው ተብለው የተመዘገቡ ዕቃዎች ከመነሻው ቢያንስ 48 ሰዓት በፊት መገለጽ አለባቸው። ያለ ቅድመ "
             "ማስያዣ በአየር ማረፊያ ልንቀበላቸው አንችልም።")]),
          (("Packing requirements", "የማሸግ መስፈርቶች"),
           [[("Bicycles must have the handlebars turned, pedals removed and tyres deflated, "
              "in a bicycle bag or box.",
              "ብስክሌቶች መሪያቸው ተዙሮ፣ ፔዳሎቻቸው ተነስተውና ጎማዎቻቸው አየር ወጥቶላቸው በብስክሌት ከረጢት ወይም ሳጥን መሆን አለባቸው።"),
             ("Firearms for sport require a permit and must be declared; ammunition is limited "
              "to 5 kg per passenger and must travel separately from the firearm.",
              "ለስፖርት የሚውሉ የጦር መሣሪያዎች ፈቃድ ያስፈልጋቸዋል፤ መገለጽም አለባቸው። ጥይት በአንድ ተሳፋሪ እስከ 5 ኪግ የተወሰነ ሲሆን "
              "ከመሣሪያው ተለይቶ መጓዝ አለበት።"),
             ("Surfboards and windsurf equipment must be in a padded board bag.",
              "የሰርፍ ሰሌዳዎችና የንፋስ ሰርፍ መሣሪያዎች በተለጠፈ የሰሌዳ ከረጢት ውስጥ መሆን አለባቸው።"),
             ("Diving cylinders must be empty, with the valve removed or open for inspection.",
              "የመጥለቂያ ሲሊንደሮች ባዶ መሆን አለባቸው፤ ቫልቫቸውም ተነስቶ ወይም ለፍተሻ ክፍት መሆን አለበት።")]]),
          (("Items we cannot carry", "ልንወስዳቸው የማንችላቸው ዕቃዎች"),
           [("Loose lithium batteries above 160 Wh, powered ride-on suitcases with "
             "non-removable batteries, and hoverboards are not accepted in either cabin or "
             "hold baggage on any route.",
             "ከ160 ዋት-ሰዓት በላይ የሆኑ ነጠላ የሊቲየም ባትሪዎች፣ የማይነሱ ባትሪ ያላቸው በኤሌክትሪክ የሚነዱ ሻንጣዎችና ሆቨርቦርዶች "
             "በማንኛውም መስመር በእጅም ሆነ በተመዘገበ ሻንጣ አይፈቀዱም።")]),
         ]),

    brief("cabin-baggage", "baggage", 2,
        ("Cabin baggage", "የእጅ ሻንጣ"),
        ("Size, weight and what must go in the hold instead.",
         "መጠን፣ ክብደትና በምትኩ በጭነት ክፍል መሄድ ያለበት።"),
        [(("What you may carry into the cabin", "ወደ ካቢን ይዘው መግባት የሚችሉት"),
          [("One cabin bag of up to 7 kg in Selam Economy and 14 kg in " + BIZ_EN +
            ", not exceeding 55 x 38 x 20 cm including wheels and handles. One personal "
            "item such as a handbag or laptop bag may be carried in addition.",
            "በሰላም ኢኮኖሚ እስከ 7 ኪግ እና በ" + BIZ_AM + " እስከ 14 ኪግ የሚመዝን አንድ የእጅ ሻንጣ፤ መንኮራኩሮችንና "
            "እጀታዎችን ጨምሮ ከ55 x 38 x 20 ሴሜ መብለጥ የለበትም። እንደ የእጅ ቦርሳ ወይም የላፕቶፕ ቦርሳ ያለ አንድ የግል ዕቃ "
            "በተጨማሪ ሊያዝ ይችላል።"),
           ("On full flights and on Dash 8-400 services, cabin bags may be placed in the "
            "hold at the gate at no charge. Remove medication, documents and valuables first.",
            "በሙሉ በረራዎችና በዳሽ 8-400 አገልግሎቶች የእጅ ሻንጣዎች ያለክፍያ በበሩ ላይ ወደ ጭነት ክፍል ሊገቡ ይችላሉ። መድኃኒት፣ "
            "ሰነዶችንና ውድ ዕቃዎችን አስቀድመው ያውጡ።")]),
         (("Liquids", "ፈሳሾች"),
          [("Containers of up to 100 ml each, in a single transparent resealable bag of no "
            "more than one litre. Baby food and prescribed medication for the journey are "
            "exempt but must be declared at security.",
            "እያንዳንዳቸው እስከ 100 ሚሊ ሊትር የሆኑ ዕቃዎች፣ ከአንድ ሊትር በማይበልጥ አንድ ግልጽ ሊዘጋ በሚችል ከረጢት ውስጥ። "
            "የሕፃናት ምግብና ለጉዞው የታዘዘ መድኃኒት ነጻ ናቸው፤ ነገር ግን በደህንነት ፍተሻ መገለጽ አለባቸው።")])]),

    brief("baggage-infants", "baggage", 3,
        ("Baggage for infants and children", "ለጨቅላዎችና ለሕፃናት ሻንጣ"),
        ("Allowances for passengers under 12, and what counts as equipment.",
         "ከ12 ዓመት በታች ላሉ ተሳፋሪዎች ፈቃዶች፣ እና እንደ መሣሪያ የሚቆጠረው።"),
        [(("Infants under two", "ከሁለት ዓመት በታች ጨቅላዎች"),
          [("An infant travelling on an adult's lap has one checked bag of up to 10 kg and no "
            "cabin baggage allowance of their own.",
            "በአዋቂ ጭን ላይ የሚጓዝ ጨቅላ እስከ 10 ኪግ የሚመዝን አንድ የተመዘገበ ሻንጣ አለው፤ የራሱ የእጅ ሻንጣ ፈቃድ የለውም።"),
           ("One pushchair and one car seat travel free on every route, in addition to the "
            "allowance, and may be taken to the aircraft door.",
            "አንድ የሕፃን ጋሪና አንድ የመኪና መቀመጫ ከፈቃዱ በተጨማሪ በሁሉም መስመር በነጻ ይጓዛሉ፤ እስከ አውሮፕላኑ በር ሊወሰዱም "
            "ይችላሉ።")]),
         (("Children aged two to eleven", "ከሁለት እስከ አስራ አንድ ዓመት ሕፃናት"),
          [("A child with their own seat has the same free allowance as an adult on the same "
            "route and cabin.",
            "የራሱ መቀመጫ ያለው ሕፃን በተመሳሳይ መስመርና የጉዞ ክፍል ከአዋቂ ጋር እኩል የነጻ ፈቃድ አለው።")])]),

    brief("baggage-codeshare", "baggage", 4,
        ("Baggage on partner-operated flights", "በአጋር በሚከናወኑ በረራዎች ሻንጣ"),
        ("Whose rules apply when part of your journey is flown by another airline.",
         "የጉዞዎ አንድ ክፍል በሌላ አየር መንገድ ሲከናወን የማን ደንብ እንደሚሠራ።"),
        [(("The first marketing carrier sets the allowance", "የመጀመሪያው ሻጭ አየር መንገድ ፈቃዱን ይወስናል"),
          [("Where a journey booked with us includes a sector operated by a partner, our "
            "allowance applies throughout, provided the whole journey is on one booking "
            "reference. Separate bookings are treated as separate journeys and each carrier's "
            "own rules apply.",
            "ከእኛ ጋር የተያዘ ጉዞ በአጋር የሚከናወን ክፍል ካካተተ፣ ጉዞው በሙሉ በአንድ የቦታ ማስያዣ ማጣቀሻ እስከሆነ ድረስ የእኛ ፈቃድ "
            "በሙሉ ጉዞው ላይ ይሠራል። የተለያዩ የቦታ ማስያዣዎች እንደ የተለያዩ ጉዞዎች ይቆጠራሉ፤ የእያንዳንዱም አየር መንገድ ደንብ "
            "ይሠራል።"),
           ("Partner-operated sectors cannot be checked in online; use the airport desk.",
            "በአጋር የሚከናወኑ ክፍሎች በመስመር ላይ ቼክ-ኢን ሊደረጉ አይችሉም፤ የአየር ማረፊያውን ጠረጴዛ ይጠቀሙ።")])]),

    brief("baggage-restricted", "baggage", 5,
        ("Restricted and prohibited items", "የተገደቡና የተከለከሉ ዕቃዎች"),
        ("What may not travel at all, and what may travel only in the hold.",
         "በፍጹም መጓዝ የማይችለው፣ እና በጭነት ክፍል ብቻ መጓዝ የሚችለው።"),
        [(("Never accepted", "በፍጹም የማይፈቀዱ"),
          [[("Explosives, fireworks and flares.", "ፈንጂዎች፣ ርችቶችና ችቦዎች።"),
            ("Compressed gases, including camping gas and unapproved oxygen cylinders.",
             "የተጨመቁ ጋዞች፣ የካምፕ ጋዝንና ያልጸደቁ የኦክስጅን ሲሊንደሮችን ጨምሮ።"),
            ("Corrosives such as mercury, wet-cell batteries and drain cleaner.",
             "እንደ ሜርኩሪ፣ እርጥብ ባትሪዎችና የቱቦ ማጽጃ ያሉ የሚበሉ ንጥረ ነገሮች።")]]),
         (("Hold only", "በጭነት ክፍል ብቻ"),
          [("Sharp articles, tools longer than 6 cm, sporting bats and cricket stumps must be "
            "checked. Spare lithium batteries are the reverse: they must travel in the cabin "
            "and never in the hold.",
            "ስለታም ዕቃዎች፣ ከ6 ሴሜ የሚረዝሙ መሣሪያዎች፣ የስፖርት ዱላዎችና የክሪኬት እንጨቶች መመዝገብ አለባቸው። ተጠባባቂ የሊቲየም "
            "ባትሪዎች ግን ተቃራኒ ናቸው፤ በካቢን ውስጥ መጓዝ አለባቸው እንጂ በጭነት ክፍል በፍጹም አይደለም።")])]),

    brief("airport-checkin", "booking-help", 1,
        ("Airport check-in and bag drop", "የአየር ማረፊያ ቼክ-ኢንና ሻንጣ ማስረከቢያ"),
        ("Desk opening and closing times, and when you must use a desk.",
         "የጠረጴዛ መክፈቻና መዝጊያ ሰዓቶች፣ እና ጠረጴዛ መጠቀም ያለብዎት መቼ እንደሆነ።"),
        [(("Desk times", "የጠረጴዛ ሰዓቶች"),
          [("Desks open 3 hours before an international departure and 2 hours before a "
            "domestic one, and close 60 minutes before departure on all routes. Bag drop for "
            "passengers already checked in online closes at the same time.",
            "ጠረጴዛዎች ከዓለም አቀፍ መነሻ 3 ሰዓት በፊት እና ከአገር ውስጥ 2 ሰዓት በፊት ይከፈታሉ፤ በሁሉም መስመሮች ከመነሻው 60 "
            "ደቂቃ በፊት ይዘጋሉ። አስቀድመው በመስመር ላይ ቼክ-ኢን ላደረጉ ተሳፋሪዎች የሻንጣ ማስረከቢያም በተመሳሳይ ሰዓት ይዘጋል።")]),
         (("When a desk is required", "ጠረጴዛ የሚያስፈልግበት ጊዜ"),
          [("Passengers travelling with an infant on the lap, an unaccompanied minor, booked "
            "special assistance, or on a partner-operated sector must check in at a desk. "
            "Group bookings of ten or more are handled by the group desk.",
            "ጨቅላን በጭን ይዘው የሚጓዙ፣ ያለአጃቢ ሕፃናት፣ ልዩ ድጋፍ ያስያዙ፣ ወይም በአጋር በሚከናወን ክፍል ላይ ያሉ ተሳፋሪዎች "
            "በጠረጴዛ ቼክ-ኢን ማድረግ አለባቸው። አሥርና ከዚያ በላይ የቡድን ቦታ ማስያዣዎች በቡድን ጠረጴዛ ይስተናገዳሉ።")])]),

    brief("boarding-and-gates", "booking-help", 2,
        ("Boarding and gate closure", "መሳፈሪያና የበር መዘጋት"),
        ("When boarding starts, and what happens if you arrive late at the gate.",
         "መሳፈር መቼ እንደሚጀምር፣ እና በበሩ ዘግይተው ከደረሱ ምን እንደሚሆን።"),
        [(("Timings", "ሰዓቶች"),
          [("Boarding begins 40 minutes before departure and the gate closes 20 minutes "
            "before. A boarding pass shows the boarding time, not the departure time, in its "
            "boarding field.",
            "መሳፈር ከመነሻው 40 ደቂቃ በፊት ይጀምራል፤ በሩም 20 ደቂቃ በፊት ይዘጋል። የመሳፈሪያ ፈቃድ በመሳፈሪያ ሳጥኑ ውስጥ "
            "የመሳፈሪያ ሰዓቱን እንጂ የመነሻ ሰዓቱን አያሳይም።"),
           ("Passengers not at the gate at closure are offloaded with their baggage and the "
            "fare rules of their ticket determine whether a rebooking is chargeable.",
            "በመዘጋቻ ሰዓት በበሩ ያልተገኙ ተሳፋሪዎች ከሻንጣቸው ጋር ይወርዳሉ፤ የትኬታቸው የታሪፍ ደንቦችም እንደገና ማስያዝ "
            "የሚያስከፍል መሆኑን ይወስናሉ።")])]),

    brief("fare-rules-explained", "booking-help", 3,
        ("Understanding fare rules", "የታሪፍ ደንቦችን መረዳት"),
        ("What each fare family allows, and where to find the rules for your own ticket.",
         "እያንዳንዱ የታሪፍ ቤተሰብ የሚፈቅደው፣ እና የራስዎን ትኬት ደንቦች የት እንደሚያገኙ።"),
        [(("Fare families", "የታሪፍ ቤተሰቦች"),
          [("Promo and Lite fares are neither refundable nor changeable. Basic and Group "
            "fares may be changed for a fee but are not refundable. Standard is half "
            "refundable. Flex is fully refundable and changes are free. " + BIZ_EN +
            " fares are refundable in full, with a fee on the Saver family only.",
            "የፕሮሞና የላይት ታሪፎች ተመላሽም ሆነ የሚቀየሩ አይደሉም። የቤዚክና የግሩፕ ታሪፎች በክፍያ ሊቀየሩ ይችላሉ፤ ተመላሽ ግን "
            "አይደረጉም። ስታንዳርድ በግማሽ ተመላሽ ይደረጋል። ፍሌክስ ሙሉ በሙሉ ተመላሽ ይደረጋል፤ ለውጦችም ነጻ ናቸው። የ" +
            BIZ_AM + " ታሪፎች ሙሉ በሙሉ ተመላሽ ይደረጋሉ፤ ክፍያም በሴቨር ቤተሰብ ላይ ብቻ ነው።"),
           ("The fare family of your own ticket is shown beside each flight when you open "
            "your booking, as a two-letter code such as EF or HC.",
            "የራስዎ ትኬት የታሪፍ ቤተሰብ የቦታ ማስያዣዎን ሲከፍቱ እንደ EF ወይም HC ባለ የሁለት ፊደል ኮድ ከእያንዳንዱ በረራ ጎን "
            "ይታያል።")])]),

    brief("involuntary-changes", "booking-help", 4,
        ("If we change or cancel your flight", "በረራዎን ብንቀይር ወይም ብንሰርዝ"),
        ("Your options when the change is ours rather than yours.",
         "ለውጡ የእኛ እንጂ የእርስዎ ካልሆነ ያሉዎት አማራጮች።"),
        [(("Rebooking and refunds", "እንደገና ማስያዝና ተመላሽ ክፍያ"),
          [("Where we cancel a flight or reschedule it by more than three hours, you may take "
            "the next available flight at no charge, or request a full refund regardless of "
            "the fare rules of your ticket. This is separate from a voluntary change and no "
            "change fee or fare difference applies.",
            "በረራ ስንሰርዝ ወይም ከሦስት ሰዓት በላይ ስናዘገይ፣ ያለክፍያ የሚቀጥለውን ያለ በረራ መውሰድ ወይም የትኬትዎ የታሪፍ ደንቦች "
            "ምንም ይሁኑ ምን ሙሉ ተመላሽ ክፍያ መጠየቅ ይችላሉ። ይህ ከፈቃደኝነት ለውጥ የተለየ ሲሆን ምንም የለውጥ ክፍያ ወይም የታሪፍ "
            "ልዩነት አይተገበርም።"),
           ("Requests under this policy are handled by the contact office for your country, "
            "not by the online refund form.",
            "በዚህ ፖሊሲ የሚቀርቡ ጥያቄዎች በመስመር ላይ የተመላሽ ክፍያ ቅጽ ሳይሆን በአገርዎ የመገናኛ ቢሮ ይስተናገዳሉ።")])]),

    brief("special-meals", "onboard", 1,
        ("Special meals", "ልዩ ምግቦች"),
        ("The meal codes we carry and when they must be ordered.",
         "የምንይዛቸው የምግብ ኮዶችና መቼ መታዘዝ እንዳለባቸው።"),
        [(("Ordering", "ማዘዝ"),
          [("Special meals must be requested at least 24 hours before departure through your "
            "booking. They cannot be arranged at the airport or on board, and a request made "
            "inside the cut-off will not be loaded.",
            "ልዩ ምግቦች ከመነሻው ቢያንስ 24 ሰዓት በፊት በቦታ ማስያዣዎ በኩል መጠየቅ አለባቸው። በአየር ማረፊያ ወይም በበረራ ላይ "
            "ሊዘጋጁ አይችሉም፤ ከመዝጊያው በኋላ የቀረበ ጥያቄም አይጫንም።"),
           ("A special meal is prepared to a dietary specification. It is not an allergy "
            "control: it reduces but does not remove the risk of cross-contact, and the "
            "cabin itself is not allergen-free.",
            "ልዩ ምግብ በአመጋገብ መስፈርት ይዘጋጃል። የአለርጂ ቁጥጥር አይደለም፤ የመተላለፍ አደጋን ይቀንሳል እንጂ አያስወግድም፤ "
            "ካቢኑም ራሱ አለርጂ-ነጻ አይደለም።")]),
         (("Codes we carry", "የምንይዛቸው ኮዶች"),
          [[("VGML vegetarian, VJML Jain vegetarian, AVML Asian vegetarian.",
             "VGML ቬጀቴሪያን፣ VJML ጃይን ቬጀቴሪያን፣ AVML እስያዊ ቬጀቴሪያን።"),
            ("GFML gluten intolerant, LFML low fat, LSML low salt, DBML diabetic.",
             "GFML ግሉተን የማይስማማው፣ LFML ዝቅተኛ ስብ፣ LSML ዝቅተኛ ጨው፣ DBML የስኳር በሽተኛ።"),
            ("HNML Hindu, MOML Muslim, KSML kosher, ORML Orthodox fasting.",
             "HNML ሂንዱ፣ MOML ሙስሊም፣ KSML ኮሸር፣ ORML የኦርቶዶክስ ጾም።"),
            ("CHML child, BBML infant, FPML fruit platter.",
             "CHML የሕፃናት፣ BBML የጨቅላ፣ FPML የፍራፍሬ ሳህን።")]])]),

    brief("medical-conditions", "health", 2,
        ("Travelling with a medical condition", "ከሕመም ጋር መጓዝ"),
        ("When we need medical clearance, and what to bring.",
         "የሕክምና ፈቃድ የሚያስፈልገን መቼ እንደሆነ፣ እና ምን ይዘው መምጣት እንዳለብዎት።"),
        [(("Clearance", "ፈቃድ"),
          [("Medical clearance is required within 7 days of surgery, for conditions needing "
            "supplementary oxygen, for a pregnancy beyond 36 weeks, and where a stretcher or "
            "medical escort is needed. Apply at least 72 hours before departure.",
            "የሕክምና ፈቃድ የሚያስፈልገው በቀዶ ጥገና በ7 ቀናት ውስጥ፣ ተጨማሪ ኦክስጅን ለሚያስፈልጋቸው ሁኔታዎች፣ ከ36 ሳምንት በላይ "
            "ለሆነ እርግዝና፣ እና ቃሬዛ ወይም የሕክምና አጃቢ ሲያስፈልግ ነው። ከመነሻው ቢያንስ 72 ሰዓት በፊት ያመልክቱ።"),
           ("Carry prescribed medication in your cabin baggage in its original labelled "
            "packaging, with a doctor's letter for anything injectable.",
            "የታዘዘ መድኃኒትዎን በዋናው በተለጠፈ ማሸጊያው ውስጥ በእጅ ሻንጣዎ ይያዙ፤ ለሚወጋ ማንኛውም ነገር የሐኪም ደብዳቤ ይዘው።")])]),

    brief("assistance-mobility", "health", 3,
        ("Mobility assistance", "የእንቅስቃሴ ድጋፍ"),
        ("Wheelchair codes, and how a request changes your check-in.",
         "የተሽከርካሪ ወንበር ኮዶች፣ እና ጥያቄ ቼክ-ኢንዎን እንዴት እንደሚቀይር።"),
        [(("Codes", "ኮዶች"),
          [("WCHR means assistance to the aircraft door with the passenger able to climb "
            "steps; WCHS means unable to climb steps; WCHC means immobile throughout and "
            "requiring assistance to the seat. Request at least 48 hours ahead.",
            "WCHR ማለት ተሳፋሪው ደረጃ መውጣት ሲችል እስከ አውሮፕላኑ በር ድረስ ድጋፍ ማለት ነው፤ WCHS ደረጃ መውጣት አለመቻል "
            "ማለት ነው፤ WCHC ደግሞ በሙሉ መንቀሳቀስ አለመቻልና እስከ መቀመጫው ድረስ ድጋፍ ማስፈለግ ማለት ነው። ቢያንስ ከ48 ሰዓት "
            "በፊት ይጠይቁ።"),
           ("A booking with assistance recorded cannot be checked in online; a desk agent "
            "must confirm the arrangements in person.",
            "ድጋፍ የተመዘገበበት የቦታ ማስያዣ በመስመር ላይ ቼክ-ኢን ሊደረግ አይችልም፤ የጠረጴዛ ወኪል ዝግጅቱን በአካል ማረጋገጥ "
            "አለበት።")])]),

    brief("miles-earning", "loyalty", 1,
        ("How miles are earned", "ማይሎች እንዴት እንደሚገኙ"),
        ("Earning rates by fare family, and what does not earn.",
         "በታሪፍ ቤተሰብ የማግኛ ተመኖች፣ እና የማያስገኘው።"),
        [(("Rates", "ተመኖች"),
          [("Miles are earned as a percentage of distance flown, set by fare family: Promo "
            "earns nothing, Lite 25%, Basic 50%, Group 75%, Standard 100%, Flex 125%. " +
            BIZ_EN + " earns 150% to 250% depending on family.",
            "ማይሎች በበረረው ርቀት መቶኛ ይገኛሉ፤ በታሪፍ ቤተሰብም ይወሰናሉ፦ ፕሮሞ ምንም አያስገኝም፣ ላይት 25%፣ ቤዚክ 50%፣ "
            "ግሩፕ 75%፣ ስታንዳርድ 100%፣ ፍሌክስ 125%። " + BIZ_AM + " እንደ ቤተሰቡ ከ150% እስከ 250% ያስገኛል።"),
           ("Award tickets, staff tickets and the taxes portion of any fare do not earn "
            "miles. Miles credit within 72 hours of travel; after that, claim them.",
            "የሽልማት ትኬቶች፣ የሠራተኛ ትኬቶችና የማንኛውም ታሪፍ የግብር ክፍል ማይል አያስገኙም። ማይሎች በጉዞ በ72 ሰዓት ውስጥ "
            "ይመዘገባሉ፤ ከዚያ በኋላ ይጠይቋቸው።")])]),

    brief("miles-tiers", "loyalty", 2,
        ("Membership tiers", "የአባልነት ደረጃዎች"),
        ("Thresholds, benefits and how status is retained.",
         "ደፍዎች፣ ጥቅሞችና ደረጃ እንዴት እንደሚቆይ።"),
        [(("Thresholds", "ደፍዎች"),
          [("Blue is the entry tier. Silver requires 25,000 qualifying miles in a membership "
            "year, Gold 50,000, and Platinum 100,000. Qualifying miles are distance-based and "
            "differ from the redeemable miles shown as your balance.",
            "ብሉ የመግቢያ ደረጃ ነው። ሲልቨር በአባልነት ዓመት ውስጥ 25,000 ብቁ ማይሎችን ይጠይቃል፣ ጎልድ 50,000፣ ፕላቲነም ደግሞ "
            "100,000። ብቁ ማይሎች በርቀት ላይ የተመሠረቱ ሲሆኑ እንደ ቀሪ ሒሳብዎ ከሚታዩት ሊቤዡ ከሚችሉ ማይሎች ይለያሉ።"),
           ("Gold and Platinum members and " + BIZ_EN + " passengers have lounge access; "
            "Silver does not.",
            "የጎልድና የፕላቲነም አባላት እንዲሁም የ" + BIZ_AM + " ተሳፋሪዎች የላውንጅ መግቢያ አላቸው፤ ሲልቨር የለውም።")])]),

    brief("miles-expiry", "loyalty", 3,
        ("Mile validity and expiry", "የማይል ጊዜ ገደብና ማብቂያ"),
        ("How long miles last and what keeps an account active.",
         "ማይሎች ምን ያህል እንደሚቆዩና ሒሳብን ንቁ የሚያደርገው።"),
        [(("Validity", "የጊዜ ገደብ"),
          [("Redeemable miles are valid for 36 months from the month they are credited. Any "
            "earning or redemption activity extends the whole balance by a further 36 months. "
            "An account with no activity for 24 months is made dormant and must be "
            "reactivated before miles can be used.",
            "ሊቤዡ የሚችሉ ማይሎች ከተመዘገቡበት ወር ጀምሮ ለ36 ወራት ይሠራሉ። ማንኛውም የማግኘት ወይም የመቤዠት እንቅስቃሴ ጠቅላላውን "
            "ቀሪ ሒሳብ በተጨማሪ 36 ወራት ያራዝማል። ለ24 ወራት እንቅስቃሴ የሌለው ሒሳብ ተኝቶ ይቀመጣል፤ ማይሎች ከመዋላቸው በፊትም "
            "እንደገና መንቃት አለበት።")])]),

    brief("wifi-and-power", "onboard", 2,
        ("Power and connectivity on board", "በበረራ ላይ ኃይልና ግንኙነት"),
        ("Which aircraft have sockets, and how connectivity differs by type.",
         "የትኞቹ አውሮፕላኖች ሶኬት እንዳላቸው፣ እና ግንኙነት በዓይነት እንዴት እንደሚለያይ።"),
        [(("Power", "ኃይል"),
          [("Boeing 787-8 and Airbus A350-900 aircraft have a universal socket at every seat "
            "and USB at every seat. Boeing 737-800 and A320neo have USB only. Dash 8-400 and "
            "Embraer 175 have neither.",
            "የቦይንግ 787-8 እና የኤርባስ A350-900 አውሮፕላኖች በእያንዳንዱ መቀመጫ ሁለንተናዊ ሶኬትና USB አላቸው። ቦይንግ "
            "737-800 እና A320neo USB ብቻ አላቸው። ዳሽ 8-400 እና ኤምብራየር 175 ሁለቱም የላቸውም።"),
           ("Connectivity is available only on Wi-Fi-equipped aircraft. Whether your own "
            "flight is equipped is shown on the flight status page for that flight.",
            "ግንኙነት የሚገኘው ዋይ-ፋይ ባላቸው አውሮፕላኖች ላይ ብቻ ነው። የራስዎ በረራ የተገጠመለት መሆኑ ለዚያ በረራ በበረራ ሁኔታ "
            "ገጽ ላይ ይታያል።")])]),

    brief("entertainment", "onboard", 3,
        ("In-flight entertainment", "በበረራ ላይ መዝናኛ"),
        ("What is available, and on which aircraft.",
         "የሚገኘው ምንድን ነው፣ እና በየትኞቹ አውሮፕላኖች።"),
        [(("Seat-back and streaming", "የመቀመጫ ጀርባና ስርጭት"),
          [("Wide-body aircraft have seat-back screens with roughly 200 films, 60 series and "
            "a music library. Narrow-body aircraft stream the same library to your own device "
            "over the on-board network, which does not require a Wi-Fi package.",
            "ሰፊ አካል ያላቸው አውሮፕላኖች በግምት 200 ፊልሞች፣ 60 ተከታታዮችና የሙዚቃ ቤተ መጻሕፍት ያሉት የመቀመጫ ጀርባ ስክሪን "
            "አላቸው። ጠባብ አካል ያላቸው አውሮፕላኖች ተመሳሳዩን ቤተ መጻሕፍት በበረራ ላይ አውታረ መረብ ወደ የራስዎ መሣሪያ ያሰራጫሉ፤ "
            "ይህም የዋይ-ፋይ ፓኬጅ አይፈልግም።")])]),

    brief("travel-documents", "travel-info", 1,
        ("Passports and travel documents", "ፓስፖርቶችና የጉዞ ሰነዶች"),
        ("Validity rules and the checks we make at the airport.",
         "የጊዜ ገደብ ደንቦችና በአየር ማረፊያ የምናደርጋቸው ፍተሻዎች።"),
        [(("Validity", "የጊዜ ገደብ"),
          [("Most destinations require a passport valid for at least six months beyond your "
            "date of arrival, with at least two blank pages. It is the passenger's "
            "responsibility to hold the correct documents; we are required to refuse carriage "
            "where they are not in order.",
            "አብዛኞቹ መዳረሻዎች ከመድረሻ ቀንዎ ቢያንስ ለስድስት ወራት የሚሠራ ፓስፖርት ይጠይቃሉ፤ ቢያንስ ሁለት ባዶ ገጾችም ሊኖሩት "
            "ይገባል። ትክክለኛ ሰነዶችን መያዝ የተሳፋሪው ኃላፊነት ነው፤ በሥርዓት ካልሆኑም ጉዞን እንድንከለክል እንገደዳለን።")])]),

    brief("visa-transit", "travel-info", 2,
        ("Transit and visas", "መሸጋገሪያና ቪዛዎች"),
        ("When a transit passenger needs a visa, and when they do not.",
         "የመሸጋገሪያ ተሳፋሪ ቪዛ የሚያስፈልገው መቼ እንደሆነ፣ እና የማያስፈልገው መቼ እንደሆነ።"),
        [(("Airside transit", "በአየር ማረፊያ ውስጥ መሸጋገር"),
          [("A passenger connecting within the same terminal on a single booking generally "
            "does not need a transit visa. A visa is needed where the connection requires "
            "leaving the transit area, where baggage must be reclaimed and re-checked, or "
            "where the layover is long enough that you intend to leave the airport.",
            "በአንድ የቦታ ማስያዣ በተመሳሳይ ተርሚናል ውስጥ የሚሸጋገር ተሳፋሪ በአጠቃላይ የመሸጋገሪያ ቪዛ አያስፈልገውም። ቪዛ "
            "የሚያስፈልገው መሸጋገሪያው የመሸጋገሪያ ቀጠናውን መልቀቅ ሲጠይቅ፣ ሻንጣ ተመልሶ ተወስዶ እንደገና መመዝገብ ሲኖርበት፣ ወይም "
            "የማቆያ ጊዜው አየር ማረፊያውን ለመልቀቅ የሚያስብ ያህል ረጅም ሲሆን ነው።")])]),

    page("restricted-items-full", "baggage", 6,
        ("Dangerous goods and restricted items", "አደገኛ ዕቃዎችና የተገደቡ ዕቃዎች"),
        ("The full list, by category, with where each may travel.",
         "በምድብ የተሟላው ዝርዝር፣ እያንዳንዱ የት መጓዝ እንደሚችል።"),
        [(("Batteries and powered devices", "ባትሪዎችና በኃይል የሚሠሩ መሣሪያዎች"),
          [("Spare lithium batteries up to 100 Wh travel in the cabin only, with terminals "
            "taped. Between 100 and 160 Wh you may carry two, with prior approval. Above "
            "160 Wh we cannot carry them at all.",
            "እስከ 100 ዋት-ሰዓት የሆኑ ተጠባባቂ የሊቲየም ባትሪዎች ተርሚናሎቻቸው ተለጥፎ በካቢን ብቻ ይጓዛሉ። ከ100 እስከ 160 "
            "ዋት-ሰዓት ባለው በቅድሚያ ፈቃድ ሁለት መያዝ ይችላሉ። ከ160 ዋት-ሰዓት በላይ በፍጹም ልንወስዳቸው አንችልም።"),
           ("Powered wheelchairs are carried, but the battery type must be declared at least "
            "48 hours ahead so the right handling is arranged.",
            "በኃይል የሚሠሩ የተሽከርካሪ ወንበሮች ይወሰዳሉ፤ ነገር ግን ትክክለኛው አያያዝ እንዲዘጋጅ የባትሪው ዓይነት ቢያንስ ከ48 ሰዓት "
            "በፊት መገለጽ አለበት።")]),
         (("Liquids, aerosols and gels", "ፈሳሾች፣ ኤሮሶሎችና ጄሎች"),
          [("In the cabin: containers of up to 100 ml, in one transparent bag of up to one "
            "litre. In the hold: up to 2 litres of any single item and 2 kg in total, for "
            "toiletries and medicines only.",
            "በካቢን፦ እስከ 100 ሚሊ ሊትር የሆኑ ዕቃዎች፣ እስከ አንድ ሊትር በሚደርስ አንድ ግልጽ ከረጢት ውስጥ። በጭነት ክፍል፦ "
            "ለመታጠቢያ ቁሳቁስና ለመድኃኒት ብቻ የአንድ ዕቃ እስከ 2 ሊትር እና በጠቅላላ 2 ኪግ።")]),
         (("Sharp and pointed articles", "ስለታምና ጫፍ ያላቸው ዕቃዎች"),
          [("Scissors with blades under 6 cm are allowed in the cabin. Anything longer, and "
            "all knives, tools and needles other than medical ones, must be checked.",
            "ከ6 ሴሜ በታች ምላጭ ያላቸው መቀሶች በካቢን ይፈቀዳሉ። ከዚያ የሚረዝም ማንኛውም ነገር፣ እንዲሁም ሁሉም ቢላዎች፣ "
            "መሣሪያዎችና ከሕክምና ውጭ ያሉ መርፌዎች መመዝገብ አለባቸው።")]),
        ]),

    page("musical-instruments", "baggage", 7,
        ("Musical instruments", "የሙዚቃ መሣሪያዎች"),
        ("Which instruments travel in the cabin, which need a seat, and which go in the hold.",
         "የትኞቹ መሣሪያዎች በካቢን እንደሚጓዙ፣ የትኞቹ መቀመጫ እንደሚያስፈልጋቸው፣ የትኞቹም በጭነት ክፍል እንደሚሄዱ።"),
        [(("In the cabin", "በካቢን ውስጥ"),
          [("An instrument within the cabin baggage dimensions -- 55 x 38 x 20 cm -- counts "
            "as your cabin bag. Violins and flutes normally qualify; guitars do not.",
            "በእጅ ሻንጣ መጠን ውስጥ ያለ መሣሪያ -- 55 x 38 x 20 ሴሜ -- እንደ የእጅ ሻንጣዎ ይቆጠራል። ቫዮሊንና ፍሉት "
            "በተለምዶ ብቁ ናቸው፤ ጊታሮች ግን አይደሉም።")]),
         (("On an extra seat", "በተጨማሪ መቀመጫ"),
          [("Instruments up to 80 kg and 165 cm may travel on a seat bought for them, at the "
            "adult fare for the cabin, booked at least 72 hours ahead. The instrument must be "
            "in a hard case and is secured by the crew.",
            "እስከ 80 ኪግ እና 165 ሴሜ የሆኑ መሣሪያዎች ለእነሱ በተገዛ መቀመጫ ላይ በጉዞ ክፍሉ የአዋቂ ታሪፍ ሊጓዙ ይችላሉ፤ "
            "ቢያንስ ከ72 ሰዓት በፊት መያዝ አለበት። መሣሪያው በጠንካራ ሳጥን ውስጥ መሆን አለበት፤ በሠራተኞችም ይታሰራል።")]),
         (("In the hold", "በጭነት ክፍል"),
          [("Larger instruments travel as checked baggage in a hard flight case, at the "
            "special-baggage rate. We do not accept liability for instruments carried in the "
            "hold in a soft case.",
            "ትልልቅ መሣሪያዎች በጠንካራ የበረራ ሳጥን ውስጥ እንደ የተመዘገበ ሻንጣ በልዩ ሻንጣ ተመን ይጓዛሉ። በጭነት ክፍል በለስላሳ "
            "ሳጥን ለሚወሰዱ መሣሪያዎች ኃላፊነት አንወስድም።")]),
        ]),

    page("fitness-to-fly", "health", 4,
        ("Fitness to fly", "ለበረራ ብቁነት"),
        ("When you may travel without clearance, and when you may not travel at all.",
         "ያለ ፈቃድ መጓዝ የሚችሉት መቼ እንደሆነ፣ እና በፍጹም መጓዝ የማይችሉት መቼ እንደሆነ።"),
        [(("Pregnancy", "እርግዝና"),
          [("You may travel without a letter up to the end of the 28th week. From 29 to 36 "
            "weeks bring a letter from a doctor or midwife dated within 10 days of travel. "
            "After 36 weeks -- 32 for a multiple pregnancy -- we cannot carry you.",
            "እስከ 28ኛው ሳምንት መጨረሻ ድረስ ያለ ደብዳቤ መጓዝ ይችላሉ። ከ29 እስከ 36 ሳምንት ከጉዞ በ10 ቀናት ውስጥ የተጻፈ "
            "የሐኪም ወይም የአዋላጅ ደብዳቤ ይዘው ይምጡ። ከ36 ሳምንት በኋላ -- ለብዙ እርግዝና 32 -- ልንወስድዎ አንችልም።")]),
         (("After surgery or illness", "ከቀዶ ጥገና ወይም ከሕመም በኋላ"),
          [("Wait 24 hours after keyhole surgery and 10 days after chest or abdominal surgery. "
            "After a heart attack, wait 7 days if recovery was uncomplicated. Medical "
            "clearance is required inside these periods.",
            "ከቁልፍ ቀዳዳ ቀዶ ጥገና በኋላ 24 ሰዓት፣ ከደረት ወይም ከሆድ ቀዶ ጥገና በኋላ 10 ቀናት ይጠብቁ። ከልብ ድካም በኋላ "
            "ማገገሙ ቀላል ከነበረ 7 ቀናት ይጠብቁ። በእነዚህ ጊዜያት ውስጥ የሕክምና ፈቃድ ያስፈልጋል።")]),
         (("Infants", "ጨቅላዎች"),
          [("Infants may fly from seven days old. Below that we carry them only with a "
            "neonatal letter.",
            "ጨቅላዎች ከሰባት ቀን ዕድሜ ጀምሮ መብረር ይችላሉ። ከዚያ በታች የምንወስዳቸው በኒዮናታል ደብዳቤ ብቻ ነው።")]),
        ]),

    page("unaccompanied-minors", "travel-info", 3,
        ("Children travelling alone", "ብቻቸውን የሚጓዙ ሕፃናት"),
        ("Age bands, the escort service, and what must be arranged before travel.",
         "የዕድሜ ክፍሎች፣ የአጃቢ አገልግሎት፣ እና ከጉዞ በፊት መዘጋጀት ያለበት።"),
        [(("Age bands", "የዕድሜ ክፍሎች"),
          [("Under 5 may not travel alone. From 5 to 11 the escort service is compulsory and "
            "costs USD 60 each way. From 12 to 15 it is optional at the same price. From 16 "
            "the passenger travels as an adult.",
            "ከ5 ዓመት በታች ብቻቸውን መጓዝ አይችሉም። ከ5 እስከ 11 የአጃቢ አገልግሎት የግዴታ ሲሆን በአንድ አቅጣጫ USD 60 "
            "ያስከፍላል። ከ12 እስከ 15 በተመሳሳይ ዋጋ በምርጫ ነው። ከ16 ጀምሮ ተሳፋሪው እንደ አዋቂ ይጓዛል።")]),
         (("Before travel", "ከጉዞ በፊት"),
          [("Book at least 48 hours ahead and name the adult handing over and the adult "
            "collecting, with a telephone number for each. Both must bring photographic "
            "identification. A booking with an unaccompanied minor cannot be checked in online.",
            "ቢያንስ ከ48 ሰዓት በፊት ይያዙ፤ የሚያስረክበውንና የሚቀበለውን አዋቂ ከየስልክ ቁጥራቸው ጋር ይሰይሙ። ሁለቱም ፎቶ ያለው "
            "መታወቂያ ማምጣት አለባቸው። ያለአጃቢ ሕፃን ያለበት የቦታ ማስያዣ በመስመር ላይ ቼክ-ኢን ሊደረግ አይችልም።")]),
        ]),

    page("travelling-with-pets", "travel-info", 4,
        ("Travelling with pets", "ከቤት እንስሳት ጋር መጓዝ"),
        ("Cabin and hold rules, weight limits, and the documents each destination needs.",
         "የካቢንና የጭነት ክፍል ደንቦች፣ የክብደት ገደቦች፣ እና እያንዳንዱ መዳረሻ የሚፈልጋቸው ሰነዶች።"),
        [(("In the cabin", "በካቢን ውስጥ"),
          [("Cats and dogs up to 8 kg including the carrier may travel in the cabin, at USD 90 "
            "per sector. The carrier must fit under the seat in front, and only one animal "
            "per passenger is accepted.",
            "ድመቶችና ውሾች ማጓጓዣውን ጨምሮ እስከ 8 ኪግ በካቢን ውስጥ በአንድ ክፍል USD 90 ሊጓዙ ይችላሉ። ማጓጓዣው በፊት "
            "መቀመጫ ሥር መግባት አለበት፤ በአንድ ተሳፋሪም አንድ እንስሳ ብቻ ይፈቀዳል።")]),
         (("In the hold", "በጭነት ክፍል"),
          [("Above 8 kg the animal travels in the hold in an IATA-compliant crate, at USD 200 "
            "per sector. We do not carry snub-nosed breeds in the hold on any route, because "
            "they cannot regulate their breathing reliably.",
            "ከ8 ኪግ በላይ እንስሳው በIATA መስፈርት በተዘጋጀ ሳጥን በጭነት ክፍል በአንድ ክፍል USD 200 ይጓዛል። አጭር አፍንጫ "
            "ያላቸውን ዝርያዎች በማንኛውም መስመር በጭነት ክፍል አንወስድም፤ ምክንያቱም ትንፋሻቸውን በአስተማማኝ ሁኔታ መቆጣጠር "
            "ስለማይችሉ ነው።")]),
         (("Documents", "ሰነዶች"),
          [("Every destination sets its own import rules. A rabies vaccination certificate and "
            "an export health certificate are the minimum; some destinations add a titre test "
            "with a waiting period of several months. Check before you book.",
            "እያንዳንዱ መዳረሻ የራሱን የማስገቢያ ደንቦች ያወጣል። የእብድ ውሻ በሽታ ክትባት ምስክር ወረቀትና የወጪ ጤና ምስክር "
            "ወረቀት ዝቅተኛው ናቸው፤ አንዳንድ መዳረሻዎች የበርካታ ወራት መጠበቂያ ያለው የቲተር ምርመራ ይጨምራሉ። ከመያዝዎ በፊት "
            "ያረጋግጡ።")]),
        ]),

    page("corporate-programme", "booking-help", 5,
        ("Corporate travel programme", "የድርጅት ጉዞ መርሐ ግብር"),
        ("What the programme offers, and the threshold to join it.",
         "መርሐ ግብሩ የሚያቀርበው፣ እና ለመቀላቀል ያለው ደፍ።"),
        [(("What members get", "አባላት የሚያገኙት"),
          [("Negotiated fares on the routes you fly most, consolidated monthly billing, waived "
            "change fees on Standard and above, and a named account manager.",
            "በብዛት በሚበሩባቸው መስመሮች ላይ የተደራደሩ ታሪፎች፣ የተጠቃለለ ወርሃዊ ክፍያ፣ በስታንዳርድና ከዚያ በላይ የተነሱ የለውጥ "
            "ክፍያዎች፣ እንዲሁም በስም የተመደበ የሒሳብ አስተዳዳሪ።")]),
         (("Joining", "መቀላቀል"),
          [("Programmes start from USD 50,000 of annual travel spend. Below that, book through "
            "the website and earn Selam Miles in the usual way.",
            "መርሐ ግብሮች ከዓመታዊ USD 50,000 የጉዞ ወጪ ይጀምራሉ። ከዚያ በታች በድረ ገጹ ይያዙ፤ ሰላም ማይልስንም በተለመደው "
            "መንገድ ያግኙ።")]),
        ]),
]

PAGES += [page(*entry) for entry in EXTRA]


def main() -> None:
    slugs = [entry["slug"] for entry in PAGES]
    duplicates = sorted({s for s in slugs if slugs.count(s) > 1})
    assert not duplicates, (
        f"two pages share a slug, so one would be unreachable: {duplicates}")

    for index, entry in enumerate(PAGES, start=1):
        entry["id"] = index
    out = ROOT / "spec/seed_data/content_pages.yaml"
    out.write_text(
        "# Generated by tools/make_content.py -- edit there, not here.\n"
        "# CMS rows for every policy and help page (SPEC.md 9.7).\n"
        + yaml.safe_dump({"content_pages": PAGES}, sort_keys=False, allow_unicode=True),
        "utf-8")
    print(f"wrote {out.relative_to(ROOT)} -- {len(PAGES)} pages")
    for entry in PAGES:
        print(f"  {entry['category']:12s} {entry['slug']}")


if __name__ == "__main__":
    main()
