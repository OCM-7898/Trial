import json
import os
import random

SCHEMA = """
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS helpful_votes;
DROP TABLE IF EXISTS qa;
DROP TABLE IF EXISTS wishlist;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS coupons;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;
CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
                    default_address TEXT NOT NULL DEFAULT '');
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
                       price REAL NOT NULL, description TEXT NOT NULL DEFAULT '',
                       brand TEXT NOT NULL DEFAULT '', stock INTEGER NOT NULL DEFAULT 10);
CREATE TABLE coupons (id INTEGER PRIMARY KEY, code TEXT UNIQUE NOT NULL,
                      percent_off INTEGER NOT NULL, active INTEGER NOT NULL DEFAULT 1);
CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
                     address TEXT NOT NULL, total REAL NOT NULL, status TEXT NOT NULL,
                     placed_on TEXT NOT NULL DEFAULT '', coupon_code TEXT NOT NULL DEFAULT '');
CREATE TABLE order_items (id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id),
                          product_id INTEGER NOT NULL REFERENCES products(id),
                          qty INTEGER NOT NULL, price REAL NOT NULL);
CREATE TABLE reviews (id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id),
                      user_id INTEGER NOT NULL REFERENCES users(id), stars INTEGER NOT NULL,
                      body TEXT NOT NULL, helpful INTEGER NOT NULL DEFAULT 0);
CREATE TABLE qa (id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id),
                 user_id INTEGER NOT NULL REFERENCES users(id),
                 question TEXT NOT NULL, answer TEXT NOT NULL DEFAULT '');
CREATE TABLE helpful_votes (id INTEGER PRIMARY KEY, review_id INTEGER NOT NULL REFERENCES reviews(id),
                            user_id INTEGER NOT NULL REFERENCES users(id),
                            UNIQUE(review_id, user_id));
CREATE TABLE wishlist (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
                       product_id INTEGER NOT NULL REFERENCES products(id),
                       UNIQUE(user_id, product_id));
CREATE TABLE messages (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
                       order_ref TEXT NOT NULL DEFAULT '', body TEXT NOT NULL);
"""

USERS = [
    ("agent_smith", "password123", "12 Ocean Ave, Tampa, 33601"),
    ("reviewer_jo", "hunter2", ""), ("reviewer_kim", "hunter2", ""),
    ("bargain_ben", "hunter2", ""), ("kitchen_kat", "hunter2", ""),
    ("gymrat_gus", "hunter2", ""), ("plant_pam", "hunter2", ""),
    ("techie_tom", "hunter2", ""), ("outdoor_ollie", "hunter2", ""),
    ("bookish_bea", "hunter2", ""), ("pet_parent_pat", "hunter2", ""),
    ("office_oscar", "hunter2", ""), ("frugal_fran", "hunter2", ""),
    ("weekend_walt", "hunter2", ""), ("minimal_mia", "hunter2", ""),
]

COUPONS = [
    ("SAVE10", 10, 1),
    ("WELCOME5", 5, 0),
    ("FREESHIP", 15, 0),
]
ACTIVE_COUPON = "SAVE10"
ACTIVE_COUPON_PCT = 10

REVIEW_POOL = [
    (5, "Exactly as described, would buy again."),
    (5, "Great value for the money."),
    (5, "Bought a second one for my parents."),
    (5, "Been using it daily for a month, zero complaints."),
    (5, "Replaced a much pricier one and honestly this is better."),
    (5, "Delivery was quick and it works perfectly."),
    (5, "The photos undersell it. Very happy."),
    (5, "Does one thing and does it well."),
    (5, "Survived a house move and a toddler. Recommended."),
    (5, "Gifted one, kept one. Both still going strong."),
    (4, "Solid build, packaging was a bit beat up."),
    (4, "Does the job. Nothing fancy."),
    (4, "Good, minor quality control issues."),
    (4, "Works well, instructions could be clearer."),
    (4, "A touch smaller than expected but performs fine."),
    (4, "Four stars only because the colour runs darker than shown."),
    (4, "Sturdy. Knocked off a star for the smell out of the box."),
    (4, "Happy overall, would prefer a longer cable/strap."),
    (3, "Fine, but I expected a little more."),
    (3, "Average. Works as advertised."),
    (3, "Okay for the price."),
    (3, "Middle of the road. Neither impressed nor annoyed."),
    (3, "Does the basics; the premium feel isn't there."),
    (3, "Kept it, but I wouldn't buy it twice."),
    (2, "Broke after two weeks of light use."),
    (2, "Smaller than the photos suggest."),
    (2, "Started squeaking/rattling within days."),
    (2, "The finish scratches if you look at it wrong."),
    (2, "Returned it — didn't match the description."),
    (2, "Works, but the quality feels like half the price."),
    (2, "Second unit was fine; first arrived defective."),
    (1, "Arrived damaged and support was slow."),
    (1, "Stopped working entirely on day three."),
    (1, "Completely different from what was pictured."),
    (1, "Waste of money. Straight to the bin."),
    (1, "Leaked/shed/fell apart immediately. Avoid."),
    (1, "Missing parts and no response from the seller."),
    (5, "Five stars. My third purchase from this brand."),
    (4, "Reliable so far; will update if that changes."),
    (3, "Serviceable. Shop around before you commit."),
    (2, "Looks good in photos, feels flimsy in hand."),
    (1, "Regret buying it the moment I opened the box."),
    (5, "Perfect fit for what I needed. No notes."),
    (4, "Better than expected for the price bracket."),
    (2, "Sizing/spec info on the page is misleading."),
]

