from __future__ import annotations

import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.brand import BRANDS

BIZ_EN, BIZ_AM = BRANDS["cabin_business"]["en"], BRANDS["cabin_business"]["am"]
MILES_EN, MILES_AM = BRANDS["loyalty"]["en"], BRANDS["loyalty"]["am"]
LOUNGE_EN, LOUNGE_AM = BRANDS["lounge_business"]["en"], BRANDS["lounge_business"]["am"]


def _p(slug, category, position, title, summary, sections):
    return (slug, category, position, title, summary, sections)


EXTRA = [

 _p("changing-a-booking", "booking-help", 10,
    ("Changing a booking", "የቦታ ማስያዣን መቀየር"),
    ("What can be changed, what it costs, and what cannot be changed at all.",
     "ሊቀየር የሚችለው፣ የሚያስከፍለው፣ እንዲሁም በፍጹም ሊቀየር የማይችለው።"),
    [(("What a change covers", "ለውጥ የሚሸፍነው"),
      [("A change moves you to a different date, a different flight on the same route, or a "
        "different route. It never changes who is travelling: a new passenger needs a new "
        "booking, whatever the fare.",
        "ለውጥ ወደ ሌላ ቀን፣ በተመሳሳይ መስመር ወደ ሌላ በረራ፣ ወይም ወደ ሌላ መስመር ያዛውርዎታል። የሚጓዘውን ሰው ግን በጭራሽ አይለውጥም፤ "
        "አዲስ ተሳፋሪ ታሪፉ ምንም ይሁን ምን አዲስ የቦታ ማስያዣ ያስፈልገዋል።")]),
     (("What it costs", "የሚያስከፍለው"),
      [("Two amounts are involved and they are separate. The change fee is set by your fare "
        "class and is waived on some fares. The fare difference is the gap between what you "
        "paid and the price of the new flight on the day you change it, and no fare waives it.",
        "ሁለት መጠኖች ይሳተፋሉ፤ እነሱም የተለያዩ ናቸው። የለውጥ ክፍያ በጉዞ ክፍልዎ ይወሰናል፤ በአንዳንድ ታሪፎችም ይነሳል። የታሪፍ ልዩነት ግን "
        "በከፈሉትና በሚቀይሩበት ቀን ባለው የአዲሱ በረራ ዋጋ መካከል ያለው ልዩነት ነው፤ ማንኛውም ታሪፍ ይህን አያነሳም።"),
       ("If the new flight is cheaper, the difference is not refunded. It stays as a credit "
        "against a further change on the same booking.",
        "አዲሱ በረራ ርካሽ ከሆነ ልዩነቱ ተመላሽ አይደረግም። በተመሳሳይ የቦታ ማስያዣ ላይ ለሚደረግ ሌላ ለውጥ እንደ ክሬዲት ይቆያል።")]),
     (("What cannot be changed", "ሊቀየር የማይችለው"),
      [[("A flight that has already departed. Once a segment is flown or missed, the rest of "
         "the booking follows the no-show rules instead.",
         "አስቀድሞ የተነሳ በረራ። አንድ ክፍል ከተበረረ ወይም ካመለጠ በኋላ የቀረው የቦታ ማስያዣ የአለመቅረብ ደንቦችን ይከተላል።"),
        ("An award ticket within 72 hours of departure.",
         "ከመነሻው በ72 ሰዓት ውስጥ ያለ የሽልማት ትኬት።"),
        ("A booking made through a travel agent, which the agent must change.",
         "በጉዞ ወኪል የተያዘ የቦታ ማስያዣ፤ ወኪሉ መቀየር አለበት።")]]),
     ]),

 _p("cancelling-and-refunds", "booking-help", 11,
    ("Cancelling, and what comes back", "መሰረዝና የሚመለሰው"),
    ("Cancelling and refunding are two decisions, not one.",
     "መሰረዝና ተመላሽ ማድረግ ሁለት ውሳኔዎች እንጂ አንድ አይደሉም።"),
    [(("They are not the same thing", "አንድ ዓይነት አይደሉም"),
      [("Cancelling releases your seats. Refunding returns money. Cancelling does not trigger "
        "a refund, and on a non-refundable fare it returns nothing at all -- so cancel only "
        "after you have seen what the refund rules give you.",
        "መሰረዝ መቀመጫዎችዎን ይለቃል። ተመላሽ ማድረግ ገንዘብ ይመልሳል። መሰረዝ ተመላሽ ክፍያን አያስከትልም፤ ተመላሽ በማይደረግ ታሪፍ ላይም "
        "ምንም አይመልስም። ስለዚህ የተመላሽ ክፍያ ደንቦች የሚሰጡዎትን ካዩ በኋላ ብቻ ይሰርዙ።")]),
     (("What each fare returns", "እያንዳንዱ ታሪፍ የሚመልሰው"),
      [[("Flex fares refund in full, less a processing fee.",
         "የፍሌክስ ታሪፎች የማስኬጃ ክፍያ ተቀንሶ ሙሉ በሙሉ ተመላሽ ይደረጋሉ።"),
        ("Standard fares refund a percentage, set by the fare rules on your booking.",
         "የስታንዳርድ ታሪፎች በቦታ ማስያዣዎ ላይ ባሉት የታሪፍ ደንቦች በተወሰነ መቶኛ ተመላሽ ይደረጋሉ።"),
        ("Saver and promotional fares refund the government taxes only. The base fare is not "
         "returned.",
         "የሴቨርና የቅናሽ ታሪፎች የመንግሥት ግብሮችን ብቻ ተመላሽ ያደርጋሉ። መሠረታዊው ታሪፍ አይመለስም።")]]),
     (("How long it takes", "የሚወስደው ጊዜ"),
      [("Approved refunds reach the original payment method in 7 to 21 working days. Bookings "
        "made through an agent are refunded to the agent, not to you.",
        "የተፈቀዱ ተመላሽ ክፍያዎች በ7 እስከ 21 የሥራ ቀናት ውስጥ ወደ መጀመሪያው የክፍያ መንገድ ይደርሳሉ። በወኪል የተያዙ የቦታ ማስያዣዎች "
        "ተመላሽ የሚደረጉት ለወኪሉ እንጂ ለእርስዎ አይደለም።")]),
     ]),

 _p("name-corrections", "booking-help", 12,
    ("Correcting a name", "ስምን ማረም"),
    ("Which spelling mistakes we can fix, and which need a new ticket.",
     "ልናስተካክላቸው የምንችላቸው የፊደል ስህተቶች፣ እና አዲስ ትኬት የሚያስፈልጋቸው።"),
    [(("Corrections we make free of charge", "ያለክፍያ የምናደርጋቸው እርማቶች"),
      [[("Up to three letters in a first or last name, where the name is clearly the same "
         "person -- a transposed pair, a missing letter, an accented character dropped.",
         "በስም ወይም በአያት ስም ውስጥ እስከ ሦስት ፊደላት፣ ስሙ በግልጽ የአንድ ሰው መሆኑ ሲታወቅ -- የተቀያየሩ ጥንድ፣ የጎደለ ፊደል፣ "
         "የወደቀ ምልክት ያለው ፊደል።"),
        ("Reversed first and last name.",
         "የተገላቢጦሽ የስምና የአያት ስም።"),
        ("Adding or removing a middle name to match the passport.",
         "ከፓስፖርቱ ጋር ለማዛመድ የአባት ስም መጨመር ወይም ማንሳት።")]]),
     (("What needs a new booking", "አዲስ የቦታ ማስያዣ የሚያስፈልገው"),
      [("A different person, a legal name change, or a correction of more than three letters. "
        "A ticket is not transferable, so this is a cancellation under your fare rules "
        "followed by a fresh purchase.",
        "ሌላ ሰው፣ ሕጋዊ የስም ለውጥ፣ ወይም ከሦስት ፊደላት በላይ የሆነ እርማት። ትኬት ወደ ሌላ ሰው አይተላለፍም፤ ስለዚህ ይህ በታሪፍ ደንቦችዎ "
        "መሠረት መሰረዝ ከዚያም አዲስ ግዢ ነው።"),
       ("Bring the correction to us before check-in opens. After a boarding pass is issued the "
        "name is fixed and the airport cannot change it.",
        "እርማቱን ቼክ-ኢን ከመከፈቱ በፊት ያምጡልን። የመሳፈሪያ ፈቃድ ከወጣ በኋላ ስሙ ይቆለፋል፤ አየር ማረፊያውም ሊለውጠው አይችልም።")]),
     ]),

 _p("payment-methods", "booking-help", 13,
    ("Ways to pay", "የመክፈያ መንገዶች"),
    ("Cards, bank transfer, vouchers and miles, and when each is available.",
     "ካርዶች፣ የባንክ ዝውውር፣ ቫውቸሮችና ማይሎች፣ እንዲሁም እያንዳንዱ የሚገኝበት ጊዜ።"),
    [(("Accepted methods", "ተቀባይነት ያላቸው መንገዶች"),
      [[("Major credit and debit cards, in USD.",
         "ዋና ዋና የክሬዲትና የዴቢት ካርዶች፣ በUSD።"),
        ("Bank transfer, for bookings made more than 14 days before departure. The booking is "
         "held for 72 hours while the transfer clears.",
         "የባንክ ዝውውር፣ ከመነሻው ከ14 ቀን በላይ አስቀድመው ለሚያዙ ቦታዎች። ዝውውሩ እስኪጠናቀቅ የቦታ ማስያዣው ለ72 ሰዓት ይያዛል።"),
        ("Gift vouchers, in part or in full, against the base fare.",
         "የስጦታ ቫውቸሮች፣ በከፊል ወይም በሙሉ፣ በመሠረታዊ ታሪፉ ላይ።"),
        (MILES_EN + ", for award tickets and for upgrades.",
         MILES_AM + "፣ ለሽልማት ትኬቶችና ለማሻሻያዎች።")]]),
     (("What we do not accept", "የማንቀበለው"),
      [("Cash at the airport for a web booking, cheques, and payment by a third party whose "
        "name is not on the booking. Taxes and carrier charges cannot be paid in vouchers.",
        "በድረ ገጽ ለተያዘ ቦታ በአየር ማረፊያ ጥሬ ገንዘብ፣ ቼኮች፣ እንዲሁም ስሙ በቦታ ማስያዣው ላይ ባልሆነ ሦስተኛ ወገን ክፍያ። ግብሮችና "
        "የአጓጓዥ ክፍያዎች በቫውቸር ሊከፈሉ አይችሉም።")]),
     ]),

 _p("online-checkin-guide", "booking-help", 14,
    ("How online check-in works", "የመስመር ላይ ቼክ-ኢን እንዴት እንደሚሠራ"),
    ("The window, what you need, and the eight reasons it can refuse you.",
     "የሚከፈትበት ጊዜ፣ የሚያስፈልግዎት፣ እንዲሁም ሊከለክልዎት የሚችልባቸው ስምንት ምክንያቶች።"),
    [(("The window", "የሚከፈትበት ጊዜ"),
      [("Check-in opens 48 hours before departure and closes 2 hours before. Outside that "
        "window the page will tell you which of the two applies; it does not queue your "
        "request for later.",
        "ቼክ-ኢን ከመነሻው 48 ሰዓት በፊት ይከፈታል፤ 2 ሰዓት በፊትም ይዘጋል። ከዚያ ጊዜ ውጭ ገጹ ከሁለቱ የትኛው እንደሚሠራ ይነግርዎታል፤ "
        "ጥያቄዎን ለኋላ አያስቀምጥም።")]),
     (("When it will refuse", "የሚከለክልበት ጊዜ"),
      [("Eight conditions stop online check-in, and each shows its own message rather than a "
        "generic failure: too early, closed, an infant on a lap, special assistance booked, an "
        "unaccompanied minor, a document check we must do in person, a flight operated by a "
        "partner airline, and a group booking.",
        "ስምንት ሁኔታዎች የመስመር ላይ ቼክ-ኢንን ያስቆማሉ፤ እያንዳንዱም አጠቃላይ የስህተት መልእክት ሳይሆን የራሱን መልእክት ያሳያል፦ በጣም ገና፣ "
        "ተዘግቷል፣ በጭን ላይ ያለ ጨቅላ፣ የተያዘ ልዩ እገዛ፣ ያለአጃቢ ሕፃን፣ በአካል ልናደርገው የሚገባ የሰነድ ፍተሻ፣ በአጋር አየር መንገድ "
        "የሚከናወን በረራ፣ እንዲሁም የቡድን ቦታ ማስያዣ።"),
       ("In every one of those cases you check in at the airport instead, and the desk closes "
        "at the same time as online check-in.",
        "በእያንዳንዱ በእነዚያ ሁኔታዎች በምትኩ በአየር ማረፊያ ቼክ-ኢን ያደርጋሉ፤ ጠረጴዛውም ከመስመር ላይ ቼክ-ኢን ጋር በተመሳሳይ ሰዓት ይዘጋል።")]),
     ]),

 _p("seat-choice-explained", "booking-help", 15,
    ("What the seat markings mean", "የመቀመጫ ምልክቶች ትርጉም"),
    ("Window, aisle, bulkhead, exit row and bassinet, and who may sit where.",
     "መስኮት፣ መተላለፊያ፣ የፊት ግድግዳ፣ የመውጫ ረድፍና የሕፃን አልጋ፣ እንዲሁም ማን የት መቀመጥ እንደሚችል።"),
    [(("The markings", "ምልክቶቹ"),
      [[("Window: against the cabin wall, with no direct access to the aisle.",
         "መስኮት፦ ከካቢን ግድግዳ ጋር፣ ወደ መተላለፊያ ቀጥታ መድረሻ የለውም።"),
        ("Aisle: beside the aisle, the easiest seat to leave the row from.",
         "መተላለፊያ፦ ከመተላለፊያው አጠገብ፤ ከረድፉ ለመውጣት ቀላሉ መቀመጫ።"),
        ("Bulkhead: the first row of a cabin. More legroom, but nothing in front to store a "
         "bag under, so everything goes in the overhead locker for take-off.",
         "የፊት ግድግዳ፦ የካቢን የመጀመሪያ ረድፍ። ተጨማሪ የእግር ቦታ አለው፤ ግን ከፊት ሻንጣ ማስቀመጫ ስለሌለ ለመነሳት ሁሉም ነገር ወደ "
         "ላይኛው ማስቀመጫ ይሄዳል።"),
        ("Exit row: extra legroom, and a duty to help the crew in an evacuation.",
         "የመውጫ ረድፍ፦ ተጨማሪ የእግር ቦታ፤ እንዲሁም በመልቀቅ ጊዜ ሠራተኞችን የመርዳት ግዴታ።"),
        ("Bassinet: a bassinet can be fitted, so these are held for passengers with an infant.",
         "የሕፃን አልጋ፦ የሕፃን አልጋ ሊገጠም ስለሚችል እነዚህ ጨቅላ ላላቸው ተሳፋሪዎች ይያዛሉ።")]]),
     (("Who may not sit in an exit row", "በመውጫ ረድፍ መቀመጥ የማይችለው"),
      [("Passengers under 15, passengers travelling with an infant, passengers who need an "
        "extension seatbelt, and anyone who would find it hard to operate a heavy door. Cabin "
        "crew reseat anyone who does not qualify, and the seat charge is refunded.",
        "ከ15 ዓመት በታች ያሉ ተሳፋሪዎች፣ ከጨቅላ ጋር የሚጓዙ ተሳፋሪዎች፣ ተጨማሪ የመቀመጫ ቀበቶ የሚያስፈልጋቸው ተሳፋሪዎች፣ እንዲሁም ከባድ በር "
        "ማንቀሳቀስ የሚከብደው ማንኛውም ሰው። የካቢን ሠራተኞች ብቁ ያልሆነውን ማንኛውንም ሰው ያዛውራሉ፤ የመቀመጫው ክፍያም ተመላሽ ይደረጋል።")]),
     ]),

 _p("waitlist-and-standby", "booking-help", 16,
    ("Waitlists and standby", "የመጠባበቂያ ዝርዝርና ተጠባባቂ"),
    ("How a waitlist clears, and how standby differs from it.",
     "የመጠባበቂያ ዝርዝር እንዴት እንደሚጸዳ፣ እንዲሁም ተጠባባቂ ከእሱ በምን እንደሚለይ።"),
    [(("Waitlist", "የመጠባበቂያ ዝርዝር"),
      [("A waitlist holds you for a fare class that is sold out on a flight you have already "
        "booked. It clears in the order requests were received, and it clears automatically -- "
        "you are emailed and the booking updates itself. Waitlists close 24 hours before "
        "departure.",
        "የመጠባበቂያ ዝርዝር አስቀድመው በያዙት በረራ ላይ ለተሸጠ የታሪፍ ክፍል ይይዝዎታል። ጥያቄዎች በደረሱበት ቅደም ተከተል ይጸዳል፤ "
        "በራሱም ይጸዳል -- በኢሜይል ይነገርዎታል፤ የቦታ ማስያዣውም ራሱን ያዘምናል። የመጠባበቂያ ዝርዝሮች ከመነሻው 24 ሰዓት በፊት ይዘጋሉ።")]),
     (("Standby", "ተጠባባቂ"),
      [("Standby moves you to an earlier or later flight on the same day, at the airport, if a "
        "seat is free at the gate. It is not a waitlist and it is not free: same-day standby "
        "carries a flat charge, and it opens 24 hours before departure.",
        "ተጠባባቂ በበሩ ላይ መቀመጫ ካለ በአየር ማረፊያ በተመሳሳይ ቀን ወደ ቀደመ ወይም ወደ ዘገየ በረራ ያዛውርዎታል። የመጠባበቂያ ዝርዝር "
        "አይደለም፤ ነጻም አይደለም፦ የዕለቱ ተጠባባቂ ቋሚ ክፍያ አለው፤ ከመነሻውም 24 ሰዓት በፊት ይከፈታል።")]),
     ]),

 _p("booking-for-someone-else", "booking-help", 17,
    ("Booking for someone else", "ለሌላ ሰው ቦታ መያዝ"),
    ("Whose details go where, and who can then manage the booking.",
     "የማን መረጃ የት እንደሚገባ፣ እና ከዚያ በኋላ የቦታ ማስያዣውን ማን ማስተዳደር እንደሚችል።"),
    [(("Passenger details and contact details are different", "የተሳፋሪ መረጃና የመገናኛ መረጃ የተለያዩ ናቸው"),
      [("Passenger names must match each traveller's passport exactly. The contact email and "
        "telephone can be yours, and that is where every notice about the flight is sent.",
        "የተሳፋሪ ስሞች ከእያንዳንዱ ተጓዥ ፓስፖርት ጋር በትክክል መዛመድ አለባቸው። የመገናኛ ኢሜይልና ስልክ ግን የእርስዎ ሊሆኑ ይችላሉ፤ ስለ "
        "በረራው የሚሰጠው እያንዳንዱ ማሳወቂያም ወደዚያ ይላካል።")]),
     (("Who can manage it afterwards", "ከዚያ በኋላ ማን ማስተዳደር እንደሚችል"),
      [("Anyone holding the booking reference and the lead passenger's surname. There is no "
        "password on a booking, so treat the reference as you would a ticket.",
        "የቦታ ማስያዣ ማጣቀሻውንና የዋናውን ተሳፋሪ የአያት ስም የያዘ ማንኛውም ሰው። በቦታ ማስያዣ ላይ የይለፍ ቃል የለም፤ ስለዚህ ማጣቀሻውን "
        "እንደ ትኬት ይያዙት።")]),
     ]),

 _p("codeshare-explained", "booking-help", 18,
    ("Flights operated by a partner", "በአጋር የሚከናወኑ በረራዎች"),
    ("What changes when the aircraft is not ours.",
     "አውሮፕላኑ የእኛ ካልሆነ የሚለወጠው።"),
    [(("Reading the flight number", "የበረራ ቁጥሩን ማንበብ"),
      [("A flight sold under our number but flown by another airline is marked 'operated by' "
        "on the results page, on your itinerary and on the flight status page. The number you "
        "quote at the airport is the operating airline's, not ours.",
        "በእኛ ቁጥር ተሸጦ በሌላ አየር መንገድ የሚበረር በረራ በውጤቶች ገጽ፣ በጉዞ ዝርዝርዎና በበረራ ሁኔታ ገጽ ላይ ‘የሚከናወነው በ’ ተብሎ "
        "ይመዘገባል። በአየር ማረፊያ የሚጠቅሱት ቁጥር የእኛ ሳይሆን የአስኪያጁ አየር መንገድ ነው።")]),
     (("What follows the operating airline", "የአስኪያጁን አየር መንገድ የሚከተለው"),
      [[("Baggage allowance, cabin service and seat pitch.",
         "የሻንጣ ፈቃድ፣ የካቢን አገልግሎትና የመቀመጫ ርቀት።"),
        ("Online check-in, which must be done on their website, not ours.",
         "የመስመር ላይ ቼክ-ኢን፤ በእነሱ ድረ ገጽ እንጂ በእኛ መደረግ የለበትም።"),
        ("Seat selection, which we cannot make on your behalf.",
         "የመቀመጫ ምርጫ፤ በእርስዎ ወክለን ልናደርገው አንችልም።")]]),
     (("What stays with us", "ከእኛ ጋር የሚቀረው"),
      [("The fare rules, the refund, the change fee, and the miles you earn. Those follow the "
        "ticket, not the aircraft.",
        "የታሪፍ ደንቦች፣ ተመላሽ ክፍያው፣ የለውጥ ክፍያውና የሚያገኙት ማይል። እነዚያ ትኬቱን እንጂ አውሮፕላኑን አይከተሉም።")]),
     ]),

 _p("checked-baggage-basics", "baggage", 10,
    ("Checked baggage, in principle", "የተመዘገበ ሻንጣ፣ በመርህ ደረጃ"),
    ("How allowances are structured. For your own route, use the allowance calculator.",
     "ፈቃዶች እንዴት እንደተዋቀሩ። ለራስዎ መስመር የፈቃድ ማስያ ይጠቀሙ።"),
    [(("Pieces or weight", "ዕቃ ወይም ክብደት"),
      [("Two systems are in use and the route decides which. On a piece system you get a "
        "number of bags, each under a weight cap. On a weight system you get a total, and one "
        "bag may be heavier as long as the total holds. Mixing the two -- three bags on a "
        "weight route, say -- is what most excess charges come from.",
        "ሁለት ሥርዓቶች በሥራ ላይ ናቸው፤ የትኛው እንደሚሠራም መስመሩ ይወስናል። በዕቃ ሥርዓት እያንዳንዳቸው ከክብደት ጣሪያ በታች የሆኑ የተወሰኑ "
        "ሻንጣዎች ያገኛሉ። በክብደት ሥርዓት ጠቅላላ መጠን ያገኛሉ፤ ጠቅላላው እስከጠበቀ ድረስ አንድ ሻንጣ ሊከብድ ይችላል። ሁለቱን መቀላቀል -- "
        "ለምሳሌ በክብደት መስመር ላይ ሦስት ሻንጣ -- አብዛኞቹ የትርፍ ክፍያዎች የሚመጡበት ነው።")]),
     (("What shifts the allowance", "ፈቃዱን የሚያንቀሳቅሰው"),
      [[("Cabin: " + BIZ_EN + " carries more than economy on every route.",
         "የጉዞ ክፍል፦ " + BIZ_AM + " በእያንዳንዱ መስመር ከኢኮኖሚ የበለጠ ይይዛል።"),
        ("Tier: silver and above add a piece or a weight bracket.",
         "ደረጃ፦ ሲልቨርና ከዚያ በላይ አንድ ዕቃ ወይም የክብደት ደረጃ ይጨምራሉ።"),
        ("Passenger type: infants have their own small allowance plus a pushchair.",
         "የተሳፋሪ ዓይነት፦ ጨቅላዎች የራሳቸው አነስተኛ ፈቃድ እንዲሁም የሕፃን ጋሪ አላቸው።")]]),
     (("This page does not give your number", "ይህ ገጽ ቁጥርዎን አይሰጥም"),
      [("Allowances differ by route region, cabin and passenger type, so no figure printed "
        "here would be right for every reader. The allowance calculator asks for those three "
        "and returns the exact allowance for your journey.",
        "ፈቃዶች በመስመር ክልል፣ በጉዞ ክፍልና በተሳፋሪ ዓይነት ይለያያሉ፤ ስለዚህ እዚህ የታተመ ማንኛውም አኀዝ ለእያንዳንዱ አንባቢ ትክክል "
        "አይሆንም። የፈቃድ ማስያው እነዚያን ሦስቱን ጠይቆ ለጉዞዎ ትክክለኛውን ፈቃድ ይመልሳል።")]),
     ]),

 _p("excess-baggage-charges", "baggage", 11,
    ("How excess is charged", "ትርፍ እንዴት እንደሚከፈል"),
    ("The order the charges are applied in, and where each is cheaper.",
     "ክፍያዎቹ የሚተገበሩበት ቅደም ተከተል፣ እና እያንዳንዱ የሚረክስበት ቦታ።"),
    [(("Three separate charges", "ሦስት የተለያዩ ክፍያዎች"),
      [[("Extra weight, charged per kilogram over your allowance.",
         "ተጨማሪ ክብደት፤ ከፈቃድዎ በላይ በኪሎግራም ይከፈላል።"),
        ("An extra piece, charged as a flat fee per bag beyond your piece count.",
         "ተጨማሪ ዕቃ፤ ከዕቃ ብዛትዎ በላይ በአንድ ሻንጣ ቋሚ ክፍያ ይከፈላል።"),
        ("An outsize or special item, charged at its own fixed fee, which replaces the "
         "per-kilogram rate rather than adding to it.",
         "ከመጠን ያለፈ ወይም ልዩ ዕቃ፤ በራሱ ቋሚ ክፍያ ይከፈላል፤ ይህም በኪሎግራም ተመኑ ላይ ከመጨመር ይልቅ ይተካዋል።")]]),
     (("Prepaying is cheaper", "አስቀድሞ መክፈል ይረክሳል"),
      [("Weight bought online before departure costs less per kilogram than weight paid at the "
        "bag drop, and a prepaid bundle costs less per kilogram than buying kilos one at a "
        "time. The airport rate is the highest of the three and is not negotiable.",
        "ከመነሻው በፊት በመስመር ላይ የተገዛ ክብደት በሻንጣ ማስረከቢያ ከሚከፈለው በኪሎግራም ያንሳል፤ አስቀድሞ የተከፈለ ጥቅልም ኪሎዎችን "
        "አንድ በአንድ ከመግዛት በኪሎግራም ያንሳል። የአየር ማረፊያው ተመን ከሦስቱ ከፍተኛው ነው፤ አይደራደርም።")]),
     ]),

 _p("sports-baggage-quick", "baggage", 12,
    ("Sports equipment at a glance", "የስፖርት መሣሪያ በአጭሩ"),
    ("A short summary. The full rules, with packing requirements, are on the special baggage page.",
     "አጭር ማጠቃለያ። ሙሉ ደንቦቹ ከማሸጊያ መስፈርቶች ጋር በልዩ ሻንጣ ገጽ ላይ ናቸው።"),
    [(("The short version", "አጭሩ ቅጂ"),
      [("Most sports equipment travels as one checked piece if it is inside your allowance and "
        "under the item's weight cap. Bulky items -- bicycles, surfboards, kayaks, windsurf "
        "rigs -- carry a fixed fee instead of the per-kilogram rate, and several must be "
        "declared before you travel.",
        "አብዛኛው የስፖርት መሣሪያ በፈቃድዎ ውስጥና ከዕቃው የክብደት ጣሪያ በታች ከሆነ እንደ አንድ የተመዘገበ ዕቃ ይጓዛል። ግዙፍ ዕቃዎች -- "
        "ብስክሌት፣ የሰርፍ ቦርድ፣ ካያክ፣ የንፋስ ሰርፍ መሣሪያ -- በኪሎግራም ተመን ፋንታ ቋሚ ክፍያ አላቸው፤ ብዙዎቹም ከመጓዝዎ በፊት "
        "መገለጽ አለባቸው።")]),
     (("What this page leaves out", "ይህ ገጽ የተወው"),
      [("It does not say how any item must be packed, which fee applies to which item, or "
        "which items we refuse. Those are on the special and sports baggage page, and the "
        "airport goes by that page rather than by this summary.",
        "ማንኛውም ዕቃ እንዴት መታሸግ እንዳለበት፣ የትኛው ክፍያ ለየትኛው ዕቃ እንደሚሠራ፣ ወይም የትኞቹን ዕቃዎች እንደምንከለክል አይናገርም። "
        "እነዚያ በልዩና በስፖርት ሻንጣ ገጽ ላይ ናቸው፤ አየር ማረፊያውም በዚህ ማጠቃለያ ሳይሆን በዚያ ገጽ ይሄዳል።")]),
     ]),

 _p("delayed-baggage", "baggage", 13,
    ("If your bag does not arrive", "ሻንጣዎ ካልደረሰ"),
    ("What to do at the airport, and what we pay while a bag is missing.",
     "በአየር ማረፊያ ምን ማድረግ እንዳለብዎ፣ እና ሻንጣ በጠፋበት ጊዜ የምንከፍለው።"),
    [(("Report it before you leave the airport", "አየር ማረፊያውን ከመልቀቅዎ በፊት ያሳውቁ"),
      [("Go to the baggage desk in the arrivals hall and open a report. You are given a "
        "reference in the form PIR-100001. Reports opened after you leave the airport are "
        "accepted for 7 days but are harder to trace, because the bag has left our custody "
        "chain.",
        "በመድረሻ አዳራሽ ወዳለው የሻንጣ ጠረጴዛ ሄደው ሪፖርት ይክፈቱ። በPIR-100001 ቅርጽ ያለ ማጣቀሻ ይሰጥዎታል። አየር ማረፊያውን ከለቀቁ በኋላ "
        "የተከፈቱ ሪፖርቶች ለ7 ቀናት ተቀባይነት አላቸው፤ ነገር ግን ሻንጣው ከቁጥጥር ሰንሰለታችን ስለወጣ ለመከታተል ይከብዳሉ።")]),
     (("While it is missing", "በጠፋበት ጊዜ"),
      [("Away from home we reimburse essentials -- toiletries and a change of clothes -- up to "
        "USD 100 for the first 48 hours, against receipts. Most bags are located within three "
        "days. After 21 days a bag is declared lost and the claim moves to compensation.",
        "ከቤት ርቀው ሲሆኑ አስፈላጊ ነገሮችን -- የመታጠቢያ ቁሳቁስና የመቀየሪያ ልብስ -- ለመጀመሪያዎቹ 48 ሰዓታት እስከ USD 100 "
        "በደረሰኝ እንመልሳለን። አብዛኞቹ ሻንጣዎች በሦስት ቀናት ውስጥ ይገኛሉ። ከ21 ቀናት በኋላ ሻንጣ እንደጠፋ ተቆጥሮ ጥያቄው ወደ ካሳ ይሸጋገራል።")]),
     ]),

 _p("damaged-baggage", "baggage", 14,
    ("Damaged bags", "የተጎዱ ሻንጣዎች"),
    ("The deadline, and the damage we do not cover.",
     "የጊዜ ገደቡ፣ እና የማንሸፍነው ጉዳት።"),
    [(("Seven days", "ሰባት ቀናት"),
      [("Report damage within 7 days of arrival, with the bag, the tag and the boarding pass. "
        "We repair where a repair is possible and pay the depreciated value where it is not. "
        "After 7 days we cannot accept the claim; this deadline is set by the carriage "
        "convention, not by us.",
        "ጉዳቱን ከደረሱ በ7 ቀናት ውስጥ ከሻንጣው፣ ከመለያውና ከመሳፈሪያ ፈቃዱ ጋር ያሳውቁ። ጥገና በሚቻልበት እንጠግናለን፤ በማይቻልበትም "
        "የቀነሰውን ዋጋ እንከፍላለን። ከ7 ቀናት በኋላ ጥያቄውን ልንቀበል አንችልም፤ ይህ የጊዜ ገደብ በእኛ ሳይሆን በማጓጓዝ ስምምነቱ የተቀመጠ ነው።")]),
     (("Not covered", "የማይሸፈን"),
      [("Scuffs, scratches, dents and marks from ordinary handling; wheels, feet, handles and "
        "straps, which are wear items; overpacking that split a seam; and anything inside a "
        "bag that should not have been checked -- money, jewellery, electronics, documents, "
        "medication.",
        "ከተለመደ አያያዝ የሚመጡ ጭረቶች፣ ስንጥቆች፣ ሽንቁሮችና ምልክቶች፤ የሚያልቁ ዕቃዎች የሆኑ ጎማዎች፣ እግሮች፣ እጀታዎችና ማሰሪያዎች፤ "
        "ስፌት ያሰነጠቀ ከመጠን በላይ ማሸግ፤ እንዲሁም መመዝገብ የሌለበት በሻንጣ ውስጥ ያለ ማንኛውም ነገር -- ገንዘብ፣ ጌጣጌጥ፣ "
        "ኤሌክትሮኒክስ፣ ሰነዶች፣ መድኃኒት።")]),
     ]),

 _p("baggage-on-connections", "baggage", 15,
    ("Bags on a connection", "በመሸጋገሪያ ላይ ያሉ ሻንጣዎች"),
    ("When a bag is through-checked, and when you must collect it.",
     "ሻንጣ መቼ እስከመጨረሻው እንደሚመዘገብ፣ እና መቼ መውሰድ እንዳለብዎ።"),
    [(("Through-checked", "እስከመጨረሻው የተመዘገበ"),
      [("On a single booking your bag is tagged to your final destination and you do not see "
        "it in between, whichever airlines operate the legs.",
        "በአንድ የቦታ ማስያዣ ላይ ሻንጣዎ እስከ መጨረሻ መድረሻዎ ይመዘገባል፤ ክፍሎቹን የትኛውም አየር መንገድ ቢያከናውን በመሃል አያዩትም።")]),
     (("When you must collect and recheck", "መውሰድና እንደገና መመዝገብ ያለብዎት ጊዜ"),
      [[("Two separate bookings, even on the same airline and the same day.",
         "ሁለት የተለያዩ የቦታ ማስያዣዎች፤ በተመሳሳይ አየር መንገድና በተመሳሳይ ቀን ቢሆኑም እንኳ።"),
        ("A country that requires every arriving bag to clear customs, whatever your onward "
         "plan.",
         "ቀጣይ ዕቅድዎ ምንም ይሁን ምን የሚደርስ እያንዳንዱ ሻንጣ ጉምሩክ እንዲያልፍ የምትጠይቅ አገር።"),
        ("A change of terminal where the two are not connected airside.",
         "ሁለቱ ከደህንነት ፍተሻ በኋላ ባልተገናኙበት የተርሚናል ለውጥ።")]]),
     (("Minimum connection time", "አነስተኛ የመሸጋገሪያ ጊዜ"),
      [("We do not sell a connection shorter than the minimum for that airport, so a legal "
        "connection is long enough for the bag as well. If the first flight is late and the "
        "bag misses the second, it follows on the next service and we deliver it.",
        "ለዚያ አየር ማረፊያ ካለው አነስተኛ ጊዜ የሚያጥር መሸጋገሪያ አንሸጥም፤ ስለዚህ ሕጋዊ መሸጋገሪያ ለሻንጣውም በቂ ነው። የመጀመሪያው በረራ "
        "ከዘገየና ሻንጣው ሁለተኛውን ካመለጠ በሚቀጥለው በረራ ይከተላል፤ እኛም እናደርስልዎታለን።")]),
     ]),

 _p("valuables-and-fragile", "baggage", 16,
    ("Valuables and fragile items", "ውድና ተሰባሪ ዕቃዎች"),
    ("What must stay with you, and the limit of our liability.",
     "ከእርስዎ ጋር መቆየት ያለበት፣ እና የኃላፊነታችን ገደብ።"),
    [(("Carry these yourself", "እነዚህን እርስዎ ይያዙ"),
      [("Money, jewellery, precious metals, electronics, cameras, keys, passports and other "
        "documents, prescription medication, and anything irreplaceable. We accept no "
        "liability for these in checked baggage, whether the bag is lost, delayed or damaged.",
        "ገንዘብ፣ ጌጣጌጥ፣ የከበሩ ማዕድናት፣ ኤሌክትሮኒክስ፣ ካሜራዎች፣ ቁልፎች፣ ፓስፖርቶችና ሌሎች ሰነዶች፣ በሐኪም የታዘዘ መድኃኒት፣ "
        "እንዲሁም የማይተካ ማንኛውም ነገር። እነዚህ በተመዘገበ ሻንጣ ውስጥ ሲሆኑ ሻንጣው ይጥፋ፣ ይዘግይ ወይም ይጎዳ ምንም ኃላፊነት አንወስድም።")]),
     (("Fragile items in the hold", "በጭነት ክፍል ውስጥ ያሉ ተሰባሪ ዕቃዎች"),
      [("A fragile item may be checked if it is packed for transport in a rigid case. It is "
        "tagged 'limited release', which means we carry it but do not cover damage to it. A "
        "fragile tag is not insurance.",
        "ተሰባሪ ዕቃ በጠንካራ ሳጥን ውስጥ ለማጓጓዝ ታሽጎ ከሆነ ሊመዘገብ ይችላል። ‘ውስን ኃላፊነት’ ተብሎ ይመዘገባል፤ ትርጉሙም እናጓጉዘዋለን "
        "እንጂ ጉዳቱን አንሸፍንም ማለት ነው። የተሰባሪ መለያ ዋስትና አይደለም።")]),
     ]),

 _p("connecting-at-addis", "travel-info", 10,
    ("Connecting at Addis Ababa", "በአዲስ አበባ መሸጋገር"),
    ("Minimum times, terminal moves, and what a long layover unlocks.",
     "አነስተኛ ጊዜያት፣ የተርሚናል ዝውውሮች፣ እና ረጅም ማቆያ የሚከፍተው።"),
    [(("Minimum connection time", "አነስተኛ የመሸጋገሪያ ጊዜ"),
      [("60 minutes between two international flights, 90 minutes when one leg is domestic, "
        "and 120 minutes when the terminal changes. We do not sell a shorter connection, so "
        "anything you can book is long enough.",
        "በሁለት ዓለም አቀፍ በረራዎች መካከል 60 ደቂቃ፣ አንዱ ክፍል የአገር ውስጥ ሲሆን 90 ደቂቃ፣ ተርሚናል ሲቀየር ደግሞ 120 ደቂቃ። "
        "ከዚያ የሚያጥር መሸጋገሪያ አንሸጥም፤ ስለዚህ ሊይዙት የሚችሉት ማንኛውም ነገር በቂ ነው።")]),
     (("Long layovers", "ረጅም ማቆያዎች"),
      [("Between 8 and 72 hours on a single booking, a connection becomes a stopover: hotel, "
        "airport transfer, lounge and city tour options open up. Below 8 hours it is an "
        "ordinary connection and none of those apply.",
        "በአንድ የቦታ ማስያዣ ላይ ከ8 እስከ 72 ሰዓት ሲሆን መሸጋገሪያ ወደ ማቆያ ይለወጣል፦ የሆቴል፣ የአየር ማረፊያ ትራንስፖርት፣ የላውንጅና "
        "የከተማ ጉብኝት አማራጮች ይከፈታሉ። ከ8 ሰዓት በታች ተራ መሸጋገሪያ ነው፤ ከእነዚያም አንዱም አይሠራም።")]),
     (("Staying airside", "ከደህንነት ፍተሻ በኋላ መቆየት"),
      [("If you do not leave the transit area you need no visa. The in-terminal hotel, the "
        "lounges and the prayer rooms are all airside. Leaving the airport means clearing "
        "immigration, and that needs a visa or an e-Visa.",
        "የመሸጋገሪያ ቀጠናውን ካልለቀቁ ቪዛ አያስፈልግዎትም። በተርሚናል ውስጥ ያለው ሆቴል፣ ላውንጆቹና የጸሎት ክፍሎቹ ሁሉም ከደህንነት ፍተሻ "
        "በኋላ ናቸው። አየር ማረፊያውን መልቀቅ ማለት ኢሚግሬሽን ማለፍ ማለት ነው፤ ያም ቪዛ ወይም ኢ-ቪዛ ይፈልጋል።")]),
     ]),

 _p("security-screening", "travel-info", 11,
    ("Security screening", "የደህንነት ፍተሻ"),
    ("What comes out of the bag, and the liquid rule.",
     "ከሻንጣው የሚወጣው፣ እና የፈሳሽ ደንቡ።"),
    [(("The liquid rule", "የፈሳሽ ደንብ"),
      [("Containers of up to 100 ml, all together in one transparent resealable bag of up to "
        "one litre, one bag per passenger. A 200 ml bottle that is half empty is still refused: "
        "the rule is the container size, not the amount inside it.",
        "እስከ 100 ሚሊ ሊትር የሆኑ ዕቃዎች፣ ሁሉም በአንድነት እስከ አንድ ሊትር በሚይዝ አንድ ግልጽና እንደገና በሚዘጋ ከረጢት ውስጥ፣ በአንድ "
        "ተሳፋሪ አንድ ከረጢት። ግማሽ ባዶ የሆነ የ200 ሚሊ ሊትር ጠርሙስ አሁንም አይፈቀድም፦ ደንቡ በውስጡ ያለው መጠን ሳይሆን የዕቃው መጠን ነው።")]),
     (("Exempt from the bag", "ከከረጢቱ የተለዩ"),
      [("Baby food and milk for a travelling infant, and prescription medication, in the "
        "quantity needed for the journey. Declare both at the checkpoint. Screening staff may "
        "ask you to open them.",
        "ለሚጓዝ ጨቅላ የሚሆን የሕፃን ምግብና ወተት፣ እንዲሁም በሐኪም የታዘዘ መድኃኒት፣ ለጉዞው በሚያስፈልገው መጠን። ሁለቱንም በፍተሻ ቦታው "
        "ላይ ያሳውቁ። የፍተሻ ሠራተኞች እንዲከፍቷቸው ሊጠይቁዎት ይችላሉ።")]),
     (("Out of the bag", "ከሻንጣው የሚወጣ"),
      [("Laptops and tablets, the liquids bag, and coats. Shoes and belts only if asked. Duty "
        "free bought before a connection stays sealed in its tamper-evident bag with the "
        "receipt visible, or it will be taken at the next checkpoint.",
        "ላፕቶፖችና ታብሌቶች፣ የፈሳሽ ከረጢቱ፣ እንዲሁም ኮቶች። ጫማና ቀበቶ የሚጠየቁት ሲጠየቁ ብቻ ነው። ከመሸጋገሪያ በፊት የተገዛ ከቀረጥ "
        "ነጻ ዕቃ ደረሰኙ እየታየ በማይከፈት ከረጢቱ ውስጥ ታሽጎ መቆየት አለበት፤ አለበለዚያ በሚቀጥለው የፍተሻ ቦታ ይወሰዳል።")]),
     ]),

 _p("customs-and-duty-free", "travel-info", 12,
    ("Customs and duty free", "ጉምሩክና ከቀረጥ ነጻ"),
    ("Allowances on arrival, and what must be declared.",
     "በመድረስ ጊዜ ያሉ ፈቃዶች፣ እና መገለጽ ያለበት።"),
    [(("Declare on arrival", "በመድረስ ጊዜ ያሳውቁ"),
      [("Currency above the local threshold, goods for sale, plant and animal products, and "
        "anything you were asked to carry for another person. Declaring costs nothing; failing "
        "to declare is what carries a penalty.",
        "ከአገር ውስጥ ገደብ በላይ ያለ ገንዘብ፣ ለሽያጭ የሚሆኑ ዕቃዎች፣ የእጽዋትና የእንስሳት ተዋጽኦዎች፣ እንዲሁም ለሌላ ሰው እንዲይዙ "
        "የተጠየቁት ማንኛውም ነገር። ማሳወቅ ምንም አያስከፍልም፤ ቅጣት የሚያስከትለው አለማሳወቅ ነው።")]),
     (("Duty free on a connection", "በመሸጋገሪያ ላይ ከቀረጥ ነጻ"),
      [("Liquids bought airside travel in a sealed tamper-evident bag with the receipt inside. "
        "The seal must be intact at the next screening point. If your onward journey passes "
        "through a country that re-screens, buy on the last leg instead.",
        "ከደህንነት ፍተሻ በኋላ የተገዙ ፈሳሾች ደረሰኙ ውስጡ ሆኖ በማይከፈት ማሸጊያ ከረጢት ውስጥ ይጓዛሉ። ማኅተሙ በሚቀጥለው የፍተሻ ቦታ "
        "ሳይነካ መቆየት አለበት። ቀጣይ ጉዞዎ እንደገና በሚፈትሽ አገር የሚያልፍ ከሆነ በምትኩ በመጨረሻው ክፍል ላይ ይግዙ።")]),
     ]),

 _p("weather-and-disruption", "travel-info", 13,
    ("Weather and disruption", "የአየር ሁኔታና መስተጓጎል"),
    ("What we owe you when a flight is disrupted, and what we do not.",
     "በረራ ሲስተጓጎል የምንዳዎት፣ እና የማንዳዎት።"),
    [(("Within our control", "በእኛ ቁጥጥር ውስጥ"),
      [("A technical fault, crew shortage or scheduling decision. We rebook you at no charge on "
        "the next available service, provide meals for a delay over 2 hours, and a hotel with "
        "transfers when an overnight stay is unavoidable.",
        "የቴክኒክ ብልሽት፣ የሠራተኛ እጥረት ወይም የመርሐ ግብር ውሳኔ። ያለክፍያ በሚቀጥለው በሚገኝ በረራ እንደግምዎታለን፤ ከ2 ሰዓት በላይ "
        "ለሚዘገይ ምግብ እናቀርባለን፤ ማደር የግድ ሲሆንም ከትራንስፖርት ጋር ሆቴል እናዘጋጃለን።")]),
     (("Outside our control", "ከእኛ ቁጥጥር ውጭ"),
      [("Weather, volcanic ash, air traffic restrictions, airport closure, strike action by "
        "third parties, and security instructions from an authority. We still rebook you at no "
        "charge, and a refund remains available if you no longer wish to travel, but meals and "
        "accommodation are not provided.",
        "የአየር ሁኔታ፣ የእሳተ ገሞራ አመድ፣ የአየር ትራፊክ ገደቦች፣ የአየር ማረፊያ መዘጋት፣ በሦስተኛ ወገኖች የሚደረግ የሥራ ማቆም አድማ፣ "
        "እንዲሁም ከባለሥልጣን የሚሰጡ የደህንነት መመሪያዎች። አሁንም ያለክፍያ እንደግምዎታለን፤ መጓዝ ካልፈለጉም ተመላሽ ክፍያ ይገኛል፤ "
        "ነገር ግን ምግብና ማረፊያ አይቀርብም።")]),
     (("Either way", "በሁለቱም ሁኔታ"),
      [("Your checked bags travel on whichever flight you end up on, and a connection missed "
        "because of our delay is rebooked without a change fee.",
        "የተመዘገቡ ሻንጣዎችዎ በመጨረሻ በሚሳፈሩበት በረራ ይጓዛሉ፤ በእኛ መዘግየት ምክንያት ያመለጠ መሸጋገሪያም ያለ የለውጥ ክፍያ ይደገማል።")]),
     ]),

 _p("airport-arrival-times", "travel-info", 14,
    ("When to arrive at the airport", "ወደ አየር ማረፊያ መቼ መድረስ እንዳለብዎ"),
    ("Recommended times, and the three deadlines that actually bind.",
     "የሚመከሩ ጊዜያት፣ እና በእውነት የሚያስገድዱት ሦስት የጊዜ ገደቦች።"),
    [(("Recommended", "የሚመከር"),
      [("Two hours before a domestic departure and three hours before an international one. "
        "Add an hour if you are checking sports equipment, travelling with an unaccompanied "
        "minor, or need a document check.",
        "ከአገር ውስጥ መነሻ ሁለት ሰዓት በፊት፤ ከዓለም አቀፍ ደግሞ ሦስት ሰዓት በፊት። የስፖርት መሣሪያ የሚመዘግቡ ከሆነ፣ ከያለአጃቢ ሕፃን "
        "ጋር የሚጓዙ ከሆነ፣ ወይም የሰነድ ፍተሻ የሚያስፈልግዎት ከሆነ አንድ ሰዓት ይጨምሩ።")]),
     (("The deadlines", "የጊዜ ገደቦቹ"),
      [[("Check-in closes 2 hours before departure, online and at the desk alike.",
         "ቼክ-ኢን ከመነሻው 2 ሰዓት በፊት ይዘጋል፤ በመስመር ላይም ሆነ በጠረጴዛው።"),
        ("Bag drop closes 60 minutes before departure.",
         "የሻንጣ ማስረከቢያ ከመነሻው 60 ደቂቃ በፊት ይዘጋል።"),
        ("The gate closes 20 minutes before departure, and a boarding pass does not hold it "
         "open.",
         "በሩ ከመነሻው 20 ደቂቃ በፊት ይዘጋል፤ የመሳፈሪያ ፈቃድም ክፍት አያደርገውም።")]]),
     ]),

 _p("vaccinations", "health", 10,
    ("Vaccinations and health certificates", "ክትባቶችና የጤና ምስክር ወረቀቶች"),
    ("Which certificates are checked, and who decides.",
     "የትኞቹ ምስክር ወረቀቶች እንደሚፈተሹ፣ እና ማን እንደሚወስን።"),
    [(("Yellow fever", "ቢጫ ወባ"),
      [("A yellow fever certificate is required by many countries when you arrive from, or "
        "have transited, a country where the disease is present. It becomes valid 10 days "
        "after vaccination, so a certificate dated within 10 days of arrival is refused.",
        "በሽታው ካለበት አገር ሲመጡ ወይም በእሱ ሲሸጋገሩ ብዙ አገሮች የቢጫ ወባ ምስክር ወረቀት ይጠይቃሉ። ከክትባቱ 10 ቀናት በኋላ ሥራ ላይ "
        "ይውላል፤ ስለዚህ ከመድረሻ በ10 ቀናት ውስጥ የተጻፈ ምስክር ወረቀት አይቀበልም።")]),
     (("Who decides", "ማን እንደሚወስን"),
      [("The destination government, not us. We check that you hold what your destination "
        "requires, and we are obliged to refuse carriage if you do not -- but the requirement "
        "itself is theirs, and it changes. Confirm with the embassy before you travel.",
        "የመድረሻው መንግሥት እንጂ እኛ አይደለንም። መድረሻዎ የሚጠይቀውን መያዝዎን እናረጋግጣለን፤ ካልያዙም ማጓጓዝን የመከልከል ግዴታ አለብን። "
        "መስፈርቱ ራሱ ግን የእነሱ ነው፤ እንዲሁም ይለወጣል። ከመጓዝዎ በፊት ከኤምባሲው ያረጋግጡ።")]),
     ]),

 _p("cabin-comfort-health", "health", 11,
    ("Staying comfortable on a long flight", "በረጅም በረራ ላይ ምቾትን መጠበቅ"),
    ("Cabin altitude, dehydration and circulation.",
     "የካቢን ከፍታ፣ የውሃ እጥረትና የደም ዝውውር።"),
    [(("Why the cabin feels dry", "ካቢኑ ደረቅ የሚመስለው ለምንድን ነው"),
      [("Cabin air is pressurised to about 2,400 metres and its humidity sits near 15 per "
        "cent, well below a room on the ground. That is why skin, eyes and throat feel dry and "
        "why alcohol has a stronger effect than it does on the ground.",
        "የካቢን አየር ወደ 2,400 ሜትር ገደማ ግፊት ይደረግበታል፤ እርጥበቱም ከመሬት ላይ ካለ ክፍል በጣም ያነሰ ወደ 15 በመቶ ገደማ ነው። "
        "ቆዳ፣ ዓይንና ጉሮሮ ደረቅ የሚሰማቸው፣ አልኮልም ከመሬት ላይ በበለጠ የሚሠራው ለዚህ ነው።")]),
     (("Circulation", "የደም ዝውውር"),
      [("Sitting still for hours slows blood flow in the legs. Walk the cabin roughly every "
        "two hours when the seatbelt sign is off, flex your ankles in the seat, and keep "
        "drinking water. If you have had recent surgery, a clotting disorder or a previous "
        "thrombosis, ask your doctor about compression stockings before you fly.",
        "ለሰዓታት ሳይንቀሳቀሱ መቀመጥ በእግሮች ውስጥ ያለውን የደም ፍሰት ያዘገየዋል። የመቀመጫ ቀበቶ ምልክቱ ሲጠፋ በየሁለት ሰዓቱ ገደማ "
        "በካቢኑ ውስጥ ይራመዱ፤ በመቀመጫዎ ላይ ሆነው ቁርጭምጭሚትዎን ያንቀሳቅሱ፤ ውሃም መጠጣትዎን ይቀጥሉ። በቅርቡ ቀዶ ጥገና ካደረጉ፣ "
        "የደም መርጋት ችግር ካለብዎ ወይም ቀደም ሲል የደም መርጋት ካጋጠምዎ ከመብረርዎ በፊት ስለ መጭመቂያ ካልሲዎች ሐኪምዎን ይጠይቁ።")]),
     ]),

 _p("travelling-with-medication", "health", 12,
    ("Travelling with medication", "ከመድኃኒት ጋር መጓዝ"),
    ("Where it goes, and the letter that prevents a problem.",
     "የት እንደሚቀመጥ፣ እና ችግርን የሚከላከለው ደብዳቤ።"),
    [(("Keep it in the cabin", "በካቢን ውስጥ ይያዙት"),
      [("Prescription medication travels in your cabin bag, in its original labelled "
        "packaging, in the quantity needed for the journey plus a few days. Hold baggage can "
        "be delayed, and the hold is cold.",
        "በሐኪም የታዘዘ መድኃኒት በእጅ ሻንጣዎ ውስጥ፣ በመጀመሪያው መለያ ባለው ማሸጊያው፣ ለጉዞው በሚያስፈልገው መጠን ላይ የጥቂት ቀናት "
        "ተጨምሮ ይጓዛል። የተመዘገበ ሻንጣ ሊዘገይ ይችላል፤ የጭነት ክፍሉም ቀዝቃዛ ነው።")]),
     (("The letter", "ደብዳቤው"),
      [("Carry a doctor's letter naming the medication and the condition if you travel with "
        "injectables, controlled drugs, liquids above 100 ml, or a device such as a syringe "
        "driver. Some destinations restrict medicines that are ordinary elsewhere; check with "
        "the embassy rather than assuming.",
        "የመርፌ መድኃኒት፣ ቁጥጥር የሚደረግባቸው መድኃኒቶች፣ ከ100 ሚሊ ሊትር በላይ ፈሳሾች፣ ወይም እንደ የመርፌ መሣሪያ ያለ መሣሪያ ይዘው "
        "የሚጓዙ ከሆነ መድኃኒቱንና ሕመሙን የሚጠቅስ የሐኪም ደብዳቤ ይያዙ። አንዳንድ መድረሻዎች በሌላ ቦታ የተለመዱ መድኃኒቶችን "
        "ይገድባሉ፤ ከመገመት ይልቅ ከኤምባሲው ያረጋግጡ።")]),
     ]),

 _p("onboard-comfort", "onboard", 10,
    ("What is at your seat", "በመቀመጫዎ ላይ ያለው"),
    ("Power, screens and amenities, and which aircraft have them.",
     "ኃይል፣ ማሳያዎችና አገልግሎቶች፣ እንዲሁም የትኞቹ አውሮፕላኖች እንዳሏቸው።"),
    [(("Power", "ኃይል"),
      [("Wide-body aircraft have a universal socket and a USB port at every seat. Narrow-body "
        "aircraft have USB only. Turboprops have neither, so charge before you board.",
        "ሰፊ አካል አውሮፕላኖች በእያንዳንዱ መቀመጫ ሁለንተናዊ ሶኬትና የUSB መሰኪያ አላቸው። ጠባብ አካል አውሮፕላኖች USB ብቻ አላቸው። "
        "ተርቦፕሮፖች ደግሞ አንዱም የላቸውም፤ ስለዚህ ከመሳፈርዎ በፊት ኃይል ይሙሉ።")]),
     (("Amenities", "አገልግሎቶች"),
      [(BIZ_EN + " on flights over six hours carries a flat bed, a duvet and an amenity kit. "
        "Economy on the same flights carries a blanket, a pillow and an eye mask on request.",
        BIZ_AM + " ከስድስት ሰዓት በላይ በሚደረጉ በረራዎች ላይ ጠፍጣፋ አልጋ፣ ብርድ ልብስና የአገልግሎት ስብስብ ይይዛል። በተመሳሳይ "
        "በረራዎች ላይ ኢኮኖሚ በጥያቄ ብርድ ልብስ፣ ትራስና የዓይን መሸፈኛ ይይዛል።")]),
     ]),

 _p("alcohol-and-water", "onboard", 11,
    ("Drinks on board", "በበረራ ላይ መጠጦች"),
    ("What is complimentary, and the limits on alcohol.",
     "በነጻ የሚቀርበው፣ እና በአልኮል ላይ ያሉ ገደቦች።"),
    [(("Complimentary", "በነጻ የሚቀርብ"),
      [("Water, tea, coffee and soft drinks on every flight. Beer and wine with a meal on "
        "flights over three hours. A full bar in " + BIZ_EN + ".",
        "በእያንዳንዱ በረራ ውሃ፣ ሻይ፣ ቡናና ለስላሳ መጠጦች። ከሦስት ሰዓት በላይ በሚደረጉ በረራዎች ከምግብ ጋር ቢራና ወይን። "
        "በ" + BIZ_AM + " ደግሞ ሙሉ መጠጥ ቤት።")]),
     (("Limits", "ገደቦች"),
      [("Cabin crew serve alcohol at their discretion and will stop serving a passenger who "
        "has had enough. You may not drink your own alcohol on board, including duty free. "
        "Both rules are safety requirements, not house policy.",
        "የካቢን ሠራተኞች አልኮል የሚያቀርቡት በራሳቸው ውሳኔ ነው፤ በቂ ለጠጣ ተሳፋሪም ማቅረብ ያቆማሉ። ከቀረጥ ነጻ የተገዛውን ጨምሮ "
        "የራስዎን አልኮል በበረራ ላይ መጠጣት አይችሉም። ሁለቱም ደንቦች የቤት ውስጥ ፖሊሲ ሳይሆኑ የደህንነት መስፈርቶች ናቸው።")]),
     ]),

 _p("smoking-and-devices", "onboard", 12,
    ("Smoking and electronic devices", "ማጨስና የኤሌክትሮኒክ መሣሪያዎች"),
    ("What is prohibited outright, and what flight mode covers.",
     "በፍጹም የተከለከለው፣ እና የበረራ ሁኔታ የሚሸፍነው።"),
    [(("Smoking", "ማጨስ"),
      [("Smoking is prohibited on every flight, in every cabin, including electronic "
        "cigarettes and heated tobacco. Lavatory smoke detectors are monitored and tampering "
        "with one is an offence in its own right.",
        "ማጨስ በእያንዳንዱ በረራ፣ በእያንዳንዱ ካቢን የተከለከለ ነው፤ የኤሌክትሮኒክ ሲጋራዎችንና የሚሞቅ ትምባሆን ጨምሮ። የመጸዳጃ ቤት "
        "የጭስ ማወቂያዎች ይቆጣጠራሉ፤ አንዱን መንካትም በራሱ ወንጀል ነው።")]),
     (("Electronic cigarettes in baggage", "የኤሌክትሮኒክ ሲጋራዎች በሻንጣ ውስጥ"),
      [("Carry them in the cabin, never in the hold, and do not charge them on board. This is "
        "the same lithium-battery rule that applies to power banks.",
        "በካቢን ይያዟቸው፤ በጭነት ክፍል በጭራሽ አይሁን፤ በበረራ ላይም አይሙሏቸው። ይህ ለኃይል ማጠራቀሚያዎች የሚሠራው ተመሳሳይ "
        "የሊቲየም ባትሪ ደንብ ነው።")]),
     (("Flight mode", "የበረራ ሁኔታ"),
      [("Phones, tablets and laptops may be used in flight mode throughout. Larger devices are "
        "stowed for take-off and landing. Bluetooth headphones are permitted; a device that "
        "cannot be switched to flight mode must be off.",
        "ስልኮች፣ ታብሌቶችና ላፕቶፖች በበረራው ጊዜ ሁሉ በበረራ ሁኔታ ሊውሉ ይችላሉ። ትልልቅ መሣሪያዎች ለመነሳትና ለማረፍ ይቀመጣሉ። "
        "የብሉቱዝ ማዳመጫዎች ይፈቀዳሉ፤ ወደ በረራ ሁኔታ ሊቀየር የማይችል መሣሪያ ግን መጥፋት አለበት።")]),
     ]),

 _p("miles-family-pooling", "loyalty", 10,
    ("Pooling miles with family", "ማይሎችን ከቤተሰብ ጋር ማጠራቀም"),
    ("Who can join a pool, and what pooling does not do.",
     "ማን ማጠራቀሚያ መቀላቀል እንደሚችል፣ እና ማጠራቀም የማያደርገው።"),
    [(("The pool", "ማጠራቀሚያው"),
      [("Up to eight members of one household may pool. Every member keeps their own account "
        "and earns as usual; the pool is a shared balance that any nominated member may spend, "
        "and the pool head sets who may.",
        "ከአንድ ቤተሰብ እስከ ስምንት አባላት ማጠራቀም ይችላሉ። እያንዳንዱ አባል የራሱን ሒሳብ ይዞ እንደተለመደው ያገኛል፤ ማጠራቀሚያው "
        "ማንኛውም የተመደበ አባል ሊጠቀምበት የሚችል የጋራ ቀሪ ሒሳብ ነው፤ ማን እንደሚችልም የማጠራቀሚያው ኃላፊ ይወስናል።")]),
     (("What it does not do", "የማያደርገው"),
      [("Pooled miles do not count towards anyone's tier. Qualifying miles stay with the "
        "member who flew, so pooling changes what you can spend and never what tier you reach.",
        "የተጠራቀሙ ማይሎች ለማንም ደረጃ አይቆጠሩም። የብቁነት ማይሎች የበረረው አባል ጋር ይቀራሉ፤ ስለዚህ ማጠራቀም ሊያወጡት የሚችሉትን "
        "ይለውጣል እንጂ የሚደርሱበትን ደረጃ በጭራሽ አይለውጥም።")]),
     ]),

 _p("partner-earning", "loyalty", 11,
    ("Earning on partner flights", "በአጋር በረራዎች ማግኘት"),
    ("How to credit a partner flight, and when it will not credit.",
     "የአጋር በረራን እንዴት ማስመዝገብ እንደሚቻል፣ እና መቼ እንደማይመዘገብ።"),
    [(("Quote the number when you book", "ሲይዙ ቁጥሩን ይጥቀሱ"),
      [("Give your membership number at booking, not at the gate. A flight added afterwards "
        "credits within 6 to 8 weeks; one that never credits can be claimed for up to 6 months "
        "from the flight date, with the ticket number and the boarding pass.",
        "የአባልነት ቁጥርዎን በበሩ ላይ ሳይሆን ቦታ ሲይዙ ይስጡ። በኋላ የተጨመረ በረራ በ6 እስከ 8 ሳምንታት ውስጥ ይመዘገባል፤ "
        "በጭራሽ የማይመዘገብ ደግሞ ከበረራው ቀን ጀምሮ እስከ 6 ወር ድረስ ከትኬት ቁጥሩና ከመሳፈሪያ ፈቃዱ ጋር ሊጠየቅ ይችላል።")]),
     (("Fares that earn nothing", "ምንም የማያስገኙ ታሪፎች"),
      [("Award tickets, staff and industry-discount tickets, tickets bought with a voucher for "
        "the full fare, and the deepest promotional fares on partner airlines. The fare rules "
        "on your booking say which applies.",
        "የሽልማት ትኬቶች፣ የሠራተኛና የኢንዱስትሪ ቅናሽ ትኬቶች፣ ሙሉ ታሪፉን በቫውቸር የተገዙ ትኬቶች፣ እንዲሁም በአጋር አየር መንገዶች "
        "ላይ ያሉ በጣም ጥልቅ የቅናሽ ታሪፎች። በቦታ ማስያዣዎ ላይ ያሉት የታሪፍ ደንቦች የትኛው እንደሚሠራ ይናገራሉ።")]),
     ]),

 _p("lounge-eligibility-explained", "loyalty", 12,
    ("Who gets into a lounge", "ወደ ላውንጅ ማን እንደሚገባ"),
    ("The four ways in, and what each one includes.",
     "አራቱ የመግቢያ መንገዶች፣ እና እያንዳንዱ የሚያካትተው።"),
    [(("Four ways in", "አራት የመግቢያ መንገዶች"),
      [[("A " + BIZ_EN + " boarding pass for the flight you are about to take.",
         "ሊሳፈሩበት ላለው በረራ የ" + BIZ_AM + " የመሳፈሪያ ፈቃድ።"),
        ("Gold or platinum tier, in any cabin, including one guest.",
         "የወርቅ ወይም የፕላቲነም ደረጃ፣ በማንኛውም የጉዞ ክፍል፣ አንድ እንግዳን ጨምሮ።"),
        ("Silver tier, in any cabin, without a guest.",
         "የሲልቨር ደረጃ፣ በማንኛውም የጉዞ ክፍል፣ ያለ እንግዳ።"),
        ("A walk-in pass bought for the visit, which anyone with a boarding pass may buy.",
         "ለጉብኝቱ የተገዛ የመግቢያ ፈቃድ፤ የመሳፈሪያ ፈቃድ ያለው ማንኛውም ሰው ሊገዛው ይችላል።")]]),
     (("What entry includes", "መግቢያው የሚያካትተው"),
      [("Buffet and bar, wi-fi, showers where the lounge has them, and a three-hour stay. "
        "Entry is at the departure airport only: a lounge at your destination is not part of "
        "your ticket, however you got into the one you left from.",
        "ቡፌና መጠጥ ቤት፣ ዋይ-ፋይ፣ ላውንጁ ሲኖረው ሻወር፣ እንዲሁም የሦስት ሰዓት ቆይታ። መግቢያው በመነሻ አየር ማረፊያ ብቻ ነው፦ "
        "ወደ ወጡበት ላውንጅ እንዴት ቢገቡም በመድረሻዎ ያለ ላውንጅ የትኬትዎ አካል አይደለም።")]),
     ]),
]
