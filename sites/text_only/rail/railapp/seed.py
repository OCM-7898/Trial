import datetime
import json
import os

TODAY = "2026-04-01"

DIGITS_HI = str.maketrans("0123456789", "०१२३४५६७८९")

DIGITS = {"en": "0123456789", "hi": "०१२३४५६७८९", "bn": "০১২৩৪৫৬৭৮৯",
          "ur": "۰۱۲۳۴۵۶۷۸۹", "am": "0123456789"}

LANG_META = {
    "en": dict(cur="₹", rate=1.0, dir="ltr"),
    "hi": dict(cur="₹", rate=1.0, dir="ltr"),
    "bn": dict(cur="৳", rate=120 / 85, dir="ltr"),
    "ur": dict(cur="Rs.", rate=280 / 85, dir="rtl"),
    "am": dict(cur="ብር", rate=130 / 85, dir="ltr"),
}

_HAND = {}


def hand_table(lang):
    if lang not in _HAND:
        path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "hand_rail", f"{lang}.json")
        with open(path, encoding="utf-8") as f:
            _HAND[lang] = json.load(f)
    return _HAND[lang]


def money(amount, lang="en"):
    rate = LANG_META[lang]["rate"]
    if rate == 1.0:
        return int(amount)
    return max(4, int(round(amount * rate / 4)) * 4)

STATIONS = {
    "NDLS": ("New Delhi", "नई दिल्ली"),
    "BCT":  ("Mumbai Central", "मुंबई सेंट्रल"),
    "HWH":  ("Howrah Jn", "हावड़ा जंक्शन"),
    "MAS":  ("Chennai Central", "चेन्नई सेंट्रल"),
    "SBC":  ("Bengaluru City", "बेंगलुरु सिटी"),
    "SC":   ("Secunderabad Jn", "सिकंदराबाद जंक्शन"),
    "PUNE": ("Pune Jn", "पुणे जंक्शन"),
    "JP":   ("Jaipur Jn", "जयपुर जंक्शन"),
    "LKO":  ("Lucknow", "लखनऊ"),
    "CNB":  ("Kanpur Central", "कानपुर सेंट्रल"),
    "ADI":  ("Ahmedabad Jn", "अहमदाबाद जंक्शन"),
    "BPL":  ("Bhopal Jn", "भोपाल जंक्शन"),
    "PNBE": ("Patna Jn", "पटना जंक्शन"),
    "GHY":  ("Guwahati", "गुवाहाटी"),
    "BSB":  ("Varanasi Jn", "वाराणसी जंक्शन"),
    "NGP":  ("Nagpur Jn", "नागपुर जंक्शन"),
    "AGC":  ("Agra Cantt", "आगरा कैंट"),
    "AII":  ("Ajmer Jn", "अजमेर जंक्शन"),
    "ABR":  ("Abu Road", "आबू रोड"),
    "RTM":  ("Ratlam Jn", "रतलाम जंक्शन"),
    "NJP":  ("New Jalpaiguri", "न्यू जलपाईगुड़ी"),
    "VSKP": ("Visakhapatnam", "विशाखापत्तनम"),
}


def station_name(code, lang):
    if lang == "en":
        return STATIONS[code][0]
    if lang == "hi":
        return STATIONS[code][1]
    return hand_table(lang)["stations"][code]


DAILY = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