PAST_ORDERS = [
    ("12 Ocean Ave, Tampa, 33601", "delivered", "2026-06-02",
     [(0, 1), (601, 2)]),
    ("12 Ocean Ave, Tampa, 33601", "delivered", "2026-07-15",
     [(2300, 3)]),
    ("12 Ocean Ave, Tampa, 33601", "shipped", "2026-08-21",
     [(851, 1), (2020, 1), (2021, 1)]),
    ("12 Ocean Ave, Tampa, 33601", "placed", "2026-09-10",
     [(305, 1), (1770, 2)]),
]

PRESEEDED_WISHLIST = [10, 320, 1510]

ADDRESS_L10N = {
    "en": {},
    "bn": {"12 Ocean Ave, Tampa, 33601": "12 ওশান অ্যাভিনিউ, ট্যাম্পা, 33601"},
    "hi": {"12 Ocean Ave, Tampa, 33601": "12 ओशन एवेन्यू, टैम्पा, 33601"},
    "ur": {"12 Ocean Ave, Tampa, 33601": "12 اوشن ایونیو، ٹیمپا، 33601"},
    "am": {"12 Ocean Ave, Tampa, 33601": "12 ኦሽን አቬኑ, ታምፓ, 33601"},
}


def loc_addr(lang, addr):
    return ADDRESS_L10N.get(lang, {}).get(addr, addr)

_HERE = os.path.dirname(os.path.abspath(__file__))


def load_catalog(lang="en"):
    with open(os.path.join(_HERE, "catalog.json"), encoding="utf-8") as f:
        cat = json.load(f)
    if lang != "en":
        from .strings import LANG_META
        ov_path = os.path.join(_HERE, f"catalog_{lang}.json")
        overlay = {}
        if os.path.exists(ov_path):
            with open(ov_path, encoding="utf-8") as f:
                overlay = json.load(f)
        rate = LANG_META[lang]["rate"]
        for c in cat:
            c.update(overlay.get(str(c["id"]), {}))
            c["price"] = round(c["price"] * rate, 2)
    return cat


