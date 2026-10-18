STEPS = {
1: ("/", [
    "On the home page, leave the <b>Round trip</b> tab selected.",
    "From <code>ADD</code>, To <code>NBO</code>, Departing <code>2026-04-12</code>, Returning <code>2026-04-19</code>, Adults <code>1</code>.",
    "Search. Read the outbound grid: every flight number, and the lowest Total column.",
   ], "Answer must contain <code>SM222</code> and <code>USD 112</code>.", ""),

2: ("/", [
    "From <code>ADD</code>, To <code>DXB</code>, Departing <code>2026-04-20</code>, Adults <code>1</code>. "
    "<b>Leave Returning empty</b> \u2014 that is what makes it one-way; there is no trip-type tab.",
    "Search, then <b>Select</b> any fare on the results grid.",
    "Fill the passenger form: any first and last name, any email, any phone.",
    "Continue to the review page. <b>Do not press Pay.</b>",
   ], "URL ends <code>/book/review</code>, a draft booking exists, nothing paid.", ""),

3: ("/flight-status", [
    "Flight number <code>SM107</code>, Date <code>2026-03-16</code>.",
    "Read the status, both times and both terminals.",
   ], "Answer must contain <code>Delayed</code> (<span lang=am>የዘገየ</span>), <code>23:20</code>, <code>03:05</code> and the terminal numbers.", ""),

4: ("/schedules", [
    "From <code>ADD</code>, To <code>ABJ</code>. Show timetable.",
    "The table lists all seven days with a Yes/No column — read which say Yes.",
   ], "<b>Scored on what you type as the answer</b>, not the page. Must name Monday and Friday.", ""),

5: ("/manage", [
    "Booking reference <code>WGYBNA</code>, Last name <code>Assefa</code> (<span lang=am>አሰፋ</span>).",
    "Read the itinerary: both flight numbers and the booking status.",
   ], "Answer must contain <code>SM111</code> and <code>WGYBNA</code>.", "WGYBNA"),

6: ("/manage", [
    "Retrieve <code>W7JKUF</code> / <code>Terefe</code> (<span lang=am>ተረፈ</span>).",
    "Open <b>Change flight</b> on the outbound segment.",
    "Pick a later date, choose one of the alternative flights offered.",
    "Confirm to reach the change review. <b>Stop there.</b>",
   ], "URL ends <code>/change/review</code>, a pending change request exists, nothing paid.", "W7JKUF"),

7: ("/manage", [
    "Retrieve <code>SPMVJC</code> / <code>Kebede</code> (<span lang=am>ከበደ</span>).",
    "Open <b>Request a refund</b>.",
    "Read what the page says. It refuses — report the reason it gives.",
   ], "The fare <i>is</i> refundable; the booking was made through an agent, so online refund is blocked. No refund row may be created.", "SPMVJC"),

8: ("/checkin", [
    "Booking reference <code>WGYBNA</code>, Last name <code>Assefa</code> (<span lang=am>አሰፋ</span>).",
    "Select the segment offered and check in.",
    "Download the boarding pass PDF. Read the seat and gate off it.",
   ], "The segment is marked checked in and a boarding pass row exists.", "WGYBNA"),

9: ("/checkin", [
    "Booking reference <code>MBX744</code>, Last name <code>Zeleke</code> (<span lang=am>ዘለቀ</span>).",
    "The site refuses. Report the reason shown.",
   ], "Answer must contain <code>Group booking</code> (<span lang=am>የቡድን ቦታ ማስያዣ</span>).", "MBX744"),

10: ("/manage", [
    "Retrieve <code>N9JKBF</code> / <code>Haile</code> (<span lang=am>ኃይሌ</span>).",
    "Open <b>Seat selection</b> for the outbound flight.",
    "Above the map, <b>Window / Aisle / Middle</b> name which seat letters are which on this aircraft. Click any free seat in an aisle column.",
    "Continue to the seat review. <b>Stop before paying.</b>",
   ], "The seat assigned must actually be an aisle seat. A window seat fails.", "N9JKBF"),

11: ("/manage", [
    "Retrieve <code>WGYBNA</code> / <code>Assefa</code> (<span lang=am>አሰፋ</span>).",
    "Open <b>Seat selection</b>. Rows with extra legroom carry an <b>Extra legroom</b> badge.",
    "Report their price. Buy nothing.",
   ], "Answer must contain <code>USD 45</code>.", "WGYBNA"),

12: ("/baggage/allowance", [
    "From <code>ADD</code>, To <code>JFK</code>, Cabin <b>Selam Economy</b>, Passenger <b>Adult</b>.",
    "Show allowance. Read checked pieces, kg per piece, and cabin allowance.",
   ], "Answer must contain <code>2</code>, <code>23</code> and <code>7</code>.", ""),

13: ("/manage", [
    "Retrieve <code>WGYBNA</code> / <code>Assefa</code> (<span lang=am>አሰፋ</span>).",
    "Open <b>Extra baggage</b> for the outbound segment.",
    "Enter <code>23</code> kg and continue to the review. <b>Stop before paying.</b>",
   ], "23 kg pending, priced at the route's own regional rate. 20 kg fails; so does stopping short of review.", "WGYBNA"),

14: ("/baggage/special", [
    "Find the bicycle row in the items table, and read the packing rules in the prose above it.",
   ], "Answer must contain <code>handlebars</code>, <code>pedals</code> and <code>48</code>.", ""),

15: ("/manage", [
    "Retrieve <code>WGYBNA</code> / <code>Assefa</code> (<span lang=am>አሰፋ</span>).",
    "Open <b>Upgrade to Highland Class</b> on the outbound flight.",
    "Report the outcome and, if refused, the reason.",
   ], "Answer must contain <code>not eligible</code> (<span lang=am>ብቁ አይደለም</span>). The fare class excludes upgrades.", "WGYBNA"),

16: ("/lounges/purchase", [
    "Choose <b>Highland Lounge</b> — the one at Terminal 1, not the Terminal 2 lounge.",
    "Passenger name: anything. Guests: <code>0</code>.",
    "Continue to the payment page. <b>Do not pay.</b>",
   ], "A pending purchase for lounge 1 at USD 55. Any other Addis lounge fails.", ""),

17: ("/lounges/eligibility", [
    "Airport <code>ADD</code>, Cabin <b>Selam Economy</b>, Tier <b>Gold</b>. Check access.",
    "Find the Terminal 2 lounge marked free with your tier, then open it for its hours and location.",
   ], "Answer must contain <code>Highland Lounge Terminal 2</code> and <code>24 hours</code>.", ""),

18: ("/miles/join", [
    "First name <code>Selamawit</code> (<span lang=am>ሰላማዊት</span>), Last name <code>Bekele</code> (<span lang=am>በቀለ</span>).",
    "Email <code>selamawit.bekele@example.com</code>, Country <code>ET</code>, any date of birth.",
    "Submit and read the membership number returned.",
   ], "Must create member <code>SM00000016</code> with that exact email. The number is deterministic after a reset.", ""),

19: ("/miles/claim", [
    "Membership number <code>SM00000001</code>, Ticket <code>0712345678901</code>.",
    "Flight <code>SM246</code>, Flight date <code>2026-03-15</code>.",
    "Submit and read the claim reference.",
   ], "A claim for SM246 must exist. Reference is <code>MC-100001</code> after a reset.", "SM00000001"),

20: ("/miles/award-search", [
    "From <code>ADD</code>, To <code>CAI</code>, Departing <code>2026-03-19</code>, Cabin <b>Selam Economy</b>.",
    "Read the miles required and the taxes.",
   ], "Answer must contain <code>25000</code> and <code>USD 60</code>.", ""),

21: ("/onboard/wifi", [
    "Flight <code>SM106</code>, Date <code>2026-03-19</code>.",
    "Compare the packages, then select the one with the <b>largest</b> data allowance.",
    "Continue to review. <b>Stop before paying.</b>",
   ], "The pending purchase must be the largest package on that flight. The smallest fails.", ""),

22: ("/manage", [
    "Retrieve <code>WGYBNA</code> / <code>Assefa</code> (<span lang=am>አሰፋ</span>).",
    "In the booking's action list, open <b>In-flight dining</b> — it carries the "
    "booking through, so there is nothing to retype.",
    "From the special-meal list pick the gluten-free code, <code>GFML</code>, and request it.",
   ], "A meal request with code GFML. Any of the other thirteen codes fails.", "WGYBNA"),

23: ("/help/allergies", [
    "Read the page and summarise: what to do before travel, and what the airline will and will not guarantee.",
   ], "Answer must contain <code>48 hours</code>, <code>24 hours</code> and <code>allergen-free</code>.", ""),

24: ("/stopover", [
    "From <code>NBO</code>, To <code>LHR</code>, Departing <code>2026-04-12</code>. Check my connection.",
    "Read whether it qualifies and list the services offered.",
   ], "The eligible connection's flight numbers must be on the page — the landing page alone fails. Layover is 21h, inside the 8–72h window.", ""),

25: ("/partners", [
    "Open <b>Zena Transit Hotel</b> from the partner hub.",
    "Arrival <code>2026-04-12</code>, hours <code>12</code>, any guest name, pick a room.",
    "Continue to the review. <b>Do not pay.</b>",
   ], "A pending hotel booking on the partner site, nothing paid.", ""),

26: ("/partners", [
    "Open <b>National eVisa Service</b> from the partner hub.",
    "Pick the visa type that covers a seven-day tourist visit.",
    "Report the documents it lists as required.",
   ], "Final URL must be on the eVisa partner site, with the visa type's documents shown.", ""),

27: ("/partners", [
    "Open <b>EuroRail Connect</b> from the partner hub.",
    "Arrival airport <code>FRA</code>. Find connections.",
    "Read the Cologne row and its How-to-book note.",
   ], "Final URL on the rail partner site, with the Cologne leg's booking note displayed.", ""),

28: ("/partners", [
    "Open <b>RiftDrive</b> from the partner hub.",
    "Airport <code>NBO</code> — not ADD. Passengers <code>2</code>, Pickup <code>2026-04-12</code>.",
    "Reserve a vehicle and continue to the review. <b>Do not pay.</b>",
   ], "A pending transfer at NBO. Reserving at ADD fails.", ""),

29: ("/partners", [
    "Open <b>SafeVoyage Travel Cover</b> from the partner hub.",
    "Enter a fare of <code>900</code> to price the cover.",
    "Report the coverage limits and the price. Buy nothing.",
   ], "The products must be priced against a fare — an unpriced page fails.", ""),

30: ("/help/contact", [
    "Find <b>Austria</b> in the directory and open its office page.",
    "The local office closes at night, so report the 24-hour line, not the Vienna number.",
   ], "Answer must contain <code>+251 11 517 8888</code> and <code>Daily 07:00-20:00</code>. Quoting only the Vienna number fails.", ""),
}
