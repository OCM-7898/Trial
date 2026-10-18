import collections
import json
import os
import sys
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(1, os.path.join(ROOT, "sites"))

from visual.ministore.seed import (ACTIVE_COUPON, COUPONS, PAST_ORDERS,
                                   PRESEEDED_WISHLIST, USERS,
                                   build_rows, load_catalog, loc_addr)
from visual.ministore.strings import LANG_META

LOGIN = ["goto /login", "fill 1 username=agent_smith; password=password123"]

CRED = {
    "en": " Log in as agent_smith (password: password123) if needed.",
    "bn": " প্রয়োজনে agent_smith (পাসওয়ার্ড: password123) হিসেবে লগ ইন "
          "করুন।",
    "hi": " ज़रूरत हो तो agent_smith (पासवर्ड: password123) के रूप में "
          "लॉग इन करें।",
    "ur": " ضرورت ہو تو agent_smith (پاس ورڈ: password123) کے طور پر لاگ "
          "اِن کریں۔",
    "am": " አስፈላጊ ከሆነ በ agent_smith (የይለፍ ቃል፡ password123) ይግቡ።",
}
NA_SUFFIX = {
    "en": " If this cannot be determined from the site, answer N/A.",
    "bn": " সাইট থেকে এটি নির্ধারণ করা না গেলে N/A উত্তর দিন।",
    "hi": " अगर साइट से यह तय न हो सके, तो N/A उत्तर दें।",
    "ur": " اگر سائٹ سے یہ معلوم نہ ہو سکے تو N/A جواب دیں۔",
    "am": " ይህ ከድረ-ገጹ ሊታወቅ ካልቻለ N/A ብለው ይመልሱ።",
}

ADDR_EN = ["5 Harbor Ln, Austin, 78701", "22 Birch Way, Denver, 80014",
           "9 Cedar Ct, Portland, 97205", "310 Elm Rd, Madison, 53703",
           "41 Maple St, Reno, 89501", "68 Willow Dr, Boise, 83702",
           "7 Juniper Ave, Salem, 97301", "150 Aspen Pl, Ogden, 84401",
           "26 Poplar Ln, Fresno, 93650", "88 Laurel St, Tucson, 85701",
           "13 Sycamore Rd, Akron, 44301", "55 Magnolia Ct, Boca, 33427",
           "2 Hickory Way, Provo, 84601", "71 Alder Dr, Chico, 95926",
           "34 Redwood Ave, Davis, 95616", "96 Cypress St, Tempe, 85281",
           "13 Detour Dr, Mobile, 36602", "48 Update Blvd, Springfield"]
ADDR_BN = ["5 হারবার লেন, অস্টিন, 78701", "22 বার্চ ওয়ে, ডেনভার, 80014",
           "9 সিডার কোর্ট, পোর্টল্যান্ড, 97205", "310 এলম রোড, ম্যাডিসন, 53703",
           "41 মেপল স্ট্রিট, রিনো, 89501", "68 উইলো ড্রাইভ, বয়সি, 83702",
           "7 জুনিপার অ্যাভিনিউ, সেলেম, 97301", "150 অ্যাসপেন প্লেস, অগডেন, 84401",
           "26 পপলার লেন, ফ্রেসনো, 93650", "88 লরেল স্ট্রিট, টুসন, 85701",
           "13 সিকামোর রোড, অ্যাক্রন, 44301", "55 ম্যাগনোলিয়া কোর্ট, বোকা, 33427",
           "2 হিকরি ওয়ে, প্রোভো, 84601", "71 অ্যালডার ড্রাইভ, চিকো, 95926",
           "34 রেডউড অ্যাভিনিউ, ডেভিস, 95616", "96 সাইপ্রেস স্ট্রিট, টেম্পি, 85281",
           "13 ডিটুর ড্রাইভ, মোবিল, 36602", "48 আপডেট বুলেভার্ড, স্প্রিংফিল্ড"]
assert len(ADDR_BN) == len(ADDR_EN)
ADDR_HI = ["5 हार्बर लेन, ऑस्टिन, 78701", "22 बर्च वे, डेनवर, 80014",
           "9 सीडर कोर्ट, पोर्टलैंड, 97205", "310 एल्म रोड, मैडिसन, 53703",
           "41 मेपल स्ट्रीट, रीनो, 89501", "68 विलो ड्राइव, बॉइज़ी, 83702",
           "7 जूनिपर एवेन्यू, सेलम, 97301", "150 एस्पेन प्लेस, ऑग्डेन, 84401",
           "26 पॉपलर लेन, फ़्रेस्नो, 93650", "88 लॉरेल स्ट्रीट, टक्सन, 85701",
           "13 सिकामोर रोड, एक्रन, 44301", "55 मैग्नोलिया कोर्ट, बोका, 33427",
           "2 हिकरी वे, प्रोवो, 84601", "71 एल्डर ड्राइव, चिको, 95926",
           "34 रेडवुड एवेन्यू, डेविस, 95616", "96 साइप्रस स्ट्रीट, टेम्पी, 85281",
           "13 डिटूर ड्राइव, मोबील, 36602", "48 अपडेट बुलेवार्ड, स्प्रिंगफ़ील्ड"]
assert len(ADDR_HI) == len(ADDR_EN)
ADDR_UR = ["5 ہاربر لین، آسٹن، 78701", "22 برچ وے، ڈینور، 80014",
           "9 سیڈر کورٹ، پورٹلینڈ، 97205", "310 ایلم روڈ، میڈیسن، 53703",
           "41 میپل اسٹریٹ، رینو، 89501", "68 ولو ڈرائیو، بوائزی، 83702",
           "7 جونیپر ایونیو، سیلم، 97301", "150 ایسپن پلیس، آگڈن، 84401",
           "26 پاپلر لین، فریسنو، 93650", "88 لارل اسٹریٹ، ٹکسن، 85701",
           "13 سیکامور روڈ، ایکرن، 44301", "55 میگنولیا کورٹ، بوکا، 33427",
           "2 ہکری وے، پروو، 84601", "71 ایلڈر ڈرائیو، چیکو، 95926",
           "34 ریڈ ووڈ ایونیو، ڈیوس، 95616", "96 سائپرس اسٹریٹ، ٹیمپی، 85281",
           "13 ڈیٹور ڈرائیو، موبائل، 36602", "48 اپ ڈیٹ بلیوارڈ، اسپرنگ فیلڈ"]
assert len(ADDR_UR) == len(ADDR_EN)
ADDR_AM = ["5 ሃርበር ሌን, ኦስቲን, 78701", "22 በርች ዌይ, ዴንቨር, 80014",
           "9 ሲዳር ኮርት, ፖርትላንድ, 97205", "310 ኤልም ሮድ, ማዲሰን, 53703",
           "41 ሜፕል ስትሪት, ሪኖ, 89501", "68 ዊሎው ድራይቭ, ቦይዚ, 83702",
           "7 ጁኒፐር አቬኑ, ሴለም, 97301", "150 አስፐን ፕሌስ, ኦግደን, 84401",
           "26 ፖፕላር ሌን, ፍሬዝኖ, 93650", "88 ሎሬል ስትሪት, ቱሰን, 85701",
           "13 ሲካሞር ሮድ, አክሮን, 44301", "55 ማግኖሊያ ኮርት, ቦካ, 33427",
           "2 ሂኮሪ ዌይ, ፕሮቮ, 84601", "71 አልደር ድራይቭ, ቺኮ, 95926",
           "34 ሬድዉድ አቬኑ, ዴቪስ, 95616", "96 ሳይፕረስ ስትሪት, ቴምፒ, 85281",
           "13 ዲቱር ድራይቭ, ሞቢል, 36602", "48 አፕዴት ቡሌቫርድ, ስፕሪንግፊልድ"]
assert len(ADDR_AM) == len(ADDR_EN)
ADDR = {"en": ADDR_EN, "bn": ADDR_BN, "hi": ADDR_HI, "ur": ADDR_UR,
        "am": ADDR_AM}