REVIEW_POOL_BN = [
    (5, "ঠিক যেমন বর্ণনা করা হয়েছে, আবার কিনব।"),
    (5, "টাকার তুলনায় দারুণ জিনিস।"),
    (5, "বাবা-মায়ের জন্য আরেকটা কিনেছি।"),
    (5, "এক মাস ধরে রোজ ব্যবহার করছি, কোনো অভিযোগ নেই।"),
    (5, "অনেক দামি একটার বদলে নিয়েছি, সত্যি বলতে এটাই ভালো।"),
    (5, "ডেলিভারি দ্রুত ছিল আর একদম ঠিকঠাক কাজ করে।"),
    (5, "ছবিতে যা দেখায় জিনিসটা তার চেয়ে ভালো। খুব খুশি।"),
    (5, "একটা কাজই করে, আর সেটা ভালোভাবে করে।"),
    (5, "বাসা বদল আর ছোট বাচ্চা — দুটোই সামলে টিকে গেছে। সুপারিশ করছি।"),
    (5, "একটা উপহার দিয়েছি, একটা রেখেছি। দুটোই এখনো দিব্যি চলছে।"),
    (4, "মজবুত জিনিস, তবে প্যাকেজিং একটু চটকে গিয়েছিল।"),
    (4, "কাজ চলে যায়। বাড়তি কিছু নেই।"),
    (4, "ভালো, ছোটখাটো কোয়ালিটির সমস্যা আছে।"),
    (4, "ভালোই কাজ করে, নির্দেশনাটা আরও পরিষ্কার হতে পারত।"),
    (4, "ভেবেছিলাম একটু বড় হবে, তবে কাজ ঠিকই করে।"),
    (4, "চার স্টার শুধু এই কারণে যে রংটা ছবির চেয়ে গাঢ়।"),
    (4, "মজবুত। বাক্স খোলার সময়ের গন্ধের জন্য এক স্টার কাটলাম।"),
    (4, "মোটের ওপর খুশি, তারটা/ফিতাটা একটু লম্বা হলে ভালো হতো।"),
    (3, "চলনসই, তবে আরেকটু আশা করেছিলাম।"),
    (3, "গড়পড়তা। যেমন বলা হয়েছে তেমনই কাজ করে।"),
    (3, "দামের তুলনায় ঠিক আছে।"),
    (3, "মাঝামাঝি। মুগ্ধও হইনি, বিরক্তও হইনি।"),
    (3, "মৌলিক কাজগুলো করে; প্রিমিয়াম ভাবটা নেই।"),
    (3, "রেখে দিয়েছি, তবে দ্বিতীয়বার কিনতাম না।"),
    (2, "হালকা ব্যবহারেই দুই সপ্তাহে ভেঙে গেছে।"),
    (2, "ছবিতে যা মনে হয় তার চেয়ে ছোট।"),
    (2, "কয়েক দিনের মধ্যেই ক্যাঁচক্যাঁচ/খটখট শব্দ শুরু হয়েছে।"),
    (2, "একটু হাত লাগলেই ফিনিশে দাগ পড়ে যায়।"),
    (2, "ফেরত দিয়েছি — বর্ণনার সাথে মেলে না।"),
    (2, "কাজ করে, তবে কোয়ালিটি অর্ধেক দামের জিনিসের মতো লাগে।"),
    (2, "দ্বিতীয়টা ঠিক ছিল; প্রথমটা নষ্ট অবস্থায় এসেছিল।"),
    (1, "ক্ষতিগ্রস্ত অবস্থায় এসেছে আর সাপোর্ট খুব ধীর।"),
    (1, "তিন দিনের মাথায় একেবারে কাজ করা বন্ধ করে দিয়েছে।"),
    (1, "ছবিতে যা দেখানো হয়েছে তার থেকে পুরোপুরি আলাদা।"),
    (1, "টাকা নষ্ট। সোজা ডাস্টবিনে।"),
    (1, "সাথে সাথেই লিক করেছে/ঝরেছে/খুলে গেছে। এড়িয়ে চলুন।"),
    (1, "যন্ত্রাংশ কম ছিল আর বিক্রেতার কোনো সাড়া নেই।"),
    (5, "পাঁচ স্টার। এই ব্র্যান্ড থেকে আমার তৃতীয় কেনাকাটা।"),
    (4, "এখন পর্যন্ত নির্ভরযোগ্য; বদলালে আপডেট দেব।"),
    (3, "কাজ চালানোর মতো। কেনার আগে একটু যাচাই করে নিন।"),
    (2, "ছবিতে ভালো দেখায়, হাতে নিলে পাতলা লাগে।"),
    (1, "বাক্স খোলার মুহূর্তেই কেনার জন্য আফসোস হয়েছে।"),
    (5, "আমার যা দরকার ছিল তার জন্য একদম ঠিকঠাক। আর কিছু বলার নেই।"),
    (4, "এই দামের মধ্যে যা আশা করেছিলাম তার চেয়ে ভালো।"),
    (2, "পাতায় দেওয়া সাইজ/স্পেসিফিকেশনের তথ্য বিভ্রান্তিকর।"),
]

