AIRLINE_CODE = "SM"
FLIGHT_NO_MIN = 100
FLIGHT_NO_MAX = 999
CURRENCY = "USD"

BRANDS = {
    "airline":          {"en": "Selam Airways",              "am": "ሰላም አየር መንገድ",
                         "bn": "সেলাম এয়ারওয়েজ", "hi": "सेलाम एयरवेज़", "ur": "سلام ایئرویز"},
    "airline_short":    {"en": "Selam",                      "am": "ሰላም",
                         "bn": "সেলাম", "hi": "सेलाम", "ur": "سلام"},
    "loyalty":          {"en": "Selam Miles",                "am": "ሰላም ማይልስ",
                         "bn": "সেলাম মাইলস", "hi": "सेलाम माइल्स", "ur": "سلام مائلز"},
    "cabin_business":   {"en": "Highland Class",             "am": "ሃይላንድ ክላስ",
                         "bn": "হাইল্যান্ড ক্লাস", "hi": "हाइलैंड क्लास", "ur": "ہائی لینڈ کلاس"},
    "cabin_economy":    {"en": "Selam Economy",              "am": "ሰላም ኢኮኖሚ",
                         "bn": "সেলাম ইকোনমি", "hi": "सेलाम इकोनॉमी", "ur": "سلام اکانومی"},
    "fare_economy_flex":{"en": "Economy Flex",               "am": "ኢኮኖሚ ፍሌክስ",
                         "bn": "ইকোনমি ফ্লেক্স", "hi": "इकोनॉमी फ़्लेक्स", "ur": "اکانومی فلیکس"},
    "hotel":            {"en": "Zena Transit Hotel",         "am": "ዜና ትራንዚት ሆቴል",
                         "bn": "জেনা ট্রানজিট হোটেল", "hi": "ज़ेना ट्रांज़िट होटल", "ur": "زینا ٹرانزٹ ہوٹل"},
    "wifi":             {"en": "SkyLink Wi-Fi",              "am": "ስካይሊንክ ዋይ-ፋይ",
                         "bn": "স্কাইলিংক ওয়াই-ফাই", "hi": "स्काईलिंक वाई-फ़ाई", "ur": "اسکائی لنک وائی فائی"},
    "car_partner":      {"en": "RiftDrive",                  "am": "ሪፍት ድራይቭ",
                         "bn": "রিফটড্রাইভ", "hi": "रिफ़्टड्राइव", "ur": "رفٹ ڈرائیو"},
    "insurance":        {"en": "SafeVoyage Travel Cover",    "am": "ሴፍቮያጅ የጉዞ መድን",
                         "bn": "সেফভয়েজ ট্রাভেল কভার", "hi": "सेफ़वॉयेज ट्रैवल कवर", "ur": "سیف وائج ٹریول کور"},
    "rail":             {"en": "EuroRail Connect",           "am": "ዩሮሬል ኮኔክት",
                         "bn": "ইউরোরেল কানেক্ট", "hi": "यूरोरेल कनेक्ट", "ur": "یورو ریل کنیکٹ"},
    "evisa":            {"en": "National eVisa Service",     "am": "ብሔራዊ ኢ-ቪዛ አገልግሎት",
                         "bn": "ন্যাশনাল ই-ভিসা সার্ভিস", "hi": "नेशनल ई-वीज़ा सर्विस", "ur": "نیشنل ای ویزا سروس"},
    "lounge_business":  {"en": "Highland Lounge",            "am": "ሃይላንድ ላውንጅ",
                         "bn": "হাইল্যান্ড লাউঞ্জ", "hi": "हाइलैंड लाउंज", "ur": "ہائی لینڈ لاؤنج"},
    "lounge_premium":   {"en": "Selam Sky Lounge",           "am": "ሰላም ስካይ ላውንጅ",
                         "bn": "সেলাম স্কাই লাউঞ্জ", "hi": "सेलाम स्काई लाउंज", "ur": "سلام اسکائی لاؤنج"},
}

def brand(key: str, lang: str) -> str:
    return BRANDS[key][lang]