I18N = {
 "en": {
  "ord1": "Order 1 x {p} in a single order, shipping to '{a}'. Complete the full checkout.",
  "ordq": "Order {q} x {p} in a single order, shipping to '{a}'. Complete the full checkout.",
  "ord2": "Order 1 x {p1} and 1 x {p2} in a single order, shipping to '{a}'. Complete the full checkout.",
  "ord1_v": [
    "Order 1 x {p} in a single order, shipping to '{a}'. Complete the full checkout.",
    "Buy {p} (quantity 1) and have it shipped to '{a}'. Go all the way through checkout so the order is actually placed.",
    "I need one unit of {p} delivered to '{a}'. Place that order — one order, fully checked out.",
    "Place an order for {p}, quantity 1, using '{a}' as the shipping address, and finish checkout."
  ],
  "ordq_v": [
    "Order {q} x {p} in a single order, shipping to '{a}'. Complete the full checkout.",
    "Buy {q} units of {p} in one order, shipped to '{a}'. Complete checkout.",
    "I want {q} of {p} sent to '{a}' — put them all in one order and check out fully.",
    "Purchase {p}, quantity {q}, with '{a}' as the delivery address; make sure the order is actually placed."
  ],
  "ord2_v": [
    "Order 1 x {p1} and 1 x {p2} in a single order, shipping to '{a}'. Complete the full checkout.",
    "Buy {p1} together with {p2} (one of each, both in the same order), shipped to '{a}'. Complete checkout.",
    "Put {p1} and {p2} (one each) in the cart and check out as one order to '{a}'.",
    "I need {p1} and {p2}, one of each, delivered to '{a}' in a single shipment; place that order."
  ],
  "ordcoupon": "Find the active coupon code on the Deals page, then order 1 x {p} shipped to '{a}' with that coupon applied.",
  "orddefault": "Order 1 x {p} shipped to the default address saved in your account settings (leave the checkout address as suggested).",
  "ordsetdefault": "In your account settings, change your default shipping address to '{a}'. Then order 1 x {p} shipped to that (new default) address.",
  "wladd1": "Add {p} to your wishlist.",
  "wladd2": "Add {p1} and {p2} to your wishlist.",
  "wlremove": "Remove {p} from your wishlist.",
  "wlcheapest": "Sort the {cat} category by price and add the single cheapest {cat} product to your wishlist.",
  "wlmostrev": "Find the most-reviewed product in the {cat} category (sort by most reviewed) and add it to your wishlist.",
  "setdefault": "In your account settings, change your default shipping address to '{a}'.",
  "chgaddr": "Change the delivery address of order #{oid} to '{a}'.",
  "cancel": "Cancel order #{oid} (confirming when asked).",
  "chgcancel": "Change the delivery address of order #{oid} to '{a}', then cancel that order (confirming when asked).",
  "cancelcontact": "Cancel order #{oid}, then use the contact form to send the message '{msg}' referencing order {oid}.",
  "setwl": "Change your default shipping address to '{a}' in settings, and add {p} to your wishlist.",
  "ordcancelnew": "Order 1 x {p} shipped to '{a}', then cancel the order you just placed (confirming when asked).",
  "wlreview": "Add {p} to your wishlist and post a 4-star review on it saying '{rv}'.",
  "na_brand": "How many products does the brand 'Zenithware' sell?",
  "na_product": "What is the price of the '{name}'?",
  "na_coupon": "What percentage discount does the coupon code SAVE25 give at checkout?",
  "na_oos": "Order 1 x {p}. If it cannot be ordered, answer N/A.",
  "na_ghost": "What star rating did the user 'ghost_gary' give {p} in their review?",
  "na_under": "Find any product in the {cat} category priced under {cur}{limit} and report its name.",
  "na_order9": "What is the current status of order #9?",
  "na_qty": "What quantity of {p} did you buy in order #2?",
  "na_freeship": "What percentage discount does the coupon code FREESHIP currently give at checkout? If the coupon is expired or no longer gives a discount, answer N/A.",
  "na_ultra": "How many units of the '{name} Ultra' are in stock?",
  "price_q": "What is the price of {p}? Answer with the amount.",
  "brand_q": "Which brand sells {p}?",
  "stock_q": "How many units of {p} are currently in stock?",
  "cheaper_q": "Which is cheaper, {p1} or {p2}? Answer with the exact product name.",
  "dearest_q": "Which of these is the most expensive: {ps}? Answer with the exact product name.",
  "nrev_q": "How many reviews does {p} have?",
  "onestar_q": "How many 1-star reviews does {p} have?",
  "avg_q": "What is the average star rating shown for {p}?",
  "higher_q": "Which has the higher average star rating: {p1} or {p2}? Answer with the exact product name.",
  "coupon_q": "What is the currently active coupon code listed on the Deals page?",
  "review_t": "Write a 5-star review saying '{rv}' on {p}.",
  "contact_t": "Use the contact form to send the message '{msg}' referencing order {oid}.",
  "brandcount_q": "How many products does the brand '{b}' sell?",
  "msg_cancel": "Order 4 is no longer needed, please confirm the cancellation.",
  "msg_missing": "Order 2 arrived with one item missing, please advise.",
  "rv_sturdy": "Sturdy frame, easy assembly, colour matches the photo.",
  "rv_fresh": "Fresh on arrival and the packaging held up well.",
  "fake_product": "Self-Watering Titanium Bookshelf",
  "qa_warranty_q": "The product page of {p} has a Questions & answers section. According to the seller's answer there, how many months of warranty does it come with?",
  "qa_delivery_q": "According to the Q&A section on the product page of {p}, how many business days does standard delivery take?",
  "qa_count_q": "How many questions are listed in the Questions & answers section of {p}?",
  "ask_t": "On the product page of {p}, use the Q&A form to ask the question '{q}'.",
  "ask_wl_t": "Ask the question '{q}' on the product page of {p}, and also add that product to your wishlist.",
  "helpful_top_q": "On the product page of {p}, which reviewer's review has the most helpful votes? Answer with the username.",
  "helpful_n_q": "On the product page of {p}, how many people found the review by '{u}' helpful?",
  "helpful_mark_t": "On the product page of {p}, press the Helpful button on the review written by '{u}'.",
  "helpful_mark_top_t": "On the product page of {p}, find the review with the MOST helpful votes and press its Helpful button.",
  "brands_total_q": "How many brands does the store list on its Brands page?",
  "brands_more_q": "According to the Brands page, which brand lists more products: '{b1}' or '{b2}'? Answer with the brand name.",
  "brands_avg_q": "According to the Brands page, which of '{b1}' and '{b2}' has the higher average review rating? Answer with the brand name.",
  "q_colour": "Does the colour match the photos exactly?",
  "q_spare": "Are replacement parts available to order?",
  "re_warranty": "(\\d+)-month warranty",
  "re_delivery": "(\\d+) business days",
  "na_alts": {
   "brand": [
    "no such brand",
    "does not exist",
    "not listed",
    "not found",
    "no products",
    "0",
    "zero"
   ],
   "product": [
    "not found",
    "no such product",
    "does not exist",
    "not listed",
    "not available",
    "not be found",
    "could not find",
    "couldn't find",
    "cannot find"
   ],
   "coupon": [
    "unknown",
    "not a valid",
    "does not exist",
    "invalid",
    "not exist",
    "no such coupon"
   ],
   "oos": [
    "out of stock",
    "cannot be ordered",
    "unavailable",
    "not be added"
   ],
   "ghost": [
    "no review",
    "did not review",
    "no such user",
    "has not reviewed",
    "not reviewed",
    "no rating"
   ],
   "under": [
    "no product",
    "none",
    "nothing under",
    "no products"
   ],
   "order9": [
    "no order",
    "does not exist",
    "not found",
    "no such order",
    "not exist"
   ],
   "qty": [
    "not in",
    "was not",
    "not part of",
    "0",
    "zero",
    "none",
    "did not buy",
    "not included"
   ],
   "freeship": [
    "expired",
    "no longer",
    "not active",
    "inactive",
    "0%"
   ],
   "ultra": [
    "not found",
    "no such product",
    "does not exist",
    "not listed",
    "not exist",
    "not be found",
    "could not find",
    "couldn't find",
    "cannot find"
   ]
  },
  "d_bpf": "the {brand} {frag} priced at {cur}{price}",
  "d_bcf": "the {brand} {frag} in {cat}",
  "d_cpf": "the {frag} in {cat} priced at {cur}{price}",
  "d_cf": "the {frag} in {cat}",
  "d_bfc": "the {brand} {frag} whose listed colour is '{colour}'",
  "d_cheapest": "the cheapest product in {cat} (sort the category by price)",
  "d_mostrev": "the most-reviewed product in {cat}",
  "ord_min_total": "Order the fewest units of {p} needed for the subtotal to reach at least {cur}{amt}, shipped to '{a}'. Complete the full checkout.",
  "ord_cheaper2": "Compare {p1} and {p2}, and order 1 x whichever is cheaper (only that one), shipped to '{a}'. Complete the full checkout.",
  "ord_mixed": "Order 1 x {p1} and {q} x {p2} in a single order, shipping to '{a}'. Complete the full checkout."
 },
 "bn": {
  "ord1": "একটি মাত্র অর্ডারে {p} ১টি কিনুন, '{a}' ঠিকানায় পাঠাতে। পুরো চেকআউট সম্পন্ন করুন।",
  "ordq": "একটি মাত্র অর্ডারে {p} {q}টি কিনুন, '{a}' ঠিকানায় পাঠাতে। পুরো চেকআউট সম্পন্ন করুন।",
  "ord2": "একটি মাত্র অর্ডারে {p1} ১টি এবং {p2} ১টি কিনুন, '{a}' ঠিকানায় পাঠাতে। পুরো চেকআউট সম্পন্ন করুন।",
  "ord1_v": [
    "একটি মাত্র অর্ডারে {p} ১টি কিনুন, '{a}' ঠিকানায় পাঠাতে। পুরো চেকআউট সম্পন্ন করুন।",
    "{p} ১টি কিনে '{a}' ঠিকানায় পাঠান। অর্ডারটি যেন সত্যিই প্লেস হয়, সেজন্য চেকআউট শেষ পর্যন্ত সম্পন্ন করুন।",
    "আমার {p} একটি দরকার, ডেলিভারি হবে '{a}' ঠিকানায়। একটি অর্ডারে পুরো চেকআউট করে অর্ডারটি দিন।",
    "'{a}' শিপিং ঠিকানা ব্যবহার করে {p} একটির জন্য অর্ডার দিন এবং চেকআউট সম্পূর্ণ করুন।"
  ],
  "ordq_v": [
    "একটি মাত্র অর্ডারে {p} {q}টি কিনুন, '{a}' ঠিকানায় পাঠাতে। পুরো চেকআউট সম্পন্ন করুন।",
    "{p} {q}টি এক অর্ডারে কিনুন, '{a}' ঠিকানায় শিপ করে। চেকআউট সম্পন্ন করুন।",
    "আমি {p} {q}টি '{a}' ঠিকানায় পাঠাতে চাই — সবগুলো একটি অর্ডারে রেখে পুরোপুরি চেকআউট করুন।",
    "{p} কিনুন, পরিমাণ {q}, ডেলিভারি ঠিকানা '{a}'; অর্ডারটি যেন সত্যিই প্লেস হয় তা নিশ্চিত করুন।"
  ],
  "ord2_v": [
    "একটি মাত্র অর্ডারে {p1} ১টি এবং {p2} ১টি কিনুন, '{a}' ঠিকানায় পাঠাতে। পুরো চেকআউট সম্পন্ন করুন।",
    "{p1} এবং {p2} একসাথে কিনুন — দুটোই একই অর্ডারে, প্রতিটি ১টি করে — '{a}' ঠিকানায় শিপ করে। চেকআউট সম্পন্ন করুন।",
    "{p1} এবং {p2} (প্রতিটি ১টি) কার্টে রাখুন এবং একটি অর্ডার হিসেবে '{a}' ঠিকানায় চেকআউট করুন।",
    "আমার {p1} এবং {p2} প্রতিটি ১টি করে '{a}' ঠিকানায় একটি শিপমেন্টে দরকার; সেই অর্ডারটি দিন।"
  ],
  "ordcoupon": "অফার পাতা থেকে সক্রিয় কুপন কোডটি খুঁজে বের করুন, তারপর সেই কুপন প্রয়োগ করে {p} ১টি '{a}' ঠিকানায় অর্ডার করুন।",
  "orddefault": "আপনার অ্যাকাউন্ট সেটিংসে সংরক্ষিত ডিফল্ট ঠিকানায় {p} ১টি অর্ডার করুন (চেকআউটে প্রস্তাবিত ঠিকানাটিই রাখুন)।",
  "ordsetdefault": "আপনার অ্যাকাউন্ট সেটিংসে ডিফল্ট শিপিং ঠিকানা বদলে '{a}' করুন। তারপর সেই (নতুন ডিফল্ট) ঠিকানায় {p} ১টি অর্ডার করুন।",
  "wladd1": "{p} আপনার উইশলিস্টে যোগ করুন।",
  "wladd2": "{p1} এবং {p2} আপনার উইশলিস্টে যোগ করুন।",
  "wlremove": "{p} আপনার উইশলিস্ট থেকে সরান।",
  "wlcheapest": "{cat} বিভাগটি দাম অনুযায়ী সাজান এবং সবচেয়ে সস্তা {cat} পণ্যটি আপনার উইশলিস্টে যোগ করুন।",
  "wlmostrev": "{cat} বিভাগে সবচেয়ে বেশি রিভিউ পাওয়া পণ্যটি খুঁজুন (সবচেয়ে বেশি রিভিউ অনুযায়ী সাজান) এবং সেটি আপনার উইশলিস্টে যোগ করুন।",
  "setdefault": "আপনার অ্যাকাউন্ট সেটিংসে ডিফল্ট শিপিং ঠিকানা বদলে '{a}' করুন।",
  "chgaddr": "অর্ডার #{oid}-এর ডেলিভারি ঠিকানা বদলে '{a}' করুন।",
  "cancel": "অর্ডার #{oid} বাতিল করুন (জিজ্ঞেস করা হলে নিশ্চিত করুন)।",
  "chgcancel": "অর্ডার #{oid}-এর ডেলিভারি ঠিকানা বদলে '{a}' করুন, তারপর সেই অর্ডারটি বাতিল করুন (জিজ্ঞেস করা হলে নিশ্চিত করুন)।",
  "cancelcontact": "অর্ডার #{oid} বাতিল করুন, তারপর যোগাযোগ ফর্ম ব্যবহার করে অর্ডার {oid} উল্লেখ করে '{msg}' বার্তাটি পাঠান।",
  "setwl": "সেটিংসে আপনার ডিফল্ট শিপিং ঠিকানা বদলে '{a}' করুন, এবং {p} আপনার উইশলিস্টে যোগ করুন।",
  "ordcancelnew": "{p} ১টি '{a}' ঠিকানায় অর্ডার করুন, তারপর এইমাত্র দেওয়া অর্ডারটি বাতিল করুন (জিজ্ঞেস করা হলে নিশ্চিত করুন)।",
  "wlreview": "{p} আপনার উইশলিস্টে যোগ করুন এবং এটির ওপর '{rv}' লিখে একটি ৪-স্টার রিভিউ পোস্ট করুন।",
  "na_brand": "'Zenithware' ব্র্যান্ডটি কতটি পণ্য বিক্রি করে?",
  "na_product": "'{name}'-এর দাম কত?",
  "na_coupon": "চেকআউটে SAVE25 কুপন কোডটি কত শতাংশ ছাড় দেয়?",
  "na_oos": "{p} ১টি অর্ডার করুন। অর্ডার করা সম্ভব না হলে N/A উত্তর দিন।",
  "na_ghost": "'ghost_gary' ব্যবহারকারী তাঁর রিভিউতে {p}-কে কত স্টার রেটিং দিয়েছেন?",
  "na_under": "{cat} বিভাগে {cur}{limit}-এর কম দামের যেকোনো একটি পণ্য খুঁজে তার নাম জানান।",
  "na_order9": "অর্ডার #9-এর বর্তমান অবস্থা কী?",
  "na_qty": "অর্ডার #2-এ আপনি {p} কতটি কিনেছিলেন?",
  "na_freeship": "চেকআউটে FREESHIP কুপন কোডটি বর্তমানে কত শতাংশ ছাড় দেয়? কুপনটির মেয়াদ শেষ হয়ে থাকলে বা আর ছাড় না দিলে N/A উত্তর দিন।",
  "na_ultra": "'{name} Ultra'-এর কতটি ইউনিট স্টকে আছে?",
  "price_q": "{p}-এর দাম কত? পরিমাণটি লিখে উত্তর দিন।",
  "brand_q": "{p} কোন ব্র্যান্ডের পণ্য?",
  "stock_q": "{p}-এর কতটি ইউনিট বর্তমানে স্টকে আছে?",
  "cheaper_q": "কোনটি সস্তা, {p1} নাকি {p2}? পণ্যের সঠিক নামটি লিখে উত্তর দিন।",
  "dearest_q": "এগুলোর মধ্যে কোনটি সবচেয়ে দামি: {ps}? পণ্যের সঠিক নামটি লিখে উত্তর দিন।",
  "nrev_q": "{p}-এর কতটি রিভিউ আছে?",
  "onestar_q": "{p}-এর কতটি ১-স্টার রিভিউ আছে?",
  "avg_q": "{p}-এর জন্য দেখানো গড় স্টার রেটিং কত?",
  "higher_q": "কোনটির গড় স্টার রেটিং বেশি: {p1} নাকি {p2}? পণ্যের সঠিক নামটি লিখে উত্তর দিন।",
  "coupon_q": "অফার পাতায় তালিকাভুক্ত বর্তমানে সক্রিয় কুপন কোডটি কী?",
  "review_t": "{p}-এর ওপর '{rv}' লিখে একটি ৫-স্টার রিভিউ লিখুন।",
  "contact_t": "যোগাযোগ ফর্ম ব্যবহার করে অর্ডার {oid} উল্লেখ করে '{msg}' বার্তাটি পাঠান।",
  "brandcount_q": "'{b}' ব্র্যান্ডটি কতটি পণ্য বিক্রি করে?",
  "msg_cancel": "অর্ডার 4 আর দরকার নেই, অনুগ্রহ করে বাতিল নিশ্চিত করুন।",
  "msg_missing": "অর্ডার 2 একটি পণ্য ছাড়া এসেছে, অনুগ্রহ করে পরামর্শ দিন।",
  "rv_sturdy": "মজবুত ফ্রেম, সহজে জোড়া লাগে, রং ছবির সাথে মিলে যায়।",
  "rv_fresh": "তাজা অবস্থায় এসেছে আর প্যাকেজিংও ভালো ছিল।",
  "fake_product": "সেলফ-ওয়াটারিং টাইটানিয়াম বুকশেল্ফ",
  "qa_warranty_q": "{p}-এর পণ্য পাতায় একটি প্রশ্ন ও উত্তর অংশ আছে। সেখানে বিক্রেতার উত্তর অনুযায়ী এটির সাথে কত মাসের ওয়ারেন্টি আসে?",
  "qa_delivery_q": "{p}-এর পণ্য পাতার প্রশ্ন ও উত্তর অংশ অনুযায়ী সাধারণ ডেলিভারিতে কত কর্মদিবস লাগে?",
  "qa_count_q": "{p}-এর প্রশ্ন ও উত্তর অংশে কতটি প্রশ্ন তালিকাভুক্ত আছে?",
  "ask_t": "{p}-এর পণ্য পাতায় প্রশ্ন ও উত্তর ফর্ম ব্যবহার করে '{q}' প্রশ্নটি করুন।",
  "ask_wl_t": "{p}-এর পণ্য পাতায় '{q}' প্রশ্নটি করুন, এবং পণ্যটি আপনার উইশলিস্টেও যোগ করুন।",
  "helpful_top_q": "{p}-এর পণ্য পাতায় কোন রিভিউয়ারের রিভিউ সবচেয়ে বেশি 'সহায়ক' ভোট পেয়েছে? ইউজারনেম লিখে উত্তর দিন।",
  "helpful_n_q": "{p}-এর পণ্য পাতায় '{u}'-এর লেখা রিভিউটি কতজনের কাছে সহায়ক মনে হয়েছে?",
  "helpful_mark_t": "{p}-এর পণ্য পাতায় '{u}'-এর লেখা রিভিউটির 'সহায়ক' বোতামটি চাপুন।",
  "helpful_mark_top_t": "{p}-এর পণ্য পাতায় সবচেয়ে বেশি 'সহায়ক' ভোট পাওয়া রিভিউটি খুঁজে তার 'সহায়ক' বোতামটি চাপুন।",
  "brands_total_q": "দোকানটি তার ব্র্যান্ড পাতায় কতটি ব্র্যান্ড তালিকাভুক্ত করেছে?",
  "brands_more_q": "ব্র্যান্ড পাতা অনুযায়ী কোন ব্র্যান্ডের পণ্য বেশি: '{b1}' নাকি '{b2}'? ব্র্যান্ডের নাম লিখে উত্তর দিন।",
  "brands_avg_q": "ব্র্যান্ড পাতা অনুযায়ী '{b1}' ও '{b2}'-এর মধ্যে কোনটির গড় রিভিউ রেটিং বেশি? ব্র্যান্ডের নাম লিখে উত্তর দিন।",
  "q_colour": "রংটা কি ছবির সাথে হুবহু মেলে?",
  "q_spare": "বদলি যন্ত্রাংশ কি অর্ডার করা যায়?",
  "re_warranty": "(\\d+) মাসের ওয়ারেন্টি",
  "re_delivery": "(\\d+) কর্মদিবস",
  "na_alts": {
   "brand": [
    "এমন কোনো ব্র্যান্ড নেই",
    "ব্র্যান্ড নেই",
    "পাওয়া যায়নি",
    "কোনো পণ্য নেই",
    "০",
    "0",
    "শূন্য"
   ],
   "product": [
    "পাওয়া যায়নি",
    "এমন কোনো পণ্য নেই",
    "খুঁজে পাওয়া যায়নি",
    "তালিকায় নেই",
    "পণ্য নেই"
   ],
   "coupon": [
    "অজানা",
    "অবৈধ",
    "এমন কোনো কুপন নেই",
    "কুপন নেই",
    "পাওয়া যায়নি"
   ],
   "oos": [
    "স্টকে নেই",
    "অর্ডার করা যাবে না",
    "পাওয়া যাচ্ছে না",
    "অর্ডার করা সম্ভব নয়"
   ],
   "ghost": [
    "কোনো রিভিউ নেই",
    "রিভিউ দেননি",
    "এমন কোনো ব্যবহারকারী নেই",
    "রেটিং দেননি",
    "রিভিউ করেননি"
   ],
   "under": [
    "কোনো পণ্য নেই",
    "একটিও নেই",
    "পাওয়া যায়নি",
    "পণ্য নেই"
   ],
   "order9": [
    "এমন কোনো অর্ডার নেই",
    "অর্ডার নেই",
    "পাওয়া যায়নি",
    "অর্ডার খুঁজে পাওয়া যায়নি"
   ],
   "qty": [
    "ছিল না",
    "কেনা হয়নি",
    "০",
    "0",
    "শূন্য",
    "অন্তর্ভুক্ত নয়",
    "অর্ডারে নেই"
   ],
   "freeship": [
    "মেয়াদ শেষ",
    "মেয়াদোত্তীর্ণ",
    "আর ছাড় দেয় না",
    "সক্রিয় নয়",
    "0%",
    "০%"
   ],
   "ultra": [
    "পাওয়া যায়নি",
    "এমন কোনো পণ্য নেই",
    "খুঁজে পাওয়া যায়নি",
    "তালিকায় নেই",
    "পণ্য নেই"
   ]
  },
  "d_bpf": "{brand} ব্র্যান্ডের {cur}{price} দামের {frag}",
  "d_bcf": "{cat} বিভাগের {brand} ব্র্যান্ডের {frag}",
  "d_cpf": "{cat} বিভাগের {cur}{price} দামের {frag}",
  "d_cf": "{cat} বিভাগের {frag}",
  "d_bfc": "'{colour}' রঙের {brand} ব্র্যান্ডের {frag}",
  "d_cheapest": "{cat} বিভাগের সবচেয়ে সস্তা পণ্যটি (বিভাগটি দাম অনুযায়ী সাজান)",
  "d_mostrev": "{cat} বিভাগের সবচেয়ে বেশি রিভিউ পাওয়া পণ্যটি",
  "ord_min_total": "সাবটোটাল অন্তত {cur}{amt} হওয়ার জন্য {p}-এর যতটি ইউনিট দরকার, ঠিক ততটি (সবচেয়ে কম সংখ্যক) অর্ডার করুন, '{a}' ঠিকানায় পাঠাতে। পুরো চেকআউট সম্পন্ন করুন।",
  "ord_cheaper2": "{p1} এবং {p2} তুলনা করুন, এবং যেটি সস্তা শুধু সেটিই ১টি অর্ডার করুন, '{a}' ঠিকানায় পাঠাতে। পুরো চেকআউট সম্পন্ন করুন।",
  "ord_mixed": "একটি মাত্র অর্ডারে {p1} ১টি এবং {p2} {q}টি কিনুন, '{a}' ঠিকানায় পাঠাতে। পুরো চেকআউট সম্পন্ন করুন।"
 },
 "hi": {
  "ord1": "एक ही ऑर्डर में {p} १ खरीदें, शिपिंग पता '{a}'। पूरा चेकआउट करें।",
  "ordq": "एक ही ऑर्डर में {p} {q} खरीदें, शिपिंग पता '{a}'। पूरा चेकआउट करें।",
  "ord2": "एक ही ऑर्डर में {p1} १ और {p2} १ खरीदें, शिपिंग पता '{a}'। पूरा चेकआउट करें।",
  "ord1_v": [
    "एक ही ऑर्डर में {p} १ खरीदें, शिपिंग पता '{a}'। पूरा चेकआउट करें।",
    "{p} १ खरीदकर '{a}' पर भेजें। चेकआउट पूरा करें ताकि ऑर्डर सचमुच प्लेस हो जाए।",
    "मुझे {p} एक चाहिए, डिलीवरी '{a}' पर। एक ही ऑर्डर में पूरा चेकआउट करके ऑर्डर दें।",
    "'{a}' को शिपिंग पते के रूप में इस्तेमाल करते हुए {p} एक का ऑर्डर दें और चेकआउट पूरा करें।"
  ],
  "ordq_v": [
    "एक ही ऑर्डर में {p} {q} खरीदें, शिपिंग पता '{a}'। पूरा चेकआउट करें।",
    "{p} {q} यूनिट एक ऑर्डर में खरीदें, '{a}' पर शिप करें। चेकआउट पूरा करें।",
    "मैं {p} {q} '{a}' पर भेजना चाहता हूँ — सब एक ही ऑर्डर में रखकर पूरा चेकआउट करें।",
    "{p} खरीदें, मात्रा {q}, डिलीवरी पता '{a}'; सुनिश्चित करें कि ऑर्डर वाकई प्लेस हो।"
  ],
  "ord2_v": [
    "एक ही ऑर्डर में {p1} १ और {p2} १ खरीदें, शिपिंग पता '{a}'। पूरा चेकआउट करें।",
    "{p1} और {p2} साथ में खरीदें — दोनों एक ही ऑर्डर में, हर एक १ — '{a}' पर शिप करके। चेकआउट पूरा करें।",
    "{p1} और {p2} (हर एक १) कार्ट में डालें और एक ऑर्डर के रूप में '{a}' पर चेकआउट करें।",
    "मुझे {p1} और {p2} हर एक १ '{a}' पर एक ही शिपमेंट में चाहिए; वह ऑर्डर दें।"
  ],
  "ordcoupon": "डील्स पेज पर सक्रिय कूपन कोड खोजें, फिर वह कूपन लागू करके {p} १ को '{a}' पर ऑर्डर करें।",
  "orddefault": "{p} १ को अपने खाता सेटिंग्स में सहेजे डिफ़ॉल्ट पते पर ऑर्डर करें (चेकआउट में सुझाया गया पता वैसा ही रहने दें)।",
  "ordsetdefault": "अपने खाता सेटिंग्स में डिफ़ॉल्ट शिपिंग पता बदलकर '{a}' करें। फिर {p} १ को उसी (नए डिफ़ॉल्ट) पते पर ऑर्डर करें।",
  "wladd1": "{p} को अपनी विशलिस्ट में जोड़ें।",
  "wladd2": "{p1} और {p2} को अपनी विशलिस्ट में जोड़ें।",
  "wlremove": "{p} को अपनी विशलिस्ट से हटाएँ।",
  "wlcheapest": "{cat} श्रेणी को कीमत के अनुसार क्रमबद्ध करें और सबसे सस्ता {cat} उत्पाद अपनी विशलिस्ट में जोड़ें।",
  "wlmostrev": "{cat} श्रेणी में सबसे ज़्यादा रिव्यू वाला उत्पाद खोजें (सबसे ज़्यादा रिव्यू के अनुसार क्रमबद्ध करें) और उसे अपनी विशलिस्ट में जोड़ें।",
  "setdefault": "अपने खाता सेटिंग्स में डिफ़ॉल्ट शिपिंग पता बदलकर '{a}' करें।",
  "chgaddr": "ऑर्डर #{oid} का डिलीवरी पता बदलकर '{a}' करें।",
  "cancel": "ऑर्डर #{oid} रद्द करें (पूछे जाने पर पुष्टि करें)।",
  "chgcancel": "ऑर्डर #{oid} का डिलीवरी पता बदलकर '{a}' करें, फिर उस ऑर्डर को रद्द करें (पूछे जाने पर पुष्टि करें)।",
  "cancelcontact": "ऑर्डर #{oid} रद्द करें, फिर संपर्क फ़ॉर्म से ऑर्डर {oid} का हवाला देते हुए '{msg}' संदेश भेजें।",
  "setwl": "सेटिंग्स में अपना डिफ़ॉल्ट शिपिंग पता बदलकर '{a}' करें, और {p} को अपनी विशलिस्ट में जोड़ें।",
  "ordcancelnew": "{p} १ को '{a}' पर ऑर्डर करें, फिर अभी किया गया ऑर्डर रद्द करें (पूछे जाने पर पुष्टि करें)।",
  "wlreview": "{p} को अपनी विशलिस्ट में जोड़ें और उस पर '{rv}' लिखकर ४-स्टार रिव्यू पोस्ट करें।",
  "na_brand": "'Zenithware' ब्रांड कितने उत्पाद बेचता है?",
  "na_product": "'{name}' की कीमत क्या है?",
  "na_coupon": "चेकआउट पर कूपन कोड SAVE25 कितने प्रतिशत की छूट देता है?",
  "na_oos": "{p} १ ऑर्डर करें। अगर ऑर्डर नहीं हो सकता, तो N/A उत्तर दें।",
  "na_ghost": "यूज़र 'ghost_gary' ने अपने रिव्यू में {p} को कितने स्टार दिए?",
  "na_under": "{cat} श्रेणी में {cur}{limit} से कम कीमत का कोई भी उत्पाद खोजें और उसका नाम बताएँ।",
  "na_order9": "ऑर्डर #9 की वर्तमान स्थिति क्या है?",
  "na_qty": "ऑर्डर #2 में आपने {p} कितनी मात्रा में खरीदा?",
  "na_freeship": "चेकआउट पर कूपन कोड FREESHIP अभी कितने प्रतिशत की छूट देता है? अगर कूपन समाप्त हो चुका है या अब छूट नहीं देता, तो N/A उत्तर दें।",
  "na_ultra": "'{name} Ultra' की कितनी इकाइयाँ स्टॉक में हैं?",
  "price_q": "{p} की कीमत क्या है? राशि बताएँ।",
  "brand_q": "{p} किस ब्रांड का है?",
  "stock_q": "{p} की कितनी इकाइयाँ अभी स्टॉक में हैं?",
  "cheaper_q": "कौन सा सस्ता है, {p1} या {p2}? उत्पाद का सटीक नाम बताएँ।",
  "dearest_q": "इनमें से सबसे महँगा कौन सा है: {ps}? उत्पाद का सटीक नाम बताएँ।",
  "nrev_q": "{p} के कितने रिव्यू हैं?",
  "onestar_q": "{p} के कितने १-स्टार रिव्यू हैं?",
  "avg_q": "{p} के लिए दिखाई गई औसत स्टार रेटिंग क्या है?",
  "higher_q": "किसकी औसत स्टार रेटिंग ज़्यादा है: {p1} या {p2}? उत्पाद का सटीक नाम बताएँ।",
  "coupon_q": "डील्स पेज पर सूचीबद्ध अभी सक्रिय कूपन कोड क्या है?",
  "review_t": "{p} पर '{rv}' लिखकर ५-स्टार रिव्यू लिखें।",
  "contact_t": "संपर्क फ़ॉर्म से ऑर्डर {oid} का हवाला देते हुए '{msg}' संदेश भेजें।",
  "brandcount_q": "'{b}' ब्रांड कितने उत्पाद बेचता है?",
  "msg_cancel": "ऑर्डर 4 की अब ज़रूरत नहीं है, कृपया रद्दीकरण की पुष्टि करें।",
  "msg_missing": "ऑर्डर 2 में एक वस्तु गायब थी, कृपया बताएँ।",
  "rv_sturdy": "मज़बूत फ़्रेम, आसानी से जुड़ जाता है, रंग फ़ोटो से मेल खाता है।",
  "rv_fresh": "ताज़ा पहुँचा और पैकेजिंग भी ठीक रही।",
  "fake_product": "सेल्फ़-वॉटरिंग टाइटेनियम बुकशेल्फ़",
  "qa_warranty_q": "{p} के उत्पाद पेज पर प्रश्न और उत्तर अनुभाग है। वहाँ विक्रेता के उत्तर के अनुसार इसके साथ कितने महीने की वारंटी मिलती है?",
  "qa_delivery_q": "{p} के उत्पाद पेज के प्रश्न और उत्तर अनुभाग के अनुसार स्टैंडर्ड डिलीवरी में कितने कार्यदिवस लगते हैं?",
  "qa_count_q": "{p} के प्रश्न और उत्तर अनुभाग में कितने प्रश्न सूचीबद्ध हैं?",
  "ask_t": "{p} के उत्पाद पेज पर प्रश्न-उत्तर फ़ॉर्म से '{q}' प्रश्न पूछें।",
  "ask_wl_t": "{p} के उत्पाद पेज पर '{q}' प्रश्न पूछें, और उस उत्पाद को अपनी विशलिस्ट में भी जोड़ें।",
  "helpful_top_q": "{p} के उत्पाद पेज पर किस रिव्यूअर के रिव्यू को सबसे ज़्यादा 'उपयोगी' वोट मिले हैं? यूज़रनेम बताएँ।",
  "helpful_n_q": "{p} के उत्पाद पेज पर '{u}' के रिव्यू को कितने लोगों ने उपयोगी पाया?",
  "helpful_mark_t": "{p} के उत्पाद पेज पर '{u}' द्वारा लिखे रिव्यू का 'उपयोगी' बटन दबाएँ।",
  "helpful_mark_top_t": "{p} के उत्पाद पेज पर सबसे ज़्यादा 'उपयोगी' वोट वाला रिव्यू खोजें और उसका 'उपयोगी' बटन दबाएँ।",
  "brands_total_q": "स्टोर अपने ब्रांड पेज पर कितने ब्रांड सूचीबद्ध करता है?",
  "brands_more_q": "ब्रांड पेज के अनुसार कौन सा ब्रांड ज़्यादा उत्पाद सूचीबद्ध करता है: '{b1}' या '{b2}'? ब्रांड का नाम बताएँ।",
  "brands_avg_q": "ब्रांड पेज के अनुसार '{b1}' और '{b2}' में से किसकी औसत रिव्यू रेटिंग ज़्यादा है? ब्रांड का नाम बताएँ।",
  "q_colour": "क्या रंग फ़ोटो से बिल्कुल मेल खाता है?",
  "q_spare": "क्या बदलने के पुर्ज़े ऑर्डर किए जा सकते हैं?",
  "re_warranty": "(\\d+) महीने की वारंटी",
  "re_delivery": "(\\d+) कार्यदिवस",
  "na_alts": {
   "brand": [
    "ऐसा कोई ब्रांड नहीं",
    "ब्रांड नहीं",
    "नहीं मिला",
    "कोई उत्पाद नहीं",
    "०",
    "0",
    "शून्य"
   ],
   "product": [
    "नहीं मिला",
    "ऐसा कोई उत्पाद नहीं",
    "मौजूद नहीं",
    "सूचीबद्ध नहीं",
    "उपलब्ध नहीं"
   ],
   "coupon": [
    "अज्ञात",
    "अमान्य",
    "ऐसा कोई कूपन नहीं",
    "कूपन नहीं",
    "नहीं मिला"
   ],
   "oos": [
    "स्टॉक में नहीं",
    "ऑर्डर नहीं किया जा सकता",
    "उपलब्ध नहीं",
    "नहीं डाला जा सकता"
   ],
   "ghost": [
    "कोई रिव्यू नहीं",
    "रिव्यू नहीं दिया",
    "ऐसा कोई यूज़र नहीं",
    "रेटिंग नहीं दी",
    "रिव्यू नहीं किया"
   ],
   "under": [
    "कोई उत्पाद नहीं",
    "एक भी नहीं",
    "नहीं मिला",
    "उत्पाद नहीं"
   ],
   "order9": [
    "ऐसा कोई ऑर्डर नहीं",
    "ऑर्डर नहीं",
    "नहीं मिला",
    "मौजूद नहीं"
   ],
   "qty": [
    "नहीं था",
    "नहीं खरीदा",
    "०",
    "0",
    "शून्य",
    "शामिल नहीं",
    "ऑर्डर में नहीं"
   ],
   "freeship": [
    "समाप्त",
    "अब छूट नहीं",
    "सक्रिय नहीं",
    "निष्क्रिय",
    "0%",
    "०%"
   ],
   "ultra": [
    "नहीं मिला",
    "ऐसा कोई उत्पाद नहीं",
    "मौजूद नहीं",
    "सूचीबद्ध नहीं",
    "उत्पाद नहीं"
   ]
  },
  "d_bpf": "{cur}{price} कीमत वाला {brand} का {frag}",
  "d_bcf": "{cat} श्रेणी का {brand} का {frag}",
  "d_cpf": "{cat} श्रेणी का {cur}{price} कीमत वाला {frag}",
  "d_cf": "{cat} श्रेणी का {frag}",
  "d_bfc": "'{colour}' रंग का {brand} का {frag}",
  "d_cheapest": "{cat} श्रेणी का सबसे सस्ता उत्पाद (श्रेणी को कीमत के अनुसार क्रमबद्ध करें)",
  "d_mostrev": "{cat} श्रेणी का सबसे ज़्यादा रिव्यू वाला उत्पाद",
  "ord_min_total": "सबटोटल कम से कम {cur}{amt} पहुँचाने के लिए {p} की जितनी इकाइयाँ ज़रूरी हैं, उतनी ही (सबसे कम संख्या) ऑर्डर करें, शिपिंग पता '{a}'। पूरा चेकआउट करें।",
  "ord_cheaper2": "{p1} और {p2} की तुलना करें, और जो सस्ता है सिर्फ़ उसी का १ ऑर्डर करें, शिपिंग पता '{a}'। पूरा चेकआउट करें।",
  "ord_mixed": "एक ही ऑर्डर में {p1} १ और {p2} {q} खरीदें, शिपिंग पता '{a}'। पूरा चेकआउट करें।"
 },
 "ur": {
  "ord1": "ایک ہی آرڈر میں {p} ۱ عدد خریدیں، شپنگ ایڈریس '{a}'۔ مکمل چیک آؤٹ کریں۔",
  "ordq": "ایک ہی آرڈر میں {p} {q} عدد خریدیں، شپنگ ایڈریس '{a}'۔ مکمل چیک آؤٹ کریں۔",
  "ord2": "ایک ہی آرڈر میں {p1} ۱ عدد اور {p2} ۱ عدد خریدیں، شپنگ ایڈریس '{a}'۔ مکمل چیک آؤٹ کریں۔",
  "ord1_v": [
    "ایک ہی آرڈر میں {p} ۱ عدد خریدیں، شپنگ ایڈریس '{a}'۔ مکمل چیک آؤٹ کریں۔",
    "{p} ۱ عدد خرید کر '{a}' پر بھیجیں۔ چیک آؤٹ مکمل کریں تاکہ آرڈر واقعی پلیس ہو جائے۔",
    "مجھے {p} ایک عدد چاہیے، ڈیلیوری '{a}' پر۔ ایک ہی آرڈر میں مکمل چیک آؤٹ کر کے آرڈر دیں۔",
    "'{a}' کو شپنگ ایڈریس کے طور پر استعمال کرتے ہوئے {p} ایک عدد کا آرڈر دیں اور چیک آؤٹ مکمل کریں۔"
  ],
  "ordq_v": [
    "ایک ہی آرڈر میں {p} {q} عدد خریدیں، شپنگ ایڈریس '{a}'۔ مکمل چیک آؤٹ کریں۔",
    "{p} {q} عدد ایک آرڈر میں خریدیں، '{a}' پر شپ کریں۔ چیک آؤٹ مکمل کریں۔",
    "میں {p} {q} عدد '{a}' پر بھیجنا چاہتا ہوں — سب ایک ہی آرڈر میں رکھ کر پورا چیک آؤٹ کریں۔",
    "{p} خریدیں، مقدار {q}، ڈیلیوری ایڈریس '{a}'؛ یقینی بنائیں کہ آرڈر واقعی پلیس ہو۔"
  ],
  "ord2_v": [
    "ایک ہی آرڈر میں {p1} ۱ عدد اور {p2} ۱ عدد خریدیں، شپنگ ایڈریس '{a}'۔ مکمل چیک آؤٹ کریں۔",
    "{p1} اور {p2} ایک ساتھ خریدیں — دونوں ایک ہی آرڈر میں، ہر ایک ۱ عدد — '{a}' پر شپ کر کے۔ چیک آؤٹ مکمل کریں۔",
    "{p1} اور {p2} (ہر ایک ۱ عدد) کارٹ میں ڈالیں اور ایک آرڈر کے طور پر '{a}' پر چیک آؤٹ کریں۔",
    "مجھے {p1} اور {p2} ہر ایک ۱ عدد '{a}' پر ایک ہی شپمنٹ میں چاہیے؛ وہ آرڈر دیں۔"
  ],
  "ordcoupon": "ڈیلز صفحے پر فعال کوپن کوڈ تلاش کریں، پھر وہ کوپن لاگو کر کے {p} ۱ عدد '{a}' پر آرڈر کریں۔",
  "orddefault": "{p} ۱ عدد اپنی اکاؤنٹ سیٹنگز میں محفوظ ڈیفالٹ ایڈریس پر آرڈر کریں (چیک آؤٹ میں تجویز کردہ ایڈریس ویسا ہی رہنے دیں)۔",
  "ordsetdefault": "اپنی اکاؤنٹ سیٹنگز میں ڈیفالٹ شپنگ ایڈریس تبدیل کر کے '{a}' کریں۔ پھر {p} ۱ عدد اسی (نئے ڈیفالٹ) ایڈریس پر آرڈر کریں۔",
  "wladd1": "{p} کو اپنی وش لسٹ میں شامل کریں۔",
  "wladd2": "{p1} اور {p2} کو اپنی وش لسٹ میں شامل کریں۔",
  "wlremove": "{p} کو اپنی وش لسٹ سے ہٹائیں۔",
  "wlcheapest": "{cat} کیٹیگری کو قیمت کے لحاظ سے ترتیب دیں اور سب سے سستی {cat} پروڈکٹ اپنی وش لسٹ میں شامل کریں۔",
  "wlmostrev": "{cat} کیٹیگری میں سب سے زیادہ ریویوز والی پروڈکٹ تلاش کریں (سب سے زیادہ ریویوز کے لحاظ سے ترتیب دیں) اور اسے اپنی وش لسٹ میں شامل کریں۔",
  "setdefault": "اپنی اکاؤنٹ سیٹنگز میں ڈیفالٹ شپنگ ایڈریس تبدیل کر کے '{a}' کریں۔",
  "chgaddr": "آرڈر #{oid} کا ڈیلیوری ایڈریس تبدیل کر کے '{a}' کریں۔",
  "cancel": "آرڈر #{oid} منسوخ کریں (پوچھے جانے پر تصدیق کریں)۔",
  "chgcancel": "آرڈر #{oid} کا ڈیلیوری ایڈریس تبدیل کر کے '{a}' کریں، پھر وہ آرڈر منسوخ کریں (پوچھے جانے پر تصدیق کریں)۔",
  "cancelcontact": "آرڈر #{oid} منسوخ کریں، پھر رابطہ فارم سے آرڈر {oid} کا حوالہ دیتے ہوئے '{msg}' پیغام بھیجیں۔",
  "setwl": "سیٹنگز میں اپنا ڈیفالٹ شپنگ ایڈریس تبدیل کر کے '{a}' کریں، اور {p} کو اپنی وش لسٹ میں شامل کریں۔",
  "ordcancelnew": "{p} ۱ عدد '{a}' پر آرڈر کریں، پھر ابھی کیا گیا آرڈر منسوخ کریں (پوچھے جانے پر تصدیق کریں)۔",
  "wlreview": "{p} کو اپنی وش لسٹ میں شامل کریں اور اس پر '{rv}' لکھ کر ۴-اسٹار ریویو پوسٹ کریں۔",
  "na_brand": "'Zenithware' برانڈ کتنی پروڈکٹس بیچتا ہے؟",
  "na_product": "'{name}' کی قیمت کیا ہے؟",
  "na_coupon": "چیک آؤٹ پر کوپن کوڈ SAVE25 کتنے فیصد رعایت دیتا ہے؟",
  "na_oos": "{p} ۱ عدد آرڈر کریں۔ اگر آرڈر نہیں ہو سکتا تو N/A جواب دیں۔",
  "na_ghost": "یوزر 'ghost_gary' نے اپنے ریویو میں {p} کو کتنے اسٹار دیے؟",
  "na_under": "{cat} کیٹیگری میں {cur}{limit} سے کم قیمت کی کوئی بھی پروڈکٹ تلاش کریں اور اس کا نام بتائیں۔",
  "na_order9": "آرڈر #9 کا موجودہ اسٹیٹس کیا ہے؟",
  "na_qty": "آرڈر #2 میں آپ نے {p} کتنی مقدار میں خریدا؟",
  "na_freeship": "چیک آؤٹ پر کوپن کوڈ FREESHIP اس وقت کتنے فیصد رعایت دیتا ہے؟ اگر کوپن کی میعاد ختم ہو چکی ہے یا اب رعایت نہیں دیتا تو N/A جواب دیں۔",
  "na_ultra": "'{name} Ultra' کے کتنے یونٹ اسٹاک میں ہیں؟",
  "price_q": "{p} کی قیمت کیا ہے؟ رقم بتائیں۔",
  "brand_q": "{p} کس برانڈ کی ہے؟",
  "stock_q": "{p} کے کتنے یونٹ اس وقت اسٹاک میں ہیں؟",
  "cheaper_q": "کون سی سستی ہے، {p1} یا {p2}؟ پروڈکٹ کا درست نام بتائیں۔",
  "dearest_q": "ان میں سب سے مہنگی کون سی ہے: {ps}؟ پروڈکٹ کا درست نام بتائیں۔",
  "nrev_q": "{p} کے کتنے ریویوز ہیں؟",
  "onestar_q": "{p} کے کتنے ۱-اسٹار ریویوز ہیں؟",
  "avg_q": "{p} کے لیے دکھائی گئی اوسط اسٹار ریٹنگ کیا ہے؟",
  "higher_q": "کس کی اوسط اسٹار ریٹنگ زیادہ ہے: {p1} یا {p2}؟ پروڈکٹ کا درست نام بتائیں۔",
  "coupon_q": "ڈیلز صفحے پر درج اس وقت فعال کوپن کوڈ کیا ہے؟",
  "review_t": "{p} پر '{rv}' لکھ کر ۵-اسٹار ریویو لکھیں۔",
  "contact_t": "رابطہ فارم سے آرڈر {oid} کا حوالہ دیتے ہوئے '{msg}' پیغام بھیجیں۔",
  "brandcount_q": "'{b}' برانڈ کتنی پروڈکٹس بیچتا ہے؟",
  "msg_cancel": "آرڈر 4 کی اب ضرورت نہیں، براہ کرم منسوخی کی تصدیق کریں۔",
  "msg_missing": "آرڈر 2 میں ایک چیز غائب تھی، براہ کرم رہنمائی کریں۔",
  "rv_sturdy": "مضبوط فریم، آسانی سے جڑ جاتا ہے، رنگ تصویر سے میل کھاتا ہے۔",
  "rv_fresh": "تازہ پہنچا اور پیکنگ بھی ٹھیک رہی۔",
  "fake_product": "سیلف واٹرنگ ٹائٹینیم بک شیلف",
  "qa_warranty_q": "{p} کے پروڈکٹ صفحے پر سوالات و جوابات کا حصہ ہے۔ وہاں بیچنے والے کے جواب کے مطابق اس کے ساتھ کتنے ماہ کی وارنٹی ملتی ہے؟",
  "qa_delivery_q": "{p} کے پروڈکٹ صفحے کے سوالات و جوابات کے مطابق معیاری ڈیلیوری میں کتنے کاروباری دن لگتے ہیں؟",
  "qa_count_q": "{p} کے سوالات و جوابات کے حصے میں کتنے سوالات درج ہیں؟",
  "ask_t": "{p} کے پروڈکٹ صفحے پر سوال و جواب فارم سے '{q}' سوال پوچھیں۔",
  "ask_wl_t": "{p} کے پروڈکٹ صفحے پر '{q}' سوال پوچھیں، اور اس پروڈکٹ کو اپنی وش لسٹ میں بھی شامل کریں۔",
  "helpful_top_q": "{p} کے پروڈکٹ صفحے پر کس ریویوئر کے ریویو کو سب سے زیادہ 'مددگار' ووٹ ملے ہیں؟ یوزر نیم بتائیں۔",
  "helpful_n_q": "{p} کے پروڈکٹ صفحے پر '{u}' کے ریویو کو کتنے لوگوں نے مددگار پایا؟",
  "helpful_mark_t": "{p} کے پروڈکٹ صفحے پر '{u}' کے لکھے ریویو کا 'مددگار' بٹن دبائیں۔",
  "helpful_mark_top_t": "{p} کے پروڈکٹ صفحے پر سب سے زیادہ 'مددگار' ووٹ والا ریویو تلاش کریں اور اس کا 'مددگار' بٹن دبائیں۔",
  "brands_total_q": "اسٹور اپنے برانڈز صفحے پر کتنے برانڈز درج کرتا ہے؟",
  "brands_more_q": "برانڈز صفحے کے مطابق کون سا برانڈ زیادہ پروڈکٹس درج کرتا ہے: '{b1}' یا '{b2}'؟ برانڈ کا نام بتائیں۔",
  "brands_avg_q": "برانڈز صفحے کے مطابق '{b1}' اور '{b2}' میں سے کس کی اوسط ریویو ریٹنگ زیادہ ہے؟ برانڈ کا نام بتائیں۔",
  "q_colour": "کیا رنگ تصویروں سے بالکل میل کھاتا ہے؟",
  "q_spare": "کیا متبادل پرزے آرڈر کیے جا سکتے ہیں؟",
  "re_warranty": "(\\d+) ماہ کی وارنٹی",
  "re_delivery": "(\\d+) کاروباری دن",
  "na_alts": {
   "brand": [
    "ایسا کوئی برانڈ نہیں",
    "برانڈ نہیں",
    "نہیں ملا",
    "کوئی پروڈکٹ نہیں",
    "۰",
    "0",
    "صفر"
   ],
   "product": [
    "نہیں ملی",
    "نہیں ملا",
    "ایسی کوئی پروڈکٹ نہیں",
    "موجود نہیں",
    "درج نہیں",
    "دستیاب نہیں"
   ],
   "coupon": [
    "نامعلوم",
    "غلط",
    "ایسا کوئی کوپن نہیں",
    "کوپن نہیں",
    "نہیں ملا"
   ],
   "oos": [
    "اسٹاک میں نہیں",
    "آرڈر نہیں کیا جا سکتا",
    "دستیاب نہیں",
    "شامل نہیں کی جا سکتی"
   ],
   "ghost": [
    "کوئی ریویو نہیں",
    "ریویو نہیں دیا",
    "ایسا کوئی یوزر نہیں",
    "ریٹنگ نہیں دی",
    "ریویو نہیں کیا"
   ],
   "under": [
    "کوئی پروڈکٹ نہیں",
    "ایک بھی نہیں",
    "نہیں ملی",
    "پروڈکٹ نہیں"
   ],
   "order9": [
    "ایسا کوئی آرڈر نہیں",
    "آرڈر نہیں",
    "نہیں ملا",
    "موجود نہیں"
   ],
   "qty": [
    "نہیں تھا",
    "نہیں تھی",
    "نہیں خریدا",
    "۰",
    "0",
    "صفر",
    "شامل نہیں",
    "آرڈر میں نہیں"
   ],
   "freeship": [
    "میعاد ختم",
    "اب رعایت نہیں",
    "فعال نہیں",
    "غیر فعال",
    "0%",
    "۰%"
   ],
   "ultra": [
    "نہیں ملی",
    "نہیں ملا",
    "ایسی کوئی پروڈکٹ نہیں",
    "موجود نہیں",
    "درج نہیں",
    "پروڈکٹ نہیں"
   ]
  },
  "d_bpf": "{brand} کا {cur}{price} قیمت والا {frag}",
  "d_bcf": "{cat} کیٹیگری کا {brand} کا {frag}",
  "d_cpf": "{cat} کیٹیگری کا {cur}{price} قیمت والا {frag}",
  "d_cf": "{cat} کیٹیگری کا {frag}",
  "d_bfc": "'{colour}' رنگ کا {brand} کا {frag}",
  "d_cheapest": "{cat} کیٹیگری کی سب سے سستی پروڈکٹ (کیٹیگری کو قیمت کے لحاظ سے ترتیب دیں)",
  "d_mostrev": "{cat} کیٹیگری کی سب سے زیادہ ریویوز والی پروڈکٹ",
  "ord_min_total": "سب ٹوٹل کم از کم {cur}{amt} تک پہنچانے کے لیے {p} کے جتنے یونٹ درکار ہیں، بس اتنے ہی (کم سے کم تعداد) آرڈر کریں، شپنگ ایڈریس '{a}'۔ مکمل چیک آؤٹ کریں۔",
  "ord_cheaper2": "{p1} اور {p2} کا موازنہ کریں، اور جو سستی ہے صرف اسی کا ۱ عدد آرڈر کریں، شپنگ ایڈریس '{a}'۔ مکمل چیک آؤٹ کریں۔",
  "ord_mixed": "ایک ہی آرڈر میں {p1} ۱ عدد اور {p2} {q} عدد خریدیں، شپنگ ایڈریس '{a}'۔ مکمل چیک آؤٹ کریں۔"
 },
 "am": {
  "ord1": "{p} 1 በአንድ ትዕዛዝ ይዘዙ፣ ወደ '{a}' ይላክ። ሙሉውን ቼክአውት ያጠናቅቁ።",
  "ordq": "{p} {q} በአንድ ትዕዛዝ ይዘዙ፣ ወደ '{a}' ይላክ። ሙሉውን ቼክአውት ያጠናቅቁ።",
  "ord2": "{p1} 1 እና {p2} 1 በአንድ ትዕዛዝ ይዘዙ፣ ወደ '{a}' ይላክ። ሙሉውን ቼክአውት ያጠናቅቁ።",
  "ord1_v": [
    "{p} 1 በአንድ ትዕዛዝ ይዘዙ፣ ወደ '{a}' ይላክ። ሙሉውን ቼክአውት ያጠናቅቁ።",
    "{p} 1 ገዝተው ወደ '{a}' ያስላኩ። ትዕዛዙ በእርግጥ እንዲመዘገብ ቼክአውቱን እስከ መጨረሻው ያጠናቅቁ።",
    "{p} አንድ ያስፈልገኛል፣ ማድረሻው '{a}' ነው። በአንድ ትዕዛዝ ሙሉውን ቼክአውት አጠናቅቀው ትዕዛዙን ይስጡ።",
    "'{a}'ን የመላኪያ አድራሻ አድርገው {p} አንድ ይዘዙ እና ቼክአውቱን ያጠናቅቁ።"
  ],
  "ordq_v": [
    "{p} {q} በአንድ ትዕዛዝ ይዘዙ፣ ወደ '{a}' ይላክ። ሙሉውን ቼክአውት ያጠናቅቁ።",
    "{p} {q} ቁርጥራጭ በአንድ ትዕዛዝ ይግዙ፣ ወደ '{a}' ይላክ። ቼክአውቱን ያጠናቅቁ።",
    "{p} {q} ወደ '{a}' እንዲላክ እፈልጋለሁ — ሁሉንም በአንድ ትዕዛዝ አድርገው ሙሉውን ቼክአውት ያድርጉ።",
    "{p} ይግዙ፣ ብዛት {q}፣ የማድረሻ አድራሻ '{a}'፤ ትዕዛዙ በእርግጥ መመዝገቡን ያረጋግጡ።"
  ],
  "ord2_v": [
    "{p1} 1 እና {p2} 1 በአንድ ትዕዛዝ ይዘዙ፣ ወደ '{a}' ይላክ። ሙሉውን ቼክአውት ያጠናቅቁ።",
    "{p1} እና {p2} አብረው ይግዙ — ሁለቱም በአንድ ትዕዛዝ፣ እያንዳንዱ 1 — ወደ '{a}' እንዲላክ። ቼክአውቱን ያጠናቅቁ።",
    "{p1} እና {p2} (እያንዳንዱ 1) ወደ ጋሪ ያስገቡ እና እንደ አንድ ትዕዛዝ ወደ '{a}' ቼክአውት ያድርጉ።",
    "{p1} እና {p2} እያንዳንዱ 1 ወደ '{a}' በአንድ ጭነት ያስፈልገኛል፤ ያንን ትዕዛዝ ይስጡ።"
  ],
  "ordcoupon": "በቅናሾች ገጽ ላይ ንቁውን የኩፖን ኮድ ያግኙ፣ ከዚያ ያንን ኩፖን ተግብረው {p} 1 ወደ '{a}' ይዘዙ።",
  "orddefault": "{p} 1 በመለያ ቅንብሮችዎ ውስጥ ወደተቀመጠው ነባሪ አድራሻ ይዘዙ (በቼክአውት የተጠቆመውን አድራሻ እንዳለ ይተዉት)።",
  "ordsetdefault": "በመለያ ቅንብሮችዎ ውስጥ ነባሪ የመላኪያ አድራሻዎን ወደ '{a}' ይቀይሩ። ከዚያ {p} 1 ወደዚያ (አዲሱ ነባሪ) አድራሻ ይዘዙ።",
  "wladd1": "{p} ወደ ዊሽሊስትዎ ይጨምሩ።",
  "wladd2": "{p1} እና {p2} ወደ ዊሽሊስትዎ ይጨምሩ።",
  "wlremove": "{p} ከዊሽሊስትዎ ያስወግዱ።",
  "wlcheapest": "የ{cat} ምድብን በዋጋ ደርድረው በጣም ርካሹን የ{cat} ምርት ወደ ዊሽሊስትዎ ይጨምሩ።",
  "wlmostrev": "በ{cat} ምድብ ውስጥ በጣም የተገመገመውን ምርት ያግኙ (በጣም የተገመገመ በሚለው ደርድሩ) እና ወደ ዊሽሊስትዎ ይጨምሩት።",
  "setdefault": "በመለያ ቅንብሮችዎ ውስጥ ነባሪ የመላኪያ አድራሻዎን ወደ '{a}' ይቀይሩ።",
  "chgaddr": "የትዕዛዝ #{oid} የመላኪያ አድራሻ ወደ '{a}' ይቀይሩ።",
  "cancel": "ትዕዛዝ #{oid} ይሰርዙ (ሲጠየቁ ያረጋግጡ)።",
  "chgcancel": "የትዕዛዝ #{oid} የመላኪያ አድራሻ ወደ '{a}' ይቀይሩ፣ ከዚያ ያንን ትዕዛዝ ይሰርዙ (ሲጠየቁ ያረጋግጡ)።",
  "cancelcontact": "ትዕዛዝ #{oid} ይሰርዙ፣ ከዚያ የአግኙን ቅጹን ተጠቅመው ትዕዛዝ {oid}ን በመጥቀስ '{msg}' የሚለውን መልዕክት ይላኩ።",
  "setwl": "በቅንብሮች ውስጥ ነባሪ የመላኪያ አድራሻዎን ወደ '{a}' ይቀይሩ፣ እና {p} ወደ ዊሽሊስትዎ ይጨምሩ።",
  "ordcancelnew": "{p} 1 ወደ '{a}' ይዘዙ፣ ከዚያ አሁን ያስገቡትን ትዕዛዝ ይሰርዙ (ሲጠየቁ ያረጋግጡ)።",
  "wlreview": "{p} ወደ ዊሽሊስትዎ ይጨምሩ እና '{rv}' የሚል የ4-ኮከብ ግምገማ በላዩ ላይ ይለጥፉ።",
  "na_brand": "'Zenithware' ብራንድ ስንት ምርቶችን ይሸጣል?",
  "na_product": "የ'{name}' ዋጋ ስንት ነው?",
  "na_coupon": "የኩፖን ኮድ SAVE25 በቼክአውት ስንት በመቶ ቅናሽ ይሰጣል?",
  "na_oos": "{p} 1 ይዘዙ። ማዘዝ ካልተቻለ N/A ብለው ይመልሱ።",
  "na_ghost": "ተጠቃሚ 'ghost_gary' በግምገማው ውስጥ {p} ስንት ኮከብ ሰጠው?",
  "na_under": "በ{cat} ምድብ ውስጥ ከ{cur}{limit} በታች ዋጋ ያለው ማንኛውንም ምርት ያግኙና ስሙን ይግለጹ።",
  "na_order9": "የትዕዛዝ #9 የአሁኑ ሁኔታ ምንድን ነው?",
  "na_qty": "በትዕዛዝ #2 ውስጥ {p} ስንት ገዙ?",
  "na_freeship": "የኩፖን ኮድ FREESHIP በአሁኑ ጊዜ በቼክአውት ስንት በመቶ ቅናሽ ይሰጣል? ኩፖኑ ጊዜው ካለፈ ወይም ቅናሽ ካልሰጠ N/A ብለው ይመልሱ።",
  "na_ultra": "የ'{name} Ultra' ስንት ክፍሎች በክምችት አሉ?",
  "price_q": "{p} ዋጋው ስንት ነው? መጠኑን ይመልሱ።",
  "brand_q": "{p} የየትኛው ብራንድ ነው?",
  "stock_q": "{p} በአሁኑ ጊዜ ስንት ክፍሎች በክምችት አሉት?",
  "cheaper_q": "የትኛው ርካሽ ነው፣ {p1} ወይስ {p2}? ትክክለኛውን የምርት ስም ይመልሱ።",
  "dearest_q": "ከእነዚህ ውስጥ በጣም ውዱ የትኛው ነው፡ {ps}? ትክክለኛውን የምርት ስም ይመልሱ።",
  "nrev_q": "{p} ስንት ግምገማዎች አሉት?",
  "onestar_q": "{p} ስንት የ1-ኮከብ ግምገማዎች አሉት?",
  "avg_q": "{p} የሚታየው አማካይ የኮከብ ደረጃ ስንት ነው?",
  "higher_q": "የትኛው ከፍ ያለ አማካይ የኮከብ ደረጃ አለው፡ {p1} ወይስ {p2}? ትክክለኛውን የምርት ስም ይመልሱ።",
  "coupon_q": "በቅናሾች ገጽ ላይ የተዘረዘረው በአሁኑ ጊዜ ንቁ የሆነው የኩፖን ኮድ ምንድን ነው?",
  "review_t": "{p} ላይ '{rv}' የሚል የ5-ኮከብ ግምገማ ይጻፉ።",
  "contact_t": "የአግኙን ቅጹን ተጠቅመው ትዕዛዝ {oid}ን በመጥቀስ '{msg}' የሚለውን መልዕክት ይላኩ።",
  "brandcount_q": "'{b}' ብራንድ ስንት ምርቶችን ይሸጣል?",
  "msg_cancel": "ትዕዛዝ 4 ከእንግዲህ አያስፈልግም፣ እባክዎ ስረዛውን ያረጋግጡ።",
  "msg_missing": "ትዕዛዝ 2 አንድ ዕቃ ጎድሎት መጣ፣ እባክዎ ይመክሩ።",
  "rv_sturdy": "ጠንካራ ፍሬም፣ ለመገጣጠም ቀላል፣ ቀለሙ ከፎቶው ጋር ይዛመዳል።",
  "rv_fresh": "ትኩስ ሆኖ ደረሰ እና ማሸጊያው በደንብ ቆይቷል።",
  "fake_product": "ራስ-ውሃ ማጠጫ ታይታኒየም መጽሐፍ መደርደሪያ",
  "qa_warranty_q": "{p} የምርት ገጽ የጥያቄዎችና መልሶች ክፍል አለው። እዚያ ባለው የሻጩ መልስ መሠረት የስንት ወር ዋስትና አለው?",
  "qa_delivery_q": "{p} የምርት ገጽ የጥያቄዎችና መልሶች ክፍል መሠረት መደበኛ መላኪያ ስንት የስራ ቀናት ይወስዳል?",
  "qa_count_q": "{p} የጥያቄዎችና መልሶች ክፍል ውስጥ ስንት ጥያቄዎች ተዘርዝረዋል?",
  "ask_t": "{p} የምርት ገጽ ላይ የጥያቄና መልስ ቅጹን ተጠቅመው '{q}' የሚለውን ጥያቄ ይጠይቁ።",
  "ask_wl_t": "{p} የምርት ገጽ ላይ '{q}' የሚለውን ጥያቄ ይጠይቁ፣ እንዲሁም ያንን ምርት ወደ ዊሽሊስትዎ ይጨምሩ።",
  "helpful_top_q": "{p} የምርት ገጽ ላይ የየትኛው ገምጋሚ ግምገማ በጣም ብዙ የ'ጠቃሚ' ድምጾች አሉት? የተጠቃሚ ስሙን ይመልሱ።",
  "helpful_n_q": "{p} የምርት ገጽ ላይ የ'{u}' ግምገማን ስንት ሰዎች ጠቃሚ ሆኖ አገኙት?",
  "helpful_mark_t": "{p} የምርት ገጽ ላይ '{u}' በጻፈው ግምገማ ላይ የ'ጠቃሚ' ቁልፉን ይጫኑ።",
  "helpful_mark_top_t": "{p} የምርት ገጽ ላይ በጣም ብዙ የ'ጠቃሚ' ድምጾች ያለውን ግምገማ አግኝተው የ'ጠቃሚ' ቁልፉን ይጫኑ።",
  "brands_total_q": "መደብሩ በብራንዶች ገጹ ላይ ስንት ብራንዶችን ይዘረዝራል?",
  "brands_more_q": "በብራንዶች ገጽ መሠረት የትኛው ብራንድ ብዙ ምርቶችን ይዘረዝራል፡ '{b1}' ወይስ '{b2}'? የብራንዱን ስም ይመልሱ።",
  "brands_avg_q": "በብራንዶች ገጽ መሠረት ከ'{b1}' እና '{b2}' የትኛው ከፍ ያለ አማካይ የግምገማ ደረጃ አለው? የብራንዱን ስም ይመልሱ።",
  "q_colour": "ቀለሙ ከፎቶዎቹ ጋር በትክክል ይዛመዳል?",
  "q_spare": "መለዋወጫ ክፍሎች ማዘዝ ይቻላል?",
  "re_warranty": "የ(\\d+) ወር ዋስትና",
  "re_delivery": "(\\d+) የስራ ቀናት",
  "na_alts": {
   "brand": [
    "እንደዚህ ያለ ብራንድ የለም",
    "ብራንድ የለም",
    "አልተገኘም",
    "ምንም ምርት የለም",
    "0",
    "ዜሮ"
   ],
   "product": [
    "አልተገኘም",
    "እንደዚህ ያለ ምርት የለም",
    "የለም",
    "አልተዘረዘረም",
    "አይገኝም"
   ],
   "coupon": [
    "ያልታወቀ",
    "ልክ ያልሆነ",
    "እንደዚህ ያለ ኩፖን የለም",
    "ኩፖን የለም",
    "አልተገኘም"
   ],
   "oos": [
    "ከክምችት ውጪ",
    "ማዘዝ አይቻልም",
    "አይገኝም",
    "ሊጨመር አይችልም"
   ],
   "ghost": [
    "ግምገማ የለም",
    "አልገመገመም",
    "እንደዚህ ያለ ተጠቃሚ የለም",
    "ደረጃ አልሰጠም",
    "ግምገማ አልሰጠም"
   ],
   "under": [
    "ምንም ምርት የለም",
    "አንድም የለም",
    "አልተገኘም",
    "ምርት የለም"
   ],
   "order9": [
    "እንደዚህ ያለ ትዕዛዝ የለም",
    "ትዕዛዝ የለም",
    "አልተገኘም",
    "የለም"
   ],
   "qty": [
    "አልነበረም",
    "አልገዙም",
    "0",
    "ዜሮ",
    "አልተካተተም",
    "በትዕዛዙ ውስጥ የለም"
   ],
   "freeship": [
    "ጊዜው አልፏል",
    "ጊዜው ያለፈ",
    "ከእንግዲህ ቅናሽ",
    "ንቁ አይደለም",
    "0%"
   ],
   "ultra": [
    "አልተገኘም",
    "እንደዚህ ያለ ምርት የለም",
    "የለም",
    "አልተዘረዘረም",
    "ምርት የለም"
   ]
  },
  "d_bpf": "በ{cur}{price} የሚሸጠው የ{brand} {frag} ምርት",
  "d_bcf": "በ{cat} ምድብ ያለው የ{brand} {frag} ምርት",
  "d_cpf": "በ{cat} ምድብ በ{cur}{price} የሚሸጠው {frag} ምርት",
  "d_cf": "በ{cat} ምድብ ያለው {frag} ምርት",
  "d_bfc": "'{colour}' ቀለም ያለው የ{brand} {frag} ምርት",
  "d_cheapest": "በ{cat} ምድብ ውስጥ በጣም ርካሹ ምርት (ምድቡን በዋጋ ደርድሩ)",
  "d_mostrev": "በ{cat} ምድብ ውስጥ በጣም የተገመገመው ምርት",
  "ord_min_total": "ንዑስ ድምሩ ቢያንስ {cur}{amt} እንዲደርስ የሚያስፈልገውን ያህል ብቻ (ትንሹን ቁጥር) {p} ይዘዙ፣ ወደ '{a}' ይላክ። ሙሉውን ቼክአውት ያጠናቅቁ።",
  "ord_cheaper2": "{p1} እና {p2}ን ያነጻጽሩ፣ እና ርካሹን ብቻ 1 ይዘዙ፣ ወደ '{a}' ይላክ። ሙሉውን ቼክአውት ያጠናቅቁ።",
  "ord_mixed": "{p1} 1 እና {p2} {q} በአንድ ትዕዛዝ ይዘዙ፣ ወደ '{a}' ይላክ። ሙሉውን ቼክአውት ያጠናቅቁ።"
 }
}
for _l, _p in I18N.items():
    assert set(_p) == set(I18N["en"]), (_l, set(_p) ^ set(I18N["en"]))