REVIEW_POOL_HI = [
    (5, "बिल्कुल जैसा बताया गया था, दोबारा खरीदूँगा।"),
    (5, "पैसे के हिसाब से बढ़िया।"),
    (5, "माता-पिता के लिए एक और खरीदा।"),
    (5, "एक महीने से रोज़ इस्तेमाल कर रहा हूँ, कोई शिकायत नहीं।"),
    (5, "एक बहुत महँगे वाले की जगह लिया और सच कहूँ तो यह बेहतर है।"),
    (5, "डिलीवरी जल्दी हुई और यह बिल्कुल सही काम करता है।"),
    (5, "फ़ोटो में यह कम लगता है। बहुत खुश हूँ।"),
    (5, "एक ही काम करता है और अच्छे से करता है।"),
    (5, "घर बदलने और एक छोटे बच्चे के बाद भी सलामत है। सिफ़ारिश करता हूँ।"),
    (5, "एक उपहार में दिया, एक रखा। दोनों अब भी बढ़िया चल रहे हैं।"),
    (4, "मज़बूत बनावट, पैकेजिंग थोड़ी टूटी-फूटी थी।"),
    (4, "काम चल जाता है। कुछ खास नहीं।"),
    (4, "अच्छा है, क्वालिटी की छोटी-मोटी दिक्कतें हैं।"),
    (4, "ठीक काम करता है, निर्देश और साफ़ हो सकते थे।"),
    (4, "उम्मीद से थोड़ा छोटा है पर काम ठीक करता है।"),
    (4, "चार स्टार सिर्फ़ इसलिए क्योंकि रंग दिखाए गए से गहरा है।"),
    (4, "मज़बूत। डिब्बा खोलने पर आई गंध के लिए एक स्टार काटा।"),
    (4, "कुल मिलाकर खुश हूँ, केबल/पट्टा थोड़ा लंबा होता तो बेहतर था।"),
    (3, "ठीक है, पर मुझे थोड़ी और उम्मीद थी।"),
    (3, "औसत। जैसा बताया गया वैसा काम करता है।"),
    (3, "कीमत के हिसाब से ठीक है।"),
    (3, "बीच का। न प्रभावित हुआ, न परेशान।"),
    (3, "बुनियादी काम करता है; प्रीमियम एहसास नहीं है।"),
    (3, "रख लिया, पर दोबारा नहीं खरीदूँगा।"),
    (2, "हल्के इस्तेमाल में दो हफ़्ते में टूट गया।"),
    (2, "फ़ोटो से छोटा है।"),
    (2, "कुछ ही दिनों में चरमराने/खड़खड़ाने लगा।"),
    (2, "ज़रा-सा छूने पर फ़िनिश पर खरोंच आ जाती है।"),
    (2, "वापस कर दिया — विवरण से मेल नहीं खाता।"),
    (2, "काम करता है, पर क्वालिटी आधी कीमत वाली लगती है।"),
    (2, "दूसरा ठीक था; पहला खराब हालत में आया।"),
    (1, "टूटा हुआ आया और सपोर्ट बहुत धीमा था।"),
    (1, "तीसरे दिन पूरी तरह काम करना बंद कर दिया।"),
    (1, "तस्वीर से बिल्कुल अलग।"),
    (1, "पैसे की बर्बादी। सीधे कूड़ेदान में।"),
    (1, "तुरंत लीक हुआ/झड़ा/टूट गया। इससे बचें।"),
    (1, "पुर्ज़े गायब थे और विक्रेता से कोई जवाब नहीं।"),
    (5, "पाँच स्टार। इस ब्रांड से मेरी तीसरी खरीद।"),
    (4, "अब तक भरोसेमंद; कुछ बदला तो अपडेट करूँगा।"),
    (3, "काम चलाऊ। खरीदने से पहले थोड़ा तुलना कर लें।"),
    (2, "फ़ोटो में अच्छा दिखता है, हाथ में हल्का-फुल्का लगता है।"),
    (1, "डिब्बा खोलते ही खरीदने का पछतावा हुआ।"),
    (5, "मेरी ज़रूरत के लिए एकदम सही। कोई शिकायत नहीं।"),
    (4, "इस कीमत में उम्मीद से बेहतर।"),
    (2, "पेज पर दी गई साइज़/स्पेसिफिकेशन की जानकारी भ्रामक है।"),
]