TRAINS = [
    dict(no="12301", mult=1.2, days=["Mon", "Wed", "Fri", "Sun"],
         stops=[("NDLS", None, "16:55", 1, 0),
                ("CNB", "21:45", "21:50", 1, 440),
                ("PNBE", "04:10", "04:20", 2, 992),
                ("HWH", "09:55", None, 2, 1451)],
         classes={"1A": 10, "2A": 26, "3A": 0, "SL": 120},
         wl={"3A": 12}),
    dict(no="12302", mult=1.0, days=DAILY,
         stops=[("HWH", None, "20:05", 1, 0),
                ("PNBE", "01:35", "01:45", 2, 459),
                ("CNB", "08:05", "08:15", 2, 1011),
                ("NDLS", "13:10", None, 2, 1451)],
         classes={"2A": 18, "3A": 44, "SL": 96}, wl={}),
    dict(no="12903", mult=1.2, days=DAILY,
         stops=[("NDLS", None, "17:40", 1, 0),
                ("RTM", "03:05", "03:15", 2, 726),
                ("BCT", "10:35", None, 2, 1384)],
         classes={"1A": 6, "2A": 30, "3A": 52, "SL": 140}, wl={}),
    dict(no="12904", mult=1.2, days=["Tue", "Thu", "Sat"],
         stops=[("BCT", None, "17:00", 1, 0),
                ("RTM", "23:45", "23:55", 1, 658),
                ("NDLS", "09:55", None, 2, 1384)],
         classes={"1A": 8, "2A": 24, "3A": 61}, wl={}),
    dict(no="12615", mult=1.0, days=DAILY,
         stops=[("NDLS", None, "06:15", 1, 0),
                ("AGC", "08:45", "08:50", 1, 195),
                ("BPL", "14:40", "14:50", 1, 701),
                ("NGP", "20:30", "20:40", 1, 1090),
                ("SC", "05:10", "05:25", 2, 1661),
                ("MAS", "12:40", None, 2, 2182)],
         classes={"2A": 21, "3A": 58, "SL": 210}, wl={}),
    dict(no="12659", mult=0.9, days=["Mon", "Thu", "Sat"],
         stops=[("JP", None, "08:20", 1, 0),
                ("AII", "10:25", "10:35", 1, 135),
                ("ABR", "15:05", "15:10", 1, 439),
                ("ADI", "19:25", None, 1, 626)],
         classes={"CC": 40, "3A": 24, "SL": 88, "2S": 150}, wl={}),
    dict(no="12417", mult=0.9, days=DAILY,
         stops=[("NDLS", None, "15:35", 1, 0),
                ("CNB", "20:55", "21:05", 1, 440),
                ("LKO", "22:35", None, 1, 512)],
         classes={"CC": 62, "3A": 20, "2S": 130}, wl={}),
    dict(no="12622", mult=1.0, days=["Tue", "Fri", "Sun"],
         stops=[("HWH", None, "15:50", 1, 0),
                ("NJP", "03:15", "03:25", 2, 561),
                ("GHY", "09:50", None, 2, 1039)],
         classes={"1A": 4, "2A": 22, "3A": 48, "SL": 130}, wl={}),
    dict(no="12138", mult=1.0, days=DAILY,
         stops=[("BCT", None, "21:10", 1, 0),
                ("RTM", "04:30", "04:40", 2, 658),
                ("BPL", "08:45", None, 2, 837)],
         classes={"2A": 16, "3A": 40, "SL": 175}, wl={}),
    dict(no="12723", mult=0.9, days=["Mon", "Wed", "Sat"],
         stops=[("SC", None, "18:20", 1, 0),
                ("PUNE", "04:35", None, 2, 597)],
         classes={"2A": 14, "3A": 36, "SL": 102}, wl={}),
    dict(no="12841", mult=1.0, days=DAILY,
         stops=[("HWH", None, "14:50", 1, 0),
                ("VSKP", "05:00", "05:20", 2, 879),
                ("MAS", "16:50", None, 2, 1659)],
         classes={"1A": 5, "2A": 28, "3A": 66, "SL": 190}, wl={}),
    dict(no="12559", mult=1.0, days=["Tue", "Thu", "Sun"],
         stops=[("NDLS", None, "18:55", 1, 0),
                ("CNB", "01:20", "01:30", 2, 440),
                ("BSB", "06:30", None, 2, 785)],
         classes={"2A": 19, "3A": 47, "SL": 160}, wl={}),
    dict(no="12049", mult=0.9, days=["Mon", "Tue", "Wed", "Thu", "Sat",
                                     "Sun"],
         stops=[("NDLS", None, "06:00", 1, 0),
                ("AGC", "08:10", None, 1, 195)],
         classes={"CC": 78, "2S": 210}, wl={}),
]