NATIVE_DIGITS = {
    "hi": str.maketrans("0123456789", "०१२३४५६७८९"),
    "bn": str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"),
    "ur": str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"),
}
EXTRA_DIGITS = {
    "ur": str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"),
}


def money(x):
    return f"{x:.2f}"


def half_up1(x):
    import math
    return math.floor(x * 10 + 0.5) / 10


def build(lang):
    P = I18N[lang]
    cred = CRED[lang]
    A = [x.translate(NATIVE_DIGITS[lang]) if lang in NATIVE_DIGITS else x
         for x in ADDR[lang]]
    default_addr = loc_addr(lang, "12 Ocean Ave, Tampa, 33601")
    meta = LANG_META[lang]

    base = load_catalog("en")
    loc = {c["id"]: c for c in load_catalog(lang)}
    _, _, _, reviews, _, _, _, qa = build_rows(lang)
    rev_by_pid = collections.defaultdict(list)
    rev_rows = collections.defaultdict(list)
    for rid_, pid, uid_, stars, _body, helpful_ in reviews:
        rev_by_pid[pid].append(stars)
        rev_rows[pid].append((rid_, uid_, stars, helpful_))
    uname = {i + 1: u for i, (u, _pw, _a) in enumerate(USERS)}
    qa_by_pid = collections.defaultdict(list)
    for _qid, pid, _uid, q_, a_ in qa:
        qa_by_pid[pid].append((q_, a_))

    def N(c):
        return loc[c["id"]]["name"]

    def price(c):
        return loc[c["id"]]["price"]

    def cat_disp(c):
        return loc[c["id"]]["category"]

    def nq(x):
        return (str(x).translate(NATIVE_DIGITS[lang])
                if lang in NATIVE_DIGITS else str(x))

    locs_all = {l: {c["id"]: c for c in load_catalog(l)} for l in LANG_META}

    _STOP = {"for", "with", "w/", "in", "on", "to", "of", "and", "&", "a",
             "an", "the", "by", "x",
             "pound", "pounds", "lb", "lbs", "inch", "inches", "ounce",
             "oz", "piece", "pieces", "pack", "ct", "count", "onez"}
    _JUNK = {"black", "white", "blk", "grey", "gray", "blue", "red", "green",
             "pink", "brown", "silver", "gold", "beige", "navy", "parent",
             "multicolor", "multicolour", "clear", "natural", "assorted"}
    _VARIANTS = ("Twin Pack", "Classic")

    def _is_junk(t):
        return any(p in _JUNK for p in t.lower().strip("()").split("-"))

    def _starts_ok(t):
        return t[0].isalpha() and len(t) >= 2 and t.lower() not in _STOP

    def _ends_ok(t):
        return (any(ch.isalpha() for ch in t) and len(t) >= 2
                and t.lower() not in _STOP and not _is_junk(t))

    def head_tail_en(name, brand):
        suffix = ""
        for v in _VARIANTS:
            if name.endswith(" " + v):
                name, suffix = name[:-len(v) - 1], " " + v
                break
        toks = name.split()
        bt = brand.lower().split()
        while toks and bt and toks[0].lower() == bt[0]:
            toks, bt = toks[1:], bt[1:]
        for i in range(1, len(toks)):
            if toks[i].endswith("-") and toks[i][:-1].isalpha():
                toks = toks[:i] + [toks[i][:-1]]
                break
        for i in range(1, len(toks)):
            if toks[i].lower() in ("for", "with", "w/"):
                toks = toks[:i]
                break
        while len(toks) > 1 and not _ends_ok(toks[-1]):
            toks = toks[:-1]
        if len(toks) <= 3:
            return " ".join(toks) + suffix
        k = 2
        while k < 4 and not _starts_ok(toks[-k]):
            k += 1
        return " ".join(toks[-k:]) + suffix

    _STOP_L = {
        "bn": {"সহ", "ও", "এবং", "জন্য", "থেকে", "-এর", "এর", "x", "X", "-",
               "বাই", "ইন",
               "পাউন্ড", "ইঞ্চি", "আউন্স", "পিস", "প্যাক", "কেজি", "গ্রাম",
               "লিটার", "মিলি", "সেমি", "মিটার", "ফুট", "গজ", "টুকরো"},
        "hi": {"के", "साथ", "और", "लिए", "से", "का", "की", "x", "X", "-", "में",
               "पाउंड", "इंच", "औंस", "पीस", "पैक", "किलो", "ग्राम", "लीटर",
               "मिली", "सेमी", "मीटर", "फुट"},
        "ur": {"کے", "ساتھ", "اور", "لیے", "سے", "کا", "کی", "x", "X", "-", "میں",
               "پاؤنڈ", "انچ", "اونس", "پیس", "پیک", "کلو", "گرام", "لیٹر",
               "ملی", "سینٹی", "میٹر", "فٹ"},
        "am": {"እና", "ጋር", "ለ", "x", "X", "-", "ከ", "ወደ", "ወይም", "እስከ", "በ",
               "ፓውንድ", "ኢንች", "አውንስ", "ፒስ", "ፓክ", "ኪሎ", "ግራም", "ሊትር",
               "ሚሊ", "ሴሜ", "ሜትር", "ጫማ"},
    }

    def _native(t, l):
        return any(ord(ch) > 0x7F and ch.isalpha() for ch in t)

    en_by_name = {c["name"]: c["id"] for c in base}

    import re as _re

    def frag_for(c, l):
        lname = locs_all[l][c["id"]]["name"]
        if l == "en":
            return head_tail_en(c["name"], c["brand"])
        suffix = ""
        for v in _VARIANTS:
            if c["name"].endswith(" " + v):
                base_id = en_by_name.get(c["name"][:-len(v) - 1])
                if base_id is not None:
                    bname = locs_all[l][base_id]["name"]
                    if lname.startswith(bname) and len(lname) > len(bname):
                        lname, suffix = bname, lname[len(bname):]
                break
        stop = _STOP_L.get(l, set())
        core = _re.split(r"[,،፣]| - ", lname)[0].strip()
        toks = core.split()
        bt = c["brand"].split()
        while toks and bt and toks[0].lower() == bt[0].lower():
            toks, bt = toks[1:], bt[1:]
        while toks and (toks[-1] in stop or toks[-1].startswith("(")
                        or not _native(toks[-1], l)):
            toks = toks[:-1]
        if not toks:
            return lname + suffix
        toks[-1] = toks[-1].rstrip("-")
        if len(toks) <= 3:
            return " ".join(toks) + suffix
        for k in (2, 3, 4):
            w = toks[-k:]
            if _native(w[0], l) and w[0] not in stop:
                return " ".join(w) + suffix
        return " ".join(toks[-4:]) + suffix

    _COL_RE = _re.compile(r"^[^:]{1,20}:\s*([^.।۔።]+?)\s*[.।۔።]")
    _COLOUR_WORDS = {"black", "white", "blue", "grey", "gray", "brown",
                     "clear", "silver", "red", "green", "beige", "pink",
                     "orange", "yellow", "purple", "gold", "navy", "teal",
                     "turquoise", "ivory", "cream", "transparent",
                     "multicolor", "multicolour", "maroon", "violet",
                     "charcoal", "copper", "bronze", "rose", "aqua",
                     "lavender", "mint", "olive", "tan", "khaki", "burgundy"}
    COLOUR = {}
    for l, lc_all in locs_all.items():
        COLOUR[l] = {}
        for x in base:
            if x["description"].startswith("Colour:"):
                m = _COL_RE.match(lc_all[x["id"]]["description"])
                assert m, (x["id"], l)
                COLOUR[l][x["id"]] = m.group(1)

    def real_colour(c):
        col = COLOUR["en"].get(c["id"], "")
        return (col.replace("-", " ").split() and
                all(w.lower() in _COLOUR_WORDS or w.lower() in ("light", "dark")
                    for w in col.replace("-", " ").split())
                and any(w.lower() in _COLOUR_WORDS for w in col.split()))

    def unique_ref(c, kind):
        if kind == "bfc" and not real_colour(c):
            return False
        for l, lc_all in locs_all.items():
            lc = lc_all[c["id"]]
            fr = frag_for(c, l)
            col = COLOUR[l].get(c["id"])
            n = 0
            for x in base:
                lx = lc_all[x["id"]]
                if fr not in lx["name"]:
                    continue
                if kind in ("bpf", "bcf", "bfc") and x["brand"] != c["brand"]:
                    continue
                if kind in ("bpf", "cpf") and abs(lx["price"] - lc["price"]) >= 0.005:
                    continue
                if kind in ("bcf", "cpf", "cf") and lx["category"] != lc["category"]:
                    continue
                if kind == "bfc" and COLOUR[l].get(x["id"]) != col:
                    continue
                n += 1
            if n != 1:
                return False
        return True

    def D(c, kind="bpf"):
        assert unique_ref(c, kind), (c["id"], kind)
        lc = loc[c["id"]]
        return P["d_" + kind].format(
            brand=c["brand"], frag=frag_for(c, lang), cat=lc["category"],
            cur=meta["cur"], price=nq(money(lc["price"])),
            colour=COLOUR[lang].get(c["id"], ""))

    def Dk(c, prefs):
        for k in prefs:
            if unique_ref(c, k):
                return D(c, k)
        raise AssertionError((c["id"], prefs))

    def R(kind, c):
        return P["d_" + kind].format(cat=cat_disp(c))

    def cheapest_in(cat, min_stock=1):
        lst = sorted((c for c in base if c["category"] == cat),
                     key=lambda c: c["price"])
        assert lst[1]["price"] > lst[0]["price"] and lst[0]["stock"] >= min_stock
        return lst[0]

    def mostrev_in(cat):
        counts = collections.Counter({c["id"]: len(rev_by_pid.get(c["id"], []))
                                      for c in base if c["category"] == cat})
        (top, tn), (_, sn) = counts.most_common(2)
        assert tn > sn
        c = next(x for x in base if x["id"] == top)
        assert c["stock"] >= 1
        return c

    in_stock = [c for c in base if c["stock"] >= 4
                and " " in c["name"] and len(c["name"]) <= 55]
    by_cat = collections.defaultdict(list)
    for c in in_stock:
        by_cat[c["category"]].append(c)

    used = set()
    brand_names_cf = {c["brand"].casefold() for c in base}

    def quotable(c):
        import re as _re2
        return ("'" not in c["name"]
                and c["name"].casefold() not in brand_names_cf
                and not _re2.search(r"\btest\d*\b", c["name"], _re2.I)
                and " x " not in head_tail_en(c["name"], c["brand"]))

    def pick(cat, min_price=5, max_price=200, kinds=("bpf", "bcf", "cpf"),
             ok=None):
        for c in by_cat[cat]:
            if c["id"] in used:
                continue
            if not (min_price <= c["price"] <= max_price):
                continue
            if not quotable(c):
                continue
            if not all(unique_ref(c, k) for k in kinds):
                continue
            if ok is not None and not ok(c):
                continue
            used.add(c["id"])
            return c
        raise AssertionError(f"no pick left in {cat} for {kinds}")

    T = []

    def task(n, intent, eval_, solution, login=True, max_steps=30):
        T.append({"id": f"visual-{n:03d}", "site": "ministore",
                  "intent": intent + (cred if login else ""),
                  "start_path": "/", "eval": eval_, "solution": solution,
                  "max_steps": max_steps,
                  "difficulty": ("hard" if n <= 51 else
                                 "medium" if n <= 63 else "easy")})

    def order_ev(items, address, total, coupon=None):
        ev = [{"type": "order_contains", "address": f"%{address}%",
               "items": {str(k): v for k, v in items.items()},
               "total": round(total, 2)}]
        if coupon:
            ev.append({"type": "db_record_exists", "table": "orders",
                       "match": {"address": f"%{address}%",
                                 "coupon_code": coupon}})
        return ev

    def num_targets(x):
        s = str(x)
        out = [s]
        digits = s.replace(".", "").replace(",", "")
        if digits.isdigit() and len(digits.split(".")[0]) > 3:
            try:
                out.append(f"{float(s):,.2f}" if "." in s
                           else f"{int(s):,}")
            except ValueError:
                pass
        if lang in NATIVE_DIGITS:
            base = list(out)
            out += [v.translate(NATIVE_DIGITS[lang]) for v in base]
            if lang in EXTRA_DIGITS:
                out += [v.translate(EXTRA_DIGITS[lang]) for v in base]
        return list(dict.fromkeys(out))

    def script_variants(s):
        if (lang in NATIVE_DIGITS and any(c.isdigit() for c in s)
                and any(ord(c) > 127 for c in s)):
            vs = [s.translate(NATIVE_DIGITS[lang])]
            if lang in EXTRA_DIGITS:
                vs.append(s.translate(EXTRA_DIGITS[lang]))
            return vs
        return []

    def ans(n, intent, targets, solution, login=False, none_of=()):
        tg = targets if isinstance(targets, list) else [targets]
        tg = list(dict.fromkeys(tg + [v for t_ in tg
                                      for v in script_variants(t_)]))
        ev = {"type": "answer_match", "mode": "contains", "any_of": tg}
        if none_of:
            ev["none_of"] = list(dict.fromkeys(
                [x for x_ in none_of for x in [x_] + script_variants(x_)]))
        task(n, intent, [ev], solution, login=login)

    def cat_url(c):
        return f"/category/{quote(cat_disp(c))}"

    n = 0

    def one_order(n, intent, p, qty, a, pre=()):
        task(n, intent, order_ev({p["id"]: qty}, a, price(p) * qty),
             LOGIN + list(pre) + [f"goto /product/{p['id']}",
                                  f"fill 1 qty={qty}", "goto /checkout",
                                  f"fill 1 address={a}", "fill 2"],
             max_steps=40 if pre else 30)

    c_cheap = cheapest_in("Sports", min_stock=2)
    c_rev = mostrev_in("Pets")
    used.update({c_cheap["id"], c_rev["id"]})

    for cat, kind in [("Electronics", "bpf"), ("Kitchen", "bpf"),
                      ("Sports", "bpf"), ("Home", "bpf"), ("Garden", "cf"),
                      ("Pets", "cf"), ("Office", "bfc"),
                      ("Electronics", "bfc")]:
        n += 1
        p = pick(cat, kinds=(kind,))
        a = A[n % len(A)]
        one_order(n, P["ord1_v"][n % 4].format(p=D(p, kind), a=a), p, 1, a)

    n += 1
    a = A[n % len(A)]
    one_order(n, P["ord1_v"][n % 4].format(p=R("cheapest", c_cheap), a=a),
              c_cheap, 1, a, pre=[f"goto {cat_url(c_cheap)}?sort=price_asc"])
    n += 1
    a = A[n % len(A)]
    one_order(n, P["ord1_v"][n % 4].format(p=R("mostrev", c_rev), a=a),
              c_rev, 1, a, pre=[f"goto {cat_url(c_rev)}?sort=reviews"])

    for qty, cat, kind in [(2, "Electronics", "bpf"), (3, "Grocery", "cf"),
                           (2, "Pets", "bfc")]:
        n += 1
        p = pick(cat, kinds=(kind,))
        a = A[n % len(A)]
        one_order(n, P["ordq_v"][n % 4].format(q=nq(qty), p=D(p, kind), a=a),
                  p, qty, a)

    for (cat1, k1), (cat2, k2) in [(("Kitchen", "bpf"), ("Grocery", "bpf")),
                                   (("Sports", "cf"), ("Pets", "cf")),
                                   (("Home", "bfc"), ("Garden", "bpf"))]:
        n += 1
        p1, p2 = pick(cat1, kinds=(k1,)), pick(cat2, kinds=(k2,))
        a = A[n % len(A)]
        task(n, P["ord2_v"][n % 4].format(p1=D(p1, k1), p2=D(p2, k2), a=a),
             order_ev({p1["id"]: 1, p2["id"]: 1}, a,
                      price(p1) + price(p2)),
             LOGIN + [f"goto /product/{p1['id']}", "fill 1 qty=1",
                      f"goto /product/{p2['id']}", "fill 1 qty=1",
                      "goto /checkout", f"fill 1 address={a}", "fill 2"])

    import math

    def min_units_ok(c):
        q = math.ceil(100 / c["price"])
        if not ((q - 1) * c["price"] <= 97 and q * c["price"] >= 103):
            return False
        return all(math.ceil(100 * LANG_META[l]["rate"]
                             / lc_all[c["id"]]["price"] - 1e-9) == q
                   for l, lc_all in locs_all.items()) and c["stock"] >= q + 1

    for cat, kind in [("Office", "bpf"), ("Kitchen", "cf")]:
        n += 1
        p = pick(cat, min_price=15, max_price=45, kinds=(kind,),
                 ok=min_units_ok)
        qty = math.ceil(100 / p["price"])
        a = A[n % len(A)]
        one_order(n, P["ord_min_total"].format(
            p=D(p, kind), cur=meta["cur"],
            amt=nq(money(100 * meta["rate"])), a=a), p, qty, a)

    for cat, kind in [("Electronics", "bpf"), ("Home", "cf"),
                      ("Sports", "bfc")]:
        n += 1
        p = pick(cat, min_price=20, kinds=(kind,))
        a = A[n % len(A)]
        total = round(round(price(p), 2) * (100 - 10) / 100.0, 2)
        task(n, P["ordcoupon"].format(p=D(p, kind), a=a),
             order_ev({p["id"]: 1}, a, total, coupon=ACTIVE_COUPON),
             LOGIN + ["goto /deals", f"goto /product/{p['id']}",
                      "fill 1 qty=1", "goto /checkout",
                      f"fill 1 address={a}",
                      f"fill 1 code={ACTIVE_COUPON}", "fill 2"])

    n += 1
    q1, q2 = pick("Kitchen", kinds=("cf",)), pick("Kitchen", kinds=("cf",))
    assert q1["price"] != q2["price"]
    cheaper = q1 if q1["price"] < q2["price"] else q2
    a = A[n % len(A)]
    one_order(n, P["ord_cheaper2"].format(p1=D(q1, "cf"), p2=D(q2, "cf"), a=a),
              cheaper, 1, a,
              pre=[f"goto /product/{q1['id']}", f"goto /product/{q2['id']}"])
    pricier = q2 if cheaper is q1 else q1
    seeded_pids = {base[ix]["id"] for _a, _s, _d, its in PAST_ORDERS
                   for ix, _q in its}
    assert pricier["id"] not in seeded_pids
    T[-1]["eval"].append({"type": "db_record_absent", "table": "order_items",
                          "match": {"product_id": pricier["id"]}})

    n += 1
    p = pick("Garden")
    task(n, P["orddefault"].format(p=D(p)),
         order_ev({p["id"]: 1}, default_addr, price(p)),
         LOGIN + [f"goto /product/{p['id']}", "fill 1 qty=1",
                  "goto /checkout", "fill 1", "fill 2"])

    n += 1
    p = pick("Books")
    new_addr = A[17]
    task(n, P["ordsetdefault"].format(a=new_addr, p=D(p)),
         order_ev({p["id"]: 1}, new_addr, price(p)) +
         [{"type": "db_field_equals", "table": "users",
           "match": {"username": "agent_smith"},
           "field": "default_address", "value": new_addr}],
         LOGIN + ["goto /settings", f"fill 1 default_address={new_addr}",
                  f"goto /product/{p['id']}", "fill 1 qty=1",
                  "goto /checkout", "fill 1", "fill 2"])

    n += 1
    m1, m2 = pick("Toys", kinds=("cf",)), pick("Books")
    a = A[n % len(A)]
    task(n, P["ord_mixed"].format(p1=D(m1, "cf"), q=nq(2), p2=D(m2), a=a),
         order_ev({m1["id"]: 1, m2["id"]: 2}, a, price(m1) + 2 * price(m2)),
         LOGIN + [f"goto /product/{m1['id']}", "fill 1 qty=1",
                  f"goto /product/{m2['id']}", "fill 1 qty=2",
                  "goto /checkout", f"fill 1 address={a}", "fill 2"])

    assert n == 25

    for cat, kind in [("Electronics", "bpf"), ("Kitchen", "cf"),
                      ("Home", "bfc")]:
        n += 1
        p = pick(cat, kinds=(kind,))
        task(n, P["wladd1"].format(p=D(p, kind)),
             [{"type": "db_record_exists", "table": "wishlist",
               "match": {"user_id": 1, "product_id": p["id"]}}],
             LOGIN + [f"goto /product/{p['id']}", "fill 2"])
    for (c1, k1), (c2, k2) in [(("Sports", "cf"), ("Grocery", "bpf")),
                               (("Toys", "bfc"), ("Books", "cf"))]:
        n += 1
        p1, p2 = pick(c1, kinds=(k1,)), pick(c2, kinds=(k2,))
        task(n, P["wladd2"].format(p1=D(p1, k1), p2=D(p2, k2)),
             [{"type": "db_record_exists", "table": "wishlist",
               "match": {"user_id": 1, "product_id": p1["id"]}},
              {"type": "db_record_exists", "table": "wishlist",
               "match": {"user_id": 1, "product_id": p2["id"]}}],
             LOGIN + [f"goto /product/{p1['id']}", "fill 2",
                      f"goto /product/{p2['id']}", "fill 2"])
    for ix, prefs in zip(PRESEEDED_WISHLIST[:2], (("cf", "bpf"), ("bpf",))):
        n += 1
        p = base[ix]
        keep = [{"type": "db_record_exists", "table": "wishlist",
                 "match": {"user_id": 1, "product_id": base[k]["id"]}}
                for k in PRESEEDED_WISHLIST if k != ix]
        task(n, P["wlremove"].format(p=Dk(p, prefs)),
             [{"type": "db_record_absent", "table": "wishlist",
               "match": {"user_id": 1, "product_id": p["id"]}}] + keep,
             LOGIN + [f"goto /product/{p['id']}", "fill 2"])
    n += 1
    cheap_all = sorted((c for c in base if c["category"] == "Office"),
                       key=lambda c: c["price"])
    cheap = cheap_all[0]
    assert cheap_all[1]["price"] > cheap["price"]
    runners = cheap_all[1:4]
    seeded_wl = {base[k]["id"] for k in PRESEEDED_WISHLIST}
    assert not seeded_wl & {c["id"] for c in runners}
    task(n, P["wlcheapest"].format(cat=cat_disp(cheap)),
         [{"type": "db_record_exists", "table": "wishlist",
           "match": {"user_id": 1, "product_id": cheap["id"]}}] +
         [{"type": "db_record_absent", "table": "wishlist",
           "match": {"user_id": 1, "product_id": c["id"]}} for c in runners],
         LOGIN + [f"goto {cat_url(cheap)}?sort=price_asc",
                  f"goto /product/{cheap['id']}", "fill 2"],
         max_steps=40)
    n += 1
    counts = collections.Counter()
    for c in base:
        if c["category"] == "Garden":
            counts[c["id"]] = len(rev_by_pid.get(c["id"], []))
    (top_id, top_n), (_, second_n) = counts.most_common(2)
    assert top_n > second_n
    top_c = next(c for c in base if c["id"] == top_id)
    task(n, P["wlmostrev"].format(cat=cat_disp(top_c)),
         [{"type": "db_record_exists", "table": "wishlist",
           "match": {"user_id": 1, "product_id": top_id}}],
         LOGIN + [f"goto {cat_url(top_c)}?sort=reviews",
                  f"goto /product/{top_id}", "fill 2"],
         max_steps=40)

    assert n == 34

    def keep(oid):
        status = PAST_ORDERS[oid - 1][1]
        assert status in ("placed", "shipped")
        return {"type": "db_field_equals", "table": "orders",
                "match": {"id": oid}, "field": "status", "value": status}

    n += 1
    task(n, P["chgaddr"].format(oid=4, a=A[16]),
         [{"type": "db_field_equals", "table": "orders", "match": {"id": 4},
           "field": "address", "value": A[16]}],
         LOGIN + ["goto /order/4/address", f"fill 1 address={A[16]}"])
    n += 1
    task(n, P["cancel"].format(oid=4),
         [{"type": "db_field_equals", "table": "orders", "match": {"id": 4},
           "field": "status", "value": "cancelled"}, keep(3)],
         LOGIN + ["goto /order/4/cancel", "fill 1"])
    n += 1
    task(n, P["chgcancel"].format(oid=3, a=A[1]),
         [{"type": "db_field_equals", "table": "orders", "match": {"id": 3},
           "field": "address", "value": A[1]},
          {"type": "db_field_equals", "table": "orders", "match": {"id": 3},
           "field": "status", "value": "cancelled"}, keep(4)],
         LOGIN + ["goto /order/3/address", f"fill 1 address={A[1]}",
                  "goto /order/3/cancel", "fill 1"])
    n += 1
    msg = P["msg_cancel"]
    task(n, P["cancelcontact"].format(oid=4, msg=msg),
         [{"type": "db_field_equals", "table": "orders", "match": {"id": 4},
           "field": "status", "value": "cancelled"},
          {"type": "db_record_exists", "table": "messages",
           "match": {"user_id": 1, "order_ref": "4", "body": f"%{msg}%"}},
          keep(3)],
         LOGIN + ["goto /order/4/cancel", "fill 1", "goto /contact",
                  f"fill 1 order_ref=4; message={msg}"])
    n += 1
    p = pick("Sports", kinds=("cf",))
    task(n, P["setwl"].format(a=A[2], p=D(p, "cf")),
         [{"type": "db_field_equals", "table": "users",
           "match": {"username": "agent_smith"},
           "field": "default_address", "value": A[2]},
          {"type": "db_record_exists", "table": "wishlist",
           "match": {"user_id": 1, "product_id": p["id"]}}],
         LOGIN + ["goto /settings", f"fill 1 default_address={A[2]}",
                  f"goto /product/{p['id']}", "fill 2"])
    n += 1
    p = pick("Kitchen", kinds=("bfc",))
    a = A[3]
    task(n, P["ordcancelnew"].format(p=D(p, "bfc"), a=a),
         order_ev({p["id"]: 1}, a, price(p)) +
         [{"type": "db_field_equals", "table": "orders", "match": {"id": 5},
           "field": "status", "value": "cancelled"}, keep(3), keep(4)],
         LOGIN + [f"goto /product/{p['id']}", "fill 1 qty=1",
                  "goto /checkout", f"fill 1 address={a}", "fill 2",
                  "goto /order/5/cancel", "fill 1"],
         max_steps=40)
    n += 1
    p = pick("Home")
    rv = P["rv_sturdy"]
    task(n, P["wlreview"].format(p=D(p), rv=rv),
         [{"type": "db_record_exists", "table": "wishlist",
           "match": {"user_id": 1, "product_id": p["id"]}},
          {"type": "db_record_exists", "table": "reviews",
           "match": {"product_id": p["id"], "user_id": 1, "stars": 4,
                     "body": f"%{rv}%"}}],
         LOGIN + [f"goto /product/{p['id']}", "fill 2",
                  f"goto /product/{p['id']}",
                  f"fill 4 stars=4; body={rv}"])

    assert n == 41

    NA = NA_SUFFIX[lang]

    def na(key):
        return ["N/A"] + P["na_alts"][key]

    n += 1
    ans(n, P["na_brand"] + NA, na("brand"),
        ["goto /?q=Zenithware", "stop N/A"])
    n += 1
    ans(n, P["na_product"].format(name=P["fake_product"]) + NA,
        na("product"),
        [f"goto /?q={quote(P['fake_product'])}", "stop N/A"])
    n += 1
    ans(n, P["na_coupon"] + NA, na("coupon"), ["goto /deals", "stop N/A"])
    oos = next(c for c in base if c["stock"] == 0 and unique_ref(c, "bpf"))
    n += 1
    ans(n, P["na_oos"].format(p=D(oos)), na("oos"),
        LOGIN + [f"goto /product/{oos['id']}", "stop N/A"], login=True)
    hot = max((c for c in base if unique_ref(c, "bpf")),
              key=lambda c: len(rev_by_pid.get(c["id"], [])))
    n += 1
    ans(n, P["na_ghost"].format(p=Dk(hot, ("cf", "bpf"))) + NA, na("ghost"),
        [f"goto /product/{hot['id']}", "stop N/A"])
    n += 1
    gro = next(c for c in base if c["category"] == "Grocery")
    LIMIT_USD = 0.50
    for l, lc_all in locs_all.items():
        floor = min(lc_all[c["id"]]["price"] for c in base
                    if c["category"] == "Grocery")
        assert floor > LIMIT_USD * LANG_META[l]["rate"], (l, floor)
    limit = nq(f"{LIMIT_USD * meta['rate']:.2f}")
    ans(n, P["na_under"].format(cat=cat_disp(gro), cur=meta["cur"],
                                limit=limit) + NA, na("under"),
        [f"goto {cat_url(gro)}?sort=price_asc", "stop N/A"])
    n += 1
    ans(n, P["na_order9"] + NA, na("order9"),
        LOGIN + ["goto /orders", "stop N/A"], login=True)
    n += 1
    p_not = pick("Toys", kinds=("cf",))
    ans(n, P["na_qty"].format(p=D(p_not, "cf")) + NA, na("qty"),
        LOGIN + ["goto /order/2", "stop N/A"], login=True)
    n += 1
    ans(n, P["na_freeship"], na("freeship"), ["goto /deals", "stop N/A"])
    n += 1
    p = pick("Pets")
    ans(n, P["na_ultra"].format(**{"name": N(p)}) + NA, na("ultra"),
        [f"goto /?q={quote(N(p))}", "stop N/A"])

    assert n == 51

    import re

    def named(c):
        return " " in c["name"] and len(c["name"]) <= 55 and quotable(c)

    def qa_num(pid, pattern):
        for q_, a_ in qa_by_pid.get(pid, []):
            m = re.search(pattern, a_)
            if m:
                return int(m.group(1))
        return None

    warr_p = next(c for c in base if named(c) and unique_ref(c, "cf") and c["id"] not in used
                  and qa_num(c["id"], P["re_warranty"]) is not None)
    used.add(warr_p["id"])
    w = qa_num(warr_p["id"], P["re_warranty"])
    n += 1
    ans(n, P["qa_warranty_q"].format(p=D(warr_p, "cf")), num_targets(w),
        [f"goto /?q={quote(N(warr_p))}", f"goto /product/{warr_p['id']}",
         f"stop {w} months"])

    del_p = next(c for c in base if named(c) and unique_ref(c, "bfc") and c["id"] not in used
                 and qa_num(c["id"], P["re_delivery"]) is not None)
    used.add(del_p["id"])
    d = qa_num(del_p["id"], P["re_delivery"])
    n += 1
    ans(n, P["qa_delivery_q"].format(p=D(del_p, "bfc")), num_targets(d),
        [f"goto /?q={quote(N(del_p))}", f"goto /product/{del_p['id']}",
         f"stop {d} business days"])

    cnt_p = next(c for c in base if named(c) and unique_ref(c, "bpf") and c["id"] not in used
                 and len(qa_by_pid.get(c["id"], [])) >= 3)
    used.add(cnt_p["id"])
    kq = len(qa_by_pid[cnt_p["id"]])
    n += 1
    ans(n, P["qa_count_q"].format(p=D(cnt_p)), num_targets(kq),
        [f"goto /?q={quote(N(cnt_p))}", f"goto /product/{cnt_p['id']}",
         f"stop {kq}"])

    n += 1
    p = pick("Garden", kinds=("cf",))
    task(n, P["ask_t"].format(p=D(p, "cf"), q=P["q_colour"]),
         [{"type": "db_record_exists", "table": "qa",
           "match": {"product_id": p["id"], "user_id": 1,
                     "question": P["q_colour"], "answer": ""}}],
         LOGIN + [f"goto /product/{p['id']}",
                  f"fill 3 question={P['q_colour']}"])

    n += 1
    p = pick("Office", kinds=("bfc",))
    task(n, P["ask_wl_t"].format(p=D(p, "bfc"), q=P["q_spare"]),
         [{"type": "db_record_exists", "table": "qa",
           "match": {"product_id": p["id"], "user_id": 1,
                     "question": P["q_spare"]}},
          {"type": "db_record_exists", "table": "wishlist",
           "match": {"user_id": 1, "product_id": p["id"]}}],
         LOGIN + [f"goto /product/{p['id']}",
                  f"fill 3 question={P['q_spare']}", "fill 2"])

    def top_helpful(pid):
        rows = rev_rows.get(pid, [])
        if len(rows) < 5:
            return None
        best = max(h for _, _, _, h in rows)
        hits = [r for r in rows if r[3] == best]
        return hits[0] if best > 0 and len(hits) == 1 else None

    def solo_review(pid, min_h=0):
        rows = rev_rows.get(pid, [])
        author_n = collections.Counter(u for _, u, _, _ in rows)
        for r in rows:
            if author_n[r[1]] == 1 and r[3] >= min_h:
                return r
        return None

    htop_p = next(c for c in base if named(c) and unique_ref(c, "bpf") and c["id"] not in used
                  and top_helpful(c["id"]))
    used.add(htop_p["id"])
    tr = top_helpful(htop_p["id"])
    n += 1
    ans(n, P["helpful_top_q"].format(p=D(htop_p)), [uname[tr[1]]],
        [f"goto /?q={quote(N(htop_p))}", f"goto /product/{htop_p['id']}",
         f"stop {uname[tr[1]]}"],
        none_of=sorted({uname[r[1]] for r in rev_rows[htop_p["id"]]}
                       - {uname[tr[1]]}))

    hn_p = next(c for c in base if named(c) and unique_ref(c, "cf") and c["id"] not in used
                and solo_review(c["id"], min_h=3))
    used.add(hn_p["id"])
    sr = solo_review(hn_p["id"], min_h=3)
    n += 1
    ans(n, P["helpful_n_q"].format(p=D(hn_p, "cf"), u=uname[sr[1]]),
        num_targets(sr[3]),
        [f"goto /?q={quote(N(hn_p))}", f"goto /product/{hn_p['id']}",
         f"stop {sr[3]}"])

    hm_p = next(c for c in base if named(c) and unique_ref(c, "bfc") and c["id"] not in used
                and c["stock"] > 0 and solo_review(c["id"]))
    used.add(hm_p["id"])
    mr = solo_review(hm_p["id"])
    pos = [r[0] for r in rev_rows[hm_p["id"]]].index(mr[0])
    n += 1
    task(n, P["helpful_mark_t"].format(p=D(hm_p, "bfc"), u=uname[mr[1]]),
         [{"type": "db_record_exists", "table": "helpful_votes",
           "match": {"review_id": mr[0], "user_id": 1}},
          {"type": "db_field_equals", "table": "reviews",
           "match": {"id": mr[0]}, "field": "helpful",
           "value": mr[3] + 1}],
         LOGIN + [f"goto /product/{hm_p['id']}", f"fill {5 + pos}"])

    hmt_p = next(c for c in base if named(c) and unique_ref(c, "bpf") and c["id"] not in used
                 and c["stock"] > 0 and top_helpful(c["id"]))
    used.add(hmt_p["id"])
    mtr = top_helpful(hmt_p["id"])
    pos2 = [r[0] for r in rev_rows[hmt_p["id"]]].index(mtr[0])
    n += 1
    task(n, P["helpful_mark_top_t"].format(p=D(hmt_p)),
         [{"type": "db_record_exists", "table": "helpful_votes",
           "match": {"review_id": mtr[0], "user_id": 1}}],
         LOGIN + [f"goto /product/{hmt_p['id']}", f"fill {5 + pos2}"])

    brand_n = collections.Counter(c["brand"] for c in base)
    n += 1
    ans(n, P["brands_total_q"], num_targets(len(brand_n)),
        ["goto /brands", f"stop {len(brand_n)}"])

    brand_stars = collections.defaultdict(list)
    base_by_id = {c["id"]: c for c in base}
    for _rid, pid, _uid, stars, _body, _h in reviews:
        brand_stars[base_by_id[pid]["brand"]].append(stars)
    cand = [b for b, k in brand_n.items()
            if 15 <= k <= 90 and b.isascii() and len(b) < 25
            and b != "Unbranded"
            and sum(1 for b2 in brand_n
                    if b2.casefold() == b.casefold()) == 1]
    bm1, bm2 = next(
        (x, y) for i, x in enumerate(cand) for y in cand[i + 1:]
        if brand_n[x] != brand_n[y]
        and x.casefold() not in y.casefold()
        and y.casefold() not in x.casefold())
    more_b = bm1 if brand_n[bm1] > brand_n[bm2] else bm2
    n += 1
    ans(n, P["brands_more_q"].format(b1=bm1, b2=bm2), [more_b],
        ["goto /brands", f"stop {more_b}"],
        none_of=[bm2 if more_b == bm1 else bm1])

    def bavg(b):
        lst = brand_stars.get(b, [])
        return half_up1(sum(lst) / len(lst)) if lst else None

    ba1, ba2 = next(
        (x, y) for i, x in enumerate(cand) for y in cand[i + 1:]
        if len(brand_stars[x]) >= 30 and len(brand_stars[y]) >= 30
        and bavg(x) is not None and bavg(y) is not None
        and abs(bavg(x) - bavg(y)) >= 0.2
        and x.casefold() not in y.casefold()
        and y.casefold() not in x.casefold())
    hi_b = ba1 if bavg(ba1) > bavg(ba2) else ba2
    n += 1
    ans(n, P["brands_avg_q"].format(b1=ba1, b2=ba2), [hi_b],
        ["goto /brands", f"stop {hi_b}"],
        none_of=[ba2 if hi_b == ba1 else ba1])

    assert n == 63

    for cat in ["Electronics"]:
        n += 1
        p = pick(cat)
        ans(n, P["price_q"].format(p=D(p, "bcf")), num_targets(money(price(p))),
            [f"goto /?q={quote(N(p))}", f"stop {money(price(p))}"])
    for cat in ["Home"]:
        n += 1
        p = pick(cat)
        ans(n, P["brand_q"].format(p=D(p, "cpf")), [p["brand"]],
            [f"goto /?q={quote(N(p))}", f"goto /product/{p['id']}",
             f"stop {p['brand']}"])
    for cat in ["Sports"]:
        n += 1
        p = pick(cat, kinds=("cf",))
        ans(n, P["stock_q"].format(p=D(p, "cf")), num_targets(p["stock"]),
            [f"goto /?q={quote(N(p))}", f"goto /product/{p['id']}",
             f"stop {p['stock']}"])
    for cat1, cat2 in [("Kitchen", "Kitchen")]:
        n += 1
        a1, a2 = pick(cat1), pick(cat2)
        cheaper = a1 if a1["price"] < a2["price"] else a2
        assert a1["price"] != a2["price"]
        ans(n, P["cheaper_q"].format(p1=D(a1, "bcf"), p2=D(a2, "bcf")), [N(cheaper)],
            [f"goto /?q={quote(N(a1))}", f"goto /?q={quote(N(a2))}",
             f"stop {N(cheaper)}"],
            none_of=[N(a2 if cheaper is a1 else a1)])
    n += 1
    trio = [pick("Electronics"), pick("Electronics"), pick("Electronics")]
    dear = max(trio, key=lambda c: c["price"])
    assert len({c["price"] for c in trio}) == 3
    ans(n, P["dearest_q"].format(
            ps=", ".join(D(c, "bcf") for c in trio)), [N(dear)],
        [f"goto /?q={quote(N(trio[0]))}", f"goto /?q={quote(N(trio[1]))}",
         f"goto /?q={quote(N(trio[2]))}", f"stop {N(dear)}"],
        none_of=[N(c) for c in trio if c is not dear])
    hots = [c for c in sorted(base, key=lambda c: -len(rev_by_pid.get(c["id"], [])))
            if unique_ref(c, "bpf")]
    h1, h2, h3 = hots[0], hots[1], hots[2]
    n += 1
    ans(n, P["nrev_q"].format(p=Dk(h1, ("bfc", "bpf"))),
        num_targets(len(rev_by_pid[h1["id"]])),
        [f"goto /?q={quote(N(h1))}", f"goto /product/{h1['id']}",
         f"stop {len(rev_by_pid[h1['id']])}"])
    n += 1
    ones = sum(1 for s in rev_by_pid[h3["id"]] if s == 1)
    ans(n, P["onestar_q"].format(p=Dk(h3, ("cf", "bpf"))), num_targets(ones),
        [f"goto /?q={quote(N(h3))}", f"goto /product/{h3['id']}",
         f"stop {ones}"])
    n += 1
    avg = half_up1(sum(rev_by_pid[h1["id"]]) / len(rev_by_pid[h1["id"]]))
    ans(n, P["avg_q"].format(p=D(h1)),
        num_targets(f"{avg:.1f}"),
        [f"goto /product/{h1['id']}", f"stop {avg:.1f}"])
    n += 1
    a1v = sum(rev_by_pid[h2["id"]]) / len(rev_by_pid[h2["id"]])
    a2v = sum(rev_by_pid[h3["id"]]) / len(rev_by_pid[h3["id"]])
    assert half_up1(a1v) != half_up1(a2v)
    hi_p = h2 if a1v > a2v else h3
    ans(n, P["higher_q"].format(p1=Dk(h2, ("cf", "bpf")), p2=D(h3)), [N(hi_p)],
        [f"goto /product/{h2['id']}", f"goto /product/{h3['id']}",
         f"stop {N(hi_p)}"],
        none_of=[N(h3 if hi_p is h2 else h2)])
    n += 1
    ans(n, P["coupon_q"], [ACTIVE_COUPON],
        ["goto /deals", f"stop {ACTIVE_COUPON}"],
        none_of=[c for c, _pct, _on in COUPONS if c != ACTIVE_COUPON])
    n += 1
    p = pick("Grocery", kinds=("cf",))
    rv = P["rv_fresh"]
    task(n, P["review_t"].format(rv=rv, p=D(p, "cf")),
         [{"type": "db_record_exists", "table": "reviews",
           "match": {"product_id": p["id"], "user_id": 1, "stars": 5,
                     "body": f"%{rv}%"}}],
         LOGIN + [f"goto /?q={quote(N(p))}", f"goto /product/{p['id']}",
                  f"fill 4 stars=5; body={rv}"])
    n += 1
    msg2 = P["msg_missing"]
    task(n, P["contact_t"].format(msg=msg2, oid=2),
         [{"type": "db_record_exists", "table": "messages",
           "match": {"user_id": 1, "order_ref": "2",
                     "body": f"%{msg2}%"}}],
         LOGIN + ["goto /contact", f"fill 1 order_ref=2; message={msg2}"])

    assert n == 75, n
    assert len(T) == 75
    return T


def write(lang, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    T = build(lang)
    out = os.path.join(out_dir, "visual_tasks.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(T, f, indent=1, ensure_ascii=False)
    print(f"wrote {len(T)} tasks to {out}")


if __name__ == "__main__":
    write("en", os.path.join(HERE, "en"))