REVIEW_POOL_UR = [
    (5, "بالکل ویسا ہی جیسا بتایا گیا تھا، دوبارہ خریدوں گا۔"),
    (5, "پیسوں کے لحاظ سے بہترین۔"),
    (5, "والدین کے لیے ایک اور خرید لیا۔"),
    (5, "ایک مہینے سے روزانہ استعمال کر رہا ہوں، کوئی شکایت نہیں۔"),
    (5, "ایک بہت مہنگے والے کی جگہ لیا اور سچ کہوں تو یہ بہتر ہے۔"),
    (5, "ڈیلیوری جلدی ہوئی اور یہ بالکل ٹھیک کام کرتا ہے۔"),
    (5, "تصویروں میں یہ کم لگتا ہے۔ بہت خوش ہوں۔"),
    (5, "ایک ہی کام کرتا ہے اور اچھی طرح کرتا ہے۔"),
    (5, "گھر بدلنے اور ایک چھوٹے بچے کے بعد بھی سلامت ہے۔ تجویز کرتا ہوں۔"),
    (5, "ایک تحفے میں دیا، ایک رکھا۔ دونوں اب بھی بہترین چل رہے ہیں۔"),
    (4, "مضبوط بناوٹ، پیکنگ تھوڑی خراب تھی۔"),
    (4, "کام چل جاتا ہے۔ کچھ خاص نہیں۔"),
    (4, "اچھا ہے، کوالٹی کے چھوٹے موٹے مسائل ہیں۔"),
    (4, "ٹھیک کام کرتا ہے، ہدایات زیادہ واضح ہو سکتی تھیں۔"),
    (4, "توقع سے تھوڑا چھوٹا ہے مگر کام ٹھیک کرتا ہے۔"),
    (4, "چار اسٹار صرف اس لیے کہ رنگ دکھائے گئے سے گہرا ہے۔"),
    (4, "مضبوط۔ ڈبہ کھولنے پر آنے والی بو کے لیے ایک اسٹار کاٹا۔"),
    (4, "مجموعی طور پر خوش ہوں، کیبل/پٹی تھوڑی لمبی ہوتی تو بہتر تھا۔"),
    (3, "ٹھیک ہے، مگر مجھے تھوڑی زیادہ توقع تھی۔"),
    (3, "اوسط۔ جیسا بتایا گیا ویسا کام کرتا ہے۔"),
    (3, "قیمت کے لحاظ سے ٹھیک ہے۔"),
    (3, "درمیانہ۔ نہ متاثر ہوا، نہ پریشان۔"),
    (3, "بنیادی کام کرتا ہے؛ پریمیم احساس نہیں ہے۔"),
    (3, "رکھ لیا، مگر دوبارہ نہیں خریدوں گا۔"),
    (2, "ہلکے استعمال میں دو ہفتوں میں ٹوٹ گیا۔"),
    (2, "تصویروں سے چھوٹا ہے۔"),
    (2, "چند دنوں میں ہی چرچرانے/کھڑکھڑانے لگا۔"),
    (2, "ذرا سا چھونے پر فنش پر خراش آ جاتی ہے۔"),
    (2, "واپس کر دیا — تفصیل سے مطابقت نہیں رکھتا۔"),
    (2, "کام کرتا ہے، مگر کوالٹی آدھی قیمت والی لگتی ہے۔"),
    (2, "دوسرا ٹھیک تھا؛ پہلا خراب حالت میں آیا۔"),
    (1, "ٹوٹا ہوا آیا اور سپورٹ بہت سست تھی۔"),
    (1, "تیسرے دن مکمل طور پر کام کرنا بند کر دیا۔"),
    (1, "تصویر سے بالکل مختلف۔"),
    (1, "پیسوں کا ضیاع۔ سیدھا کوڑے دان میں۔"),
    (1, "فوراً لیک ہوا/جھڑا/ٹوٹ گیا۔ اس سے بچیں۔"),
    (1, "پرزے غائب تھے اور بیچنے والے کا کوئی جواب نہیں۔"),
    (5, "پانچ اسٹار۔ اس برانڈ سے میری تیسری خریداری۔"),
    (4, "اب تک قابلِ اعتماد؛ کچھ بدلا تو اپ ڈیٹ کروں گا۔"),
    (3, "کام چلاؤ۔ خریدنے سے پہلے تھوڑا موازنہ کر لیں۔"),
    (2, "تصویروں میں اچھا لگتا ہے، ہاتھ میں ہلکا پھلکا لگتا ہے۔"),
    (1, "ڈبہ کھولتے ہی خریدنے پر پچھتاوا ہوا۔"),
    (5, "میری ضرورت کے لیے بالکل درست۔ کوئی شکایت نہیں۔"),
    (4, "اس قیمت میں توقع سے بہتر۔"),
    (2, "صفحے پر دی گئی سائز/اسپیسیفیکیشن کی معلومات گمراہ کن ہے۔"),
]

