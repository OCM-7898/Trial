BN_D = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def bn(n):
    return str(n).translate(BN_D)


NR_EN = " If this is not possible on the portal, answer NO_RECORD."
NR_BN = " পোর্টালে এটি সম্ভব না হলে NO_RECORD উত্তর দিন।"

LIT = {
    "en": {
        "cred": (" Log in as citizen 9999708182203 (password: citizen1234) "
                 "if needed."),
        "income": "Salary", "purpose": "employment abroad",
        "new_addr": "House 9, Lake Road, Sylhet",
        "math": "Mathematics", "eng": "English",
        "damaged": "Damaged booklet",
        "exam_l": {"secondary": "secondary",
                   "higher-secondary": "higher-secondary"},
        "nr": NR_EN,
    },
    "bn": {
        "cred": (" প্রয়োজনে নাগরিক 9999708182203 (পাসওয়ার্ড: citizen1234) "
                 "হিসেবে লগ ইন করুন।"),
        "income": "বেতন", "purpose": "বিদেশে চাকরি",
        "new_addr": "বাড়ি 9, লেক রোড, সিলেট",
        "math": "গণিত", "eng": "ইংরেজি",
        "damaged": "ক্ষতিগ্রস্ত বই",
        "exam_l": {"secondary": "মাধ্যমিক",
                   "higher-secondary": "উচ্চ মাধ্যমিক"},
        "nr": NR_BN,
    },
    "hi": {
        "cred": (" ज़रूरत हो तो नागरिक 9999708182203 (पासवर्ड: citizen1234) "
                 "के रूप में लॉग इन करें।"),
        "income": "वेतन", "purpose": "विदेश में रोज़गार",
        "new_addr": "मकान 9, लेक रोड, सिलहट",
        "math": "गणित", "eng": "अंग्रेज़ी",
        "damaged": "क्षतिग्रस्त पुस्तिका",
        "exam_l": {"secondary": "माध्यमिक",
                   "higher-secondary": "उच्च माध्यमिक"},
        "nr": " यदि पोर्टल पर यह संभव न हो तो NO_RECORD उत्तर दें।",
    },
    "ur": {
        "cred": (" ضرورت ہو تو شہری 9999708182203 (پاس ورڈ: citizen1234) کے "
                 "طور پر لاگ ان کریں۔"),
        "income": "تنخواہ", "purpose": "بیرونِ ملک ملازمت",
        "new_addr": "مکان 9، لیک روڈ، سلہٹ",
        "math": "ریاضی", "eng": "انگریزی",
        "damaged": "خراب کتابچہ",
        "exam_l": {"secondary": "سیکنڈری",
                   "higher-secondary": "ہائر سیکنڈری"},
        "nr": " اگر پورٹل پر یہ ممکن نہ ہو تو NO_RECORD جواب دیں۔",
    },
    "am": {
        "cred": (" ካስፈለገ እንደ ዜጋ 9999708182203 (የይለፍ ቃል፡ citizen1234) "
                 "ይግቡ።"),
        "income": "ደመወዝ", "purpose": "በውጭ አገር ሥራ",
        "new_addr": "ቤት 9፣ ሌክ መንገድ፣ ሲልሄት",
        "math": "ሒሳብ", "eng": "እንግሊዝኛ",
        "damaged": "የተበላሸ ደብተር",
        "exam_l": {"secondary": "ሁለተኛ ደረጃ",
                   "higher-secondary": "ከፍተኛ ሁለተኛ ደረጃ"},
        "nr": " በፖርታሉ ላይ ይህ የማይቻል ከሆነ NO_RECORD ብለው ይመልሱ።",
    },
}

