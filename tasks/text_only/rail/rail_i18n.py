D = {"bn": str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"),
     "hi": str.maketrans("0123456789", "०१२३४५६७८९"),
     "ur": str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")}


def nd(x, lang):
    return str(x).translate(D[lang]) if lang in D else str(x)


LIT = {
 "en": {
  "cred": " Sign in as priya_sharma (password: travel123) if needed.",
  "kabir": "Kabir Mehta", "sunita": "Sunita Verma", "farhan": "Farhan Ali",
  "nisha": "Nisha Rao", "anaya": "Anaya Kapoor", "ritu": "Ritu Singh",
  "mohan": "Mohan Das", "sara": "Sara Khan", "ravi": "Ravi Kumar",
  "c_email": "priya.sharma@example.in",
  "c_subject": "Refund delay",
  "c_message": "My refund for a cancelled ticket has not arrived.",
  "pnr_query": "PNR query", "refund_status_for": "Refund status for ",
  "anomaly_subject": "Fare anomaly on route 12659",
  "anomaly_msg": "The CC fare from {JP} to {AII} appears higher than the "
                 "published tariff.",
  "cur_w": "rupees", "sunday": "Sunday", "two": "two",
  "na_no_train_day": ['no train', 'no direct train', 'does not run', 'not run on', 'no trains'],
  "na_no_booking": ['no booking', 'not found', 'no record', 'does not exist', 'invalid pnr'],
  "na_no_route": ['no train', 'no direct train', 'none exists', 'no trains', 'not served'],
  "na_class": ['not offered', 'no 1a', 'does not offer', 'not available on this train', 'no ac first'],
  "na_book_refused": ['does not run', 'not run on', 'no train', 'not running', 'did not book'],
  "na_no_route2": ['no train', 'no direct train', 'not served', 'no trains', 'does not serve'],
  "na_no_train_day2": ['no train', 'does not run', 'not run on', 'no trains', 'does not depart'],
  "na_no_route3": ['no train', 'none serves', 'not served', 'no trains', 'does not serve'],
  "na_surcharge": ['not stated', 'no surcharge', 'does not state', 'not mentioned', 'no tatkal surcharge'],
 },
 "bn": {
  "cred": " প্রয়োজনে priya_sharma (পাসওয়ার্ড: travel123) হিসেবে সাইন ইন করুন।",
  "kabir": "কবির মেহতা", "sunita": "সুনীতা ভার্মা", "farhan": "ফারহান আলী",
  "nisha": "নিশা রাও", "anaya": "আনায়া কাপুর", "ritu": "ঋতু সিং",
  "mohan": "মোহন দাস", "sara": "সারা খান", "ravi": "রবি কুমার",
  "c_email": "priya.sharma@example.in",
  "c_subject": "রিফান্ডে দেরি",
  "c_message": "আমার বাতিল টিকিটের রিফান্ড এখনও আসেনি।",
  "pnr_query": "PNR প্রশ্ন", "refund_status_for": "রিফান্ডের অবস্থা: ",
  "anomaly_subject": "রুট 12659-এ ভাড়ার অসঙ্গতি",
  "anomaly_msg": "{JP} থেকে {AII} পর্যন্ত CC ভাড়া প্রকাশিত তালিকার চেয়ে "
                 "বেশি মনে হচ্ছে।",
  "cur_w": "টাকা", "sunday": "রবিবার", "two": "দুই",
  "na_no_train_day": ['কোনো ট্রেন নেই', 'সরাসরি ট্রেন নেই', 'চলে না', 'ওই দিন চলে না', 'ট্রেন চলে না'],
  "na_no_booking": ['কোনো বুকিং নেই', 'পাওয়া যায়নি', 'কোনো রেকর্ড নেই', 'নেই', 'অবৈধ pnr'],
  "na_no_route": ['কোনো ট্রেন নেই', 'সরাসরি ট্রেন নেই', 'কোনোটি নেই', 'ট্রেন নেই', 'সেবা নেই'],
  "na_class": ['দেওয়া হয় না', '1a নেই', 'নেই', 'এই ট্রেনে নেই', 'ac ফার্স্ট নেই'],
  "na_book_refused": ['চলে না', 'ওই দিন চলে না', 'কোনো ট্রেন নেই', 'চলছে না', 'বুক করিনি'],
  "na_no_route2": ['কোনো ট্রেন নেই', 'সরাসরি ট্রেন নেই', 'সেবা নেই', 'ট্রেন নেই', 'এই রুটে নেই'],
  "na_no_train_day2": ['কোনো ট্রেন নেই', 'চলে না', 'ওই দিন চলে না', 'ট্রেন নেই', 'ছাড়ে না'],
  "na_no_route3": ['কোনো ট্রেন নেই', 'কোনোটি চলে না', 'সেবা নেই', 'ট্রেন নেই', 'এই রুটে নেই'],
  "na_surcharge": ['উল্লেখ নেই', 'কোনো সারচার্জ নেই', 'বলা নেই', 'কোথাও নেই', 'তৎকাল সারচার্জ নেই'],
 },
 "hi": {
  "cred": " ज़रूरत हो तो priya_sharma (पासवर्ड: travel123) के रूप में साइन इन करें।",
  "kabir": "कबीर मेहता", "sunita": "सुनीता वर्मा", "farhan": "फ़रहान अली",
  "nisha": "निशा राव", "anaya": "अनाया कपूर", "ritu": "ऋतु सिंह",
  "mohan": "मोहन दास", "sara": "सारा ख़ान", "ravi": "रवि कुमार",
  "c_email": "priya.sharma@example.in",
  "c_subject": "रिफ़ंड में देरी",
  "c_message": "मेरे रद्द टिकट का रिफ़ंड अभी तक नहीं आया है।",
  "pnr_query": "PNR प्रश्न", "refund_status_for": "रिफ़ंड की स्थिति: ",
  "anomaly_subject": "मार्ग 12659 पर किराया विसंगति",
  "anomaly_msg": "{JP} से {AII} का CC किराया प्रकाशित दर से अधिक लग रहा है।",
  "cur_w": "रुपये", "sunday": "रविवार", "two": "दो",
  "na_no_train_day": ['कोई ट्रेन नहीं', 'सीधी ट्रेन नहीं', 'नहीं चलती', 'उस दिन नहीं चलती', 'ट्रेन नहीं'],
  "na_no_booking": ['कोई बुकिंग नहीं', 'नहीं मिली', 'कोई रिकॉर्ड नहीं', 'मौजूद नहीं', 'अमान्य pnr'],
  "na_no_route": ['कोई ट्रेन नहीं', 'सीधी ट्रेन नहीं', 'कोई नहीं', 'ट्रेन नहीं', 'सेवा नहीं'],
  "na_class": ['उपलब्ध नहीं', '1a नहीं', 'नहीं दी जाती', 'इस ट्रेन में नहीं', 'ac प्रथम नहीं'],
  "na_book_refused": ['नहीं चलती', 'उस दिन नहीं चलती', 'कोई ट्रेन नहीं', 'नहीं चल रही', 'बुक नहीं किया'],
  "na_no_route2": ['कोई ट्रेन नहीं', 'सीधी ट्रेन नहीं', 'सेवा नहीं', 'ट्रेन नहीं', 'इस मार्ग पर नहीं'],
  "na_no_train_day2": ['कोई ट्रेन नहीं', 'नहीं चलती', 'उस दिन नहीं चलती', 'ट्रेन नहीं', 'प्रस्थान नहीं'],
  "na_no_route3": ['कोई ट्रेन नहीं', 'कोई नहीं चलती', 'सेवा नहीं', 'ट्रेन नहीं', 'इस मार्ग पर नहीं'],
  "na_surcharge": ['उल्लेख नहीं', 'कोई अधिभार नहीं', 'बताया नहीं', 'कहीं नहीं', 'तत्काल अधिभार नहीं'],
 },
 "ur": {
  "cred": " ضرورت ہو تو priya_sharma (پاس ورڈ: travel123) کے طور پر سائن ان کریں۔",
  "kabir": "کبیر مہتا", "sunita": "سنیتا ورما", "farhan": "فرحان علی",
  "nisha": "نشا راؤ", "anaya": "انایا کپور", "ritu": "رتو سنگھ",
  "mohan": "موہن داس", "sara": "سارہ خان", "ravi": "روی کمار",
  "c_email": "priya.sharma@example.in",
  "c_subject": "ریفنڈ میں تاخیر",
  "c_message": "میرے منسوخ ٹکٹ کا ریفنڈ ابھی تک نہیں آیا۔",
  "pnr_query": "PNR سوال", "refund_status_for": "ریفنڈ کی حیثیت: ",
  "anomaly_subject": "روٹ 12659 پر کرائے کی بے ضابطگی",
  "anomaly_msg": "{JP} سے {AII} کا CC کرایہ شائع شدہ نرخ سے زیادہ لگتا ہے۔",
  "cur_w": "روپے", "sunday": "اتوار", "two": "دو",
  "na_no_train_day": ['کوئی ٹرین نہیں', 'براہ راست ٹرین نہیں', 'نہیں چلتی', 'اس دن نہیں چلتی', 'ٹرین نہیں'],
  "na_no_booking": ['کوئی بکنگ نہیں', 'نہیں ملی', 'کوئی ریکارڈ نہیں', 'موجود نہیں', 'غلط pnr'],
  "na_no_route": ['کوئی ٹرین نہیں', 'براہ راست ٹرین نہیں', 'کوئی نہیں', 'ٹرین نہیں', 'سروس نہیں'],
  "na_class": ['دستیاب نہیں', '1a نہیں', 'پیش نہیں', 'اس ٹرین میں نہیں', 'ac فرسٹ نہیں'],
  "na_book_refused": ['نہیں چلتی', 'اس دن نہیں چلتی', 'کوئی ٹرین نہیں', 'نہیں چل رہی', 'بک نہیں کی'],
  "na_no_route2": ['کوئی ٹرین نہیں', 'براہ راست ٹرین نہیں', 'سروس نہیں', 'ٹرین نہیں', 'اس روٹ پر نہیں'],
  "na_no_train_day2": ['کوئی ٹرین نہیں', 'نہیں چلتی', 'اس دن نہیں چلتی', 'ٹرین نہیں', 'روانہ نہیں'],
  "na_no_route3": ['کوئی ٹرین نہیں', 'کوئی نہیں چلتی', 'سروس نہیں', 'ٹرین نہیں', 'اس روٹ پر نہیں'],
  "na_surcharge": ['ذکر نہیں', 'کوئی سرچارج نہیں', 'بتایا نہیں', 'کہیں نہیں', 'تتکال سرچارج نہیں'],
 },
 "am": {
  "cred": " ካስፈለገ እንደ priya_sharma (የይለፍ ቃል፡ travel123) ይግቡ።",
  "kabir": "ካቢር ሜህታ", "sunita": "ሱኒታ ቨርማ", "farhan": "ፋርሃን አሊ",
  "nisha": "ኒሻ ራኦ", "anaya": "አናያ ካፑር", "ritu": "ሪቱ ሲንግ",
  "mohan": "ሞሃን ዳስ", "sara": "ሳራ ካን", "ravi": "ራቪ ኩማር",
  "c_email": "priya.sharma@example.in",
  "c_subject": "የተመላሽ መዘግየት",
  "c_message": "ለተሰረዘ ትኬቴ ተመላሹ አልደረሰም።",
  "pnr_query": "የPNR ጥያቄ", "refund_status_for": "የተመላሽ ሁኔታ ለ ",
  "anomaly_subject": "በመስመር 12659 የዋጋ ልዩነት",
  "anomaly_msg": "ከ{JP} ወደ {AII} ያለው የCC ዋጋ ከታተመው ታሪፍ ከፍ ያለ ይመስላል።",
  "cur_w": "ብር", "sunday": "እሁድ", "two": "ሁለት",
  "na_no_train_day": ['ባቡር የለም', 'ቀጥተኛ ባቡር የለም', 'አይሠራም', 'በዚያ ቀን አይሠራም', 'ባቡሮች የሉም'],
  "na_no_booking": ['ማስያዣ የለም', 'አልተገኘም', 'መዝገብ የለም', 'የለም', 'ልክ ያልሆነ pnr'],
  "na_no_route": ['ባቡር የለም', 'ቀጥተኛ ባቡር የለም', 'ምንም የለም', 'ባቡሮች የሉም', 'አገልግሎት የለም'],
  "na_class": ['አይሰጥም', '1a የለም', 'አይቀርብም', 'በዚህ ባቡር የለም', 'ac አንደኛ የለም'],
  "na_book_refused": ['አይሠራም', 'በዚያ ቀን አይሠራም', 'ባቡር የለም', 'እየሠራ አይደለም', 'አላስያዝኩም'],
  "na_no_route2": ['ባቡር የለም', 'ቀጥተኛ ባቡር የለም', 'አገልግሎት የለም', 'ባቡሮች የሉም', 'በዚህ መስመር የለም'],
  "na_no_train_day2": ['ባቡር የለም', 'አይሠራም', 'በዚያ ቀን አይሠራም', 'ባቡሮች የሉም', 'አይነሳም'],
  "na_no_route3": ['ባቡር የለም', 'ምንም አይሠራም', 'አገልግሎት የለም', 'ባቡሮች የሉም', 'በዚህ መስመር የለም'],
  "na_surcharge": ['አልተገለጸም', 'ተጨማሪ ክፍያ የለም', 'አይገልጽም', 'አልተጠቀሰም', 'የታትካል ተጨማሪ ክፍያ የለም'],
 },
}

I18N = {
 "en": {
  "k1": "How long does train 12903 {t12903} take from {NDLS} to {BCT}? "
        "Answer with the duration as shown.",
  "k2": "Find the lowest 3A fare for a journey from {NDLS} to {CNB} on "
        "2026-04-06 and answer with the amount in {cur_w}.",
  "k3": "Check the PNR status of PNR 6201234567 and answer with the "
        "status code.",
  "k4": "Look up PNR 6203456789 and answer with the passenger's name.",
  "k5": "Book a 2A ticket on train 12301 {t12301} from {NDLS} to {HWH} on "
        "2026-04-06 for passenger {kabir}, age 41, male, Upper berth.",
  "k6": "Book a CC (chair car) ticket on train 12417 {t12417} from {NDLS} "
        "to {LKO} on 2026-04-07 for passenger {sunita}, age 55, female, "
        "no berth preference.",
  "k7": "Book an SL (sleeper) ticket on train 12841 {t12841} from {HWH} "
        "to {MAS} on 2026-04-08 for passenger {farhan}, age 23, male, "
        "Side Upper berth.",
  "k8": "Cancel the booking with PNR 6203456789.",
  "k9": "On train 12622 {t12622} from {HWH} to {GHY}, how much more does "
        "a 2A ticket cost than a 3A ticket? Answer with the difference "
        "in {cur_w}.",
  "k10": "Find a direct train from {SC} to {PUNE} departing on "
         "2026-04-07. If no train runs that day, answer N/A.",
  "k11": "Check the PNR status of PNR 6299999999. If no booking exists, "
         "answer N/A.",
  "k12": "Send a message to customer support with the subject "
         "'{c_subject}' explaining that your refund has not arrived. "
         "Include your name and email ({c_name}, {c_email}).",
  "k13": "Update the mobile number in your profile to 9876501234.",
  "k14": "According to the refund rules, what is the flat cancellation "
         "charge in {cur_w} for a confirmed AC class ticket cancelled "
         "more than 48 hours before departure?",
  "k15": "Is there any direct train from {JP} to {LKO} on 2026-04-09? If "
         "none exists, answer N/A.",
  "a1": "Across ALL trains on this site, which single train covers the "
        "longest total distance from its origin to its terminus? Answer "
        "with the train number and the distance in km.",
  "a2": "Which train makes the most scheduled stops in total (including "
        "its origin and terminus)? Answer with the train number and the "
        "number of stops.",
  "a3": "Among trains that run DAILY, which one arrives at its terminus "
        "latest in the day (by clock time)? Answer with the train number "
        "and the arrival time.",
  "a4": "Which train has the LONGEST halt at any intermediate station on "
        "this site? Answer with the train number and the halt length in "
        "minutes.",
  "a5": "Across all trains that offer SL (Sleeper), which has the "
        "cheapest full-route SL fare? Answer with the train number and "
        "the fare in {cur_w}.",
  "a6": "Across all trains that offer 1A (AC First Class), which has the "
        "most expensive full-route 1A fare? Answer with the train number "
        "and the fare in {cur_w}.",
  "a7": "Exactly two stations on this site are each served by exactly 3 "
        "trains. Which two? Answer with both station names.",
  "a8": "Among trains that run DAILY, which departs its origin earliest "
        "in the morning? Answer with the train number and the departure "
        "time.",
  "b1": "Which train can take you from {PNBE} to {HWH} departing on "
        "2026-04-07? Answer with its train number (or N/A if none runs).",
  "b2": "Find a direct train from {NJP} to {GHY} departing on 2026-04-08. "
        "Answer with its train number (or N/A if none runs).",
  "b3": "Considering every date from 2026-04-06 through 2026-04-12, on "
        "which date do the MOST direct trains run from {NDLS} to {CNB}? "
        "Answer with the date (YYYY-MM-DD) and how many trains run that "
        "day.",
  "b4": "On how many days of the week does train 12301 {t12301} call at "
        "{PNBE}? Answer with the number.",
  "c1": "Your booking 6203456789 is a confirmed AC class ticket. If you "
        "cancelled it today (more than 48 hours before departure), what "
        "refund in {cur_w} would be due per the published refund rules? "
        "Answer with the amount.",
  "c2": "Your booking 6202345678 is waitlisted. Per the refund rules, "
        "what refund in {cur_w} would you receive if you cancelled it "
        "before departure? Answer with the amount.",
  "c3": "A confirmed 3A ticket for the full route of train 12615 "
        "{t12615} ({NDLS} to {MAS}) is cancelled 24 hours before "
        "departure. Per the refund rules, what refund in {cur_w} is due? "
        "Answer with the amount.",
  "c4": "If your confirmed booking {pnr} (an AC class ticket) were "
        "cancelled 6 hours before departure, what refund in {cur_w} "
        "would the rules allow? Answer with the amount.",
  "c5": "What would TWO 2A tickets cost in total on train 12559 {t12559} "
        "from {NDLS} to {BSB}? Answer with the total in {cur_w}.",
  "c6": "What is the combined fare in {cur_w} of all your CONFIRMED (CNF) "
        "bookings? Answer with the total.",
  "c7": "For a journey on train 12615 {t12615} from {AGC} to {SC}, how "
        "much more does 3A cost than SL? Answer with the difference in "
        "{cur_w}.",
  "c8": "Compare travelling {NDLS} to {BSB} by SL on the direct train "
        "12559 against splitting the trip into two SL legs: {NDLS} to "
        "{CNB} on train 12301, then {CNB} to {BSB} on train 12559. How "
        "many {cur_w} does the direct ticket save over the two-leg "
        "option?",
  "c9": "How many seats are available on train 12904 {t12904} in total, "
        "adding up all its classes? Answer with the number.",
  "c10": "Two of your bookings are for passengers {anita} and {meera}. "
         "Whose ticket fare is higher, and by how many {cur_w}? Answer "
         "with the passenger's name and the difference.",
  "d1": "On train 12302 {t12302} for its full route, which is the "
        "CHEAPEST class that still costs more than {t1000} {cur_w}? "
        "Answer with the class code and its fare.",
  "d2": "On train 12659 {t12659} from {JP} to {ADI}, which is the MOST "
        "expensive class that does not exceed {t500} {cur_w}? Answer "
        "with the class code and its fare.",
  "d3": "Among ALL trains that serve the {NDLS} to {CNB} segment, which "
        "offers the cheapest SL (Sleeper) fare for that segment? Answer "
        "with the train number and the fare in {cur_w}.",
  "d4": "Which costs more: a full-route 1A ticket on train 12622 "
        "{t12622}, or a 2A ticket on train 12615 {t12615} from {NDLS} to "
        "{BPL}? Answer with the winning train number and that fare in "
        "{cur_w}.",
  "d5": "Of all trains calling at {RTM}, which departs it earliest in "
        "the day (by clock time)? Answer with the train number and its "
        "departure time from there.",
  "e1": "One of your bookings is waitlisted (WL). Cancel that booking — "
        "and ONLY that one.",
  "e2": "Cancel ALL of your bookings for journeys dated 2026-04-10 or "
        "later that are not already cancelled. Leave every earlier "
        "journey untouched.",
  "e3": "In your profile, change the email address to priya.s@newmail.in "
        "AND the mobile number to 9812399999 (both, in one update).",
  "e4": "Look up PNR 6204567890 to find the passenger's name, then send "
        "a message to customer support with your name ({c_name}), your "
        "email ({c_email}), the subject '{pnr_query}' and the message "
        "exactly: '{refund_status_for}<passenger name>' — replacing "
        "<passenger name> with the name you found.",
  "e5": "Look up PNR 6201234567, then book a CC ticket on train 12049 "
        "{t12049} from {NDLS} to {AGC} on 2026-04-06 for the SAME "
        "passenger (same name and age) as that booking, male, no berth "
        "preference.",
  "e6": "Book an SL ticket on train 12138 {t12138} from {BCT} to {BPL} on "
        "2026-04-06 for passenger {nisha}, age 30, female, Lower berth — "
        "and then CANCEL that new booking.",
  "f1": "Find the EARLIEST-departing train from {NDLS} to {CNB} on "
        "2026-04-06 and book a CC ticket on it for passenger {anaya}, "
        "age 27, female, no berth preference.",
  "f2": "Travel from {NDLS} to {AGC} on 2026-04-06 as CHEAPLY as "
        "possible: compare every class on every train serving that day, "
        "and book the single cheapest option for passenger {ritu}, age "
        "24, female, no berth preference.",
  "f3": "Book a 3A ticket on the LATEST-departing train from {NDLS} to "
        "{CNB} on 2026-04-08 for passenger {mohan}, age 52, male, Lower "
        "berth.",
  "f4": "Book a 2A ticket from {NDLS} to {HWH} on 2026-04-09 for "
        "passenger {sara}, age 33, female, Upper berth. If no train runs "
        "that day, book the same journey on 2026-04-10 instead.",
  "g1": "What is the 1A (AC First Class) fare on train 12615 {t12615} for "
        "its full route? If that class is not offered on this train, "
        "answer N/A.",
  "g2": "Book a 2A ticket on train 12904 {t12904} from {BCT} to {NDLS} on "
        "2026-04-08 for passenger {ravi}, age 45, male. If the train "
        "does not run that day, do NOT book anything and answer N/A.",
  "g3": "Find a direct train from {LKO} to {AGC} on 2026-04-07. If no "
        "direct train serves this route, answer N/A.",
  "g4": "Find a direct train from {RTM} to {NDLS} departing on "
        "2026-04-06. If no train runs that day, answer N/A.",
  "g5": "Which train runs from {GHY} to {HWH} on 2026-04-08? If none "
        "serves that route, answer N/A.",
  "g6": "The booking form offers a TATKAL quota option. What extra Tatkal "
        "surcharge in {cur_w} does RailSetu state anywhere on the site? "
        "If no surcharge amount is stated, answer N/A.",
  "h1": "How many different trains call at {CNB} (in either direction)? "
        "Answer with the number.",
  "h2": "How many trains on this site run DAILY (all seven days)? Answer "
        "with the number.",
  "h3": "Check the PNR status of PNR 6207890123 and answer with the "
        "status code.",
  "h4": "For how many minutes does train 12615 {t12615} halt at {NGP}? "
        "Answer with the number of minutes.",
  "h5": "Which trains depart their ORIGIN station at 20:00 or later? "
        "Answer with both train numbers.",
  "h6": "Find the two trains with the SHORTEST total routes on this site "
        "and answer with the combined length of those two routes in km.",
  "h7": "How many of your bookings (any status) are for journeys dated "
        "BEFORE 2026-04-09? Answer with the number.",
  "h8": "Which of your bookings has the HIGHEST fare? Answer with its PNR "
        "and the fare in {cur_w}.",
  "h9": "At what time does train 12559 {t12559} arrive at {BSB}, and on "
        "which day of its run (1 or 2)? Answer with the time and the day "
        "number.",
  "h10": "On train 12659 {t12659}, how many km is it from {AII} to {ABR}? "
         "Answer with the distance in km.",
  "h11": "On train 12615 {t12615}, how many km does the train cover "
         "between {BPL} and {NGP}? Answer with the distance in km.",
  "h12": "How long does train 12723 {t12723} take from {SC} to {PUNE}? "
         "Answer with the duration as shown.",
  "h13": "On train 12301 {t12301}, what is the waitlist number shown for "
         "3A? Answer with the number.",
  "h14": "Send a message to customer support with your name ({c_name}) "
         "and email ({c_email}), the subject exactly '{anomaly_subject}' "
         "and the message exactly '{anomaly_msg}'",
  "h15": "How many bookings (of any status) are listed in your booking "
         "history? Answer with the number.",
  "h16": "How many 2A seats are available on train 12301 {t12301} from "
         "{NDLS} to {HWH} on 2026-04-06? Answer with the number.",
  "h17": "Find the train that runs from {BCT} to {BPL} and answer with "
         "its SL (sleeper) fare for that journey in {cur_w}.",
 },
 "bn": {
  "k1": "ট্রেন 12903 {t12903} {NDLS} থেকে {BCT} পর্যন্ত কত সময় নেয়? যেভাবে "
        "দেখানো আছে সেই সময়কাল উত্তর দিন।",
  "k2": "2026-04-06 তারিখে {NDLS} থেকে {CNB} ভ্রমণের সবচেয়ে কম 3A ভাড়া খুঁজুন "
        "এবং {cur_w}য় অঙ্কটি উত্তর দিন।",
  "k3": "PNR 6201234567-এর PNR অবস্থা দেখুন এবং অবস্থার কোড উত্তর দিন।",
  "k4": "PNR 6203456789 দেখুন এবং যাত্রীর নাম উত্তর দিন।",
  "k5": "2026-04-06 তারিখে ট্রেন 12301 {t12301}-এ {NDLS} থেকে {HWH} পর্যন্ত "
        "যাত্রী {kabir}, বয়স 41, পুরুষ, উপরের (Upper) বার্থের একটি 2A টিকিট "
        "বুক করুন।",
  "k6": "2026-04-07 তারিখে ট্রেন 12417 {t12417}-এ {NDLS} থেকে {LKO} পর্যন্ত "
        "যাত্রী {sunita}, বয়স 55, মহিলা, বার্থ পছন্দ নেই — একটি CC (চেয়ার "
        "কার) টিকিট বুক করুন।",
  "k7": "2026-04-08 তারিখে ট্রেন 12841 {t12841}-এ {HWH} থেকে {MAS} পর্যন্ত "
        "যাত্রী {farhan}, বয়স 23, পুরুষ, পাশের উপরের (Side Upper) বার্থের "
        "একটি SL (স্লিপার) টিকিট বুক করুন।",
  "k8": "PNR 6203456789-এর বুকিং বাতিল করুন।",
  "k9": "ট্রেন 12622 {t12622}-এ {HWH} থেকে {GHY} পর্যন্ত একটি 2A টিকিট 3A "
        "টিকিটের চেয়ে কত বেশি দামি? {cur_w}য় পার্থক্যটি উত্তর দিন।",
  "k10": "2026-04-07 তারিখে ছাড়া {SC} থেকে {PUNE} পর্যন্ত একটি সরাসরি ট্রেন "
         "খুঁজুন। ওই দিন কোনো ট্রেন না চললে N/A উত্তর দিন।",
  "k11": "PNR 6299999999-এর PNR অবস্থা দেখুন। কোনো বুকিং না থাকলে N/A উত্তর "
         "দিন।",
  "k12": "'{c_subject}' বিষয়ে গ্রাহক সহায়তায় একটি বার্তা পাঠান, যাতে বলা থাকে "
         "আপনার রিফান্ড আসেনি। আপনার নাম ও ইমেইল ({c_name}, {c_email}) দিন।",
  "k13": "আপনার প্রোফাইলের মোবাইল নম্বর 9876501234 করুন।",
  "k14": "রিফান্ড নিয়ম অনুযায়ী, ছাড়ার 48 ঘণ্টারও বেশি আগে বাতিল করা একটি "
         "নিশ্চিত AC শ্রেণির টিকিটে {cur_w}য় নির্দিষ্ট বাতিল চার্জ কত?",
  "k15": "2026-04-09 তারিখে {JP} থেকে {LKO} পর্যন্ত কোনো সরাসরি ট্রেন আছে কি? "
         "না থাকলে N/A উত্তর দিন।",
  "a1": "এই সাইটের সব ট্রেনের মধ্যে কোন একটি ট্রেন উৎস থেকে গন্তব্য পর্যন্ত "
        "সবচেয়ে বেশি মোট দূরত্ব অতিক্রম করে? ট্রেন নম্বর ও কিমি-তে দূরত্ব "
        "উত্তর দিন।",
  "a2": "কোন ট্রেন মোট সবচেয়ে বেশি নির্ধারিত স্টপে থামে (উৎস ও গন্তব্যসহ)? "
        "ট্রেন নম্বর ও স্টপের সংখ্যা উত্তর দিন।",
  "a3": "প্রতিদিন চলা ট্রেনগুলোর মধ্যে কোনটি দিনের সবচেয়ে দেরিতে (ঘড়ির সময় "
        "অনুযায়ী) গন্তব্যে পৌঁছায়? ট্রেন নম্বর ও পৌঁছানোর সময় উত্তর দিন।",
  "a4": "এই সাইটে কোন ট্রেনের কোনো মধ্যবর্তী স্টেশনে সবচেয়ে দীর্ঘ বিরতি আছে? "
        "ট্রেন নম্বর ও মিনিটে বিরতির দৈর্ঘ্য উত্তর দিন।",
  "a5": "SL (স্লিপার) আছে এমন সব ট্রেনের মধ্যে কোনটির পুরো রুটের SL ভাড়া "
        "সবচেয়ে সস্তা? ট্রেন নম্বর ও {cur_w}য় ভাড়া উত্তর দিন।",
  "a6": "1A (AC ফার্স্ট ক্লাস) আছে এমন সব ট্রেনের মধ্যে কোনটির পুরো রুটের 1A "
        "ভাড়া সবচেয়ে দামি? ট্রেন নম্বর ও {cur_w}য় ভাড়া উত্তর দিন।",
  "a7": "এই সাইটে ঠিক দুটি স্টেশনে ঠিক 3টি করে ট্রেন থামে। কোন দুটি? দুটি "
        "স্টেশনের নামই উত্তর দিন।",
  "a8": "প্রতিদিন চলা ট্রেনগুলোর মধ্যে কোনটি সকালে সবচেয়ে আগে উৎস থেকে ছাড়ে? "
        "ট্রেন নম্বর ও ছাড়ার সময় উত্তর দিন।",
  "b1": "2026-04-07 তারিখে ছেড়ে কোন ট্রেন আপনাকে {PNBE} থেকে {HWH} নিয়ে যেতে "
        "পারে? তার ট্রেন নম্বর উত্তর দিন (কোনোটি না চললে N/A)।",
  "b2": "2026-04-08 তারিখে ছাড়া {NJP} থেকে {GHY} পর্যন্ত একটি সরাসরি ট্রেন "
        "খুঁজুন। তার ট্রেন নম্বর উত্তর দিন (কোনোটি না চললে N/A)।",
  "b3": "2026-04-06 থেকে 2026-04-12 পর্যন্ত প্রতিটি তারিখ বিবেচনা করে, কোন "
        "তারিখে {NDLS} থেকে {CNB} পর্যন্ত সবচেয়ে বেশি সরাসরি ট্রেন চলে? "
        "তারিখ (YYYY-MM-DD) এবং সেদিন কতটি ট্রেন চলে তা উত্তর দিন।",
  "b4": "সপ্তাহের কত দিন ট্রেন 12301 {t12301} {PNBE}-এ থামে? সংখ্যাটি উত্তর "
        "দিন।",
  "c1": "আপনার বুকিং 6203456789 একটি নিশ্চিত AC শ্রেণির টিকিট। আজ বাতিল করলে "
        "(ছাড়ার 48 ঘণ্টারও বেশি আগে) প্রকাশিত রিফান্ড নিয়ম অনুযায়ী {cur_w}য় "
        "কত রিফান্ড প্রাপ্য হবে? অঙ্কটি উত্তর দিন।",
  "c2": "আপনার বুকিং 6202345678 অপেক্ষমাণ তালিকায়। রিফান্ড নিয়ম অনুযায়ী, "
        "ছাড়ার আগে বাতিল করলে {cur_w}য় কত রিফান্ড পাবেন? অঙ্কটি উত্তর দিন।",
  "c3": "ট্রেন 12615 {t12615}-এর পুরো রুটের ({NDLS} থেকে {MAS}) একটি নিশ্চিত 3A "
        "টিকিট ছাড়ার 24 ঘণ্টা আগে বাতিল করা হয়। রিফান্ড নিয়ম অনুযায়ী "
        "{cur_w}য় কত রিফান্ড প্রাপ্য? অঙ্কটি উত্তর দিন।",
  "c4": "আপনার নিশ্চিত বুকিং {pnr} (একটি AC শ্রেণির টিকিট) ছাড়ার 6 ঘণ্টা আগে "
        "বাতিল করা হলে নিয়ম অনুযায়ী {cur_w}য় কত রিফান্ড মিলবে? অঙ্কটি উত্তর "
        "দিন।",
  "c5": "ট্রেন 12559 {t12559}-এ {NDLS} থেকে {BSB} পর্যন্ত দুটি 2A টিকিটের মোট "
        "দাম কত হবে? {cur_w}য় মোট উত্তর দিন।",
  "c6": "আপনার সব নিশ্চিত (CNF) বুকিংয়ের সম্মিলিত ভাড়া {cur_w}য় কত? মোট "
        "উত্তর দিন।",
  "c7": "ট্রেন 12615 {t12615}-এ {AGC} থেকে {SC} ভ্রমণে 3A SL-এর চেয়ে কত বেশি "
        "দামি? {cur_w}য় পার্থক্যটি উত্তর দিন।",
  "c8": "{NDLS} থেকে {BSB} সরাসরি ট্রেন 12559-এ SL-এ যাওয়ার সঙ্গে দুটি SL "
        "পর্বে ভাগ করা যাত্রার তুলনা করুন: ট্রেন 12301-এ {NDLS} থেকে {CNB}, "
        "তারপর ট্রেন 12559-এ {CNB} থেকে {BSB}। দুই পর্বের বিকল্পের চেয়ে "
        "সরাসরি টিকিট কত {cur_w} সাশ্রয় করে?",
  "c9": "ট্রেন 12904 {t12904}-এ সব শ্রেণি মিলিয়ে মোট কতটি আসন খালি আছে? "
        "সংখ্যাটি উত্তর দিন।",
  "c10": "আপনার দুটি বুকিং যাত্রী {anita} ও {meera}-র জন্য। কার টিকিটের ভাড়া "
         "বেশি, এবং কত {cur_w} বেশি? যাত্রীর নাম ও পার্থক্য উত্তর দিন।",
  "d1": "ট্রেন 12302 {t12302}-এর পুরো রুটে {t1000} {cur_w}র বেশি দামের মধ্যে "
        "সবচেয়ে সস্তা শ্রেণি কোনটি? শ্রেণির কোড ও তার ভাড়া উত্তর দিন।",
  "d2": "ট্রেন 12659 {t12659}-এ {JP} থেকে {ADI} পর্যন্ত {t500} {cur_w} না "
        "ছাড়ানো সবচেয়ে দামি শ্রেণি কোনটি? শ্রেণির কোড ও তার ভাড়া উত্তর দিন।",
  "d3": "{NDLS} থেকে {CNB} অংশে চলা সব ট্রেনের মধ্যে কোনটি সেই অংশের জন্য "
        "সবচেয়ে সস্তা SL (স্লিপার) ভাড়া দেয়? ট্রেন নম্বর ও {cur_w}য় ভাড়া "
        "উত্তর দিন।",
  "d4": "কোনটি বেশি দামি: ট্রেন 12622 {t12622}-এর পুরো রুটের একটি 1A টিকিট, "
        "নাকি ট্রেন 12615 {t12615}-এ {NDLS} থেকে {BPL} পর্যন্ত একটি 2A টিকিট? "
        "যে ট্রেন জেতে তার নম্বর ও সেই ভাড়া {cur_w}য় উত্তর দিন।",
  "d5": "{RTM}-এ থামা সব ট্রেনের মধ্যে কোনটি দিনের সবচেয়ে আগে (ঘড়ির সময় "
        "অনুযায়ী) সেখান থেকে ছাড়ে? ট্রেন নম্বর ও সেখান থেকে ছাড়ার সময় উত্তর "
        "দিন।",
  "e1": "আপনার একটি বুকিং অপেক্ষমাণ তালিকায় (WL)। সেই বুকিংটি বাতিল করুন — "
        "শুধু সেটিই।",
  "e2": "2026-04-10 বা তার পরের তারিখের যাত্রার আপনার সব বুকিং, যেগুলো এখনও "
        "বাতিল হয়নি, বাতিল করুন। আগের প্রতিটি যাত্রা অপরিবর্তিত রাখুন।",
  "e3": "আপনার প্রোফাইলে ইমেইল ঠিকানা priya.s@newmail.in এবং মোবাইল নম্বর "
        "9812399999 করুন (দুটিই, এক হালনাগাদে)।",
  "e4": "PNR 6204567890 দেখে যাত্রীর নাম জানুন, তারপর গ্রাহক সহায়তায় আপনার নাম "
        "({c_name}), আপনার ইমেইল ({c_email}), বিষয় '{pnr_query}' এবং হুবহু "
        "এই বার্তা দিয়ে একটি বার্তা পাঠান: '{refund_status_for}<যাত্রীর নাম>' "
        "— <যাত্রীর নাম>-এর জায়গায় আপনার পাওয়া নামটি বসিয়ে।",
  "e5": "PNR 6201234567 দেখুন, তারপর 2026-04-06 তারিখে ট্রেন 12049 {t12049}-এ "
        "{NDLS} থেকে {AGC} পর্যন্ত সেই বুকিংয়ের একই যাত্রীর (একই নাম ও বয়স) "
        "জন্য, পুরুষ, বার্থ পছন্দ নেই — একটি CC টিকিট বুক করুন।",
  "e6": "2026-04-06 তারিখে ট্রেন 12138 {t12138}-এ {BCT} থেকে {BPL} পর্যন্ত "
        "যাত্রী {nisha}, বয়স 30, মহিলা, নিচের (Lower) বার্থের একটি SL টিকিট "
        "বুক করুন — এবং তারপর সেই নতুন বুকিংটি বাতিল করুন।",
  "f1": "2026-04-06 তারিখে {NDLS} থেকে {CNB} পর্যন্ত সবচেয়ে আগে ছাড়া ট্রেনটি "
        "খুঁজুন এবং তাতে যাত্রী {anaya}, বয়স 27, মহিলা, বার্থ পছন্দ নেই — "
        "একটি CC টিকিট বুক করুন।",
  "f2": "2026-04-06 তারিখে {NDLS} থেকে {AGC} যতটা সম্ভব সস্তায় ভ্রমণ করুন: "
        "সেদিন চলা প্রতিটি ট্রেনের প্রতিটি শ্রেণি তুলনা করুন এবং যাত্রী "
        "{ritu}, বয়স 24, মহিলা, বার্থ পছন্দ নেই — এর জন্য একমাত্র সবচেয়ে সস্তা "
        "বিকল্পটি বুক করুন।",
  "f3": "2026-04-08 তারিখে {NDLS} থেকে {CNB} পর্যন্ত সবচেয়ে দেরিতে ছাড়া "
        "ট্রেনে যাত্রী {mohan}, বয়স 52, পুরুষ, নিচের (Lower) বার্থের একটি 3A "
        "টিকিট বুক করুন।",
  "f4": "2026-04-09 তারিখে {NDLS} থেকে {HWH} পর্যন্ত যাত্রী {sara}, বয়স 33, "
        "মহিলা, উপরের (Upper) বার্থের একটি 2A টিকিট বুক করুন। ওই দিন কোনো "
        "ট্রেন না চললে একই যাত্রা 2026-04-10 তারিখে বুক করুন।",
  "g1": "ট্রেন 12615 {t12615}-এর পুরো রুটের 1A (AC ফার্স্ট ক্লাস) ভাড়া কত? এই "
        "ট্রেনে সেই শ্রেণি না থাকলে N/A উত্তর দিন।",
  "g2": "2026-04-08 তারিখে ট্রেন 12904 {t12904}-এ {BCT} থেকে {NDLS} পর্যন্ত "
        "যাত্রী {ravi}, বয়স 45, পুরুষের জন্য একটি 2A টিকিট বুক করুন। ট্রেন "
        "ওই দিন না চললে কিছুই বুক করবেন না এবং N/A উত্তর দিন।",
  "g3": "2026-04-07 তারিখে {LKO} থেকে {AGC} পর্যন্ত একটি সরাসরি ট্রেন খুঁজুন। "
        "কোনো সরাসরি ট্রেন এই রুটে না চললে N/A উত্তর দিন।",
  "g4": "2026-04-06 তারিখে ছাড়া {RTM} থেকে {NDLS} পর্যন্ত একটি সরাসরি ট্রেন "
        "খুঁজুন। ওই দিন কোনো ট্রেন না চললে N/A উত্তর দিন।",
  "g5": "2026-04-08 তারিখে {GHY} থেকে {HWH} পর্যন্ত কোন ট্রেন চলে? কোনোটি সেই "
        "রুটে না চললে N/A উত্তর দিন।",
  "g6": "বুকিং ফর্মে একটি তৎকাল কোটার বিকল্প আছে। রেলসেতু সাইটের কোথাও "
        "{cur_w}য় কত অতিরিক্ত তৎকাল সারচার্জ উল্লেখ করে? কোনো সারচার্জের অঙ্ক "
        "উল্লেখ না থাকলে N/A উত্তর দিন।",
  "h1": "{CNB}-এ কতটি ভিন্ন ট্রেন থামে (যেকোনো দিকে)? সংখ্যাটি উত্তর দিন।",
  "h2": "এই সাইটে কতটি ট্রেন প্রতিদিন (সাত দিনই) চলে? সংখ্যাটি উত্তর দিন।",
  "h3": "PNR 6207890123-এর PNR অবস্থা দেখুন এবং অবস্থার কোড উত্তর দিন।",
  "h4": "ট্রেন 12615 {t12615} {NGP}-এ কত মিনিট থামে? মিনিটের সংখ্যা উত্তর "
        "দিন।",
  "h5": "কোন ট্রেনগুলো 20:00 বা তার পরে উৎস স্টেশন থেকে ছাড়ে? দুটি ট্রেন "
        "নম্বরই উত্তর দিন।",
  "h6": "এই সাইটে সবচেয়ে ছোট মোট রুটের দুটি ট্রেন খুঁজুন এবং সেই দুটি রুটের "
        "সম্মিলিত দৈর্ঘ্য কিমি-তে উত্তর দিন।",
  "h7": "আপনার কতটি বুকিং (যেকোনো অবস্থার) 2026-04-09-এর আগের তারিখের যাত্রার? "
        "সংখ্যাটি উত্তর দিন।",
  "h8": "আপনার কোন বুকিংয়ের ভাড়া সবচেয়ে বেশি? তার PNR ও {cur_w}য় ভাড়া উত্তর "
        "দিন।",
  "h9": "ট্রেন 12559 {t12559} {BSB}-এ কখন পৌঁছায়, এবং তার যাত্রার কোন দিনে (1 "
        "বা 2)? সময় ও দিনের সংখ্যা উত্তর দিন।",
  "h10": "ট্রেন 12659 {t12659}-এ {AII} থেকে {ABR} কত কিমি? কিমি-তে দূরত্ব উত্তর "
         "দিন।",
  "h11": "ট্রেন 12615 {t12615}-এ ট্রেনটি {BPL} ও {NGP}-এর মধ্যে কত কিমি "
         "অতিক্রম করে? কিমি-তে দূরত্ব উত্তর দিন।",
  "h12": "ট্রেন 12723 {t12723} {SC} থেকে {PUNE} পর্যন্ত কত সময় নেয়? যেভাবে "
         "দেখানো আছে সেই সময়কাল উত্তর দিন।",
  "h13": "ট্রেন 12301 {t12301}-এ 3A-র জন্য দেখানো অপেক্ষমাণ তালিকার নম্বর কত? "
         "সংখ্যাটি উত্তর দিন।",
  "h14": "গ্রাহক সহায়তায় আপনার নাম ({c_name}) ও ইমেইল ({c_email}), হুবহু বিষয় "
         "'{anomaly_subject}' এবং হুবহু বার্তা '{anomaly_msg}' দিয়ে একটি বার্তা "
         "পাঠান",
  "h15": "আপনার বুকিং ইতিহাসে কতটি বুকিং (যেকোনো অবস্থার) তালিকাভুক্ত? সংখ্যাটি "
         "উত্তর দিন।",
  "h16": "2026-04-06 তারিখে ট্রেন 12301 {t12301}-এ {NDLS} থেকে {HWH} পর্যন্ত "
         "কতটি 2A আসন খালি আছে? সংখ্যাটি উত্তর দিন।",
  "h17": "{BCT} থেকে {BPL} পর্যন্ত চলা ট্রেনটি খুঁজুন এবং সেই যাত্রার SL "
         "(স্লিপার) ভাড়া {cur_w}য় উত্তর দিন।",
 },
 "hi": {
  "k1": "ट्रेन 12903 {t12903} को {NDLS} से {BCT} तक कितना समय लगता है? जैसा "
        "दिखाया गया है वही अवधि उत्तर दें।",
  "k2": "2026-04-06 को {NDLS} से {CNB} की यात्रा का सबसे कम 3A किराया खोजें "
        "और {cur_w} में राशि उत्तर दें।",
  "k3": "PNR 6201234567 की PNR स्थिति देखें और स्थिति कोड उत्तर दें।",
  "k4": "PNR 6203456789 देखें और यात्री का नाम उत्तर दें।",
  "k5": "2026-04-06 को ट्रेन 12301 {t12301} में {NDLS} से {HWH} तक यात्री "
        "{kabir}, आयु 41, पुरुष, ऊपरी (Upper) बर्थ का एक 2A टिकट बुक करें।",
  "k6": "2026-04-07 को ट्रेन 12417 {t12417} में {NDLS} से {LKO} तक यात्री "
        "{sunita}, आयु 55, महिला, कोई बर्थ वरीयता नहीं — एक CC (चेयर कार) "
        "टिकट बुक करें।",
  "k7": "2026-04-08 को ट्रेन 12841 {t12841} में {HWH} से {MAS} तक यात्री "
        "{farhan}, आयु 23, पुरुष, साइड ऊपरी (Side Upper) बर्थ का एक SL "
        "(स्लीपर) टिकट बुक करें।",
  "k8": "PNR 6203456789 वाली बुकिंग रद्द करें।",
  "k9": "ट्रेन 12622 {t12622} में {HWH} से {GHY} तक 2A टिकट 3A टिकट से कितना "
        "महँगा है? {cur_w} में अंतर उत्तर दें।",
  "k10": "2026-04-07 को प्रस्थान करने वाली {SC} से {PUNE} की सीधी ट्रेन खोजें। "
         "उस दिन कोई ट्रेन न चले तो N/A उत्तर दें।",
  "k11": "PNR 6299999999 की PNR स्थिति देखें। कोई बुकिंग न हो तो N/A उत्तर "
         "दें।",
  "k12": "ग्राहक सहायता को '{c_subject}' विषय से एक संदेश भेजें, जिसमें बताएँ "
         "कि आपका रिफ़ंड नहीं आया है। अपना नाम और ईमेल ({c_name}, {c_email}) शामिल करें।",
  "k13": "अपनी प्रोफ़ाइल में मोबाइल नंबर बदलकर 9876501234 करें।",
  "k14": "रिफ़ंड नियमों के अनुसार, प्रस्थान से 48 घंटे से अधिक पहले रद्द किए गए "
         "पुष्ट AC श्रेणी टिकट पर {cur_w} में निश्चित रद्दीकरण शुल्क कितना है?",
  "k15": "क्या 2026-04-09 को {JP} से {LKO} की कोई सीधी ट्रेन है? कोई न हो तो "
         "N/A उत्तर दें।",
  "a1": "इस साइट की सभी ट्रेनों में कौन सी एक ट्रेन उद्गम से गंतव्य तक सबसे "
        "लंबी कुल दूरी तय करती है? ट्रेन नंबर और किमी में दूरी उत्तर दें।",
  "a2": "कौन सी ट्रेन कुल सबसे अधिक निर्धारित स्टॉप करती है (उद्गम और गंतव्य "
        "सहित)? ट्रेन नंबर और स्टॉप की संख्या उत्तर दें।",
  "a3": "प्रतिदिन चलने वाली ट्रेनों में कौन सी अपने गंतव्य पर दिन में सबसे देर "
        "से (घड़ी के समय से) पहुँचती है? ट्रेन नंबर और आगमन समय उत्तर दें।",
  "a4": "इस साइट पर किस ट्रेन का किसी मध्यवर्ती स्टेशन पर सबसे लंबा ठहराव है? "
        "ट्रेन नंबर और मिनटों में ठहराव की अवधि उत्तर दें।",
  "a5": "SL (स्लीपर) वाली सभी ट्रेनों में किसका पूरे मार्ग का SL किराया सबसे "
        "सस्ता है? ट्रेन नंबर और {cur_w} में किराया उत्तर दें।",
  "a6": "1A (AC प्रथम श्रेणी) वाली सभी ट्रेनों में किसका पूरे मार्ग का 1A "
        "किराया सबसे महँगा है? ट्रेन नंबर और {cur_w} में किराया उत्तर दें।",
  "a7": "इस साइट पर ठीक दो स्टेशनों पर ठीक 3-3 ट्रेनें रुकती हैं। कौन से दो? "
        "दोनों स्टेशनों के नाम उत्तर दें।",
  "a8": "प्रतिदिन चलने वाली ट्रेनों में कौन सी सुबह सबसे पहले अपने उद्गम से "
        "चलती है? ट्रेन नंबर और प्रस्थान समय उत्तर दें।",
  "b1": "2026-04-07 को प्रस्थान करके कौन सी ट्रेन आपको {PNBE} से {HWH} ले जा "
        "सकती है? उसका ट्रेन नंबर उत्तर दें (कोई न चले तो N/A)।",
  "b2": "2026-04-08 को प्रस्थान करने वाली {NJP} से {GHY} की सीधी ट्रेन खोजें। "
        "उसका ट्रेन नंबर उत्तर दें (कोई न चले तो N/A)।",
  "b3": "2026-04-06 से 2026-04-12 तक की हर तिथि पर विचार करते हुए, किस तिथि "
        "को {NDLS} से {CNB} तक सबसे अधिक सीधी ट्रेनें चलती हैं? तिथि "
        "(YYYY-MM-DD) और उस दिन कितनी ट्रेनें चलती हैं, उत्तर दें।",
  "b4": "सप्ताह के कितने दिन ट्रेन 12301 {t12301} {PNBE} पर रुकती है? संख्या "
        "उत्तर दें।",
  "c1": "आपकी बुकिंग 6203456789 एक पुष्ट AC श्रेणी टिकट है। यदि आप इसे आज "
        "(प्रस्थान से 48 घंटे से अधिक पहले) रद्द करें, तो प्रकाशित रिफ़ंड "
        "नियमों के अनुसार {cur_w} में कितना रिफ़ंड देय होगा? राशि उत्तर दें।",
  "c2": "आपकी बुकिंग 6202345678 प्रतीक्षा सूची में है। रिफ़ंड नियमों के "
        "अनुसार, प्रस्थान से पहले रद्द करने पर आपको {cur_w} में कितना रिफ़ंड "
        "मिलेगा? राशि उत्तर दें।",
  "c3": "ट्रेन 12615 {t12615} के पूरे मार्ग ({NDLS} से {MAS}) का एक पुष्ट 3A "
        "टिकट प्रस्थान से 24 घंटे पहले रद्द किया जाता है। रिफ़ंड नियमों के "
        "अनुसार {cur_w} में कितना रिफ़ंड देय है? राशि उत्तर दें।",
  "c4": "यदि आपकी पुष्ट बुकिंग {pnr} (एक AC श्रेणी टिकट) प्रस्थान से 6 घंटे "
        "पहले रद्द की जाए, तो नियम {cur_w} में कितने रिफ़ंड की अनुमति देंगे? "
        "राशि उत्तर दें।",
  "c5": "ट्रेन 12559 {t12559} में {NDLS} से {BSB} तक दो 2A टिकटों की कुल "
        "लागत कितनी होगी? {cur_w} में कुल उत्तर दें।",
  "c6": "आपकी सभी पुष्ट (CNF) बुकिंग का संयुक्त किराया {cur_w} में कितना है? "
        "कुल उत्तर दें।",
  "c7": "ट्रेन 12615 {t12615} में {AGC} से {SC} की यात्रा के लिए 3A, SL से "
        "कितना महँगा है? {cur_w} में अंतर उत्तर दें।",
  "c8": "{NDLS} से {BSB} तक सीधी ट्रेन 12559 में SL से यात्रा की तुलना दो SL "
        "चरणों में बाँटी यात्रा से करें: ट्रेन 12301 में {NDLS} से {CNB}, फिर "
        "ट्रेन 12559 में {CNB} से {BSB}। दो-चरण विकल्प की तुलना में सीधा टिकट "
        "कितने {cur_w} बचाता है?",
  "c9": "ट्रेन 12904 {t12904} में सभी श्रेणियाँ मिलाकर कुल कितनी सीटें उपलब्ध "
        "हैं? संख्या उत्तर दें।",
  "c10": "आपकी दो बुकिंग यात्री {anita} और {meera} के लिए हैं। किसके टिकट का "
         "किराया अधिक है, और कितने {cur_w} अधिक? यात्री का नाम और अंतर उत्तर "
         "दें।",
  "d1": "ट्रेन 12302 {t12302} के पूरे मार्ग पर {t1000} {cur_w} से अधिक कीमत "
        "वाली सबसे सस्ती श्रेणी कौन सी है? श्रेणी कोड और उसका किराया उत्तर "
        "दें।",
  "d2": "ट्रेन 12659 {t12659} में {JP} से {ADI} तक {t500} {cur_w} से अधिक न "
        "होने वाली सबसे महँगी श्रेणी कौन सी है? श्रेणी कोड और उसका किराया "
        "उत्तर दें।",
  "d3": "{NDLS} से {CNB} खंड पर चलने वाली सभी ट्रेनों में कौन सी उस खंड का "
        "सबसे सस्ता SL (स्लीपर) किराया देती है? ट्रेन नंबर और {cur_w} में "
        "किराया उत्तर दें।",
  "d4": "कौन सा महँगा है: ट्रेन 12622 {t12622} के पूरे मार्ग का 1A टिकट, या "
        "ट्रेन 12615 {t12615} में {NDLS} से {BPL} तक का 2A टिकट? जीतने वाला "
        "ट्रेन नंबर और वह किराया {cur_w} में उत्तर दें।",
  "d5": "{RTM} पर रुकने वाली सभी ट्रेनों में कौन सी दिन में सबसे पहले (घड़ी "
        "के समय से) वहाँ से चलती है? ट्रेन नंबर और वहाँ से उसका प्रस्थान समय "
        "उत्तर दें।",
  "e1": "आपकी एक बुकिंग प्रतीक्षा सूची (WL) में है। वह बुकिंग रद्द करें — और "
        "केवल वही।",
  "e2": "2026-04-10 या उसके बाद की तिथि की यात्राओं की अपनी सभी बुकिंग जो "
        "पहले से रद्द नहीं हैं, रद्द करें। हर पहले की यात्रा अछूती रहने दें।",
  "e3": "अपनी प्रोफ़ाइल में ईमेल पता priya.s@newmail.in और मोबाइल नंबर "
        "9812399999 करें (दोनों, एक ही अद्यतन में)।",
  "e4": "PNR 6204567890 देखकर यात्री का नाम पता करें, फिर ग्राहक सहायता को अपने "
        "नाम ({c_name}), अपने ईमेल ({c_email}), विषय '{pnr_query}' और ठीक इस "
        "संदेश के साथ एक संदेश भेजें: '{refund_status_for}<यात्री का नाम>' — "
        "<यात्री का नाम> की जगह आपको मिला नाम रखते हुए।",
  "e5": "PNR 6201234567 देखें, फिर 2026-04-06 को ट्रेन 12049 {t12049} में "
        "{NDLS} से {AGC} तक उस बुकिंग के उसी यात्री (वही नाम और आयु) के लिए, "
        "पुरुष, कोई बर्थ वरीयता नहीं — एक CC टिकट बुक करें।",
  "e6": "2026-04-06 को ट्रेन 12138 {t12138} में {BCT} से {BPL} तक यात्री "
        "{nisha}, आयु 30, महिला, निचली (Lower) बर्थ का एक SL टिकट बुक करें — "
        "और फिर उस नई बुकिंग को रद्द करें।",
  "f1": "2026-04-06 को {NDLS} से {CNB} तक सबसे पहले प्रस्थान करने वाली ट्रेन "
        "खोजें और उसमें यात्री {anaya}, आयु 27, महिला, कोई बर्थ वरीयता नहीं — "
        "एक CC टिकट बुक करें।",
  "f2": "2026-04-06 को {NDLS} से {AGC} तक जितना सस्ता हो सके यात्रा करें: उस "
        "दिन चलने वाली हर ट्रेन की हर श्रेणी की तुलना करें, और यात्री {ritu}, "
        "आयु 24, महिला, कोई बर्थ वरीयता नहीं — के लिए एकमात्र सबसे सस्ता "
        "विकल्प बुक करें।",
  "f3": "2026-04-08 को {NDLS} से {CNB} तक सबसे देर से प्रस्थान करने वाली ट्रेन "
        "में यात्री {mohan}, आयु 52, पुरुष, निचली (Lower) बर्थ का एक 3A टिकट "
        "बुक करें।",
  "f4": "2026-04-09 को {NDLS} से {HWH} तक यात्री {sara}, आयु 33, महिला, ऊपरी "
        "(Upper) बर्थ का एक 2A टिकट बुक करें। उस दिन कोई ट्रेन न चले तो वही "
        "यात्रा 2026-04-10 को बुक करें।",
  "g1": "ट्रेन 12615 {t12615} के पूरे मार्ग का 1A (AC प्रथम श्रेणी) किराया "
        "कितना है? इस ट्रेन में वह श्रेणी न हो तो N/A उत्तर दें।",
  "g2": "2026-04-08 को ट्रेन 12904 {t12904} में {BCT} से {NDLS} तक यात्री "
        "{ravi}, आयु 45, पुरुष के लिए एक 2A टिकट बुक करें। यदि ट्रेन उस दिन "
        "नहीं चलती, तो कुछ भी बुक न करें और N/A उत्तर दें।",
  "g3": "2026-04-07 को {LKO} से {AGC} की सीधी ट्रेन खोजें। इस मार्ग पर कोई "
        "सीधी ट्रेन न हो तो N/A उत्तर दें।",
  "g4": "2026-04-06 को प्रस्थान करने वाली {RTM} से {NDLS} की सीधी ट्रेन खोजें। "
        "उस दिन कोई ट्रेन न चले तो N/A उत्तर दें।",
  "g5": "2026-04-08 को {GHY} से {HWH} कौन सी ट्रेन चलती है? उस मार्ग पर कोई न "
        "हो तो N/A उत्तर दें।",
  "g6": "बुकिंग फ़ॉर्म में तत्काल कोटा का विकल्प है। रेलसेतु साइट पर कहीं भी "
        "{cur_w} में कितना अतिरिक्त तत्काल अधिभार बताया गया है? कोई अधिभार "
        "राशि न बताई गई हो तो N/A उत्तर दें।",
  "h1": "{CNB} पर कितनी अलग-अलग ट्रेनें रुकती हैं (किसी भी दिशा में)? संख्या "
        "उत्तर दें।",
  "h2": "इस साइट पर कितनी ट्रेनें प्रतिदिन (सातों दिन) चलती हैं? संख्या उत्तर "
        "दें।",
  "h3": "PNR 6207890123 की PNR स्थिति देखें और स्थिति कोड उत्तर दें।",
  "h4": "ट्रेन 12615 {t12615} {NGP} पर कितने मिनट रुकती है? मिनटों की संख्या "
        "उत्तर दें।",
  "h5": "कौन सी ट्रेनें अपने उद्गम स्टेशन से 20:00 या उसके बाद चलती हैं? दोनों "
        "ट्रेन नंबर उत्तर दें।",
  "h6": "इस साइट पर सबसे छोटे कुल मार्ग वाली दो ट्रेनें खोजें और उन दो मार्गों "
        "की संयुक्त लंबाई किमी में उत्तर दें।",
  "h7": "आपकी कितनी बुकिंग (किसी भी स्थिति की) 2026-04-09 से पहले की यात्राओं "
        "के लिए हैं? संख्या उत्तर दें।",
  "h8": "आपकी किस बुकिंग का किराया सबसे अधिक है? उसका PNR और {cur_w} में "
        "किराया उत्तर दें।",
  "h9": "ट्रेन 12559 {t12559} {BSB} पर किस समय पहुँचती है, और अपने सफ़र के किस "
        "दिन (1 या 2)? समय और दिन की संख्या उत्तर दें।",
  "h10": "ट्रेन 12659 {t12659} में {AII} से {ABR} कितने किमी है? किमी में दूरी "
         "उत्तर दें।",
  "h11": "ट्रेन 12615 {t12615} में ट्रेन {BPL} और {NGP} के बीच कितने किमी तय "
         "करती है? किमी में दूरी उत्तर दें।",
  "h12": "ट्रेन 12723 {t12723} को {SC} से {PUNE} तक कितना समय लगता है? जैसा "
         "दिखाया गया है वही अवधि उत्तर दें।",
  "h13": "ट्रेन 12301 {t12301} में 3A के लिए दिखाया गया प्रतीक्षा सूची नंबर "
         "क्या है? संख्या उत्तर दें।",
  "h14": "ग्राहक सहायता को अपने नाम ({c_name}) और ईमेल ({c_email}), ठीक "
         "'{anomaly_subject}' विषय और ठीक '{anomaly_msg}' संदेश के साथ एक "
         "संदेश भेजें",
  "h15": "आपके बुकिंग इतिहास में कितनी बुकिंग (किसी भी स्थिति की) सूचीबद्ध "
         "हैं? संख्या उत्तर दें।",
  "h16": "2026-04-06 को ट्रेन 12301 {t12301} में {NDLS} से {HWH} तक कितनी 2A "
         "सीटें उपलब्ध हैं? संख्या उत्तर दें।",
  "h17": "{BCT} से {BPL} चलने वाली ट्रेन खोजें और उस यात्रा का उसका SL "
         "(स्लीपर) किराया {cur_w} में उत्तर दें।",
 },
 "ur": {
  "k1": "ٹرین 12903 {t12903} کو {NDLS} سے {BCT} تک کتنا وقت لگتا ہے؟ جیسا "
        "دکھایا گیا ہے ویسا دورانیہ جواب دیں۔",
  "k2": "2026-04-06 کو {NDLS} سے {CNB} کے سفر کا سب سے کم 3A کرایہ تلاش کریں "
        "اور {cur_w} میں رقم جواب دیں۔",
  "k3": "PNR 6201234567 کی PNR حیثیت دیکھیں اور حیثیت کا کوڈ جواب دیں۔",
  "k4": "PNR 6203456789 دیکھیں اور مسافر کا نام جواب دیں۔",
  "k5": "2026-04-06 کو ٹرین 12301 {t12301} میں {NDLS} سے {HWH} تک مسافر "
        "{kabir}، عمر 41، مرد، اوپری (Upper) برتھ کا ایک 2A ٹکٹ بک کریں۔",
  "k6": "2026-04-07 کو ٹرین 12417 {t12417} میں {NDLS} سے {LKO} تک مسافر "
        "{sunita}، عمر 55، عورت، برتھ کی کوئی ترجیح نہیں — ایک CC (چیئر کار) "
        "ٹکٹ بک کریں۔",
  "k7": "2026-04-08 کو ٹرین 12841 {t12841} میں {HWH} سے {MAS} تک مسافر "
        "{farhan}، عمر 23، مرد، سائیڈ اوپری (Side Upper) برتھ کا ایک SL "
        "(سلیپر) ٹکٹ بک کریں۔",
  "k8": "PNR 6203456789 والی بکنگ منسوخ کریں۔",
  "k9": "ٹرین 12622 {t12622} میں {HWH} سے {GHY} تک 2A ٹکٹ 3A ٹکٹ سے کتنا "
        "مہنگا ہے؟ {cur_w} میں فرق جواب دیں۔",
  "k10": "2026-04-07 کو روانہ ہونے والی {SC} سے {PUNE} کی براہِ راست ٹرین "
         "تلاش کریں۔ اس دن کوئی ٹرین نہ چلے تو N/A جواب دیں۔",
  "k11": "PNR 6299999999 کی PNR حیثیت دیکھیں۔ کوئی بکنگ نہ ہو تو N/A جواب "
         "دیں۔",
  "k12": "کسٹمر سپورٹ کو '{c_subject}' موضوع کے ساتھ ایک پیغام بھیجیں جس میں "
         "بتائیں کہ آپ کا ریفنڈ نہیں آیا۔ اپنا نام اور ای میل ({c_name}، {c_email}) شامل کریں۔",
  "k13": "اپنی پروفائل میں موبائل نمبر بدل کر 9876501234 کریں۔",
  "k14": "ریفنڈ قواعد کے مطابق، روانگی سے 48 گھنٹے سے زیادہ پہلے منسوخ کیے "
         "گئے تصدیق شدہ AC کلاس ٹکٹ پر {cur_w} میں مقررہ منسوخی چارج کتنا "
         "ہے؟",
  "k15": "کیا 2026-04-09 کو {JP} سے {LKO} کی کوئی براہِ راست ٹرین ہے؟ کوئی نہ "
         "ہو تو N/A جواب دیں۔",
  "a1": "اس سائٹ کی تمام ٹرینوں میں کون سی ایک ٹرین مبدا سے منزل تک سب سے "
        "لمبا کل فاصلہ طے کرتی ہے؟ ٹرین نمبر اور کلومیٹر میں فاصلہ جواب دیں۔",
  "a2": "کون سی ٹرین کل سب سے زیادہ طے شدہ اسٹاپ کرتی ہے (مبدا اور منزل "
        "سمیت)؟ ٹرین نمبر اور اسٹاپوں کی تعداد جواب دیں۔",
  "a3": "روزانہ چلنے والی ٹرینوں میں کون سی اپنی منزل پر دن میں سب سے دیر "
        "سے (گھڑی کے وقت سے) پہنچتی ہے؟ ٹرین نمبر اور آمد کا وقت جواب دیں۔",
  "a4": "اس سائٹ پر کس ٹرین کا کسی درمیانی اسٹیشن پر سب سے لمبا ٹھہراؤ ہے؟ "
        "ٹرین نمبر اور منٹوں میں ٹھہراؤ کا دورانیہ جواب دیں۔",
  "a5": "SL (سلیپر) والی تمام ٹرینوں میں کس کا پورے روٹ کا SL کرایہ سب سے "
        "سستا ہے؟ ٹرین نمبر اور {cur_w} میں کرایہ جواب دیں۔",
  "a6": "1A (AC فرسٹ کلاس) والی تمام ٹرینوں میں کس کا پورے روٹ کا 1A کرایہ "
        "سب سے مہنگا ہے؟ ٹرین نمبر اور {cur_w} میں کرایہ جواب دیں۔",
  "a7": "اس سائٹ پر بالکل دو اسٹیشنوں پر بالکل 3-3 ٹرینیں رکتی ہیں۔ کون سے "
        "دو؟ دونوں اسٹیشنوں کے نام جواب دیں۔",
  "a8": "روزانہ چلنے والی ٹرینوں میں کون سی صبح سب سے پہلے اپنے مبدا سے چلتی "
        "ہے؟ ٹرین نمبر اور روانگی کا وقت جواب دیں۔",
  "b1": "2026-04-07 کو روانہ ہو کر کون سی ٹرین آپ کو {PNBE} سے {HWH} لے جا "
        "سکتی ہے؟ اس کا ٹرین نمبر جواب دیں (کوئی نہ چلے تو N/A)۔",
  "b2": "2026-04-08 کو روانہ ہونے والی {NJP} سے {GHY} کی براہِ راست ٹرین "
        "تلاش کریں۔ اس کا ٹرین نمبر جواب دیں (کوئی نہ چلے تو N/A)۔",
  "b3": "2026-04-06 سے 2026-04-12 تک ہر تاریخ پر غور کرتے ہوئے، کس تاریخ کو "
        "{NDLS} سے {CNB} تک سب سے زیادہ براہِ راست ٹرینیں چلتی ہیں؟ تاریخ "
        "(YYYY-MM-DD) اور اس دن کتنی ٹرینیں چلتی ہیں، جواب دیں۔",
  "b4": "ہفتے کے کتنے دن ٹرین 12301 {t12301} {PNBE} پر رکتی ہے؟ تعداد جواب "
        "دیں۔",
  "c1": "آپ کی بکنگ 6203456789 ایک تصدیق شدہ AC کلاس ٹکٹ ہے۔ اگر آپ اسے آج "
        "(روانگی سے 48 گھنٹے سے زیادہ پہلے) منسوخ کریں تو شائع شدہ ریفنڈ "
        "قواعد کے مطابق {cur_w} میں کتنا ریفنڈ واجب ہوگا؟ رقم جواب دیں۔",
  "c2": "آپ کی بکنگ 6202345678 ویٹنگ لسٹ میں ہے۔ ریفنڈ قواعد کے مطابق، "
        "روانگی سے پہلے منسوخ کرنے پر آپ کو {cur_w} میں کتنا ریفنڈ ملے گا؟ "
        "رقم جواب دیں۔",
  "c3": "ٹرین 12615 {t12615} کے پورے روٹ ({NDLS} سے {MAS}) کا ایک تصدیق شدہ 3A "
        "ٹکٹ روانگی سے 24 گھنٹے پہلے منسوخ کیا جاتا ہے۔ ریفنڈ قواعد کے مطابق "
        "{cur_w} میں کتنا ریفنڈ واجب ہے؟ رقم جواب دیں۔",
  "c4": "اگر آپ کی تصدیق شدہ بکنگ {pnr} (ایک AC کلاس ٹکٹ) روانگی سے 6 گھنٹے "
        "پہلے منسوخ کی جائے تو قواعد {cur_w} میں کتنے ریفنڈ کی اجازت دیں گے؟ "
        "رقم جواب دیں۔",
  "c5": "ٹرین 12559 {t12559} میں {NDLS} سے {BSB} تک دو 2A ٹکٹوں کی کل قیمت "
        "کتنی ہوگی؟ {cur_w} میں کل جواب دیں۔",
  "c6": "آپ کی تمام تصدیق شدہ (CNF) بکنگز کا مجموعی کرایہ {cur_w} میں کتنا "
        "ہے؟ کل جواب دیں۔",
  "c7": "ٹرین 12615 {t12615} میں {AGC} سے {SC} کے سفر کے لیے 3A، SL سے کتنا "
        "مہنگا ہے؟ {cur_w} میں فرق جواب دیں۔",
  "c8": "{NDLS} سے {BSB} تک براہِ راست ٹرین 12559 میں SL سے سفر کا موازنہ دو "
        "SL مراحل میں بٹے سفر سے کریں: ٹرین 12301 میں {NDLS} سے {CNB}، پھر "
        "ٹرین 12559 میں {CNB} سے {BSB}۔ دو مرحلہ آپشن کے مقابلے میں براہِ راست "
        "ٹکٹ کتنے {cur_w} بچاتا ہے؟",
  "c9": "ٹرین 12904 {t12904} میں تمام کلاسیں ملا کر کل کتنی نشستیں دستیاب "
        "ہیں؟ تعداد جواب دیں۔",
  "c10": "آپ کی دو بکنگز مسافر {anita} اور {meera} کے لیے ہیں۔ کس کے ٹکٹ کا "
         "کرایہ زیادہ ہے، اور کتنے {cur_w} زیادہ؟ مسافر کا نام اور فرق جواب "
         "دیں۔",
  "d1": "ٹرین 12302 {t12302} کے پورے روٹ پر {t1000} {cur_w} سے زیادہ قیمت "
        "والی سب سے سستی کلاس کون سی ہے؟ کلاس کوڈ اور اس کا کرایہ جواب دیں۔",
  "d2": "ٹرین 12659 {t12659} میں {JP} سے {ADI} تک {t500} {cur_w} سے زیادہ نہ "
        "ہونے والی سب سے مہنگی کلاس کون سی ہے؟ کلاس کوڈ اور اس کا کرایہ جواب "
        "دیں۔",
  "d3": "{NDLS} سے {CNB} حصے پر چلنے والی تمام ٹرینوں میں کون سی اس حصے کا "
        "سب سے سستا SL (سلیپر) کرایہ دیتی ہے؟ ٹرین نمبر اور {cur_w} میں "
        "کرایہ جواب دیں۔",
  "d4": "کون سا مہنگا ہے: ٹرین 12622 {t12622} کے پورے روٹ کا 1A ٹکٹ، یا ٹرین "
        "12615 {t12615} میں {NDLS} سے {BPL} تک 2A ٹکٹ؟ جیتنے والا ٹرین نمبر "
        "اور وہ کرایہ {cur_w} میں جواب دیں۔",
  "d5": "{RTM} پر رکنے والی تمام ٹرینوں میں کون سی دن میں سب سے پہلے (گھڑی "
        "کے وقت سے) وہاں سے چلتی ہے؟ ٹرین نمبر اور وہاں سے اس کی روانگی کا "
        "وقت جواب دیں۔",
  "e1": "آپ کی ایک بکنگ ویٹنگ لسٹ (WL) میں ہے۔ وہ بکنگ منسوخ کریں — اور صرف "
        "وہی۔",
  "e2": "2026-04-10 یا اس کے بعد کی تاریخ کے سفروں کی اپنی تمام بکنگز جو "
        "پہلے سے منسوخ نہیں، منسوخ کریں۔ ہر پہلے کا سفر جوں کا توں رہنے دیں۔",
  "e3": "اپنی پروفائل میں ای میل پتہ priya.s@newmail.in اور موبائل نمبر "
        "9812399999 کریں (دونوں، ایک ہی اپ ڈیٹ میں)۔",
  "e4": "PNR 6204567890 دیکھ کر مسافر کا نام معلوم کریں، پھر کسٹمر سپورٹ کو "
        "اپنے نام ({c_name})، اپنے ای میل ({c_email})، موضوع '{pnr_query}' "
        "اور بالکل اس پیغام کے ساتھ ایک پیغام بھیجیں: '{refund_status_for}"
        "<مسافر کا نام>' — <مسافر کا نام> کی جگہ آپ کو ملا نام رکھتے ہوئے۔",
  "e5": "PNR 6201234567 دیکھیں، پھر 2026-04-06 کو ٹرین 12049 {t12049} میں "
        "{NDLS} سے {AGC} تک اس بکنگ کے اسی مسافر (وہی نام اور عمر) کے لیے، "
        "مرد، برتھ کی کوئی ترجیح نہیں — ایک CC ٹکٹ بک کریں۔",
  "e6": "2026-04-06 کو ٹرین 12138 {t12138} میں {BCT} سے {BPL} تک مسافر "
        "{nisha}، عمر 30، عورت، نچلی (Lower) برتھ کا ایک SL ٹکٹ بک کریں — "
        "اور پھر اس نئی بکنگ کو منسوخ کریں۔",
  "f1": "2026-04-06 کو {NDLS} سے {CNB} تک سب سے پہلے روانہ ہونے والی ٹرین "
        "تلاش کریں اور اس میں مسافر {anaya}، عمر 27، عورت، برتھ کی کوئی "
        "ترجیح نہیں — ایک CC ٹکٹ بک کریں۔",
  "f2": "2026-04-06 کو {NDLS} سے {AGC} تک جتنا سستا ہو سکے سفر کریں: اس دن "
        "چلنے والی ہر ٹرین کی ہر کلاس کا موازنہ کریں، اور مسافر {ritu}، عمر "
        "24، عورت، برتھ کی کوئی ترجیح نہیں — کے لیے واحد سب سے سستا آپشن بک "
        "کریں۔",
  "f3": "2026-04-08 کو {NDLS} سے {CNB} تک سب سے دیر سے روانہ ہونے والی ٹرین "
        "میں مسافر {mohan}، عمر 52، مرد، نچلی (Lower) برتھ کا ایک 3A ٹکٹ بک "
        "کریں۔",
  "f4": "2026-04-09 کو {NDLS} سے {HWH} تک مسافر {sara}، عمر 33، عورت، اوپری "
        "(Upper) برتھ کا ایک 2A ٹکٹ بک کریں۔ اس دن کوئی ٹرین نہ چلے تو وہی "
        "سفر 2026-04-10 کو بک کریں۔",
  "g1": "ٹرین 12615 {t12615} کے پورے روٹ کا 1A (AC فرسٹ کلاس) کرایہ کتنا "
        "ہے؟ اس ٹرین میں وہ کلاس نہ ہو تو N/A جواب دیں۔",
  "g2": "2026-04-08 کو ٹرین 12904 {t12904} میں {BCT} سے {NDLS} تک مسافر "
        "{ravi}، عمر 45، مرد کے لیے ایک 2A ٹکٹ بک کریں۔ اگر ٹرین اس دن نہیں "
        "چلتی تو کچھ بھی بک نہ کریں اور N/A جواب دیں۔",
  "g3": "2026-04-07 کو {LKO} سے {AGC} کی براہِ راست ٹرین تلاش کریں۔ اس روٹ پر "
        "کوئی براہِ راست ٹرین نہ ہو تو N/A جواب دیں۔",
  "g4": "2026-04-06 کو روانہ ہونے والی {RTM} سے {NDLS} کی براہِ راست ٹرین "
        "تلاش کریں۔ اس دن کوئی ٹرین نہ چلے تو N/A جواب دیں۔",
  "g5": "2026-04-08 کو {GHY} سے {HWH} کون سی ٹرین چلتی ہے؟ اس روٹ پر کوئی نہ "
        "ہو تو N/A جواب دیں۔",
  "g6": "بکنگ فارم میں تتکال کوٹے کا آپشن ہے۔ ریل سیتو سائٹ پر کہیں بھی "
        "{cur_w} میں کتنا اضافی تتکال سرچارج بتایا گیا ہے؟ کوئی سرچارج رقم "
        "نہ بتائی گئی ہو تو N/A جواب دیں۔",
  "h1": "{CNB} پر کتنی مختلف ٹرینیں رکتی ہیں (کسی بھی سمت میں)؟ تعداد جواب "
        "دیں۔",
  "h2": "اس سائٹ پر کتنی ٹرینیں روزانہ (ساتوں دن) چلتی ہیں؟ تعداد جواب دیں۔",
  "h3": "PNR 6207890123 کی PNR حیثیت دیکھیں اور حیثیت کا کوڈ جواب دیں۔",
  "h4": "ٹرین 12615 {t12615} {NGP} پر کتنے منٹ رکتی ہے؟ منٹوں کی تعداد جواب "
        "دیں۔",
  "h5": "کون سی ٹرینیں اپنے مبدا اسٹیشن سے 20:00 یا اس کے بعد چلتی ہیں؟ "
        "دونوں ٹرین نمبر جواب دیں۔",
  "h6": "اس سائٹ پر سب سے چھوٹے کل روٹ والی دو ٹرینیں تلاش کریں اور ان دو "
        "روٹوں کی مجموعی لمبائی کلومیٹر میں جواب دیں۔",
  "h7": "آپ کی کتنی بکنگز (کسی بھی حیثیت کی) 2026-04-09 سے پہلے کے سفروں کے "
        "لیے ہیں؟ تعداد جواب دیں۔",
  "h8": "آپ کی کس بکنگ کا کرایہ سب سے زیادہ ہے؟ اس کا PNR اور {cur_w} میں "
        "کرایہ جواب دیں۔",
  "h9": "ٹرین 12559 {t12559} {BSB} پر کس وقت پہنچتی ہے، اور اپنے سفر کے کس دن "
        "(1 یا 2)؟ وقت اور دن کا نمبر جواب دیں۔",
  "h10": "ٹرین 12659 {t12659} میں {AII} سے {ABR} کتنے کلومیٹر ہے؟ کلومیٹر "
         "میں فاصلہ جواب دیں۔",
  "h11": "ٹرین 12615 {t12615} میں ٹرین {BPL} اور {NGP} کے درمیان کتنے کلومیٹر "
         "طے کرتی ہے؟ کلومیٹر میں فاصلہ جواب دیں۔",
  "h12": "ٹرین 12723 {t12723} کو {SC} سے {PUNE} تک کتنا وقت لگتا ہے؟ جیسا "
         "دکھایا گیا ہے ویسا دورانیہ جواب دیں۔",
  "h13": "ٹرین 12301 {t12301} میں 3A کے لیے دکھایا گیا ویٹنگ لسٹ نمبر کیا ہے؟ "
         "تعداد جواب دیں۔",
  "h14": "کسٹمر سپورٹ کو اپنے نام ({c_name}) اور ای میل ({c_email})، بالکل "
         "'{anomaly_subject}' موضوع اور بالکل '{anomaly_msg}' پیغام کے ساتھ "
         "ایک پیغام بھیجیں",
  "h15": "آپ کی بکنگ ہسٹری میں کتنی بکنگز (کسی بھی حیثیت کی) درج ہیں؟ تعداد "
         "جواب دیں۔",
  "h16": "2026-04-06 کو ٹرین 12301 {t12301} میں {NDLS} سے {HWH} تک کتنی 2A "
         "نشستیں دستیاب ہیں؟ تعداد جواب دیں۔",
  "h17": "{BCT} سے {BPL} چلنے والی ٹرین تلاش کریں اور اس سفر کا اس کا SL "
         "(سلیپر) کرایہ {cur_w} میں جواب دیں۔",
 },
 "am": {
  "k1": "ባቡር 12903 {t12903} ከ{NDLS} ወደ {BCT} ምን ያህል ጊዜ ይወስዳል? እንደታየው "
        "ቆይታውን ይመልሱ።",
  "k2": "በ2026-04-06 ከ{NDLS} ወደ {CNB} ለሚደረግ ጉዞ ዝቅተኛውን የ3A ዋጋ ያግኙና "
        "መጠኑን በ{cur_w} ይመልሱ።",
  "k3": "የPNR 6201234567 የPNR ሁኔታ ይመልከቱና የሁኔታውን ኮድ ይመልሱ።",
  "k4": "PNR 6203456789ን ተመልክተው የተሳፋሪውን ስም ይመልሱ።",
  "k5": "በ2026-04-06 በባቡር 12301 {t12301} ከ{NDLS} ወደ {HWH} ለተሳፋሪ {kabir}፣ "
        "ዕድሜ 41፣ ወንድ፣ የላይ (Upper) መኝታ አንድ የ2A ትኬት ያስይዙ።",
  "k6": "በ2026-04-07 በባቡር 12417 {t12417} ከ{NDLS} ወደ {LKO} ለተሳፋሪ {sunita}፣ "
        "ዕድሜ 55፣ ሴት፣ የመኝታ ምርጫ የሌላት አንድ የCC (ወንበር መኪና) ትኬት ያስይዙ።",
  "k7": "በ2026-04-08 በባቡር 12841 {t12841} ከ{HWH} ወደ {MAS} ለተሳፋሪ {farhan}፣ "
        "ዕድሜ 23፣ ወንድ፣ የጎን ላይ (Side Upper) መኝታ አንድ የSL (ስሊፐር) ትኬት "
        "ያስይዙ።",
  "k8": "PNR 6203456789 ያለውን ማስያዣ ይሰርዙ።",
  "k9": "በባቡር 12622 {t12622} ከ{HWH} ወደ {GHY} የ2A ትኬት ከ3A ትኬት በምን ያህል "
        "ይበልጣል? ልዩነቱን በ{cur_w} ይመልሱ።",
  "k10": "በ2026-04-07 የሚነሳ ከ{SC} ወደ {PUNE} ቀጥተኛ ባቡር ያግኙ። በዚያ ቀን ባቡር "
         "ከሌለ N/A ብለው ይመልሱ።",
  "k11": "የPNR 6299999999 የPNR ሁኔታ ይመልከቱ። ማስያዣ ከሌለ N/A ብለው ይመልሱ።",
  "k12": "ተመላሽዎ እንዳልደረሰ የሚገልጽ መልእክት በርዕስ '{c_subject}' ለደንበኞች ድጋፍ "
         "ይላኩ። ስምዎንና ኢሜይልዎን ({c_name}፣ {c_email}) ያካትቱ።",
  "k13": "በመገለጫዎ ውስጥ የሞባይል ቁጥሩን ወደ 9876501234 ያዘምኑ።",
  "k14": "በተመላሽ ደንቦች መሠረት፣ ከመነሻ ከ48 ሰዓት በላይ ቀደም ብሎ ለተሰረዘ የተረጋገጠ "
         "የAC ክፍል ትኬት ቋሚ የስረዛ ክፍያ በ{cur_w} ስንት ነው?",
  "k15": "በ2026-04-09 ከ{JP} ወደ {LKO} ቀጥተኛ ባቡር አለ? ከሌለ N/A ብለው ይመልሱ።",
  "a1": "በዚህ ጣቢያ ካሉት ሁሉም ባቡሮች መካከል የትኛው አንድ ባቡር ከመነሻው እስከ "
        "መድረሻው ረጅሙን ጠቅላላ ርቀት ይሸፍናል? የባቡር ቁጥሩንና ርቀቱን በኪሜ ይመልሱ።",
  "a2": "የትኛው ባቡር በጠቅላላ ብዙ የተያዙ ማቆሚያዎች አሉት (መነሻውንና መድረሻውን ጨምሮ)? "
        "የባቡር ቁጥሩንና የማቆሚያዎቹን ብዛት ይመልሱ።",
  "a3": "በየቀኑ ከሚሠሩ ባቡሮች መካከል የትኛው በቀኑ ውስጥ ዘግይቶ (በሰዓት) መድረሻው ላይ "
        "ይደርሳል? የባቡር ቁጥሩንና የመድረሻ ሰዓቱን ይመልሱ።",
  "a4": "በዚህ ጣቢያ የትኛው ባቡር በማንኛውም መካከለኛ ጣቢያ ረጅሙ ቆይታ አለው? የባቡር "
        "ቁጥሩንና የቆይታውን ርዝመት በደቂቃ ይመልሱ።",
  "a5": "SL (ስሊፐር) ካላቸው ሁሉም ባቡሮች መካከል የትኛው ርካሹ የሙሉ መስመር SL ዋጋ "
        "አለው? የባቡር ቁጥሩንና ዋጋውን በ{cur_w} ይመልሱ።",
  "a6": "1A (AC አንደኛ ክፍል) ካላቸው ሁሉም ባቡሮች መካከል የትኛው ውዱ የሙሉ መስመር 1A "
        "ዋጋ አለው? የባቡር ቁጥሩንና ዋጋውን በ{cur_w} ይመልሱ።",
  "a7": "በዚህ ጣቢያ ልክ ሁለት ጣቢያዎች እያንዳንዳቸው በልክ 3 ባቡሮች ይገለገላሉ። የትኞቹ "
        "ሁለት? የሁለቱንም ጣቢያዎች ስም ይመልሱ።",
  "a8": "በየቀኑ ከሚሠሩ ባቡሮች መካከል የትኛው ጠዋት ቀድሞ ከመነሻው ይነሳል? የባቡር "
        "ቁጥሩንና የመነሻ ሰዓቱን ይመልሱ።",
  "b1": "በ2026-04-07 ተነስቶ የትኛው ባቡር ከ{PNBE} ወደ {HWH} ሊወስድዎ ይችላል? የባቡር "
        "ቁጥሩን ይመልሱ (ምንም ካልሠራ N/A)።",
  "b2": "በ2026-04-08 የሚነሳ ከ{NJP} ወደ {GHY} ቀጥተኛ ባቡር ያግኙ። የባቡር ቁጥሩን ይመልሱ "
        "(ምንም ካልሠራ N/A)።",
  "b3": "ከ2026-04-06 እስከ 2026-04-12 ያለውን እያንዳንዱን ቀን በማየት፣ በየትኛው ቀን ከ{NDLS} "
        "ወደ {CNB} ብዙ ቀጥተኛ ባቡሮች ይሠራሉ? ቀኑን (YYYY-MM-DD) እና በዚያ ቀን ስንት "
        "ባቡሮች እንደሚሠሩ ይመልሱ።",
  "b4": "ባቡር 12301 {t12301} በሳምንት ስንት ቀናት {PNBE} ላይ ይቆማል? ቁጥሩን ይመልሱ።",
  "c1": "ማስያዣዎ 6203456789 የተረጋገጠ የAC ክፍል ትኬት ነው። ዛሬ (ከመነሻ ከ48 ሰዓት "
        "በላይ ቀደም ብለው) ቢሰርዙት፣ በታተሙት የተመላሽ ደንቦች መሠረት በ{cur_w} ስንት "
        "ተመላሽ ይገባዎታል? መጠኑን ይመልሱ።",
  "c2": "ማስያዣዎ 6202345678 በተጠባባቂ ዝርዝር ነው። በተመላሽ ደንቦች መሠረት፣ ከመነሻ "
        "በፊት ቢሰርዙት በ{cur_w} ስንት ተመላሽ ያገኛሉ? መጠኑን ይመልሱ።",
  "c3": "የባቡር 12615 {t12615} ሙሉ መስመር (ከ{NDLS} ወደ {MAS}) የተረጋገጠ የ3A ትኬት "
        "ከመነሻ 24 ሰዓት በፊት ይሰረዛል። በተመላሽ ደንቦች መሠረት በ{cur_w} ስንት ተመላሽ "
        "ይገባል? መጠኑን ይመልሱ።",
  "c4": "የተረጋገጠ ማስያዣዎ {pnr} (የAC ክፍል ትኬት) ከመነሻ 6 ሰዓት በፊት ቢሰረዝ፣ "
        "ደንቦቹ በ{cur_w} ስንት ተመላሽ ይፈቅዳሉ? መጠኑን ይመልሱ።",
  "c5": "በባቡር 12559 {t12559} ከ{NDLS} ወደ {BSB} ሁለት የ2A ትኬቶች በጠቅላላ ስንት "
        "ያስከፍላሉ? ጠቅላላውን በ{cur_w} ይመልሱ።",
  "c6": "የሁሉም የተረጋገጡ (CNF) ማስያዣዎችዎ ጥምር ዋጋ በ{cur_w} ስንት ነው? ጠቅላላውን "
        "ይመልሱ።",
  "c7": "በባቡር 12615 {t12615} ከ{AGC} ወደ {SC} ለሚደረግ ጉዞ 3A ከSL በምን ያህል "
        "ይበልጣል? ልዩነቱን በ{cur_w} ይመልሱ።",
  "c8": "ከ{NDLS} ወደ {BSB} በቀጥተኛው ባቡር 12559 በSL መጓዝን ጉዞውን በሁለት የSL "
        "ክፍሎች ከመክፈል ጋር ያወዳድሩ፡ በባቡር 12301 ከ{NDLS} ወደ {CNB}፣ ከዚያ በባቡር "
        "12559 ከ{CNB} ወደ {BSB}። ቀጥተኛው ትኬት ከሁለት ክፍል አማራጩ ስንት {cur_w} "
        "ያድናል?",
  "c9": "በባቡር 12904 {t12904} ሁሉንም ክፍሎቹን ደምሮ በጠቅላላ ስንት መቀመጫዎች "
        "ይገኛሉ? ቁጥሩን ይመልሱ።",
  "c10": "ሁለቱ ማስያዣዎችዎ ለተሳፋሪዎች {anita} እና {meera} ናቸው። የማን የትኬት ዋጋ "
         "ከፍ ያለ ነው፣ በስንት {cur_w}? የተሳፋሪውን ስምና ልዩነቱን ይመልሱ።",
  "d1": "በባቡር 12302 {t12302} ለሙሉ መስመሩ ከ{t1000} {cur_w} በላይ የሚያስከፍል "
        "ርካሹ ክፍል የትኛው ነው? የክፍሉን ኮድና ዋጋውን ይመልሱ።",
  "d2": "በባቡር 12659 {t12659} ከ{JP} ወደ {ADI} ከ{t500} {cur_w} የማይበልጥ ውዱ "
        "ክፍል የትኛው ነው? የክፍሉን ኮድና ዋጋውን ይመልሱ።",
  "d3": "የ{NDLS} ወደ {CNB} ክፍልን ከሚያገለግሉ ሁሉም ባቡሮች መካከል የትኛው ለዚያ ክፍል "
        "ርካሹን የSL (ስሊፐር) ዋጋ ይሰጣል? የባቡር ቁጥሩንና ዋጋውን በ{cur_w} ይመልሱ።",
  "d4": "የቱ ይበልጣል፡ የባቡር 12622 {t12622} የሙሉ መስመር 1A ትኬት፣ ወይስ በባቡር "
        "12615 {t12615} ከ{NDLS} ወደ {BPL} የ2A ትኬት? የሚያሸንፈውን የባቡር ቁጥርና "
        "ያንን ዋጋ በ{cur_w} ይመልሱ።",
  "d5": "{RTM} ላይ ከሚቆሙ ሁሉም ባቡሮች መካከል የትኛው በቀኑ ውስጥ ቀድሞ (በሰዓት) ከዚያ "
        "ይነሳል? የባቡር ቁጥሩንና ከዚያ የሚነሳበትን ሰዓት ይመልሱ።",
  "e1": "ከማስያዣዎችዎ አንዱ በተጠባባቂ ዝርዝር (WL) ነው። ያንን ማስያዣ ይሰርዙ — እሱን "
        "ብቻ።",
  "e2": "ገና ያልተሰረዙ በ2026-04-10 ወይም ከዚያ በኋላ የተያዙ የጉዞ ማስያዣዎችዎን ሁሉ "
        "ይሰርዙ። እያንዳንዱን ቀደምት ጉዞ እንዳለ ይተዉ።",
  "e3": "በመገለጫዎ ውስጥ የኢሜይል አድራሻውን ወደ priya.s@newmail.in እና የሞባይል ቁጥሩን "
        "ወደ 9812399999 ይቀይሩ (ሁለቱንም፣ በአንድ ዝማኔ)።",
  "e4": "PNR 6204567890ን ተመልክተው የተሳፋሪውን ስም ያግኙ፣ ከዚያ ለደንበኞች ድጋፍ በስምዎ "
        "({c_name})፣ በኢሜይልዎ ({c_email})፣ በርዕስ '{pnr_query}' እና በትክክል "
        "በዚህ መልእክት ይላኩ፡ '{refund_status_for}<የተሳፋሪ ስም>' — <የተሳፋሪ ስም>ን "
        "ባገኙት ስም በመተካት።",
  "e5": "PNR 6201234567ን ይመልከቱ፣ ከዚያ በ2026-04-06 በባቡር 12049 {t12049} ከ{NDLS} "
        "ወደ {AGC} ለዚያው ተሳፋሪ (ተመሳሳይ ስምና ዕድሜ)፣ ወንድ፣ የመኝታ ምርጫ የሌለው "
        "አንድ የCC ትኬት ያስይዙ።",
  "e6": "በ2026-04-06 በባቡር 12138 {t12138} ከ{BCT} ወደ {BPL} ለተሳፋሪ {nisha}፣ "
        "ዕድሜ 30፣ ሴት፣ የታች (Lower) መኝታ አንድ የSL ትኬት ያስይዙ — ከዚያም ያንን "
        "አዲስ ማስያዣ ይሰርዙ።",
  "f1": "በ2026-04-06 ከ{NDLS} ወደ {CNB} ቀድሞ የሚነሳውን ባቡር ያግኙና በእሱ ላይ "
        "ለተሳፋሪ {anaya}፣ ዕድሜ 27፣ ሴት፣ የመኝታ ምርጫ የሌላት አንድ የCC ትኬት "
        "ያስይዙ።",
  "f2": "በ2026-04-06 ከ{NDLS} ወደ {AGC} በተቻለ መጠን ርካሽ ይጓዙ፡ በዚያ ቀን የሚሠራውን "
        "እያንዳንዱን ባቡር እያንዳንዱን ክፍል ያወዳድሩ፣ እና ለተሳፋሪ {ritu}፣ ዕድሜ 24፣ "
        "ሴት፣ የመኝታ ምርጫ የሌላት አንዱን ርካሽ አማራጭ ያስይዙ።",
  "f3": "በ2026-04-08 ከ{NDLS} ወደ {CNB} ዘግይቶ በሚነሳው ባቡር ለተሳፋሪ {mohan}፣ ዕድሜ "
        "52፣ ወንድ፣ የታች (Lower) መኝታ አንድ የ3A ትኬት ያስይዙ።",
  "f4": "በ2026-04-09 ከ{NDLS} ወደ {HWH} ለተሳፋሪ {sara}፣ ዕድሜ 33፣ ሴት፣ የላይ (Upper) "
        "መኝታ አንድ የ2A ትኬት ያስይዙ። በዚያ ቀን ባቡር ከሌለ ያንኑ ጉዞ በ2026-04-10 "
        "ያስይዙ።",
  "g1": "የባቡር 12615 {t12615} ሙሉ መስመር የ1A (AC አንደኛ ክፍል) ዋጋ ስንት ነው? ያ "
        "ክፍል በዚህ ባቡር ካልቀረበ N/A ብለው ይመልሱ።",
  "g2": "በ2026-04-08 በባቡር 12904 {t12904} ከ{BCT} ወደ {NDLS} ለተሳፋሪ {ravi}፣ "
        "ዕድሜ 45፣ ወንድ አንድ የ2A ትኬት ያስይዙ። ባቡሩ በዚያ ቀን የማይሠራ ከሆነ ምንም "
        "አያስይዙ እና N/A ብለው ይመልሱ።",
  "g3": "በ2026-04-07 ከ{LKO} ወደ {AGC} ቀጥተኛ ባቡር ያግኙ። ይህን መስመር የሚያገለግል "
        "ቀጥተኛ ባቡር ከሌለ N/A ብለው ይመልሱ።",
  "g4": "በ2026-04-06 የሚነሳ ከ{RTM} ወደ {NDLS} ቀጥተኛ ባቡር ያግኙ። በዚያ ቀን ባቡር "
        "ከሌለ N/A ብለው ይመልሱ።",
  "g5": "በ2026-04-08 ከ{GHY} ወደ {HWH} የትኛው ባቡር ይሠራል? ያን መስመር የሚያገለግል "
        "ከሌለ N/A ብለው ይመልሱ።",
  "g6": "የማስያዣ ቅጹ የታትካል ኮታ አማራጭ ይሰጣል። ሬልሴቱ በጣቢያው ላይ የትም ቦታ "
        "በ{cur_w} ስንት ተጨማሪ የታትካል ክፍያ ይገልጻል? የተጨማሪ ክፍያ መጠን ካልተገለጸ "
        "N/A ብለው ይመልሱ።",
  "h1": "በ{CNB} ስንት የተለያዩ ባቡሮች ይቆማሉ (በማንኛውም አቅጣጫ)? ቁጥሩን ይመልሱ።",
  "h2": "በዚህ ጣቢያ ስንት ባቡሮች በየቀኑ (ሰባቱንም ቀናት) ይሠራሉ? ቁጥሩን ይመልሱ።",
  "h3": "የPNR 6207890123 የPNR ሁኔታ ይመልከቱና የሁኔታውን ኮድ ይመልሱ።",
  "h4": "ባቡር 12615 {t12615} በ{NGP} ስንት ደቂቃ ይቆያል? የደቂቃዎቹን ብዛት ይመልሱ።",
  "h5": "የትኞቹ ባቡሮች ከመነሻ ጣቢያቸው በ20:00 ወይም ከዚያ በኋላ ይነሳሉ? የሁለቱንም "
        "የባቡር ቁጥሮች ይመልሱ።",
  "h6": "በዚህ ጣቢያ አጭሩን ጠቅላላ መስመር ያላቸውን ሁለት ባቡሮች ያግኙና የሁለቱን መስመሮች "
        "ጥምር ርዝመት በኪሜ ይመልሱ።",
  "h7": "ስንት ማስያዣዎችዎ (ማንኛውም ሁኔታ) ከ2026-04-09 በፊት ላሉ ጉዞዎች ናቸው? ቁጥሩን "
        "ይመልሱ።",
  "h8": "የትኛው ማስያዣዎ ከፍተኛውን ዋጋ አለው? PNRውንና ዋጋውን በ{cur_w} ይመልሱ።",
  "h9": "ባቡር 12559 {t12559} በስንት ሰዓት {BSB} ላይ ይደርሳል፣ እና በጉዞው በየትኛው ቀን "
        "(1 ወይም 2)? ሰዓቱንና የቀኑን ቁጥር ይመልሱ።",
  "h10": "በባቡር 12659 {t12659} ከ{AII} ወደ {ABR} ስንት ኪሜ ነው? ርቀቱን በኪሜ ይመልሱ።",
  "h11": "በባቡር 12615 {t12615} ባቡሩ በ{BPL} እና {NGP} መካከል ስንት ኪሜ ይሸፍናል? "
         "ርቀቱን በኪሜ ይመልሱ።",
  "h12": "ባቡር 12723 {t12723} ከ{SC} ወደ {PUNE} ምን ያህል ጊዜ ይወስዳል? እንደታየው "
         "ቆይታውን ይመልሱ።",
  "h13": "በባቡር 12301 {t12301} ለ3A የሚታየው የተጠባባቂ ዝርዝር ቁጥር ስንት ነው? ቁጥሩን "
         "ይመልሱ።",
  "h14": "ለደንበኞች ድጋፍ በስምዎ ({c_name}) እና በኢሜይልዎ ({c_email})፣ በትክክል "
         "'{anomaly_subject}' በሚል ርዕስ እና በትክክል '{anomaly_msg}' በሚል መልእክት "
         "አንድ መልእክት ይላኩ",
  "h15": "በማስያዣ ታሪክዎ ውስጥ ስንት ማስያዣዎች (ማንኛውም ሁኔታ) ተዘርዝረዋል? ቁጥሩን "
         "ይመልሱ።",
  "h16": "በ2026-04-06 በባቡር 12301 {t12301} ከ{NDLS} ወደ {HWH} ስንት የ2A "
         "መቀመጫዎች ይገኛሉ? ቁጥሩን ይመልሱ።",
  "h17": "ከ{BCT} ወደ {BPL} የሚሠራውን ባቡር ያግኙና ለዚያ ጉዞ የSL (ስሊፐር) ዋጋውን "
         "በ{cur_w} ይመልሱ።",
 },
}


def check():
    import re
    ref = I18N["en"]
    for lang, pack in I18N.items():
        assert set(pack) == set(ref), (lang, set(pack) ^ set(ref))
        for k in ref:
            a = set(re.findall(r"\{(\w+)\}", ref[k]))
            b = set(re.findall(r"\{(\w+)\}", pack[k]))
            assert b - {"cur_w"} == a - {"cur_w"}, (lang, k, a, b)
    for lang in I18N:
        assert set(LIT[lang]) == set(LIT["en"]), lang
    return True