REVIEW_POOL_AM = [
    (5, "በትክክል እንደተገለጸው ነው፣ እንደገና እገዛለሁ።"),
    (5, "ለገንዘቡ በጣም ጥሩ ዋጋ።"),
    (5, "ለወላጆቼ ሁለተኛ ገዛሁ።"),
    (5, "ለአንድ ወር በየቀኑ እየተጠቀምኩ ነው፣ ምንም ቅሬታ የለኝም።"),
    (5, "በጣም ውድ የሆነውን ተክቼዋለሁ፣ እውነቱን ለመናገር ይህ የተሻለ ነው።"),
    (5, "መላኪያው ፈጣን ነበር እና በትክክል ይሰራል።"),
    (5, "ፎቶዎቹ ከእውነቱ ያንሳሉ። በጣም ደስተኛ ነኝ።"),
    (5, "አንድ ነገር ብቻ ያደርጋል፣ እሱንም በደንብ ያደርጋል።"),
    (5, "የቤት ዝውውርንና ሕፃን ልጅን ተቋቁሟል። እመክራለሁ።"),
    (5, "አንዱን በስጦታ ሰጠሁ፣ አንዱን አስቀረሁ። ሁለቱም አሁንም በደንብ ይሰራሉ።"),
    (4, "ጠንካራ አሠራር፣ ማሸጊያው ትንሽ ተጎድቶ ነበር።"),
    (4, "ሥራውን ይሠራል። ምንም ልዩ ነገር የለም።"),
    (4, "ጥሩ ነው፣ ትንንሽ የጥራት ችግሮች አሉት።"),
    (4, "በደንብ ይሰራል፣ መመሪያዎቹ የበለጠ ግልጽ ሊሆኑ ይችሉ ነበር።"),
    (4, "ከጠበቅሁት ትንሽ ያነሰ ነው ግን በደንብ ይሰራል።"),
    (4, "አራት ኮከብ የሰጠሁት ቀለሙ ከታየው በላይ ጠቆር ስላለ ብቻ ነው።"),
    (4, "ጠንካራ። ከሳጥኑ ሲወጣ ባለው ሽታ ምክንያት አንድ ኮከብ ቀነስኩ።"),
    (4, "በአጠቃላይ ደስተኛ ነኝ፣ ገመዱ/ማሰሪያው ረዘም ቢል እመርጥ ነበር።"),
    (3, "ጥሩ ነው፣ ግን ትንሽ የበለጠ ጠብቄ ነበር።"),
    (3, "አማካይ። እንደተባለው ይሰራል።"),
    (3, "ለዋጋው ጥሩ ነው።"),
    (3, "መካከለኛ። አልተደነቅኩም፣ አልተበሳጨሁም።"),
    (3, "መሠረታዊውን ያደርጋል፤ የፕሪሚየም ስሜቱ የለውም።"),
    (3, "አስቀርቼዋለሁ፣ ግን ሁለተኛ አልገዛውም።"),
    (2, "በቀላል አጠቃቀም በሁለት ሳምንት ተሰበረ።"),
    (2, "ፎቶዎቹ ከሚያሳዩት ያነሰ ነው።"),
    (2, "በጥቂት ቀናት ውስጥ መጮህ/መንቀጥቀጥ ጀመረ።"),
    (2, "ትንሽ ስትነካው ወለሉ ይቧጠጣል።"),
    (2, "መልሼዋለሁ — ከመግለጫው ጋር አይዛመድም።"),
    (2, "ይሰራል፣ ግን ጥራቱ የግማሽ ዋጋ ይመስላል።"),
    (2, "ሁለተኛው ጥሩ ነበር፤ የመጀመሪያው ተበላሽቶ መጣ።"),
    (1, "ተጎድቶ መጣ እና ድጋፉ ዘገምተኛ ነበር።"),
    (1, "በሦስተኛው ቀን ሙሉ በሙሉ መስራት አቆመ።"),
    (1, "ከታየው ፈጽሞ የተለየ።"),
    (1, "የገንዘብ ብክነት። በቀጥታ ወደ ቆሻሻ።"),
    (1, "ወዲያውኑ ፈሰሰ/ረገፈ/ተበታተነ። ያስወግዱ።"),
    (1, "ክፍሎች ጎድለዋል እና ከሻጩ ምንም ምላሽ የለም።"),
    (5, "አምስት ኮከብ። ከዚህ ብራንድ ሦስተኛ ግዢዬ።"),
    (4, "እስካሁን አስተማማኝ ነው፤ ከተቀየረ አዘምናለሁ።"),
    (3, "የሚያገለግል ነው። ከመግዛትዎ በፊት ያወዳድሩ።"),
    (2, "በፎቶ ጥሩ ይመስላል፣ በእጅ ሲያዝ ደካማ ነው።"),
    (1, "ሳጥኑን ስከፍት ወዲያውኑ በመግዛቴ ተጸጸትኩ።"),
    (5, "ለምፈልገው ነገር ፍጹም ተስማሚ። ምንም አስተያየት የለኝም።"),
    (4, "ለዋጋው ደረጃ ከጠበቅሁት የተሻለ።"),
    (2, "በገጹ ላይ ያለው የመጠን/የዝርዝር መረጃ አሳሳች ነው።"),
]

REVIEW_POOLS = {"en": REVIEW_POOL, "bn": REVIEW_POOL_BN, "hi": REVIEW_POOL_HI,
                "ur": REVIEW_POOL_UR, "am": REVIEW_POOL_AM}