I18N = {
 "en": {
  "src_2": "Submit a correction to the name recorded on your identity "
           "card, changing it to '{nid_new_name}', attaching a supporting "
           "document.",
  "src_6": "Fill in and submit a new passport application end to end: "
           "personal information, then address, then page count, "
           "validity and delivery.",
  "src_8": "Book a passport enrolment appointment at {office_passport} "
           "for 22 June 2026 at 10:30.",
  "src_16": "Pay the outstanding electricity bill BL0000005 on consumer "
            "number 08000007.",
  "src_25": "Register for a new taxpayer identification number through "
            "the full application flow.",
  "src_31": "Look up the identity correction request with slip number "
            "NI9999999 and report its status. If no such record exists, "
            "answer NO_RECORD.",
  "src_32": "Look up khatian number 99999 in {mouza} mouza ({upazila}, "
            "{district}, {division} division). If no such record "
            "exists, answer NO_RECORD.",
  "src_33": "Retrieve the secondary result for roll number 999999, "
            "{board} board, 2021. If no such result exists, answer "
            "NO_RECORD.",
  "new_34": "Open your electricity bill history and note the amount of "
            "the 2026-01 bill. In the electricity fee schedule, find the "
            "fee whose amount is the highest that is still below that "
            "bill amount, and answer with that fee's variant name. Then "
            "settle the oldest outstanding bill on your meter.",
  "new_35": "Find khatian number 4438 somewhere in {district} district "
            "through the land record search (the upazila and mouza are "
            "not given) and report the plot number recorded on it.",
  "new_36": "Look up the secondary exam result of 2021 for roll number "
            "763370 (the board is not given — the lookup page lists the "
            "boards) and report the candidate's institution.",
  "new_37": "Verify the birth registration record with registration "
            "number 20000000000373 and report its registration date.",
  "new_38": "On the electricity service page, three notices share the "
            "same title. Report the category of the one issued on "
            "2025-10-12.",
  "new_39": "Check passport application PPA04000017 to read its booklet "
            "pages and validity, then use the passport fee schedule to "
            "report the express-delivery fee for exactly that "
            "pages/validity combination.",
  "new_40": "Open your electricity bill history and report the total "
            "amount billed across all six billing periods.",
  "a1": "Open your electricity bill history and note the amount of the "
        "2026-01 bill. On the driving-licence fee schedule, find the MOST "
        "expensive fee that is still below that bill amount, then "
        "generate and pay the challan for exactly that category/variant "
        "(by card) and report the amount you paid.",
  "a2": "Check the total outstanding amount on consumer number 08000049. "
        "On the electricity fee schedule, find the MOST expensive fee "
        "that is still below HALF of that total, and answer with that "
        "fee's variant name.",
  "b1": "Pay BOTH outstanding electricity bills on your consumer number "
        "08000007, by card.",
  "b2": "Consumer number 08000021 has more than one outstanding "
        "electricity bill. Pay ONLY the OLDEST one (by card) and leave "
        "the rest unpaid.",
  "b3": "By how much is the total outstanding amount on consumer number "
        "08000049 larger than on consumer number 08000035? Answer with "
        "the difference.",
  "b4": "Compare two of your outstanding balances: the total unpaid "
        "electricity on consumer number 08000007, and the total unpaid "
        "land development tax on holding HLD00001. Answer with the "
        "LARGER of the two amounts.",
  "b5": "In your electricity bill history, how many bills exceeded an "
        "amount of 2000? Answer with the number.",
  "c1": "Find khatian number 5265 somewhere in {district} district "
        "({division} division; the upazila and mouza are not given) "
        "through the land record search and report the owner recorded "
        "on it.",
  "c2": "Look up khatian number 9458 in {mouza} mouza ({upazila}, "
        "{district}, {division} division) and report THREE things: the "
        "owner, the land type, and the area in decimals.",
  "c3": "Look up khatian number 6743 in {mouza} mouza ({upazila}, "
        "{district}, {division} division), then apply for a land "
        "mutation COPYING from that record: seller name = the recorded "
        "owner, plot number and area as recorded. Use yourself as the "
        "buyer (buyer id 9999708182203), seller id 9999000000002.",
  "c4": "Holding HLD00003 has several years of outstanding land "
        "development tax. Pay ALL of its outstanding dues, by card.",
  "c5": "Which holding owes more in total outstanding land development "
        "tax: HLD00003 or HLD00004? Answer with the holding number.",
  "c6": "In the land record search, navigate to {upazila} upazila "
        "({district} district, {division} division) and report the JL "
        "number of {mouza} mouza.",
  "c7": "Find khatian number 2052 somewhere in {division} DIVISION "
        "through the land record search (the district, upazila and "
        "mouza are not given) and report the owner recorded on it.",
  "c8": "Find khatian number 8630 somewhere in {district} district "
        "({division} division; the upazila and mouza are not given) and "
        "report BOTH the owner and the area in decimals.",
  "c9": "Find khatian number 3232 somewhere in {district} district "
        "({division} division; the upazila and mouza are not given) "
        "through the land record search and report the land type "
        "recorded on it.",
  "c10": "On holding HLD00003, pay every outstanding land development "
         "tax due EXCEPT the most recent fiscal year, by card — the "
         "newest due must remain unpaid.",
  "c11": "Which holding owes more in total outstanding land development "
         "tax: HLD00004 or HLD00005? Answer with the holding number.",
  "e1": "Look up the secondary exam result of 2021 for roll number "
        "244479 (the board is not given — the lookup page lists the "
        "boards), then submit a rescrutiny application for that result, "
        "entering the registration number shown on the result, its "
        "board and year, for the subject {math}.",
  "e2": "Look up the {exam} exam result of {year} for roll number "
        "969953 (the board is not given — the lookup page lists the "
        "boards), then submit a rescrutiny application for that result, "
        "entering the registration number shown on the result, its "
        "board and year, for the subject {eng}.",
  "e3": "On the portal's notice board, filter to the land service's "
        "notices. Which category did that service use MOST often? "
        "Answer with the category.",
  "e4": "Submit an individual e-return for assessment year 2025-2026 "
        "with TIN 972871718941: total income 640000, deductions of "
        "exactly one eighth of the income, and tax payable of exactly "
        "10% of (income minus deductions). Enter all amounts as plain "
        "digits, declaration YES.",
  "e5": "The notice with reference {ref} appears on the portal's notice "
        "board (linked from the home page). Find which service issued "
        "it, open that service's fee schedule, and report the CHEAPEST "
        "fee amount listed there.",
  "g1": "Do BOTH of the following: pay electricity bill BL0000006 on "
        "consumer number 08000007, and recharge prepaid meter MTR000006 "
        "with 750. Pay by card.",
  "g2": "Complete new voter registration through the full form (your "
        "name, parentage, date of birth, both addresses and the "
        "{centre} as centre), and ALSO book a passport enrolment "
        "appointment at {office_passport} for 2026-06-25 at 15:00.",
  "g3": "Submit BOTH of these applications: a police clearance "
        "certificate for employment abroad (name, parentage, date of "
        "birth and both addresses), and a pilgrimage pre-registration "
        "(name, father's name, passport number PPA04000017, present "
        "address, your mobile, your mother as next of kin, government "
        "package).",
  "g4": "Apply for a land mutation (buyer: yourself, id 9999708182203; "
        "seller {rafiqul}, id 9999000000001; khatian 4438, plot 357, "
        "area 25), and ALSO pay the outstanding land development tax on "
        "holding HLD00002, by card.",
  "g5": "On consumer number 08000007, pay ONLY the NEWEST outstanding "
        "electricity bill by card, leaving the older one unpaid.",
  "h1": "Open the portal's notice board (linked from the home page). "
        "How many notices were issued in February 2026, across all "
        "services? Answer with the number.",
  "h2": "According to the portal's notice board, which service issued "
        "the MOST notices during 2025? Answer with the service name.",
  "h3": "Report the exact title of the OLDEST notice on the portal's "
        "notice board.",
  "h4": "On the portal's notice board, how many notices issued in 2026 "
        "carry the category '{closure}'? Answer with the number.",
  "n1": "Find the {exam} exam result of {year} for roll number 496396 — "
        "the board is NOT given, the lookup page lists the boards. "
        "Report BOTH the candidate's GPA and their institution.",
  "n2": "Find the {exam} exam result of {year} for roll number 969525 — "
        "the board is NOT given. Report BOTH the candidate's name and "
        "their GPA.",
  "n3": "Find khatian number 7191 somewhere in {district} district "
        "({division} division; the upazila and mouza are not given) "
        "through the land record search and report the land type "
        "recorded on it.",
  "n4": "Find khatian number 1022 somewhere in {district} district "
        "({division} division; the upazila and mouza are not given) and "
        "report BOTH the owner and the share recorded.",
  "n5": "Exactly one notice on the portal's notice board was issued in "
        "June 2026. Report BOTH its reference number and the name of "
        "the service that issued it.",
  "n6": "During 2026, which month saw the FEWEST notices on the portal's "
        "notice board? Answer with the month as YYYY-MM.",
  "n7": "Check the total outstanding electricity on consumer numbers "
        "08000021, 08000035 and 08000049, and report the COMBINED total "
        "across all three.",
  "n8": "Report the combined total of ALL outstanding land development "
        "tax across holdings HLD00003, HLD00004 and HLD00005.",
  "n9": "Across ALL six periods in your electricity bill history, how "
        "many units (kWh) were consumed in total?",
  "n10": "On the passport fee schedule, what is the difference between "
         "the most expensive fee and the cheapest NONZERO fee?",
  "n11": "Across the passport AND driving-licence fee schedules "
         "combined, how many fee rows carry an amount greater than "
         "5000? Answer with the number.",
  "n12": "Submit an individual e-return for assessment year 2025-2026 "
         "with TIN 972871718941: total income 720000, deductions of "
         "exactly one quarter of the income, and tax payable of exactly "
         "15% of (income minus deductions). Enter all amounts as plain "
         "digits, declaration YES.",
  "n13": "Look up the birth registration record numbered "
         "20000000000373. Then submit a birth registration application "
         "for a NEW child named exactly after that record's MOTHER, born "
         "2026-03-01, at the place recorded on that record, with "
         "yourself as father and your mother as mother.",
  "n14": "Find the OLDEST notice on the portal's notice board, note "
         "which service issued it, then open that service's fee "
         "schedule and report its MOST expensive fee amount.",
  "n15": "Do BOTH: book a driving test at {office_licence} on the "
         "earliest available date at the earliest time, AND generate "
         "and pay the challan for the Renewal category, Professional "
         "variant (by card). Then report the challan amount you paid.",
  "n16": "Check passport applications PPA04000034 and PPA04000068 to "
         "read each one's booklet pages and validity. According to the "
         "passport fee schedule, which application's REGULAR-delivery "
         "fee is higher? Answer with the application id.",
  "n17": "Do all THREE of the following: pay electricity bill BL0000005 "
         "on consumer 08000007, pay the outstanding land development "
         "tax on holding HLD00002, and book a passport enrolment "
         "appointment at {office_passport} for 2026-06-24 at 11:30. Pay "
         "by card.",
  "n18": "On holding HLD00003, pay ONLY the 2022-2023 land development "
         "tax due (by card), leaving both the older and the newer dues "
         "unpaid.",
  "n19": "Submit THREE corrections: change your identity record's "
         "present address to '{new_addr}' and its date of birth to "
         "{new_dob}, and change the name on your linked BIRTH "
         "registration record to '{hoque}'. Attach any locker document "
         "to each.",
  "n20": "Submit BOTH passport requests: a new application (your name, "
         "date of birth and father's name; both addresses; 64 pages, 10 "
         "years validity, express delivery), and a REISSUE application "
         "for passport number A6053903 with the reason '{damaged}'.",
  "i1": "Recharge meter MTR000001 with 300, by card.",
  "i2": "Download the vaccination certificate for identity number "
        "9999708182203 registered on 2023-09-16 and report the "
        "certificate number.",
  "i3": "Look up the delivery status of the passport belonging to "
        "application PPA04000017 and report it.",
  "i4": "Generate and pay a fee challan for category {cat_licence}, "
        "variant {var_motorcycle}.",
  "i5": "Submit a name correction on the death record linked to your "
        "account, changing the name to '{haque_sr}'.",
  "i6": "Book a passport enrolment appointment at {office_passport} for "
        "2026-06-23 at 10:30.",
  "i7": "Verify taxpayer identification number 111111111111 and report "
        "the registered name.",
  "j1": "Open the printable copy of your identity card and report BOTH "
        "the mother's name and the permanent address shown.",
 },
 "bn": {
  "src_2": "আপনার পরিচয়পত্রে রেকর্ডকৃত নামের সংশোধন দাখিল করুন, নামটি "
           "'{nid_new_name}' করে, একটি সহায়ক দলিল সংযুক্ত করে।",
  "src_6": "একটি নতুন পাসপোর্ট আবেদন শুরু থেকে শেষ পর্যন্ত পূরণ করে দাখিল "
           "করুন: ব্যক্তিগত তথ্য, তারপর ঠিকানা, তারপর পৃষ্ঠাসংখ্যা, মেয়াদ ও "
           "ডেলিভারি।",
  "src_8": "{office_passport}-এ ২০২৬ সালের ২২ জুন 10:30-এ পাসপোর্ট এনরোলমেন্ট "
           "অ্যাপয়েন্টমেন্ট বুক করুন।",
  "src_16": "গ্রাহক নম্বর 08000007-এর বকেয়া বিদ্যুৎ বিল BL0000005 পরিশোধ "
            "করুন।",
  "src_25": "সম্পূর্ণ আবেদন প্রক্রিয়ার মাধ্যমে একটি নতুন করদাতা শনাক্তকরণ "
            "নম্বরের জন্য নিবন্ধন করুন।",
  "src_31": "স্লিপ নম্বর NI9999999-এর পরিচয় সংশোধন আবেদনটি খুঁজে তার অবস্থা "
            "জানান। এমন কোনো রেকর্ড না থাকলে NO_RECORD উত্তর দিন।",
  "src_32": "{mouza} মৌজায় ({upazila}, {district}, {division} বিভাগ) খতিয়ান "
            "নম্বর 99999 খুঁজুন। এমন কোনো রেকর্ড না থাকলে NO_RECORD উত্তর "
            "দিন।",
  "src_33": "রোল নম্বর 999999, {board} বোর্ড, 2021-এর মাধ্যমিক (secondary) "
            "ফল সংগ্রহ করুন। এমন কোনো ফল না থাকলে NO_RECORD উত্তর দিন।",
  "new_34": "আপনার বিদ্যুৎ বিলের ইতিহাস খুলে 2026-01 বিলের অঙ্কটি লক্ষ করুন। "
            "বিদ্যুৎ ফি তালিকায় সেই বিলের অঙ্কের নিচে থাকা সর্বোচ্চ অঙ্কের "
            "ফিটি খুঁজে সেই ফির ভ্যারিয়েন্টের নাম উত্তর দিন। তারপর আপনার "
            "মিটারের সবচেয়ে পুরোনো বকেয়া বিলটি মেটান।",
  "new_35": "ভূমি রেকর্ড অনুসন্ধানের মাধ্যমে {district} জেলার কোথাও থাকা "
            "খতিয়ান নম্বর 4438 খুঁজুন (উপজেলা ও মৌজা দেওয়া নেই) এবং তাতে "
            "রেকর্ডকৃত দাগ নম্বর জানান।",
  "new_36": "রোল নম্বর 763370-এর 2021 সালের মাধ্যমিক (secondary) পরীক্ষার ফল "
            "দেখুন (বোর্ড দেওয়া নেই — অনুসন্ধান পাতায় বোর্ডগুলোর তালিকা আছে) "
            "এবং পরীক্ষার্থীর প্রতিষ্ঠান জানান।",
  "new_37": "নিবন্ধন নম্বর 20000000000373-এর জন্ম নিবন্ধন রেকর্ডটি যাচাই করে "
            "তার নিবন্ধনের তারিখ জানান।",
  "new_38": "বিদ্যুৎ সেবার পাতায় তিনটি বিজ্ঞপ্তির শিরোনাম একই। 2025-10-12 "
            "তারিখে জারি হওয়াটির বিভাগ (ক্যাটাগরি) জানান।",
  "new_39": "পাসপোর্ট আবেদন PPA04000017 দেখে তার বইয়ের পৃষ্ঠাসংখ্যা ও মেয়াদ "
            "পড়ুন, তারপর পাসপোর্ট ফি তালিকা ব্যবহার করে ঠিক সেই "
            "পৃষ্ঠাসংখ্যা/মেয়াদ সমন্বয়ের এক্সপ্রেস (express) ডেলিভারি ফি জানান।",
  "new_40": "আপনার বিদ্যুৎ বিলের ইতিহাস খুলে ছয়টি বিলিং সময়কাল মিলিয়ে মোট "
            "বিল করা অঙ্ক জানান।",
  "a1": "আপনার বিদ্যুৎ বিলের ইতিহাস খুলে 2026-01 বিলের অঙ্কটি লক্ষ করুন। "
        "ড্রাইভিং লাইসেন্স ফি তালিকায় সেই বিলের অঙ্কের নিচে থাকা সবচেয়ে "
        "দামি ফিটি খুঁজুন, তারপর ঠিক সেই শ্রেণি/ভ্যারিয়েন্টের চালান তৈরি করে "
        "(কার্ডে, card) পরিশোধ করুন এবং যে অঙ্ক পরিশোধ করলেন তা জানান।",
  "a2": "গ্রাহক নম্বর 08000049-এর মোট বকেয়া অঙ্ক দেখুন। বিদ্যুৎ ফি তালিকায় "
        "সেই মোটের অর্ধেকের নিচে থাকা সবচেয়ে দামি ফিটি খুঁজে সেই ফির "
        "ভ্যারিয়েন্টের নাম উত্তর দিন।",
  "b1": "আপনার গ্রাহক নম্বর 08000007-এর দুটি বকেয়া বিদ্যুৎ বিলই কার্ডে (card) "
        "পরিশোধ করুন।",
  "b2": "গ্রাহক নম্বর 08000021-এর একাধিক বকেয়া বিদ্যুৎ বিল আছে। শুধু সবচেয়ে "
        "পুরোনোটি (কার্ডে, card) পরিশোধ করুন এবং বাকিগুলো অপরিশোধিত রাখুন।",
  "b3": "গ্রাহক নম্বর 08000049-এর মোট বকেয়া অঙ্ক গ্রাহক নম্বর 08000035-এর "
        "চেয়ে কত বেশি? পার্থক্যটি উত্তর দিন।",
  "b4": "আপনার দুটি বকেয়া তুলনা করুন: গ্রাহক নম্বর 08000007-এর মোট অপরিশোধিত "
        "বিদ্যুৎ বিল, এবং হোল্ডিং HLD00001-এর মোট অপরিশোধিত ভূমি উন্নয়ন কর। "
        "দুটির মধ্যে বড় অঙ্কটি উত্তর দিন।",
  "b5": "আপনার বিদ্যুৎ বিলের ইতিহাসে কতটি বিলের অঙ্ক ২০০০-এর বেশি ছিল? "
        "সংখ্যাটি উত্তর দিন।",
  "c1": "ভূমি রেকর্ড অনুসন্ধানের মাধ্যমে {district} জেলার ({division} বিভাগ; "
        "উপজেলা ও মৌজা দেওয়া নেই) কোথাও থাকা খতিয়ান নম্বর 5265 খুঁজুন এবং "
        "তাতে রেকর্ডকৃত মালিক জানান।",
  "c2": "{mouza} মৌজায় ({upazila}, {district}, {division} বিভাগ) খতিয়ান "
        "নম্বর 9458 দেখুন এবং তিনটি জিনিস জানান: মালিক, জমির শ্রেণি এবং "
        "শতাংশে পরিমাণ।",
  "c3": "{mouza} মৌজায় ({upazila}, {district}, {division} বিভাগ) খতিয়ান "
        "নম্বর 6743 দেখুন, তারপর সেই রেকর্ড থেকে নকল করে একটি নামজারির "
        "আবেদন করুন: বিক্রেতার নাম = রেকর্ডকৃত মালিক, দাগ নম্বর ও পরিমাণ "
        "যেমন রেকর্ড আছে। ক্রেতা হিসেবে নিজেকে দিন (ক্রেতার আইডি "
        "9999708182203), বিক্রেতার আইডি 9999000000002।",
  "c4": "হোল্ডিং HLD00003-এর কয়েক বছরের ভূমি উন্নয়ন কর বকেয়া আছে। এর সব "
        "বকেয়া কার্ডে (card) পরিশোধ করুন।",
  "c5": "মোট বকেয়া ভূমি উন্নয়ন কর কোন হোল্ডিংয়ের বেশি: HLD00003 না HLD00004? "
        "হোল্ডিং নম্বরটি উত্তর দিন।",
  "c6": "ভূমি রেকর্ড অনুসন্ধানে {upazila} উপজেলায় ({district} জেলা, "
        "{division} বিভাগ) যান এবং {mouza} মৌজার জেএল নম্বর জানান।",
  "c7": "ভূমি রেকর্ড অনুসন্ধানের মাধ্যমে {division} বিভাগের কোথাও থাকা "
        "খতিয়ান নম্বর 2052 খুঁজুন (জেলা, উপজেলা ও মৌজা দেওয়া নেই) এবং তাতে "
        "রেকর্ডকৃত মালিক জানান।",
  "c8": "{district} জেলার ({division} বিভাগ; উপজেলা ও মৌজা দেওয়া নেই) "
        "কোথাও থাকা খতিয়ান নম্বর 8630 খুঁজুন এবং মালিক ও শতাংশে পরিমাণ "
        "দুটিই জানান।",
  "c9": "ভূমি রেকর্ড অনুসন্ধানের মাধ্যমে {district} জেলার ({division} বিভাগ; "
        "উপজেলা ও মৌজা দেওয়া নেই) কোথাও থাকা খতিয়ান নম্বর 3232 খুঁজুন এবং "
        "তাতে রেকর্ডকৃত জমির শ্রেণি জানান।",
  "c10": "হোল্ডিং HLD00003-এ সবচেয়ে সাম্প্রতিক অর্থবছরটি বাদে প্রতিটি বকেয়া "
         "ভূমি উন্নয়ন কর কার্ডে (card) পরিশোধ করুন — সবচেয়ে নতুন বকেয়াটি "
         "অপরিশোধিত থাকতে হবে।",
  "c11": "মোট বকেয়া ভূমি উন্নয়ন কর কোন হোল্ডিংয়ের বেশি: HLD00004 না HLD00005? "
         "হোল্ডিং নম্বরটি উত্তর দিন।",
  "e1": "রোল নম্বর 244479-এর 2021 সালের মাধ্যমিক (secondary) পরীক্ষার ফল "
        "দেখুন (বোর্ড দেওয়া নেই — অনুসন্ধান পাতায় বোর্ডগুলোর তালিকা আছে), "
        "তারপর সেই ফলের জন্য একটি পুনঃনিরীক্ষণ আবেদন দাখিল করুন, ফলে দেখানো "
        "রেজিস্ট্রেশন নম্বর, তার বোর্ড ও বছর লিখে, {math} বিষয়ের জন্য।",
  "e2": "রোল নম্বর 969953-এর {year} সালের {exam_l} ({exam}) পরীক্ষার ফল "
        "দেখুন (বোর্ড দেওয়া নেই — অনুসন্ধান পাতায় বোর্ডগুলোর তালিকা আছে), "
        "তারপর সেই ফলের জন্য একটি পুনঃনিরীক্ষণ আবেদন দাখিল করুন, ফলে দেখানো "
        "রেজিস্ট্রেশন নম্বর, তার বোর্ড ও বছর লিখে, {eng} বিষয়ের জন্য।",
  "e3": "পোর্টালের নোটিশ বোর্ডে ভূমি সেবার বিজ্ঞপ্তিগুলো ছেঁকে নিন। সেই সেবা "
        "কোন বিভাগ (ক্যাটাগরি) সবচেয়ে বেশিবার ব্যবহার করেছে? বিভাগটি উত্তর "
        "দিন।",
  "e4": "টিআইএন 972871718941 দিয়ে কর বছর 2025-2026-এর একটি ব্যক্তিগত ই-রিটার্ন "
        "দাখিল করুন: মোট আয় ৬৪০০০০, কর্তন ঠিক আয়ের এক-অষ্টমাংশ, এবং প্রদেয় "
        "কর ঠিক (আয় বাদ কর্তন)-এর ১০%। সব অঙ্ক সাধারণ সংখ্যায় লিখুন, ঘোষণা "
        "YES।",
  "e5": "রেফারেন্স {ref}-এর বিজ্ঞপ্তিটি পোর্টালের নোটিশ বোর্ডে আছে (হোম পেজ "
        "থেকে লিংক করা)। কোন সেবা এটি জারি করেছে খুঁজে বের করুন, সেই সেবার "
        "ফি তালিকা খুলুন এবং সেখানে তালিকাভুক্ত সবচেয়ে সস্তা ফির অঙ্ক জানান।",
  "g1": "দুটি কাজই করুন: গ্রাহক নম্বর 08000007-এর বিদ্যুৎ বিল BL0000006 "
        "পরিশোধ করুন, এবং প্রিপেইড মিটার MTR000006 ৭৫০ দিয়ে রিচার্জ করুন। "
        "কার্ডে (card) পরিশোধ করুন।",
  "g2": "সম্পূর্ণ ফর্মের মাধ্যমে নতুন ভোটার নিবন্ধন সম্পন্ন করুন (আপনার নাম, "
        "পিতৃ-মাতৃপরিচয়, জন্মতারিখ, দুই ঠিকানা এবং কেন্দ্র হিসেবে {centre}), "
        "এবং সেই সঙ্গে {office_passport}-এ 2026-06-25 তারিখে 15:00-এ একটি "
        "পাসপোর্ট এনরোলমেন্ট অ্যাপয়েন্টমেন্ট বুক করুন।",
  "g3": "এই দুটি আবেদনই দাখিল করুন: বিদেশে চাকরির জন্য একটি পুলিশ ক্লিয়ারেন্স "
        "সনদ (নাম, পিতৃ-মাতৃপরিচয়, জন্মতারিখ ও দুই ঠিকানা), এবং একটি হজ "
        "প্রাক-নিবন্ধন (নাম, পিতার নাম, পাসপোর্ট নম্বর PPA04000017, বর্তমান "
        "ঠিকানা, আপনার মোবাইল, নিকটাত্মীয় হিসেবে আপনার মা, সরকারি "
        "(government) প্যাকেজ)।",
  "g4": "একটি নামজারির আবেদন করুন (ক্রেতা: আপনি নিজে, আইডি 9999708182203; "
        "বিক্রেতা {rafiqul}, আইডি 9999000000001; খতিয়ান 4438, দাগ 357, পরিমাণ "
        "25), এবং সেই সঙ্গে হোল্ডিং HLD00002-এর বকেয়া ভূমি উন্নয়ন কর কার্ডে "
        "(card) পরিশোধ করুন।",
  "g5": "গ্রাহক নম্বর 08000007-এ শুধু সবচেয়ে নতুন বকেয়া বিদ্যুৎ বিলটি কার্ডে "
        "(card) পরিশোধ করুন, পুরোনোটি অপরিশোধিত রেখে।",
  "h1": "পোর্টালের নোটিশ বোর্ড খুলুন (হোম পেজ থেকে লিংক করা)। সব সেবা মিলিয়ে "
        "২০২৬ সালের ফেব্রুয়ারিতে কতটি বিজ্ঞপ্তি জারি হয়েছে? সংখ্যাটি উত্তর "
        "দিন।",
  "h2": "পোর্টালের নোটিশ বোর্ড অনুযায়ী ২০২৫ সালে কোন সেবা সবচেয়ে বেশি "
        "বিজ্ঞপ্তি জারি করেছে? সেবার নামটি উত্তর দিন।",
  "h3": "পোর্টালের নোটিশ বোর্ডের সবচেয়ে পুরোনো বিজ্ঞপ্তির হুবহু শিরোনাম জানান।",
  "h4": "পোর্টালের নোটিশ বোর্ডে ২০২৬ সালে জারি হওয়া কতটি বিজ্ঞপ্তির বিভাগ "
        "(ক্যাটাগরি) '{closure}'? সংখ্যাটি উত্তর দিন।",
  "n1": "রোল নম্বর 496396-এর {year} সালের {exam_l} ({exam}) পরীক্ষার ফল "
        "খুঁজুন — বোর্ড দেওয়া নেই, অনুসন্ধান পাতায় বোর্ডগুলোর তালিকা আছে। "
        "পরীক্ষার্থীর জিপিএ ও প্রতিষ্ঠান দুটিই জানান।",
  "n2": "রোল নম্বর 969525-এর {year} সালের {exam_l} ({exam}) পরীক্ষার ফল "
        "খুঁজুন — বোর্ড দেওয়া নেই। পরীক্ষার্থীর নাম ও জিপিএ দুটিই জানান।",
  "n3": "ভূমি রেকর্ড অনুসন্ধানের মাধ্যমে {district} জেলার ({division} বিভাগ; "
        "উপজেলা ও মৌজা দেওয়া নেই) কোথাও থাকা খতিয়ান নম্বর 7191 খুঁজুন এবং "
        "তাতে রেকর্ডকৃত জমির শ্রেণি জানান।",
  "n4": "{district} জেলার ({division} বিভাগ; উপজেলা ও মৌজা দেওয়া নেই) "
        "কোথাও থাকা খতিয়ান নম্বর 1022 খুঁজুন এবং মালিক ও রেকর্ডকৃত অংশ "
        "দুটিই জানান।",
  "n5": "পোর্টালের নোটিশ বোর্ডে ঠিক একটি বিজ্ঞপ্তি ২০২৬ সালের জুনে জারি "
        "হয়েছে। তার রেফারেন্স নম্বর এবং যে সেবা এটি জারি করেছে তার নাম — "
        "দুটিই জানান।",
  "n6": "২০২৬ সালে কোন মাসে পোর্টালের নোটিশ বোর্ডে সবচেয়ে কম বিজ্ঞপ্তি "
        "এসেছে? মাসটি YYYY-MM আকারে উত্তর দিন।",
  "n7": "গ্রাহক নম্বর 08000021, 08000035 ও 08000049-এর মোট বকেয়া বিদ্যুৎ "
        "বিল দেখুন এবং তিনটি মিলিয়ে সম্মিলিত মোট জানান।",
  "n8": "হোল্ডিং HLD00003, HLD00004 ও HLD00005-এর সব বকেয়া ভূমি উন্নয়ন করের "
        "সম্মিলিত মোট জানান।",
  "n9": "আপনার বিদ্যুৎ বিলের ইতিহাসের ছয়টি সময়কাল মিলিয়ে মোট কত ইউনিট "
        "(kWh) ব্যবহৃত হয়েছে?",
  "n10": "পাসপোর্ট ফি তালিকায় সবচেয়ে দামি ফি ও সবচেয়ে সস্তা শূন্য-নয় ফির "
         "পার্থক্য কত?",
  "n11": "পাসপোর্ট ও ড্রাইভিং লাইসেন্স ফি তালিকা মিলিয়ে কতটি ফি সারির অঙ্ক "
         "৫০০০-এর বেশি? সংখ্যাটি উত্তর দিন।",
  "n12": "টিআইএন 972871718941 দিয়ে কর বছর 2025-2026-এর একটি ব্যক্তিগত ই-রিটার্ন "
         "দাখিল করুন: মোট আয় ৭২০০০০, কর্তন ঠিক আয়ের এক-চতুর্থাংশ, এবং প্রদেয় "
         "কর ঠিক (আয় বাদ কর্তন)-এর ১৫%। সব অঙ্ক সাধারণ সংখ্যায় লিখুন, ঘোষণা "
         "YES।",
  "n13": "নিবন্ধন নম্বর 20000000000373-এর জন্ম নিবন্ধন রেকর্ডটি দেখুন। তারপর "
         "একটি নতুন শিশুর জন্ম নিবন্ধন আবেদন দাখিল করুন, যার নাম হুবহু সেই "
         "রেকর্ডের মায়ের নামে, জন্ম 2026-03-01, সেই রেকর্ডে রেকর্ডকৃত স্থানে, "
         "পিতা হিসেবে আপনি নিজে এবং মাতা হিসেবে আপনার মা।",
  "n14": "পোর্টালের নোটিশ বোর্ডের সবচেয়ে পুরোনো বিজ্ঞপ্তিটি খুঁজুন, কোন সেবা "
         "এটি জারি করেছে লক্ষ করুন, তারপর সেই সেবার ফি তালিকা খুলে তার "
         "সবচেয়ে দামি ফির অঙ্ক জানান।",
  "n15": "দুটিই করুন: {office_licence}-এ সবচেয়ে আগের খালি তারিখে সবচেয়ে আগের "
         "সময়ে একটি ড্রাইভিং টেস্ট বুক করুন, এবং নবায়ন শ্রেণি, পেশাদার "
         "ভ্যারিয়েন্টের চালান তৈরি করে (কার্ডে, card) পরিশোধ করুন। তারপর যে "
         "চালানের অঙ্ক পরিশোধ করলেন তা জানান।",
  "n16": "পাসপোর্ট আবেদন PPA04000034 ও PPA04000068 দেখে প্রতিটির বইয়ের "
         "পৃষ্ঠাসংখ্যা ও মেয়াদ পড়ুন। পাসপোর্ট ফি তালিকা অনুযায়ী কোন আবেদনের "
         "নিয়মিত (regular) ডেলিভারি ফি বেশি? আবেদন আইডিটি উত্তর দিন।",
  "n17": "তিনটি কাজই করুন: গ্রাহক 08000007-এর বিদ্যুৎ বিল BL0000005 পরিশোধ "
         "করুন, হোল্ডিং HLD00002-এর বকেয়া ভূমি উন্নয়ন কর পরিশোধ করুন, এবং "
         "{office_passport}-এ 2026-06-24 তারিখে 11:30-এ একটি পাসপোর্ট "
         "এনরোলমেন্ট অ্যাপয়েন্টমেন্ট বুক করুন। কার্ডে (card) পরিশোধ করুন।",
  "n18": "হোল্ডিং HLD00003-এ শুধু 2022-2023 অর্থবছরের ভূমি উন্নয়ন কর বকেয়াটি "
         "(কার্ডে, card) পরিশোধ করুন, পুরোনো ও নতুন দুই বকেয়াই অপরিশোধিত "
         "রেখে।",
  "n19": "তিনটি সংশোধন দাখিল করুন: আপনার পরিচয় রেকর্ডের বর্তমান ঠিকানা "
         "'{new_addr}' এবং জন্মতারিখ {new_dob} করুন, এবং আপনার যুক্ত জন্ম "
         "নিবন্ধন রেকর্ডের নাম '{hoque}' করুন। প্রতিটিতে লকারের যেকোনো দলিল "
         "সংযুক্ত করুন।",
  "n20": "দুটি পাসপোর্ট অনুরোধই দাখিল করুন: একটি নতুন আবেদন (আপনার নাম, "
         "জন্মতারিখ ও পিতার নাম; দুই ঠিকানা; 64 পৃষ্ঠা, 10 বছর মেয়াদ, "
         "এক্সপ্রেস (express) ডেলিভারি), এবং পাসপোর্ট নম্বর A6053903-এর জন্য "
         "'{damaged}' কারণ দিয়ে একটি পুনঃপ্রদানের আবেদন।",
  "i1": "মিটার MTR000001 ৩০০ দিয়ে কার্ডে (card) রিচার্জ করুন।",
  "i2": "পরিচয় নম্বর 9999708182203, নিবন্ধন 2023-09-16-এর টিকা সনদ ডাউনলোড "
        "করে সনদ নম্বর জানান।",
  "i3": "আবেদন PPA04000017-এর পাসপোর্টের ডেলিভারির অবস্থা দেখে তা জানান।",
  "i4": "শ্রেণি {cat_licence}, ভ্যারিয়েন্ট {var_motorcycle}-এর একটি ফি চালান "
        "তৈরি করে পরিশোধ করুন।",
  "i5": "আপনার অ্যাকাউন্টে যুক্ত মৃত্যু রেকর্ডে নামের সংশোধন দাখিল করুন, নামটি "
        "'{haque_sr}' করে।",
  "i6": "{office_passport}-এ 2026-06-23 তারিখে 10:30-এ একটি পাসপোর্ট "
        "এনরোলমেন্ট অ্যাপয়েন্টমেন্ট বুক করুন।",
  "i7": "করদাতা শনাক্তকরণ নম্বর 111111111111 যাচাই করে নিবন্ধিত নাম জানান।",
  "j1": "আপনার পরিচয়পত্রের মুদ্রণযোগ্য কপি খুলে মায়ের নাম ও দেখানো স্থায়ী "
        "ঠিকানা দুটিই জানান।",
 },
 "hi": {
  "src_2": "अपने पहचान पत्र में दर्ज नाम का सुधार दाखिल करें, नाम बदलकर "
           "'{nid_new_name}' करें, एक सहायक दस्तावेज़ संलग्न करके।",
  "src_6": "एक नया पासपोर्ट आवेदन शुरू से अंत तक भरकर दाखिल करें: "
           "व्यक्तिगत जानकारी, फिर पता, फिर पृष्ठ संख्या, वैधता और "
           "डिलीवरी।",
  "src_8": "{office_passport} में 22 जून 2026 को 10:30 बजे पासपोर्ट नामांकन "
           "अपॉइंटमेंट बुक करें।",
  "src_16": "उपभोक्ता संख्या 08000007 का बकाया बिजली बिल BL0000005 "
            "चुकाएँ।",
  "src_25": "पूरी आवेदन प्रक्रिया के माध्यम से नई करदाता पहचान संख्या के "
            "लिए पंजीकरण करें।",
  "src_31": "पर्ची संख्या NI9999999 वाला पहचान सुधार अनुरोध देखें और उसकी "
            "स्थिति बताएँ। ऐसा कोई अभिलेख न हो तो NO_RECORD उत्तर दें।",
  "src_32": "{mouza} मौज़ा ({upazila}, {district}, {division} विभाग) में "
            "खतियान संख्या 99999 देखें। ऐसा कोई अभिलेख न हो तो NO_RECORD "
            "उत्तर दें।",
  "src_33": "रोल नंबर 999999, {board} बोर्ड, 2021 का माध्यमिक (secondary) "
            "परिणाम प्राप्त करें। ऐसा कोई परिणाम न हो तो NO_RECORD उत्तर "
            "दें।",
  "new_34": "अपना बिजली बिलिंग इतिहास खोलें और 2026-01 के बिल की राशि नोट "
            "करें। बिजली शुल्क सूची में वह शुल्क खोजें जिसकी राशि उस बिल "
            "राशि से नीचे रहते हुए सबसे अधिक है, और उस शुल्क के वैरिएंट "
            "का नाम उत्तर दें। फिर अपने मीटर का सबसे पुराना बकाया बिल "
            "चुकाएँ।",
  "new_35": "भूमि अभिलेख खोज के माध्यम से {district} ज़िले में कहीं स्थित "
            "खतियान संख्या 4438 खोजें (उपज़िला और मौज़ा नहीं दिए गए हैं) "
            "और उसमें दर्ज प्लॉट संख्या बताएँ।",
  "new_36": "रोल नंबर 763370 का 2021 का माध्यमिक (secondary) परीक्षा परिणाम "
            "देखें (बोर्ड नहीं दिया गया है — खोज पृष्ठ पर बोर्डों की सूची "
            "है) और परीक्षार्थी का संस्थान बताएँ।",
  "new_37": "पंजीकरण संख्या 20000000000373 वाला जन्म पंजीकरण अभिलेख "
            "सत्यापित करें और उसकी पंजीकरण तिथि बताएँ।",
  "new_38": "बिजली सेवा पृष्ठ पर तीन सूचनाओं का शीर्षक एक ही है। 2025-10-12 "
            "को जारी हुई सूचना की श्रेणी बताएँ।",
  "new_39": "पासपोर्ट आवेदन PPA04000017 देखकर उसकी पुस्तिका के पृष्ठ और "
            "वैधता पढ़ें, फिर पासपोर्ट शुल्क सूची से ठीक उसी पृष्ठ/वैधता "
            "संयोजन का एक्सप्रेस (express) डिलीवरी शुल्क बताएँ।",
  "new_40": "अपना बिजली बिलिंग इतिहास खोलें और सभी छह बिलिंग अवधियों की "
            "कुल बिल राशि बताएँ।",
  "a1": "अपना बिजली बिलिंग इतिहास खोलें और 2026-01 के बिल की राशि नोट करें। "
        "ड्राइविंग लाइसेंस शुल्क सूची में वह सबसे महँगा शुल्क खोजें जो उस "
        "बिल राशि से नीचे है, फिर ठीक उसी श्रेणी/वैरिएंट का चालान बनाकर "
        "(कार्ड से, card) भुगतान करें और चुकाई गई राशि बताएँ।",
  "a2": "उपभोक्ता संख्या 08000049 की कुल बकाया राशि देखें। बिजली शुल्क सूची "
        "में वह सबसे महँगा शुल्क खोजें जो उस कुल के आधे से नीचे है, और उस "
        "शुल्क के वैरिएंट का नाम उत्तर दें।",
  "b1": "अपनी उपभोक्ता संख्या 08000007 के दोनों बकाया बिजली बिल कार्ड से "
        "(card) चुकाएँ।",
  "b2": "उपभोक्ता संख्या 08000021 के एक से अधिक बिजली बिल बकाया हैं। केवल "
        "सबसे पुराना बिल (कार्ड से, card) चुकाएँ और बाकी बकाया रहने दें।",
  "b3": "उपभोक्ता संख्या 08000049 की कुल बकाया राशि उपभोक्ता संख्या 08000035 "
        "से कितनी अधिक है? अंतर उत्तर दें।",
  "b4": "अपने दो बकायों की तुलना करें: उपभोक्ता संख्या 08000007 का कुल "
        "अवैतनिक बिजली बिल, और होल्डिंग HLD00001 का कुल अवैतनिक भूमि विकास "
        "कर। दोनों में से बड़ी राशि उत्तर दें।",
  "b5": "आपके बिजली बिलिंग इतिहास में कितने बिलों की राशि २००० से अधिक थी? "
        "संख्या उत्तर दें।",
  "c1": "भूमि अभिलेख खोज के माध्यम से {district} ज़िले ({division} विभाग; "
        "उपज़िला और मौज़ा नहीं दिए गए हैं) में कहीं स्थित खतियान संख्या "
        "5265 खोजें और उसमें दर्ज मालिक बताएँ।",
  "c2": "{mouza} मौज़ा ({upazila}, {district}, {division} विभाग) में खतियान "
        "संख्या 9458 देखें और तीन बातें बताएँ: मालिक, भूमि का प्रकार और "
        "डेसिमल में क्षेत्रफल।",
  "c3": "{mouza} मौज़ा ({upazila}, {district}, {division} विभाग) में खतियान "
        "संख्या 6743 देखें, फिर उस अभिलेख से नक़ल करते हुए नामांतरण के लिए "
        "आवेदन करें: विक्रेता का नाम = दर्ज मालिक, प्लॉट संख्या और "
        "क्षेत्रफल जैसे दर्ज हैं। क्रेता के रूप में स्वयं को रखें (क्रेता "
        "आईडी 9999708182203), विक्रेता आईडी 9999000000002।",
  "c4": "होल्डिंग HLD00003 पर कई वर्षों का भूमि विकास कर बकाया है। इसके सभी "
        "बकाया देय कार्ड से (card) चुकाएँ।",
  "c5": "कुल बकाया भूमि विकास कर किस होल्डिंग पर अधिक है: HLD00003 या "
        "HLD00004? होल्डिंग संख्या उत्तर दें।",
  "c6": "भूमि अभिलेख खोज में {upazila} उपज़िला ({district} ज़िला, {division} "
        "विभाग) तक जाएँ और {mouza} मौज़ा का JL नंबर बताएँ।",
  "c7": "भूमि अभिलेख खोज के माध्यम से {division} विभाग में कहीं स्थित खतियान "
        "संख्या 2052 खोजें (ज़िला, उपज़िला और मौज़ा नहीं दिए गए हैं) और "
        "उसमें दर्ज मालिक बताएँ।",
  "c8": "{district} ज़िले ({division} विभाग; उपज़िला और मौज़ा नहीं दिए गए "
        "हैं) में कहीं स्थित खतियान संख्या 8630 खोजें और मालिक तथा डेसिमल "
        "में क्षेत्रफल दोनों बताएँ।",
  "c9": "भूमि अभिलेख खोज के माध्यम से {district} ज़िले ({division} विभाग; "
        "उपज़िला और मौज़ा नहीं दिए गए हैं) में कहीं स्थित खतियान संख्या "
        "3232 खोजें और उसमें दर्ज भूमि का प्रकार बताएँ।",
  "c10": "होल्डिंग HLD00003 पर सबसे हाल के वित्तीय वर्ष को छोड़कर हर बकाया "
         "भूमि विकास कर कार्ड से (card) चुकाएँ — सबसे नया बकाया अवैतनिक "
         "रहना चाहिए।",
  "c11": "कुल बकाया भूमि विकास कर किस होल्डिंग पर अधिक है: HLD00004 या "
         "HLD00005? होल्डिंग संख्या उत्तर दें।",
  "e1": "रोल नंबर 244479 का 2021 का माध्यमिक (secondary) परीक्षा परिणाम देखें "
        "(बोर्ड नहीं दिया गया है — खोज पृष्ठ पर बोर्डों की सूची है), फिर "
        "उस परिणाम के लिए पुनर्जाँच आवेदन दाखिल करें, परिणाम में दिखाई "
        "पंजीकरण संख्या, उसका बोर्ड और वर्ष लिखते हुए, विषय {math} के लिए।",
  "e2": "रोल नंबर 969953 का {year} का {exam_l} ({exam}) परीक्षा परिणाम देखें "
        "(बोर्ड नहीं दिया गया है — खोज पृष्ठ पर बोर्डों की सूची है), फिर "
        "उस परिणाम के लिए पुनर्जाँच आवेदन दाखिल करें, परिणाम में दिखाई "
        "पंजीकरण संख्या, उसका बोर्ड और वर्ष लिखते हुए, विषय {eng} के लिए।",
  "e3": "पोर्टल के सूचना पट पर भूमि सेवा की सूचनाएँ छाँटें। उस सेवा ने कौन "
        "सी श्रेणी सबसे अधिक बार इस्तेमाल की? श्रेणी उत्तर दें।",
  "e4": "TIN 972871718941 के साथ कर निर्धारण वर्ष 2025-2026 का व्यक्तिगत "
        "ई-रिटर्न दाखिल करें: कुल आय ६४००००, कटौतियाँ ठीक आय का आठवाँ "
        "हिस्सा, और देय कर ठीक (आय घटा कटौतियाँ) का १०%। सभी राशियाँ "
        "सादे अंकों में लिखें, घोषणा YES।",
  "e5": "संदर्भ {ref} वाली सूचना पोर्टल के सूचना पट पर है (होम पेज से लिंक "
        "है)। पता करें कि किस सेवा ने इसे जारी किया, उस सेवा की शुल्क सूची "
        "खोलें और वहाँ सूचीबद्ध सबसे सस्ती शुल्क राशि बताएँ।",
  "g1": "दोनों काम करें: उपभोक्ता संख्या 08000007 का बिजली बिल BL0000006 "
        "चुकाएँ, और प्रीपेड मीटर MTR000006 को ७५० से रिचार्ज करें। कार्ड "
        "से (card) भुगतान करें।",
  "g2": "पूरे फ़ॉर्म के माध्यम से नया मतदाता पंजीकरण पूरा करें (आपका नाम, "
        "माता-पिता का विवरण, जन्म तिथि, दोनों पते और केंद्र के रूप में "
        "{centre}), और साथ ही {office_passport} में 2026-06-25 को 15:00 बजे "
        "पासपोर्ट नामांकन अपॉइंटमेंट बुक करें।",
  "g3": "ये दोनों आवेदन दाखिल करें: विदेश में रोज़गार के लिए पुलिस क्लियरेंस "
        "प्रमाणपत्र (नाम, माता-पिता का विवरण, जन्म तिथि और दोनों पते), "
        "और एक तीर्थयात्रा पूर्व-पंजीकरण (नाम, पिता का नाम, पासपोर्ट "
        "संख्या PPA04000017, वर्तमान पता, आपका मोबाइल, निकट संबंधी के रूप "
        "में आपकी माता, सरकारी (government) पैकेज)।",
  "g4": "नामांतरण के लिए आवेदन करें (क्रेता: आप स्वयं, आईडी 9999708182203; "
        "विक्रेता {rafiqul}, आईडी 9999000000001; खतियान 4438, प्लॉट 357, "
        "क्षेत्रफल 25), और साथ ही होल्डिंग HLD00002 का बकाया भूमि विकास कर "
        "कार्ड से (card) चुकाएँ।",
  "g5": "उपभोक्ता संख्या 08000007 पर केवल सबसे नया बकाया बिजली बिल कार्ड से "
        "(card) चुकाएँ, पुराना बकाया रहने दें।",
  "h1": "पोर्टल का सूचना पट खोलें (होम पेज से लिंक है)। सभी सेवाओं को मिलाकर "
        "फ़रवरी २०२६ में कितनी सूचनाएँ जारी हुईं? संख्या उत्तर दें।",
  "h2": "पोर्टल के सूचना पट के अनुसार २०२५ में किस सेवा ने सबसे अधिक सूचनाएँ "
        "जारी कीं? सेवा का नाम उत्तर दें।",
  "h3": "पोर्टल के सूचना पट की सबसे पुरानी सूचना का सटीक शीर्षक बताएँ।",
  "h4": "पोर्टल के सूचना पट पर २०२६ में जारी कितनी सूचनाओं की श्रेणी "
        "'{closure}' है? संख्या उत्तर दें।",
  "n1": "रोल नंबर 496396 का {year} का {exam_l} ({exam}) परीक्षा परिणाम खोजें "
        "— बोर्ड नहीं दिया गया है, खोज पृष्ठ पर बोर्डों की सूची है। "
        "परीक्षार्थी का GPA और संस्थान दोनों बताएँ।",
  "n2": "रोल नंबर 969525 का {year} का {exam_l} ({exam}) परीक्षा परिणाम खोजें "
        "— बोर्ड नहीं दिया गया है। परीक्षार्थी का नाम और GPA दोनों बताएँ।",
  "n3": "भूमि अभिलेख खोज के माध्यम से {district} ज़िले ({division} विभाग; "
        "उपज़िला और मौज़ा नहीं दिए गए हैं) में कहीं स्थित खतियान संख्या "
        "7191 खोजें और उसमें दर्ज भूमि का प्रकार बताएँ।",
  "n4": "{district} ज़िले ({division} विभाग; उपज़िला और मौज़ा नहीं दिए गए "
        "हैं) में कहीं स्थित खतियान संख्या 1022 खोजें और मालिक तथा दर्ज "
        "हिस्सा दोनों बताएँ।",
  "n5": "पोर्टल के सूचना पट पर ठीक एक सूचना जून २०२६ में जारी हुई। उसकी "
        "संदर्भ संख्या और उसे जारी करने वाली सेवा का नाम — दोनों बताएँ।",
  "n6": "२०२६ में किस महीने में पोर्टल के सूचना पट पर सबसे कम सूचनाएँ आईं? "
        "महीना YYYY-MM के रूप में उत्तर दें।",
  "n7": "उपभोक्ता संख्याओं 08000021, 08000035 और 08000049 का कुल बकाया बिजली "
        "बिल देखें और तीनों का संयुक्त कुल बताएँ।",
  "n8": "होल्डिंग HLD00003, HLD00004 और HLD00005 के सभी बकाया भूमि विकास कर "
        "का संयुक्त कुल बताएँ।",
  "n9": "आपके बिजली बिलिंग इतिहास की सभी छह अवधियों में कुल कितनी यूनिट "
        "(kWh) खपत हुईं?",
  "n10": "पासपोर्ट शुल्क सूची में सबसे महँगे शुल्क और सबसे सस्ते शून्येतर "
         "शुल्क का अंतर क्या है?",
  "n11": "पासपोर्ट और ड्राइविंग लाइसेंस शुल्क सूचियों को मिलाकर कितनी शुल्क "
         "पंक्तियों की राशि ५००० से अधिक है? संख्या उत्तर दें।",
  "n12": "TIN 972871718941 के साथ कर निर्धारण वर्ष 2025-2026 का व्यक्तिगत "
         "ई-रिटर्न दाखिल करें: कुल आय ७२००००, कटौतियाँ ठीक आय का चौथाई, "
         "और देय कर ठीक (आय घटा कटौतियाँ) का १५%। सभी राशियाँ सादे अंकों "
         "में लिखें, घोषणा YES।",
  "n13": "पंजीकरण संख्या 20000000000373 वाला जन्म पंजीकरण अभिलेख देखें। फिर "
         "एक नए बच्चे के लिए जन्म पंजीकरण आवेदन दाखिल करें, जिसका नाम ठीक "
         "उस अभिलेख की माता के नाम पर हो, जन्म 2026-03-01, उस अभिलेख में "
         "दर्ज स्थान पर, पिता के रूप में आप स्वयं और माता के रूप में आपकी "
         "माता।",
  "n14": "पोर्टल के सूचना पट की सबसे पुरानी सूचना खोजें, नोट करें कि किस "
         "सेवा ने इसे जारी किया, फिर उस सेवा की शुल्क सूची खोलें और उसकी "
         "सबसे महँगी शुल्क राशि बताएँ।",
  "n15": "दोनों करें: {office_licence} में सबसे पहली उपलब्ध तिथि पर सबसे पहले "
         "समय का ड्राइविंग टेस्ट बुक करें, और नवीनीकरण श्रेणी, पेशेवर "
         "वैरिएंट का चालान बनाकर (कार्ड से, card) भुगतान करें। फिर चुकाई "
         "गई चालान राशि बताएँ।",
  "n16": "पासपोर्ट आवेदन PPA04000034 और PPA04000068 देखकर हर एक की पुस्तिका "
         "के पृष्ठ और वैधता पढ़ें। पासपोर्ट शुल्क सूची के अनुसार किस आवेदन "
         "का नियमित (regular) डिलीवरी शुल्क अधिक है? आवेदन आईडी उत्तर दें।",
  "n17": "तीनों काम करें: उपभोक्ता 08000007 का बिजली बिल BL0000005 चुकाएँ, "
         "होल्डिंग HLD00002 का बकाया भूमि विकास कर चुकाएँ, और "
         "{office_passport} में 2026-06-24 को 11:30 बजे पासपोर्ट नामांकन "
         "अपॉइंटमेंट बुक करें। कार्ड से (card) भुगतान करें।",
  "n18": "होल्डिंग HLD00003 पर केवल 2022-2023 का भूमि विकास कर बकाया (कार्ड "
         "से, card) चुकाएँ, पुराना और नया दोनों बकाया अवैतनिक रहने दें।",
  "n19": "तीन सुधार दाखिल करें: अपने पहचान अभिलेख का वर्तमान पता '{new_addr}' "
         "और उसकी जन्म तिथि {new_dob} करें, और अपने जुड़े जन्म पंजीकरण "
         "अभिलेख का नाम बदलकर '{hoque}' करें। हर एक में लॉकर का कोई भी "
         "दस्तावेज़ संलग्न करें।",
  "n20": "दोनों पासपोर्ट अनुरोध दाखिल करें: एक नया आवेदन (आपका नाम, जन्म "
         "तिथि और पिता का नाम; दोनों पते; 64 पृष्ठ, 10 वर्ष वैधता, "
         "एक्सप्रेस (express) डिलीवरी), और पासपोर्ट संख्या A6053903 के लिए "
         "'{damaged}' कारण के साथ पुनर्निर्गम आवेदन।",
  "i1": "मीटर MTR000001 को ३०० से कार्ड से (card) रिचार्ज करें।",
  "i2": "पहचान संख्या 9999708182203, पंजीकरण 2023-09-16 का टीकाकरण प्रमाणपत्र "
        "डाउनलोड करें और प्रमाणपत्र संख्या बताएँ।",
  "i3": "आवेदन PPA04000017 के पासपोर्ट की डिलीवरी स्थिति देखें और बताएँ।",
  "i4": "श्रेणी {cat_licence}, वैरिएंट {var_motorcycle} का शुल्क चालान बनाकर "
        "भुगतान करें।",
  "i5": "अपने खाते से जुड़े मृत्यु अभिलेख में नाम का सुधार दाखिल करें, नाम "
        "बदलकर '{haque_sr}' करें।",
  "i6": "{office_passport} में 2026-06-23 को 10:30 बजे पासपोर्ट नामांकन "
        "अपॉइंटमेंट बुक करें।",
  "i7": "करदाता पहचान संख्या 111111111111 सत्यापित करें और पंजीकृत नाम "
        "बताएँ।",
  "j1": "अपने पहचान पत्र की मुद्रण योग्य प्रति खोलें और दिखाए गए माता के "
        "नाम और स्थायी पते — दोनों बताएँ।",
 },
 "ur": {
  "src_2": "اپنے شناختی کارڈ پر درج نام کی تصحیح جمع کریں، نام بدل کر "
           "'{nid_new_name}' کریں، ایک معاون دستاویز منسلک کر کے۔",
  "src_6": "ایک نئی پاسپورٹ درخواست شروع سے آخر تک بھر کر جمع کریں: ذاتی "
           "معلومات، پھر پتہ، پھر صفحات کی تعداد، میعاد اور ڈیلیوری۔",
  "src_8": "{office_passport} میں 22 جون 2026 کو 10:30 بجے پاسپورٹ اندراج "
           "اپائنٹمنٹ بک کریں۔",
  "src_16": "صارف نمبر 08000007 کا بقایا بجلی بل BL0000005 ادا کریں۔",
  "src_25": "مکمل درخواستی عمل کے ذریعے نئے ٹیکس دہندہ شناختی نمبر کے لیے "
            "رجسٹر ہوں۔",
  "src_31": "سلپ نمبر NI9999999 والی شناختی تصحیح کی درخواست دیکھیں اور اس "
            "کی حیثیت بتائیں۔ ایسا کوئی ریکارڈ نہ ہو تو NO_RECORD جواب دیں۔",
  "src_32": "{mouza} موضع ({upazila}، {district}، {division} ڈویژن) میں "
            "کھتیان نمبر 99999 دیکھیں۔ ایسا کوئی ریکارڈ نہ ہو تو NO_RECORD "
            "جواب دیں۔",
  "src_33": "رول نمبر 999999، {board} بورڈ، 2021 کا سیکنڈری (secondary) "
            "نتیجہ حاصل کریں۔ ایسا کوئی نتیجہ نہ ہو تو NO_RECORD جواب دیں۔",
  "new_34": "اپنا بجلی بلنگ تاریخچہ کھولیں اور 2026-01 کے بل کی رقم نوٹ "
            "کریں۔ بجلی فیس فہرست میں وہ فیس تلاش کریں جس کی رقم اس بل کی "
            "رقم سے کم رہتے ہوئے سب سے زیادہ ہے، اور اس فیس کے ویرینٹ کا "
            "نام جواب دیں۔ پھر اپنے میٹر کا سب سے پرانا بقایا بل ادا کریں۔",
  "new_35": "لینڈ ریکارڈ تلاش کے ذریعے {district} ضلع میں کہیں واقع کھتیان "
            "نمبر 4438 تلاش کریں (تحصیل اور موضع نہیں دیے گئے) اور اس میں "
            "درج پلاٹ نمبر بتائیں۔",
  "new_36": "رول نمبر 763370 کا 2021 کا سیکنڈری (secondary) امتحانی نتیجہ "
            "دیکھیں (بورڈ نہیں دیا گیا — تلاش کے صفحے پر بورڈوں کی فہرست "
            "ہے) اور امیدوار کا ادارہ بتائیں۔",
  "new_37": "رجسٹریشن نمبر 20000000000373 والے پیدائش رجسٹریشن ریکارڈ کی "
            "تصدیق کریں اور اس کی رجسٹریشن کی تاریخ بتائیں۔",
  "new_38": "بجلی سروس کے صفحے پر تین نوٹسز کا عنوان ایک ہی ہے۔ 2025-10-12 "
            "کو جاری ہونے والے نوٹس کا زمرہ بتائیں۔",
  "new_39": "پاسپورٹ درخواست PPA04000017 دیکھ کر اس کے کتابچے کے صفحات اور "
            "میعاد پڑھیں، پھر پاسپورٹ فیس فہرست سے بالکل اسی صفحات/میعاد "
            "امتزاج کی ایکسپریس (express) ڈیلیوری فیس بتائیں۔",
  "new_40": "اپنا بجلی بلنگ تاریخچہ کھولیں اور تمام چھ بلنگ مدتوں کی کل بل "
            "شدہ رقم بتائیں۔",
  "a1": "اپنا بجلی بلنگ تاریخچہ کھولیں اور 2026-01 کے بل کی رقم نوٹ کریں۔ "
        "ڈرائیونگ لائسنس فیس فہرست میں وہ سب سے مہنگی فیس تلاش کریں جو اس "
        "بل کی رقم سے کم ہے، پھر بالکل اسی زمرے/ویرینٹ کا چالان بنا کر "
        "(کارڈ سے، card) ادا کریں اور ادا کی گئی رقم بتائیں۔",
  "a2": "صارف نمبر 08000049 کی کل بقایا رقم دیکھیں۔ بجلی فیس فہرست میں وہ "
        "سب سے مہنگی فیس تلاش کریں جو اس کل کے نصف سے کم ہے، اور اس فیس "
        "کے ویرینٹ کا نام جواب دیں۔",
  "b1": "اپنے صارف نمبر 08000007 کے دونوں بقایا بجلی بل کارڈ سے (card) ادا "
        "کریں۔",
  "b2": "صارف نمبر 08000021 کے ایک سے زیادہ بجلی بل بقایا ہیں۔ صرف سب سے "
        "پرانا بل (کارڈ سے، card) ادا کریں اور باقی بقایا رہنے دیں۔",
  "b3": "صارف نمبر 08000049 کی کل بقایا رقم صارف نمبر 08000035 سے کتنی "
        "زیادہ ہے؟ فرق جواب دیں۔",
  "b4": "اپنے دو بقایا جات کا موازنہ کریں: صارف نمبر 08000007 کا کل غیر ادا "
        "شدہ بجلی بل، اور ہولڈنگ HLD00001 کا کل غیر ادا شدہ زمین ترقیاتی "
        "ٹیکس۔ دونوں میں سے بڑی رقم جواب دیں۔",
  "b5": "آپ کے بجلی بلنگ تاریخچے میں کتنے بلوں کی رقم ۲۰۰۰ سے زیادہ تھی؟ "
        "تعداد جواب دیں۔",
  "c1": "لینڈ ریکارڈ تلاش کے ذریعے {district} ضلع ({division} ڈویژن؛ تحصیل "
        "اور موضع نہیں دیے گئے) میں کہیں واقع کھتیان نمبر 5265 تلاش کریں "
        "اور اس میں درج مالک بتائیں۔",
  "c2": "{mouza} موضع ({upazila}، {district}، {division} ڈویژن) میں کھتیان "
        "نمبر 9458 دیکھیں اور تین باتیں بتائیں: مالک، زمین کی قسم اور "
        "ڈیسیمل میں رقبہ۔",
  "c3": "{mouza} موضع ({upazila}، {district}، {division} ڈویژن) میں کھتیان "
        "نمبر 6743 دیکھیں، پھر اس ریکارڈ سے نقل کرتے ہوئے انتقال کی "
        "درخواست دیں: فروخت کنندہ کا نام = درج مالک، پلاٹ نمبر اور رقبہ "
        "جیسے درج ہیں۔ خریدار کے طور پر خود کو رکھیں (خریدار آئی ڈی "
        "9999708182203)، فروخت کنندہ آئی ڈی 9999000000002۔",
  "c4": "ہولڈنگ HLD00003 پر کئی سال کا زمین ترقیاتی ٹیکس بقایا ہے۔ اس کے "
        "تمام بقایا واجبات کارڈ سے (card) ادا کریں۔",
  "c5": "کل بقایا زمین ترقیاتی ٹیکس کس ہولڈنگ پر زیادہ ہے: HLD00003 یا "
        "HLD00004؟ ہولڈنگ نمبر جواب دیں۔",
  "c6": "لینڈ ریکارڈ تلاش میں {upazila} تحصیل ({district} ضلع، {division} "
        "ڈویژن) تک جائیں اور {mouza} موضع کا JL نمبر بتائیں۔",
  "c7": "لینڈ ریکارڈ تلاش کے ذریعے {division} ڈویژن میں کہیں واقع کھتیان "
        "نمبر 2052 تلاش کریں (ضلع، تحصیل اور موضع نہیں دیے گئے) اور اس میں "
        "درج مالک بتائیں۔",
  "c8": "{district} ضلع ({division} ڈویژن؛ تحصیل اور موضع نہیں دیے گئے) میں "
        "کہیں واقع کھتیان نمبر 8630 تلاش کریں اور مالک اور ڈیسیمل میں "
        "رقبہ دونوں بتائیں۔",
  "c9": "لینڈ ریکارڈ تلاش کے ذریعے {district} ضلع ({division} ڈویژن؛ تحصیل "
        "اور موضع نہیں دیے گئے) میں کہیں واقع کھتیان نمبر 3232 تلاش کریں "
        "اور اس میں درج زمین کی قسم بتائیں۔",
  "c10": "ہولڈنگ HLD00003 پر تازہ ترین مالی سال کے سوا ہر بقایا زمین ترقیاتی "
         "ٹیکس کارڈ سے (card) ادا کریں — سب سے نیا بقایا غیر ادا شدہ رہنا "
         "چاہیے۔",
  "c11": "کل بقایا زمین ترقیاتی ٹیکس کس ہولڈنگ پر زیادہ ہے: HLD00004 یا "
         "HLD00005؟ ہولڈنگ نمبر جواب دیں۔",
  "e1": "رول نمبر 244479 کا 2021 کا سیکنڈری (secondary) امتحانی نتیجہ دیکھیں "
        "(بورڈ نہیں دیا گیا — تلاش کے صفحے پر بورڈوں کی فہرست ہے)، پھر اس "
        "نتیجے کے لیے دوبارہ جانچ کی درخواست جمع کریں، نتیجے میں دکھایا "
        "گیا رجسٹریشن نمبر، اس کا بورڈ اور سال لکھتے ہوئے، مضمون {math} کے "
        "لیے۔",
  "e2": "رول نمبر 969953 کا {year} کا {exam_l} ({exam}) امتحانی نتیجہ دیکھیں "
        "(بورڈ نہیں دیا گیا — تلاش کے صفحے پر بورڈوں کی فہرست ہے)، پھر اس "
        "نتیجے کے لیے دوبارہ جانچ کی درخواست جمع کریں، نتیجے میں دکھایا "
        "گیا رجسٹریشن نمبر، اس کا بورڈ اور سال لکھتے ہوئے، مضمون {eng} کے "
        "لیے۔",
  "e3": "پورٹل کے نوٹس بورڈ پر زمین سروس کے نوٹسز چھانٹیں۔ اس سروس نے کون "
        "سا زمرہ سب سے زیادہ بار استعمال کیا؟ زمرہ جواب دیں۔",
  "e4": "TIN 972871718941 کے ساتھ تشخیصی سال 2025-2026 کا انفرادی ای-ریٹرن "
        "جمع کریں: کل آمدنی ۶۴۰۰۰۰، کٹوتیاں بالکل آمدنی کا آٹھواں حصہ، اور "
        "قابلِ ادا ٹیکس بالکل (آمدنی منفی کٹوتیاں) کا ۱۰٪۔ تمام رقمیں سادہ "
        "ہندسوں میں لکھیں، اقرار YES۔",
  "e5": "حوالہ {ref} والا نوٹس پورٹل کے نوٹس بورڈ پر ہے (ہوم پیج سے لنک "
        "ہے)۔ معلوم کریں کہ کس سروس نے اسے جاری کیا، اس سروس کی فیس فہرست "
        "کھولیں اور وہاں درج سب سے سستی فیس کی رقم بتائیں۔",
  "g1": "دونوں کام کریں: صارف نمبر 08000007 کا بجلی بل BL0000006 ادا کریں، "
        "اور پری پیڈ میٹر MTR000006 کو ۷۵۰ سے ری چارج کریں۔ کارڈ سے (card) "
        "ادائیگی کریں۔",
  "g2": "مکمل فارم کے ذریعے نئی ووٹر رجسٹریشن مکمل کریں (آپ کا نام، والدین "
        "کے کوائف، تاریخِ پیدائش، دونوں پتے اور مرکز کے طور پر {centre})، "
        "اور ساتھ ہی {office_passport} میں 2026-06-25 کو 15:00 بجے پاسپورٹ "
        "اندراج اپائنٹمنٹ بک کریں۔",
  "g3": "یہ دونوں درخواستیں جمع کریں: بیرونِ ملک ملازمت کے لیے پولیس کلیئرنس "
        "سرٹیفکیٹ (نام، والدین کے کوائف، تاریخِ پیدائش اور دونوں پتے)، اور "
        "ایک حج پیشگی رجسٹریشن (نام، والد کا نام، پاسپورٹ نمبر PPA04000017، "
        "موجودہ پتہ، آپ کا موبائل، قریبی رشتہ دار کے طور پر آپ کی والدہ، "
        "سرکاری (government) پیکج)۔",
  "g4": "انتقال کی درخواست دیں (خریدار: آپ خود، آئی ڈی 9999708182203؛ فروخت "
        "کنندہ {rafiqul}، آئی ڈی 9999000000001؛ کھتیان 4438، پلاٹ 357، رقبہ "
        "25)، اور ساتھ ہی ہولڈنگ HLD00002 کا بقایا زمین ترقیاتی ٹیکس کارڈ "
        "سے (card) ادا کریں۔",
  "g5": "صارف نمبر 08000007 پر صرف سب سے نیا بقایا بجلی بل کارڈ سے (card) "
        "ادا کریں، پرانا بقایا رہنے دیں۔",
  "h1": "پورٹل کا نوٹس بورڈ کھولیں (ہوم پیج سے لنک ہے)۔ تمام خدمات ملا کر "
        "فروری ۲۰۲۶ میں کتنے نوٹسز جاری ہوئے؟ تعداد جواب دیں۔",
  "h2": "پورٹل کے نوٹس بورڈ کے مطابق ۲۰۲۵ میں کس سروس نے سب سے زیادہ نوٹسز "
        "جاری کیے؟ سروس کا نام جواب دیں۔",
  "h3": "پورٹل کے نوٹس بورڈ کے سب سے پرانے نوٹس کا بعینہ عنوان بتائیں۔",
  "h4": "پورٹل کے نوٹس بورڈ پر ۲۰۲۶ میں جاری کتنے نوٹسز کا زمرہ '{closure}' "
        "ہے؟ تعداد جواب دیں۔",
  "n1": "رول نمبر 496396 کا {year} کا {exam_l} ({exam}) امتحانی نتیجہ تلاش "
        "کریں — بورڈ نہیں دیا گیا، تلاش کے صفحے پر بورڈوں کی فہرست ہے۔ "
        "امیدوار کا GPA اور ادارہ دونوں بتائیں۔",
  "n2": "رول نمبر 969525 کا {year} کا {exam_l} ({exam}) امتحانی نتیجہ تلاش "
        "کریں — بورڈ نہیں دیا گیا۔ امیدوار کا نام اور GPA دونوں بتائیں۔",
  "n3": "لینڈ ریکارڈ تلاش کے ذریعے {district} ضلع ({division} ڈویژن؛ تحصیل "
        "اور موضع نہیں دیے گئے) میں کہیں واقع کھتیان نمبر 7191 تلاش کریں "
        "اور اس میں درج زمین کی قسم بتائیں۔",
  "n4": "{district} ضلع ({division} ڈویژن؛ تحصیل اور موضع نہیں دیے گئے) میں "
        "کہیں واقع کھتیان نمبر 1022 تلاش کریں اور مالک اور درج حصہ دونوں "
        "بتائیں۔",
  "n5": "پورٹل کے نوٹس بورڈ پر بالکل ایک نوٹس جون ۲۰۲۶ میں جاری ہوا۔ اس کا "
        "حوالہ نمبر اور اسے جاری کرنے والی سروس کا نام — دونوں بتائیں۔",
  "n6": "۲۰۲۶ میں کس مہینے میں پورٹل کے نوٹس بورڈ پر سب سے کم نوٹسز آئے؟ "
        "مہینہ YYYY-MM کی صورت میں جواب دیں۔",
  "n7": "صارف نمبروں 08000021، 08000035 اور 08000049 کا کل بقایا بجلی بل "
        "دیکھیں اور تینوں کا مجموعی کل بتائیں۔",
  "n8": "ہولڈنگ HLD00003، HLD00004 اور HLD00005 کے تمام بقایا زمین ترقیاتی "
        "ٹیکس کا مجموعی کل بتائیں۔",
  "n9": "آپ کے بجلی بلنگ تاریخچے کی تمام چھ مدتوں میں کل کتنے یونٹ (kWh) "
        "استعمال ہوئے؟",
  "n10": "پاسپورٹ فیس فہرست میں سب سے مہنگی فیس اور سب سے سستی غیر صفر فیس "
         "کا فرق کیا ہے؟",
  "n11": "پاسپورٹ اور ڈرائیونگ لائسنس فیس فہرستوں کو ملا کر کتنی فیس قطاروں "
         "کی رقم ۵۰۰۰ سے زیادہ ہے؟ تعداد جواب دیں۔",
  "n12": "TIN 972871718941 کے ساتھ تشخیصی سال 2025-2026 کا انفرادی ای-ریٹرن "
         "جمع کریں: کل آمدنی ۷۲۰۰۰۰، کٹوتیاں بالکل آمدنی کا چوتھائی، اور "
         "قابلِ ادا ٹیکس بالکل (آمدنی منفی کٹوتیاں) کا ۱۵٪۔ تمام رقمیں سادہ "
         "ہندسوں میں لکھیں، اقرار YES۔",
  "n13": "رجسٹریشن نمبر 20000000000373 والا پیدائش رجسٹریشن ریکارڈ دیکھیں۔ "
         "پھر ایک نئے بچے کے لیے پیدائش رجسٹریشن درخواست جمع کریں، جس کا "
         "نام بالکل اس ریکارڈ کی والدہ کے نام پر ہو، پیدائش 2026-03-01، اس "
         "ریکارڈ میں درج جگہ پر، والد کے طور پر آپ خود اور والدہ کے طور پر "
         "آپ کی والدہ۔",
  "n14": "پورٹل کے نوٹس بورڈ کا سب سے پرانا نوٹس تلاش کریں، نوٹ کریں کہ کس "
         "سروس نے اسے جاری کیا، پھر اس سروس کی فیس فہرست کھولیں اور اس کی "
         "سب سے مہنگی فیس کی رقم بتائیں۔",
  "n15": "دونوں کریں: {office_licence} میں سب سے پہلی دستیاب تاریخ پر سب سے "
         "پہلے وقت کا ڈرائیونگ ٹیسٹ بک کریں، اور تجدید زمرے، پیشہ ور "
         "ویرینٹ کا چالان بنا کر (کارڈ سے، card) ادا کریں۔ پھر ادا کی گئی "
         "چالان رقم بتائیں۔",
  "n16": "پاسپورٹ درخواستیں PPA04000034 اور PPA04000068 دیکھ کر ہر ایک کے "
         "کتابچے کے صفحات اور میعاد پڑھیں۔ پاسپورٹ فیس فہرست کے مطابق کس "
         "درخواست کی معمولی (regular) ڈیلیوری فیس زیادہ ہے؟ درخواست آئی ڈی "
         "جواب دیں۔",
  "n17": "تینوں کام کریں: صارف 08000007 کا بجلی بل BL0000005 ادا کریں، "
         "ہولڈنگ HLD00002 کا بقایا زمین ترقیاتی ٹیکس ادا کریں، اور "
         "{office_passport} میں 2026-06-24 کو 11:30 بجے پاسپورٹ اندراج "
         "اپائنٹمنٹ بک کریں۔ کارڈ سے (card) ادائیگی کریں۔",
  "n18": "ہولڈنگ HLD00003 پر صرف 2022-2023 کا زمین ترقیاتی ٹیکس بقایا (کارڈ "
         "سے، card) ادا کریں، پرانا اور نیا دونوں بقایا غیر ادا شدہ رہنے "
         "دیں۔",
  "n19": "تین تصحیحات جمع کریں: اپنے شناختی ریکارڈ کا موجودہ پتہ '{new_addr}' "
         "اور اس کی تاریخِ پیدائش {new_dob} کریں، اور اپنے منسلک پیدائش "
         "رجسٹریشن ریکارڈ کا نام بدل کر '{hoque}' کریں۔ ہر ایک میں لاکر کی "
         "کوئی بھی دستاویز منسلک کریں۔",
  "n20": "دونوں پاسپورٹ درخواستیں جمع کریں: ایک نئی درخواست (آپ کا نام، "
         "تاریخِ پیدائش اور والد کا نام؛ دونوں پتے؛ 64 صفحات، 10 سال میعاد، "
         "ایکسپریس (express) ڈیلیوری)، اور پاسپورٹ نمبر A6053903 کے لیے "
         "'{damaged}' وجہ کے ساتھ دوبارہ اجرا کی درخواست۔",
  "i1": "میٹر MTR000001 کو ۳۰۰ سے کارڈ سے (card) ری چارج کریں۔",
  "i2": "شناختی نمبر 9999708182203، رجسٹریشن 2023-09-16 کا ویکسینیشن "
        "سرٹیفکیٹ ڈاؤن لوڈ کریں اور سرٹیفکیٹ نمبر بتائیں۔",
  "i3": "درخواست PPA04000017 کے پاسپورٹ کی ڈیلیوری حیثیت دیکھیں اور بتائیں۔",
  "i4": "زمرہ {cat_licence}، ویرینٹ {var_motorcycle} کا فیس چالان بنا کر ادا "
        "کریں۔",
  "i5": "اپنے اکاؤنٹ سے منسلک وفات ریکارڈ میں نام کی تصحیح جمع کریں، نام "
        "بدل کر '{haque_sr}' کریں۔",
  "i6": "{office_passport} میں 2026-06-23 کو 10:30 بجے پاسپورٹ اندراج "
        "اپائنٹمنٹ بک کریں۔",
  "i7": "ٹیکس دہندہ شناختی نمبر 111111111111 کی تصدیق کریں اور رجسٹرڈ نام "
        "بتائیں۔",
  "j1": "اپنے شناختی کارڈ کی قابلِ طباعت نقل کھولیں اور دکھایا گیا والدہ کا "
        "نام اور مستقل پتہ — دونوں بتائیں۔",
 },
 "am": {
  "src_2": "በመታወቂያ ካርድዎ ላይ የተመዘገበውን ስም ወደ '{nid_new_name}' በመቀየር "
           "እርማት ያስገቡ፤ ደጋፊ ሰነድ ያያይዙ።",
  "src_6": "አዲስ የፓስፖርት ማመልከቻ ከመጀመሪያ እስከ መጨረሻ ሞልተው ያስገቡ፡ የግል "
           "መረጃ፣ ከዚያ አድራሻ፣ ከዚያ የገጽ ብዛት፣ ተቀባይነትና አቅርቦት።",
  "src_8": "በ{office_passport} ለ22 ሰኔ 2026 በ10:30 የፓስፖርት ምዝገባ ቀጠሮ "
           "ይያዙ።",
  "src_16": "በደንበኛ ቁጥር 08000007 ላይ ያልተከፈለውን የኤሌክትሪክ ሂሳብ BL0000005 "
            "ይክፈሉ።",
  "src_25": "በሙሉ የማመልከቻ ሂደት አዲስ የግብር ከፋይ መለያ ቁጥር ይመዝገቡ።",
  "src_31": "የስሊፕ ቁጥር NI9999999 ያለውን የመታወቂያ እርማት ጥያቄ ይመልከቱና ሁኔታውን "
            "ይግለጹ። እንዲህ ያለ መዝገብ ከሌለ NO_RECORD ብለው ይመልሱ።",
  "src_32": "በ{mouza} ሙዛ ({upazila}፣ {district}፣ {division} ክልል) የካቲያን ቁጥር "
            "99999 ይመልከቱ። እንዲህ ያለ መዝገብ ከሌለ NO_RECORD ብለው ይመልሱ።",
  "src_33": "የሮል ቁጥር 999999፣ {board} ቦርድ፣ 2021 የሁለተኛ ደረጃ (secondary) ውጤት "
            "ያግኙ። እንዲህ ያለ ውጤት ከሌለ NO_RECORD ብለው ይመልሱ።",
  "new_34": "የኤሌክትሪክ ሂሳብ ታሪክዎን ከፍተው የ2026-01 ሂሳብ መጠን ያስተውሉ። በኤሌክትሪክ "
            "ክፍያ ዝርዝር ውስጥ ከዚያ የሂሳብ መጠን በታች ሆኖ ከፍተኛውን ክፍያ ያግኙና የዚያን "
            "ክፍያ የዓይነት ስም ይመልሱ። ከዚያ በቆጣሪዎ ላይ ያለውን በጣም አሮጌ ያልተከፈለ "
            "ሂሳብ ይክፈሉ።",
  "new_35": "በመሬት መዝገብ ፍለጋ በኩል በ{district} ወረዳ ውስጥ የሆነ ቦታ ያለውን የካቲያን "
            "ቁጥር 4438 ያግኙ (ንዑስ ወረዳውና ሙዛው አልተሰጡም) እና በላዩ የተመዘገበውን "
            "የቦታ ቁጥር ይግለጹ።",
  "new_36": "የሮል ቁጥር 763370 የ2021 የሁለተኛ ደረጃ (secondary) ፈተና ውጤት ይመልከቱ "
            "(ቦርዱ አልተሰጠም — የፍለጋ ገጹ ቦርዶቹን ይዘረዝራል) እና የተፈታኙን ተቋም "
            "ይግለጹ።",
  "new_37": "የምዝገባ ቁጥር 20000000000373 ያለውን የልደት ምዝገባ መዝገብ አረጋግጠው "
            "የምዝገባ ቀኑን ይግለጹ።",
  "new_38": "በኤሌክትሪክ አገልግሎት ገጽ ላይ ሦስት ማስታወቂያዎች አንድ ርዕስ አላቸው። በ2025-10-12 "
            "የወጣውን ምድብ ይግለጹ።",
  "new_39": "የፓስፖርት ማመልከቻ PPA04000017ን ተመልክተው የደብተሩን ገጾችና ተቀባይነት "
            "ያንብቡ፤ ከዚያ የፓስፖርት ክፍያ ዝርዝርን ተጠቅመው ለዚያው የገጽ/ተቀባይነት ጥምረት "
            "የፈጣን (express) አቅርቦት ክፍያ ይግለጹ።",
  "new_40": "የኤሌክትሪክ ሂሳብ ታሪክዎን ከፍተው በስድስቱም የሂሳብ ጊዜያት የተጠየቀውን "
            "ጠቅላላ መጠን ይግለጹ።",
  "a1": "የኤሌክትሪክ ሂሳብ ታሪክዎን ከፍተው የ2026-01 ሂሳብ መጠን ያስተውሉ። በመንጃ ፈቃድ "
        "ክፍያ ዝርዝር ውስጥ ከዚያ የሂሳብ መጠን በታች ሆኖ በጣም ውድ የሆነውን ክፍያ ያግኙ፤ "
        "ከዚያ ለዚያው ምድብ/ዓይነት ቻላን አዘጋጅተው (በካርድ፣ card) ይክፈሉና የከፈሉትን "
        "መጠን ይግለጹ።",
  "a2": "በደንበኛ ቁጥር 08000049 ላይ ያለውን ጠቅላላ ያልተከፈለ መጠን ይመልከቱ። በኤሌክትሪክ "
        "ክፍያ ዝርዝር ውስጥ ከዚያ ጠቅላላ ግማሽ በታች ሆኖ በጣም ውድ የሆነውን ክፍያ ያግኙና "
        "የዚያን ክፍያ የዓይነት ስም ይመልሱ።",
  "b1": "በደንበኛ ቁጥርዎ 08000007 ላይ ያሉትን ሁለቱንም ያልተከፈሉ የኤሌክትሪክ ሂሳቦች በካርድ "
        "(card) ይክፈሉ።",
  "b2": "ደንበኛ ቁጥር 08000021 ከአንድ በላይ ያልተከፈለ የኤሌክትሪክ ሂሳብ አለው። በጣም "
        "አሮጌውን ብቻ (በካርድ፣ card) ይክፈሉና ቀሪዎቹን ሳይከፈሉ ይተዉ።",
  "b3": "በደንበኛ ቁጥር 08000049 ላይ ያለው ጠቅላላ ያልተከፈለ መጠን ከደንበኛ ቁጥር 08000035 "
        "በምን ያህል ይበልጣል? ልዩነቱን ይመልሱ።",
  "b4": "ሁለት ያልተከፈሉ ሂሳቦችዎን ያወዳድሩ፡ በደንበኛ ቁጥር 08000007 ላይ ያለው ጠቅላላ "
        "ያልተከፈለ ኤሌክትሪክ፣ እና በይዞታ HLD00001 ላይ ያለው ጠቅላላ ያልተከፈለ የመሬት "
        "ልማት ግብር። ከሁለቱ መጠኖች ትልቁን ይመልሱ።",
  "b5": "በኤሌክትሪክ ሂሳብ ታሪክዎ ውስጥ ስንት ሂሳቦች ከ2000 መጠን በላይ ነበሩ? ቁጥሩን "
        "ይመልሱ።",
  "c1": "በመሬት መዝገብ ፍለጋ በኩል በ{district} ወረዳ ({division} ክልል፤ ንዑስ ወረዳውና "
        "ሙዛው አልተሰጡም) ውስጥ የሆነ ቦታ ያለውን የካቲያን ቁጥር 5265 ያግኙና በላዩ "
        "የተመዘገበውን ባለቤት ይግለጹ።",
  "c2": "በ{mouza} ሙዛ ({upazila}፣ {district}፣ {division} ክልል) የካቲያን ቁጥር 9458 "
        "ይመልከቱና ሦስት ነገሮች ይግለጹ፡ ባለቤቱን፣ የመሬት ዓይነቱን እና ስፋቱን በዴሲማል።",
  "c3": "በ{mouza} ሙዛ ({upazila}፣ {district}፣ {division} ክልል) የካቲያን ቁጥር 6743 "
        "ይመልከቱ፤ ከዚያ ከዚያ መዝገብ በመቅዳት ለመሬት ባለቤትነት ዝውውር ያመልክቱ፡ የሻጭ ስም = "
        "የተመዘገበው ባለቤት፣ የቦታ ቁጥርና ስፋት እንደተመዘገበው። ራስዎን እንደ ገዢ ይጠቀሙ "
        "(የገዢ መታወቂያ 9999708182203)፣ የሻጭ መታወቂያ 9999000000002።",
  "c4": "ይዞታ HLD00003 የበርካታ ዓመታት ያልተከፈለ የመሬት ልማት ግብር አለበት። ሁሉንም "
        "ያልተከፈሉ ዕዳዎቹን በካርድ (card) ይክፈሉ።",
  "c5": "በጠቅላላ ያልተከፈለ የመሬት ልማት ግብር የትኛው ይዞታ የበለጠ ዕዳ አለበት፡ HLD00003 "
        "ወይስ HLD00004? የይዞታ ቁጥሩን ይመልሱ።",
  "c6": "በመሬት መዝገብ ፍለጋ ውስጥ ወደ {upazila} ንዑስ ወረዳ ({district} ወረዳ፣ "
        "{division} ክልል) ሄደው የ{mouza} ሙዛ JL ቁጥር ይግለጹ።",
  "c7": "በመሬት መዝገብ ፍለጋ በኩል በ{division} ክልል ውስጥ የሆነ ቦታ ያለውን የካቲያን ቁጥር "
        "2052 ያግኙ (ወረዳው፣ ንዑስ ወረዳውና ሙዛው አልተሰጡም) እና በላዩ የተመዘገበውን "
        "ባለቤት ይግለጹ።",
  "c8": "በ{district} ወረዳ ({division} ክልል፤ ንዑስ ወረዳውና ሙዛው አልተሰጡም) ውስጥ የሆነ "
        "ቦታ ያለውን የካቲያን ቁጥር 8630 ያግኙና ባለቤቱንም ስፋቱንም በዴሲማል ይግለጹ።",
  "c9": "በመሬት መዝገብ ፍለጋ በኩል በ{district} ወረዳ ({division} ክልል፤ ንዑስ ወረዳውና "
        "ሙዛው አልተሰጡም) ውስጥ የሆነ ቦታ ያለውን የካቲያን ቁጥር 3232 ያግኙና በላዩ "
        "የተመዘገበውን የመሬት ዓይነት ይግለጹ።",
  "c10": "በይዞታ HLD00003 ላይ ከቅርቡ የበጀት ዓመት በስተቀር እያንዳንዱን ያልተከፈለ የመሬት "
         "ልማት ግብር ዕዳ በካርድ (card) ይክፈሉ — በጣም አዲሱ ዕዳ ሳይከፈል መቆየት አለበት።",
  "c11": "በጠቅላላ ያልተከፈለ የመሬት ልማት ግብር የትኛው ይዞታ የበለጠ ዕዳ አለበት፡ HLD00004 "
         "ወይስ HLD00005? የይዞታ ቁጥሩን ይመልሱ።",
  "e1": "የሮል ቁጥር 244479 የ2021 የሁለተኛ ደረጃ (secondary) ፈተና ውጤት ይመልከቱ (ቦርዱ "
        "አልተሰጠም — የፍለጋ ገጹ ቦርዶቹን ይዘረዝራል)፤ ከዚያ ለዚያ ውጤት የዳግም ምርመራ "
        "ማመልከቻ ያስገቡ፤ በውጤቱ ላይ የሚታየውን የምዝገባ ቁጥር፣ ቦርዱንና ዓመቱን "
        "በማስገባት፣ ለትምህርት {math}።",
  "e2": "የሮል ቁጥር 969953 የ{year} የ{exam_l} ({exam}) ፈተና ውጤት ይመልከቱ (ቦርዱ "
        "አልተሰጠም — የፍለጋ ገጹ ቦርዶቹን ይዘረዝራል)፤ ከዚያ ለዚያ ውጤት የዳግም ምርመራ "
        "ማመልከቻ ያስገቡ፤ በውጤቱ ላይ የሚታየውን የምዝገባ ቁጥር፣ ቦርዱንና ዓመቱን "
        "በማስገባት፣ ለትምህርት {eng}።",
  "e3": "በፖርታሉ የማስታወቂያ ሰሌዳ ላይ ወደ መሬት አገልግሎት ማስታወቂያዎች ያጣሩ። ያ አገልግሎት "
        "የትኛውን ምድብ በብዛት ተጠቀመ? ምድቡን ይመልሱ።",
  "e4": "በTIN 972871718941 ለግምገማ ዓመት 2025-2026 የግል ኢ-ሪተርን ያስገቡ፡ ጠቅላላ ገቢ "
        "640000፣ ተቀናሾች በትክክል የገቢው አንድ ስምንተኛ፣ እና የሚከፈል ግብር በትክክል የ(ገቢ "
        "ሲቀነስ ተቀናሾች) 10%። ሁሉንም መጠኖች እንደ ተራ አሃዞች ያስገቡ፣ መግለጫ YES።",
  "e5": "ማጣቀሻ {ref} ያለው ማስታወቂያ በፖርታሉ የማስታወቂያ ሰሌዳ ላይ ይገኛል (ከመነሻ ገጹ "
        "ተያይዟል)። የትኛው አገልግሎት እንዳወጣው ያግኙ፣ የዚያን አገልግሎት የክፍያ ዝርዝር "
        "ይክፈቱ፣ እና እዚያ የተዘረዘረውን በጣም ርካሽ የክፍያ መጠን ይግለጹ።",
  "g1": "ሁለቱንም ያድርጉ፡ በደንበኛ ቁጥር 08000007 ላይ የኤሌክትሪክ ሂሳብ BL0000006 ይክፈሉ፣ "
        "እና የቅድመ ክፍያ ቆጣሪ MTR000006ን በ750 ይሙሉ። በካርድ (card) ይክፈሉ።",
  "g2": "አዲስ የመራጭ ምዝገባን በሙሉ ቅጹ ያጠናቅቁ (ስምዎ፣ የወላጅነት መረጃ፣ የልደት ቀን፣ "
        "ሁለቱም አድራሻዎችና እንደ ማዕከል {centre})፣ እንዲሁም በ{office_passport} "
        "ለ2026-06-25 በ15:00 የፓስፖርት ምዝገባ ቀጠሮ ይያዙ።",
  "g3": "እነዚህን ሁለቱንም ማመልከቻዎች ያስገቡ፡ ለውጭ አገር ሥራ የፖሊስ ክሊራንስ ምስክር ወረቀት "
        "(ስም፣ የወላጅነት መረጃ፣ የልደት ቀንና ሁለቱም አድራሻዎች)፣ እና የሐጅ ቅድመ ምዝገባ "
        "(ስም፣ የአባት ስም፣ የፓስፖርት ቁጥር PPA04000017፣ የአሁን አድራሻ፣ ሞባይልዎ፣ "
        "እናትዎ እንደ ቅርብ ዘመድ፣ የመንግሥት (government) ፓኬጅ)።",
  "g4": "ለመሬት ባለቤትነት ዝውውር ያመልክቱ (ገዢ፡ ራስዎ፣ መታወቂያ 9999708182203፤ ሻጭ "
        "{rafiqul}፣ መታወቂያ 9999000000001፤ ካቲያን 4438፣ ቦታ 357፣ ስፋት 25)፣ "
        "እንዲሁም በይዞታ HLD00002 ላይ ያልተከፈለውን የመሬት ልማት ግብር በካርድ (card) "
        "ይክፈሉ።",
  "g5": "በደንበኛ ቁጥር 08000007 ላይ በጣም አዲሱን ያልተከፈለ የኤሌክትሪክ ሂሳብ ብቻ በካርድ "
        "(card) ይክፈሉ፤ አሮጌውን ሳይከፈል ይተዉ።",
  "h1": "የፖርታሉን የማስታወቂያ ሰሌዳ ይክፈቱ (ከመነሻ ገጹ ተያይዟል)። በሁሉም አገልግሎቶች "
        "በየካቲት 2026 ስንት ማስታወቂያዎች ወጡ? ቁጥሩን ይመልሱ።",
  "h2": "በፖርታሉ የማስታወቂያ ሰሌዳ መሠረት በ2025 የትኛው አገልግሎት ብዙ ማስታወቂያዎችን "
        "አወጣ? የአገልግሎቱን ስም ይመልሱ።",
  "h3": "በፖርታሉ የማስታወቂያ ሰሌዳ ላይ ያለውን በጣም አሮጌ ማስታወቂያ ትክክለኛ ርዕስ ይግለጹ።",
  "h4": "በፖርታሉ የማስታወቂያ ሰሌዳ ላይ በ2026 የወጡ ስንት ማስታወቂያዎች '{closure}' ምድብ "
        "አላቸው? ቁጥሩን ይመልሱ።",
  "n1": "የሮል ቁጥር 496396 የ{year} የ{exam_l} ({exam}) ፈተና ውጤት ያግኙ — ቦርዱ "
        "አልተሰጠም፤ የፍለጋ ገጹ ቦርዶቹን ይዘረዝራል። የተፈታኙን GPA እና ተቋም ሁለቱንም "
        "ይግለጹ።",
  "n2": "የሮል ቁጥር 969525 የ{year} የ{exam_l} ({exam}) ፈተና ውጤት ያግኙ — ቦርዱ "
        "አልተሰጠም። የተፈታኙን ስምና GPA ሁለቱንም ይግለጹ።",
  "n3": "በመሬት መዝገብ ፍለጋ በኩል በ{district} ወረዳ ({division} ክልል፤ ንዑስ ወረዳውና "
        "ሙዛው አልተሰጡም) ውስጥ የሆነ ቦታ ያለውን የካቲያን ቁጥር 7191 ያግኙና በላዩ "
        "የተመዘገበውን የመሬት ዓይነት ይግለጹ።",
  "n4": "በ{district} ወረዳ ({division} ክልል፤ ንዑስ ወረዳውና ሙዛው አልተሰጡም) ውስጥ የሆነ "
        "ቦታ ያለውን የካቲያን ቁጥር 1022 ያግኙና ባለቤቱንም የተመዘገበውን ድርሻም ይግለጹ።",
  "n5": "በፖርታሉ የማስታወቂያ ሰሌዳ ላይ በሰኔ 2026 የወጣው ማስታወቂያ አንድ ብቻ ነው። "
        "የማጣቀሻ ቁጥሩንና ያወጣውን አገልግሎት ስም ሁለቱንም ይግለጹ።",
  "n6": "በ2026 በፖርታሉ የማስታወቂያ ሰሌዳ ላይ በጣም ጥቂት ማስታወቂያዎች የወጡት በየትኛው ወር "
        "ነው? ወሩን በYYYY-MM ቅርጽ ይመልሱ።",
  "n7": "በደንበኛ ቁጥሮች 08000021፣ 08000035 እና 08000049 ላይ ያለውን ጠቅላላ ያልተከፈለ "
        "ኤሌክትሪክ ይመልከቱና በሦስቱም ላይ ያለውን የተጣመረ ጠቅላላ ይግለጹ።",
  "n8": "በይዞታዎች HLD00003፣ HLD00004 እና HLD00005 ላይ ያለውን ሁሉንም ያልተከፈለ የመሬት "
        "ልማት ግብር የተጣመረ ጠቅላላ ይግለጹ።",
  "n9": "በኤሌክትሪክ ሂሳብ ታሪክዎ ውስጥ በስድስቱም ጊዜያት በጠቅላላ ስንት ዩኒት (kWh) "
        "ተጠቅመዋል?",
  "n10": "በፓስፖርት ክፍያ ዝርዝር ላይ በጣም ውዱ ክፍያና በጣም ርካሹ ዜሮ ያልሆነ ክፍያ "
         "ልዩነት ስንት ነው?",
  "n11": "የፓስፖርትና የመንጃ ፈቃድ ክፍያ ዝርዝሮችን አጣምረው ስንት የክፍያ ረድፎች ከ5000 "
         "በላይ መጠን አላቸው? ቁጥሩን ይመልሱ።",
  "n12": "በTIN 972871718941 ለግምገማ ዓመት 2025-2026 የግል ኢ-ሪተርን ያስገቡ፡ ጠቅላላ ገቢ "
         "720000፣ ተቀናሾች በትክክል የገቢው አንድ አራተኛ፣ እና የሚከፈል ግብር በትክክል "
         "የ(ገቢ ሲቀነስ ተቀናሾች) 15%። ሁሉንም መጠኖች እንደ ተራ አሃዞች ያስገቡ፣ መግለጫ "
         "YES።",
  "n13": "ቁጥሩ 20000000000373 የሆነውን የልደት ምዝገባ መዝገብ ይመልከቱ። ከዚያ በዚያ "
         "መዝገብ እናት ስም በትክክል የተሰየመ አዲስ ልጅ፣ በ2026-03-01 የተወለደ፣ በዚያ "
         "መዝገብ በተመዘገበው ቦታ፣ ራስዎ እንደ አባትና እናትዎ እንደ እናት ሆነው የልደት "
         "ምዝገባ ማመልከቻ ያስገቡ።",
  "n14": "በፖርታሉ የማስታወቂያ ሰሌዳ ላይ ያለውን በጣም አሮጌ ማስታወቂያ ያግኙ፣ የትኛው "
         "አገልግሎት እንዳወጣው ያስተውሉ፣ ከዚያ የዚያን አገልግሎት የክፍያ ዝርዝር ከፍተው "
         "በጣም ውዱን የክፍያ መጠን ይግለጹ።",
  "n15": "ሁለቱንም ያድርጉ፡ በ{office_licence} በመጀመሪያው በሚገኝ ቀን በመጀመሪያው ሰዓት "
         "የመንዳት ፈተና ይያዙ፣ እና ለእድሳት ምድብ፣ ሙያዊ ዓይነት ቻላን አዘጋጅተው (በካርድ፣ "
         "card) ይክፈሉ። ከዚያ የከፈሉትን የቻላን መጠን ይግለጹ።",
  "n16": "የፓስፖርት ማመልከቻዎች PPA04000034 እና PPA04000068ን ተመልክተው የእያንዳንዱን "
         "የደብተር ገጾችና ተቀባይነት ያንብቡ። በፓስፖርት ክፍያ ዝርዝር መሠረት የትኛው ማመልከቻ "
         "የመደበኛ (regular) አቅርቦት ክፍያ ከፍ ያለ ነው? የማመልከቻ መለያውን ይመልሱ።",
  "n17": "ሦስቱንም ያድርጉ፡ በደንበኛ 08000007 ላይ የኤሌክትሪክ ሂሳብ BL0000005 ይክፈሉ፣ "
         "በይዞታ HLD00002 ላይ ያልተከፈለውን የመሬት ልማት ግብር ይክፈሉ፣ እና "
         "በ{office_passport} ለ2026-06-24 በ11:30 የፓስፖርት ምዝገባ ቀጠሮ ይያዙ። በካርድ "
         "(card) ይክፈሉ።",
  "n18": "በይዞታ HLD00003 ላይ የ2022-2023 የመሬት ልማት ግብር ዕዳ ብቻ (በካርድ፣ card) "
         "ይክፈሉ፤ አሮጌውንም አዲሱንም ዕዳ ሳይከፈሉ ይተዉ።",
  "n19": "ሦስት እርማቶች ያስገቡ፡ የመታወቂያ መዝገብዎን የአሁን አድራሻ ወደ '{new_addr}' እና "
         "የልደት ቀኑን ወደ {new_dob} ይቀይሩ፣ እና በተያያዘው የልደት ምዝገባ መዝገብዎ ላይ "
         "ያለውን ስም ወደ '{hoque}' ይቀይሩ። ለእያንዳንዱ ማንኛውንም የሎከር ሰነድ ያያይዙ።",
  "n20": "ሁለቱንም የፓስፖርት ጥያቄዎች ያስገቡ፡ አዲስ ማመልከቻ (ስምዎ፣ የልደት ቀንና የአባት "
         "ስም፤ ሁለቱም አድራሻዎች፤ 64 ገጽ፣ 10 ዓመት ተቀባይነት፣ ፈጣን (express) "
         "አቅርቦት)፣ እና ለፓስፖርት ቁጥር A6053903 በምክንያት '{damaged}' የዳግም ማውጣት "
         "ማመልከቻ።",
  "i1": "ቆጣሪ MTR000001ን በ300 በካርድ (card) ይሙሉ።",
  "i2": "የመታወቂያ ቁጥር 9999708182203፣ በ2023-09-16 የተመዘገበውን የክትባት ምስክር "
        "ወረቀት አውርደው የምስክር ወረቀቱን ቁጥር ይግለጹ።",
  "i3": "የማመልከቻ PPA04000017 ፓስፖርት የአቅርቦት ሁኔታ ተመልክተው ይግለጹ።",
  "i4": "ለምድብ {cat_licence}፣ ዓይነት {var_motorcycle} የክፍያ ቻላን አዘጋጅተው ይክፈሉ።",
  "i5": "ከመለያዎ ጋር በተያያዘው የሞት መዝገብ ላይ ስሙን ወደ '{haque_sr}' በመቀየር የስም "
        "እርማት ያስገቡ።",
  "i6": "በ{office_passport} ለ2026-06-23 በ10:30 የፓስፖርት ምዝገባ ቀጠሮ ይያዙ።",
  "i7": "የግብር ከፋይ መለያ ቁጥር 111111111111ን አረጋግጠው የተመዘገበውን ስም ይግለጹ።",
  "j1": "የመታወቂያ ካርድዎን ሊታተም የሚችል ቅጂ ከፍተው የሚታየውን የእናት ስምና ቋሚ አድራሻ "
        "ሁለቱንም ይግለጹ።",
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
            assert b - {"exam_l"} == a, (lang, k, a, b)
    for lang in I18N:
        assert set(LIT[lang]) == set(LIT["en"]), lang
    return True


check()