TRAIN_BY_NO = {t["no"]: t for t in TRAINS}

TRAIN_NAMES = {
    "12301": ("Yamuna Express", "यमुना एक्सप्रेस"),
    "12302": ("Howrah Mail", "हावड़ा मेल"),
    "12903": ("Sagarmala Express", "सागरमाला एक्सप्रेस"),
    "12904": ("Mumbai Sampark Express", "मुंबई संपर्क एक्सप्रेस"),
    "12615": ("Dakshin Express", "दक्षिण एक्सप्रेस"),
    "12659": ("Aravalli Express", "अरावली एक्सप्रेस"),
    "12417": ("Gomti Sampark", "गोमती संपर्क"),
    "12622": ("Brahmaputra Link Express", "ब्रह्मपुत्र लिंक एक्सप्रेस"),
    "12138": ("Narmada Mail", "नर्मदा मेल"),
    "12723": ("Deccan Sampark", "दक्कन संपर्क"),
    "12841": ("Coromandel Link Express", "कोरोमंडल लिंक एक्सप्रेस"),
    "12559": ("Kashi Express", "काशी एक्सप्रेस"),
    "12049": ("Taj Sampark", "ताज संपर्क"),
}


def train_name(no, lang):
    if lang == "en":
        return TRAIN_NAMES[no][0]
    if lang == "hi":
        return TRAIN_NAMES[no][1]
    return hand_table(lang)["trains"][no]


CLASSES = ["1A", "2A", "3A", "CC", "SL", "2S"]
RATES = {"1A": 3.8, "2A": 2.35, "3A": 1.65, "CC": 1.25, "SL": 0.62,
         "2S": 0.34}


def _km(train, code):
    for c, _a, _d, _day, km in train["stops"]:
        if c == code:
            return km
    return None


def serves(train, a, b):
    order = [s[0] for s in train["stops"]]
    return a in order and b in order and order.index(a) < order.index(b)


def fare(no, cls, a=None, b=None, lang="en"):
    t = TRAIN_BY_NO[no]
    a = a or t["stops"][0][0]
    b = b or t["stops"][-1][0]
    dist = _km(t, b) - _km(t, a)
    base = max(30, int(RATES[cls] * dist * t["mult"] / 5 + 0.5) * 5)
    return money(base, lang)


def seg(no, a=None, b=None):
    t = TRAIN_BY_NO[no]
    a = a or t["stops"][0][0]
    b = b or t["stops"][-1][0]
    sa = next(s for s in t["stops"] if s[0] == a)
    sb = next(s for s in t["stops"] if s[0] == b)
    dep, arr = sa[2], sb[1]
    dep_min = int(dep[:2]) * 60 + int(dep[3:])
    arr_min = int(arr[:2]) * 60 + int(arr[3:])
    dur = (sb[3] - sa[3]) * 1440 + arr_min - dep_min
    return dict(dep=dep, arr=arr, dep_day=sa[3], arr_day=sb[3],
                dist=_km(t, b) - _km(t, a), dur_min=dur)


def dur_str(mins):
    return f"{mins // 60}h {mins % 60}m"


def days_at(no, code):
    t = TRAIN_BY_NO[no]
    stop = next(s for s in t["stops"] if s[0] == code)
    shift = stop[3] - 1
    here = {DAILY[(DAILY.index(d) + shift) % 7] for d in t["days"]}
    return [d for d in DAILY if d in here]


def runs_on(no, date_str, from_code=None):
    t = TRAIN_BY_NO[no]
    from_code = from_code or t["stops"][0][0]
    stop = next(s for s in t["stops"] if s[0] == from_code)
    d = datetime.date.fromisoformat(date_str)
    origin_date = d - datetime.timedelta(days=stop[3] - 1)
    return DAILY[origin_date.weekday()] in t["days"]