QA_TEMPLATES = [
    ("Does this come with a warranty?",
     "Yes, it is covered by a {w}-month warranty."),
    ("How long does delivery usually take?",
     "Standard delivery takes {d} business days."),
    ("Is this a genuine {brand} product?",
     "Yes, it ships in original {brand} packaging."),
    ("Can I return it if it does not suit me?",
     "Yes, returns are free within the 30-day window."),
    ("How heavy is the shipping package?",
     "The shipping weight is about {kg} kg."),
    ("Is this suitable as a gift?",
     "Absolutely - a gift receipt can be added at checkout."),
]
HELPFUL_CHOICES = [0, 0, 0, 0, 1, 1, 2, 2, 3, 4, 5, 7, 9, 12, 18, 26]

QA_TEMPLATES_BN = [
    ("এটির সাথে কি কোনো ওয়ারেন্টি আছে?",
     "হ্যাঁ, এটি {w} মাসের ওয়ারেন্টির আওতায় আছে।"),
    ("ডেলিভারি হতে সাধারণত কত দিন লাগে?",
     "সাধারণ ডেলিভারিতে {d} কর্মদিবস লাগে।"),
    ("এটি কি আসল {brand} পণ্য?",
     "হ্যাঁ, এটি আসল {brand} প্যাকেজিংয়ে পাঠানো হয়।"),
    ("পছন্দ না হলে কি ফেরত দিতে পারব?",
     "হ্যাঁ, ৩০ দিনের মধ্যে বিনামূল্যে ফেরত দেওয়া যায়।"),
    ("শিপিং প্যাকেজটির ওজন কত?",
     "শিপিং ওজন প্রায় {kg} কেজি।"),
    ("এটি কি উপহার হিসেবে দেওয়ার উপযুক্ত?",
     "অবশ্যই - চেকআউটে গিফট রসিদ যোগ করা যায়।"),
]
QA_TEMPLATES_HI = [
    ("क्या इसके साथ वारंटी मिलती है?",
     "हाँ, इस पर {w} महीने की वारंटी है।"),
    ("डिलीवरी में आमतौर पर कितना समय लगता है?",
     "स्टैंडर्ड डिलीवरी में {d} कार्यदिवस लगते हैं।"),
    ("क्या यह असली {brand} उत्पाद है?",
     "हाँ, यह असली {brand} पैकेजिंग में भेजा जाता है।"),
    ("अगर पसंद न आए तो क्या वापस कर सकता हूँ?",
     "हाँ, ३० दिनों के भीतर वापसी मुफ़्त है।"),
    ("शिपिंग पैकेज कितना भारी है?",
     "शिपिंग वज़न लगभग {kg} किलो है।"),
    ("क्या यह उपहार के लिए उपयुक्त है?",
     "बिल्कुल - चेकआउट पर गिफ़्ट रसीद जोड़ी जा सकती है।"),
]
QA_TEMPLATES_UR = [
    ("کیا اس کے ساتھ وارنٹی ملتی ہے؟",
     "ہاں، اس پر {w} ماہ کی وارنٹی ہے۔"),
    ("ڈیلیوری میں عموماً کتنا وقت لگتا ہے؟",
     "معیاری ڈیلیوری میں {d} کاروباری دن لگتے ہیں۔"),
    ("کیا یہ اصلی {brand} پروڈکٹ ہے؟",
     "ہاں، یہ اصلی {brand} پیکنگ میں بھیجی جاتی ہے۔"),
    ("اگر پسند نہ آئے تو کیا واپس کر سکتا ہوں؟",
     "ہاں، ۳۰ دنوں کے اندر واپسی مفت ہے۔"),
    ("شپنگ پیکج کتنا بھاری ہے؟",
     "شپنگ وزن تقریباً {kg} کلو ہے۔"),
    ("کیا یہ تحفے کے لیے موزوں ہے؟",
     "بالکل - چیک آؤٹ پر گفٹ رسید شامل کی جا سکتی ہے۔"),
]
QA_TEMPLATES_AM = [
    ("ዋስትና አለው?",
     "አዎ፣ የ{w} ወር ዋስትና አለው።"),
    ("መላኪያ ብዙውን ጊዜ ስንት ጊዜ ይወስዳል?",
     "መደበኛ መላኪያ {d} የስራ ቀናት ይወስዳል።"),
    ("ይህ እውነተኛ የ{brand} ምርት ነው?",
     "አዎ፣ በኦሪጅናል የ{brand} ማሸጊያ ይላካል።"),
    ("ካልተስማማኝ መመለስ እችላለሁ?",
     "አዎ፣ በ30 ቀናት ውስጥ መመለስ ነጻ ነው።"),
    ("የመላኪያ ጥቅሉ ምን ያህል ይከብዳል?",
     "የመላኪያ ክብደት ወደ {kg} ኪ.ግ ነው።"),
    ("ለስጦታ ተስማሚ ነው?",
     "በእርግጥ - በቼክአውት የስጦታ ደረሰኝ ሊጨመር ይችላል።"),
]
QA_POOLS = {"en": QA_TEMPLATES, "bn": QA_TEMPLATES_BN, "hi": QA_TEMPLATES_HI,
            "ur": QA_TEMPLATES_UR, "am": QA_TEMPLATES_AM}


