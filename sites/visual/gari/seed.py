import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = "2026-03-16"

SCHEMA = """
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS dealers;
DROP TABLE IF EXISTS listings;
DROP TABLE IF EXISTS saved;
DROP TABLE IF EXISTS offers;
DROP TABLE IF EXISTS ads;
DROP TABLE IF EXISTS messages;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    city TEXT NOT NULL
);
CREATE TABLE listings (
    id INTEGER PRIMARY KEY,
    brand TEXT, model TEXT, year INTEGER, price INTEGER,
    mileage_km INTEGER, color TEXT, body_type TEXT,
    transmission TEXT, fuel TEXT, engine_cc INTEGER,
    city TEXT, reg_city TEXT, assembly TEXT, owners INTEGER,
    seller_name TEXT, seller_type TEXT, posted_on TEXT,
    status TEXT, features TEXT, description TEXT, n_images INTEGER,
    days_listed INTEGER, prev_price INTEGER, dealer_id INTEGER,
    insp_engine REAL, insp_body REAL, insp_interior REAL,
    insp_tires REAL, insp_overall REAL
);
CREATE TABLE dealers (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    city TEXT NOT NULL,
    rating REAL NOT NULL,
    member_since INTEGER NOT NULL,
    phone TEXT NOT NULL
);
CREATE TABLE saved (
    user_id INTEGER NOT NULL,
    listing_id INTEGER NOT NULL,
    UNIQUE(user_id, listing_id)
);
CREATE TABLE offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    listing_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    message TEXT DEFAULT '',
    status TEXT DEFAULT 'pending',
    made_on TEXT
);
CREATE TABLE ads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    brand TEXT, model TEXT, year INTEGER, price INTEGER,
    mileage_km INTEGER, color TEXT,
    transmission TEXT, fuel TEXT, engine_cc INTEGER,
    city TEXT, phone TEXT, description TEXT,
    status TEXT DEFAULT 'active', posted_on TEXT
);
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject TEXT, body TEXT
);
"""

USERS = [
    (1, "ahmed.raza@garibazaar.test", "garibazaar2026",
     "Ahmed Raza", "0300-8451234", "Lahore"),
]

PRESEEDED_ADS = [
    (1, "Suzuki", "Cultus", 2021, 11_250, 48_000, "Silver",
     "Manual", "Petrol", 1000, "Lahore", "0300-8451234",
     "Family-used Cultus VXL, first owner, all documents complete.",
     "active", "2026-03-02"),
    (2, "Honda", "City", 2017, 12_150, 96_000, "White",
     "Automatic", "Petrol", 1500, "Lahore", "0300-8451234",
     "Honda City Aspire, new tyres, sold to a colleague.",
     "sold", "2026-02-11"),
]

PRESEEDED_SAVED = [25, 210, 330]

DEALER_INFO = [
    (1, "Khan Motors", "Karachi", 4.6, 2018, "021-34567801"),
    (2, "City Auto Traders", "Lahore", 4.2, 2019, "042-35761202"),
    (3, "Prime Wheels", "Karachi", 4.8, 2020, "021-35887703"),
    (4, "Capital Car Point", "Islamabad", 4.5, 2017, "051-22114404"),
    (5, "Star Motors", "Lahore", 3.9, 2016, "042-36901505"),
    (6, "Elite Auto Gallery", "Islamabad", 4.7, 2021, "051-28334406"),
    (7, "Metro Cars", "Rawalpindi", 4.1, 2019, "051-55667707"),
    (8, "Crescent Automobiles", "Faisalabad", 4.4, 2020, "041-87220308"),
    (9, "Highway Motors", "Multan", 3.8, 2015, "061-45009909"),
    (10, "Galaxy Car Centre", "Peshawar", 4.3, 2022, "091-52716610"),
]
DEALER_ID = {d[1]: d[0] for d in DEALER_INFO}


def load_listings():
    with open(os.path.join(HERE, "listings.json"), encoding="utf-8") as f:
        return json.load(f)


def hand_table(lang):
    if lang == "en":
        return None
    p = os.path.join(os.path.dirname(HERE), "hand_gari", f"{lang}.json")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_overlay(lang):
    with open(os.path.join(HERE, f"listings_{lang}.json"),
              encoding="utf-8") as f:
        return json.load(f)


def localized(lang):
    L = load_listings()
    for l in L:
        l["dealer_id"] = (DEALER_ID[l["seller_name"]]
                          if l["seller_type"] == "Dealer" else None)
    if lang == "en":
        return L, DEALER_INFO, PRESEEDED_ADS, USERS
    T, ov = hand_table(lang), load_overlay(lang)
    for l in L:
        l.update(ov[str(l["id"])])
    dealers = [(d[0], T["dealers"][d[1]], T["city"][d[2]], d[3], d[4], d[5])
               for d in DEALER_INFO]
    ads = [a[:6] + (T["color"][a[6]], T["transmission"][a[7]],
                    T["fuel"][a[8]], a[9], T["city"][a[10]], a[11],
                    T["preseeded_ads"][a[12]]) + a[13:]
           for a in PRESEEDED_ADS]
    users = [(u[0], u[1], u[2], T["account_name"][u[3]], u[4],
              T["city"][u[5]]) for u in USERS]
    return L, dealers, ads, users


def seed(con, lang="en"):
    L, dealers, ads, users = localized(lang)
    from .strings import LANG_META
    rate = LANG_META[lang]["rate"]
    if rate != 1:
        for l in L:
            l["price"] = l["price"] * rate
            if l["prev_price"]:
                l["prev_price"] = l["prev_price"] * rate
        ads = [a[:4] + (a[4] * rate,) + a[5:] for a in ads]
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO users VALUES (?,?,?,?,?,?)", users)
    con.executemany("INSERT INTO dealers VALUES (?,?,?,?,?,?)", dealers)
    cols = ("id", "brand", "model", "year", "price", "mileage_km", "color",
            "body_type", "transmission", "fuel", "engine_cc", "city",
            "reg_city", "assembly", "owners", "seller_name", "seller_type",
            "posted_on", "status", "features", "description", "n_images",
            "days_listed", "prev_price")
    insp = ("engine", "body", "interior", "tires", "overall")

    def row(l):
        ins = l["inspection"] or {}
        return (tuple(l[c] for c in cols) + (l["dealer_id"],)
                + tuple(ins.get(k) for k in insp))

    con.executemany(
        f"INSERT INTO listings ({','.join(cols)}, dealer_id, "
        "insp_engine, insp_body, insp_interior, insp_tires, insp_overall)"
        f" VALUES ({','.join('?' * (len(cols) + 6))})",
        [row(l) for l in L])
    con.executemany(
        "INSERT INTO ads (id, user_id, brand, model, year, price, mileage_km,"
        " color, transmission, fuel, engine_cc, city, phone, description,"
        " status, posted_on) VALUES (?,1,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ads)
    con.executemany("INSERT INTO saved (user_id, listing_id) VALUES (1,?)",
                    [(i,) for i in PRESEEDED_SAVED])
    con.commit()