def search(a, b, date_str):
    out = []
    for t in TRAINS:
        if serves(t, a, b) and runs_on(t["no"], date_str, a):
            out.append(t["no"])
    return sorted(out, key=lambda no: seg(no, a, b)["dep"])


def resolve_station(text, lang):
    q = " ".join(str(text).strip().split()).casefold()
    for code, names in STATIONS.items():
        if q == code.casefold():
            return code
    for code in STATIONS:
        if q == station_name(code, lang).casefold():
            return code
    return None


USER = dict(username="priya_sharma", password="travel123",
            full_name=("Priya Sharma", "प्रिया शर्मा"),
            email="priya.sharma@example.in", mobile="9812304567")

BOOKINGS = [
    ("6201234567", "12301", "NDLS", "HWH", "2026-04-06", "3A",
     "Rohan Sharma", "रोहन शर्मा", 34, "M", "Lower", "CNF"),
    ("6202345678", "12615", "NDLS", "MAS", "2026-04-08", "SL",
     "Anita Desai", "अनीता देसाई", 41, "F", "Middle", "WL"),
    ("6203456789", "12903", "NDLS", "BCT", "2026-04-10", "2A",
     "Vikram Rao", "विक्रम राव", 29, "M", "Upper", "CNF"),
    ("6204567890", "12841", "HWH", "MAS", "2026-04-07", "SL",
     "Meera Iyer", "मीरा अय्यर", 26, "F", "Side Lower", "CNF"),
    ("6205678901", "12049", "NDLS", "AGC", "2026-04-06", "CC",
     "Priya Sharma", "प्रिया शर्मा", 31, "F", "No Preference", "CNF"),
    ("6206789012", "12559", "NDLS", "BSB", "2026-04-09", "2A",
     "Arjun Nair", "अर्जुन नायर", 37, "M", "Lower", "CNF"),
    ("6207890123", "12723", "SC", "PUNE", "2026-04-11", "SL",
     "Kavita Joshi", "कविता जोशी", 48, "F", "Middle", "CAN"),
    ("6208901234", "12622", "HWH", "NJP", "2026-04-12", "3A",
     "Dev Patel", "देव पटेल", 19, "M", "Side Upper", "CNF"),
]


def passenger_name(pnr, lang):
    for b in BOOKINGS:
        if b[0] == pnr:
            if lang == "en":
                return b[6]
            if lang == "hi":
                return b[7]
            return hand_table(lang)["passengers"][b[6]]
    return None


def user_name(lang):
    if lang == "en":
        return USER["full_name"][0]
    if lang == "hi":
        return USER["full_name"][1]
    return hand_table(lang)["user"]


SCHEMA = """
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS messages;
CREATE TABLE users (
    id INTEGER PRIMARY KEY, username TEXT, password TEXT,
    full_name TEXT, email TEXT, mobile TEXT);
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY, pnr TEXT, user_id INTEGER, train_no TEXT,
    from_code TEXT, to_code TEXT, date TEXT, class_code TEXT,
    passenger TEXT, age INTEGER, gender TEXT, berth TEXT,
    fare INTEGER, status TEXT);
CREATE TABLE messages (
    id INTEGER PRIMARY KEY, name TEXT, email TEXT, subject TEXT,
    message TEXT, created_date TEXT);
"""


def seed(con, lang):
    con.executescript(SCHEMA)
    con.execute(
        "INSERT INTO users (username, password, full_name, email, mobile)"
        " VALUES (?,?,?,?,?)",
        (USER["username"], USER["password"], user_name(lang),
         USER["email"], USER["mobile"]))
    for (pnr, no, a, b, date, cls, p_en, p_hi, age, gender, berth,
         status) in BOOKINGS:
        con.execute(
            "INSERT INTO bookings (pnr, user_id, train_no, from_code,"
            " to_code, date, class_code, passenger, age, gender, berth,"
            " fare, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (pnr, 1, no, a, b, date, cls,
             passenger_name(pnr, lang), age, gender, berth,
             fare(no, cls, a, b, lang), status))
    con.commit()