def build_rows(lang="en"):
    pool = REVIEW_POOLS.get(lang, REVIEW_POOL)
    assert len(pool) == len(REVIEW_POOL)
    assert [s for s, _ in pool] == [s for s, _ in REVIEW_POOL]
    qa_pool = QA_POOLS.get(lang, QA_TEMPLATES)
    assert len(qa_pool) == len(QA_TEMPLATES)
    import re as _re
    for (q_en, a_en), (q_l, a_l) in zip(QA_TEMPLATES, qa_pool):
        assert set(_re.findall(r"{\w+}", a_en)) == \
            set(_re.findall(r"{\w+}", a_l)), (a_en, a_l)
        assert set(_re.findall(r"{\w+}", q_en)) == \
            set(_re.findall(r"{\w+}", q_l)), (q_en, q_l)
    rng = random.Random(20260915)
    uid = {u[0]: i + 1 for i, u in enumerate(USERS)}
    users = [(i + 1, u, p, a) for i, (u, p, a) in enumerate(USERS)]

    catalog = load_catalog(lang)
    products = [(c["id"], c["name"], c["category"], c["price"],
                 c["description"], c["brand"], c["stock"]) for c in catalog]
    users = [(uid_, u, pw, loc_addr(lang, a))
             for uid_, u, pw, a in users]

    coupons = [(i + 1, code, pct, act)
               for i, (code, pct, act) in enumerate(COUPONS)]

    reviews, rid = [], 0
    reviewers = [u for u in uid if u != "agent_smith"]
    hot = set(rng.sample(range(len(catalog)), 40))
    for i, c in enumerate(catalog):
        if i in hot:
            n = rng.randint(15, 25)
        else:
            n = rng.choice([0, 1, 2, 2, 3, 3, 4, 4, 5, 6, 8, 10, 12])
        for _ in range(n):
            rid += 1
            stars, body = pool[rng.randrange(len(pool))]
            reviews.append((rid, c["id"], uid[rng.choice(reviewers)],
                            stars, body))

    orders, order_items, oid, oiid = [], [], 0, 0
    for address, status, placed_on, items in PAST_ORDERS:
        address = loc_addr(lang, address)
        oid += 1
        total = round(sum(catalog[ix]["price"] * q for ix, q in items), 2)
        orders.append((oid, uid["agent_smith"], address, total, status,
                       placed_on, ""))
        for ix, q in items:
            oiid += 1
            order_items.append((oiid, oid, catalog[ix]["id"], q,
                                catalog[ix]["price"]))

    wishlist = [(i + 1, uid["agent_smith"], catalog[ix]["id"])
                for i, ix in enumerate(PRESEEDED_WISHLIST)]

    rng2 = random.Random(777_915)
    reviews = [(rid_, pid, u, stars, body, rng2.choice(HELPFUL_CHOICES))
               for rid_, pid, u, stars, body in reviews]
    qa, qid = [], 0
    for c in catalog:
        if rng2.random() >= 0.16:
            continue
        k = rng2.randint(1, 4)
        for t in sorted(rng2.sample(range(len(QA_TEMPLATES)), k)):
            w = rng2.choice([3, 6, 12, 24])
            d = rng2.randint(2, 7)
            kg = round(rng2.uniform(0.2, 9.5), 1)
            asker = uid[rng2.choice(reviewers)]
            q_tmpl, a_tmpl = qa_pool[t]
            qid += 1
            qa.append((qid, c["id"], asker,
                       q_tmpl.format(brand=c["brand"]),
                       a_tmpl.format(brand=c["brand"], w=w, d=d, kg=kg)))

    return (users, products, coupons, reviews, orders, order_items,
            wishlist, qa)


def seed(con, lang="en"):
    con.executescript(SCHEMA)
    (users, products, coupons, reviews, orders, order_items, wishlist,
     qa) = build_rows(lang)
    con.executemany("INSERT INTO users VALUES (?,?,?,?)", users)
    con.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?)", products)
    con.executemany("INSERT INTO coupons VALUES (?,?,?,?)", coupons)
    con.executemany("INSERT INTO reviews VALUES (?,?,?,?,?,?)", reviews)
    con.executemany("INSERT INTO qa VALUES (?,?,?,?,?)", qa)
    con.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?)", orders)
    con.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)",
                    order_items)
    con.executemany("INSERT INTO wishlist VALUES (?,?,?)", wishlist)
    con.commit()
