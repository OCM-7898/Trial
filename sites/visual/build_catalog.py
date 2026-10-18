import csv
import glob
import gzip
import json
import os
import random
import re
import shutil
import collections

ABO_IMG = os.path.expanduser("~/Downloads/abo-images-small/images")
ABO_LST = os.path.expanduser("~/Downloads/abo-listings/listings/metadata")
HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "ministore")
OUT_IMG = os.path.join(STORE, "static", "img", "products")
ASSETS = os.path.join(os.path.dirname(HERE), "..", "assets", "abo",
                      "images")

MAP = {
 "Electronics": ["HEADPHONES", "SPEAKERS", "OFFICE_ELECTRONICS",
   "ELECTRONIC_ADAPTER", "CHARGING_ADAPTER", "BATTERY", "INPUT_MOUSE",
   "KEYBOARDS", "MICROPHONE", "CAMERA_TRIPOD", "WATCH",
   "SECURITY_ELECTRONICS", "CONSUMER_ELECTRONICS",
   "PORTABLE_ELECTRONIC_DEVICE_STAND", "PORTABLE_ELECTRONIC_DEVICE_MOUNT",
   "VIDEO_GAME_ACCESSORIES", "CAMERA_OTHER_ACCESSORIES", "MOUSE_PAD"],
 "Kitchen": ["KITCHEN", "DRINKING_CUP", "FOOD_SERVICE_SUPPLY", "BOTTLE"],
 "Sports": ["SPORTING_GOODS", "RECREATION_BALL", "EXERCISE_MAT",
            "EXERCISE_BAND", "TECHNICAL_SPORT_SHOE"],
 "Home": ["CHAIR", "SOFA", "RUG", "TABLE", "LAMP", "LIGHT_FIXTURE",
   "PILLOW", "WALL_ART", "SHELF", "BED", "OTTOMAN", "HOME",
   "HOME_BED_AND_BATH", "HOME_FURNITURE_AND_DECOR", "STOOL_SEATING",
   "HEADBOARD", "LIGHT_BULB", "FLAT_SHEET"],
 "Garden": ["OUTDOOR_LIVING", "PLANTER", "HERB", "ABIS_LAWN_AND_GARDEN"],
 "Books": ["PAPER_PRODUCT", "WRITING_BOARD", "PRINT_COPY_PAPER"],
 "Toys": ["TOY_FIGURE", "TOYS_AND_GAMES"],
 "Pets": ["PET_SUPPLIES"],
 "Office": ["OFFICE_PRODUCTS", "WRITING_INSTRUMENT", "MARKING_PEN"],
 "Grocery": ["GROCERY", "COFFEE", "COOKIE", "LEGUME"],
}
PT2CAT = {pt: c for c, pts in MAP.items() for pt in pts}

TARGET = {"Electronics": 300, "Kitchen": 300, "Sports": 250, "Home": 400,
          "Garden": 250, "Books": 115, "Toys": 150, "Pets": 250,
          "Office": 250, "Grocery": 300}
PRICE = {"Electronics": (8, 180), "Kitchen": (6, 120), "Sports": (7, 90),
         "Home": (12, 350), "Garden": (6, 140), "Books": (4, 30),
         "Toys": (5, 60), "Pets": (5, 70), "Office": (3, 60),
         "Grocery": (2, 35)}

PREFIXES = ["amazonbasics", "amazoncommercial", "amazon basics",
            "amazon brand", "amazon collection", "amazon essentials",
            "solimo", "eono by amazon", "eono", "umi essentials", "umi.",
            "umi", "pinzon", "rivet", "stone & beam", "stone and beam",
            "365 by whole foods market", "by amazon", "happy belly",
            "mama bear", "wickedly prime", "find.", "find", "arthur harvey",
            "daily ritual", "goodthreads", "core 10", "wag", "presto!",
            "jam & honey", "jam and honey", "ravenna home", "movian",
            "alkove", "aiho", "-", "–"]
SUFFIX_VARIANTS = ["Classic", "Twin Pack", "Compact", "Family Size",
                   "Travel Edition", "Gift Set", "Refill", "Value Pack",
                   "Mini", "Deluxe"]


def clean_name(raw):
    s = re.sub(r"\((renewed|refurbished)\)", "", raw, flags=re.I)
    s = re.sub(r"[\[\(][^\)\]]*[\)\]]", "", s)
    changed = True
    while changed:
        changed = False
        low = s.lower().strip(" -–—.,|&\t")
        s = s.strip(" -–—.,|&\t")
        for p in sorted(PREFIXES, key=len, reverse=True):
            if low.startswith(p) and (len(low) == len(p)
                                      or not low[len(p)].isalnum()):
                s = s[len(p):]
                changed = True
                break
    s = re.split(r"[,，|]| - | – | — ", s)[0]
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > 64:
        s = s[:64].rsplit(" ", 1)[0]
    return s.strip(" -–—.,&")


def main():
    img_path = {}
    with gzip.open(os.path.join(ABO_IMG, "metadata", "images.csv.gz"),
                   "rt") as f:
        for row in csv.DictReader(f):
            img_path[row["image_id"]] = row["path"]

    pools = collections.defaultdict(list)
    for fp in sorted(glob.glob(os.path.join(ABO_LST, "*.json.gz"))):
        with gzip.open(fp, "rt", encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                mid = row.get("main_image_id")
                if not mid or mid not in img_path:
                    continue
                en = [n["value"] for n in row.get("item_name", [])
                      if n.get("language_tag", "").startswith("en")]
                if not en:
                    continue
                cat = None
                for pt in row.get("product_type", []):
                    cat = PT2CAT.get(pt["value"]) or cat
                if not cat:
                    continue

                def attr(key):
                    v = [x["value"] for x in row.get(key, [])
                         if x.get("language_tag", "").startswith("en")]
                    return v[0] if v else ""
                pools[cat].append(dict(
                    item_id=row["item_id"], mid=mid, raw=en[0],
                    brand=attr("brand"), color=attr("color"),
                    material=attr("material")))

    rng = random.Random("visual-ministore-1")
    os.makedirs(OUT_IMG, exist_ok=True)
    catalog, man_rows = [], []
    pid = 0
    for cat in MAP:
        pool = pools[cat][:]
        rng.shuffle(pool)
        chosen, seen_key, seen_img = [], set(), set()
        for it in pool:
            if len(chosen) >= TARGET[cat]:
                break
            name = clean_name(it["raw"])
            toks = name.split()
            if len(toks) < 3 or len(name) < 12:
                continue
            key = " ".join(t.lower() for t in toks[:3])
            if key in seen_key or it["mid"] in seen_img:
                continue
            seen_key.add(key)
            seen_img.add(it["mid"])
            it["name"] = name
            chosen.append(it)
        base_n = len(chosen)
        i = 0
        while len(chosen) < TARGET[cat] and base_n:
            src = chosen[i % base_n]
            suffix = SUFFIX_VARIANTS[(i // base_n) % len(SUFFIX_VARIANTS)]
            it = dict(src)
            it["name"] = f"{src['name']} {suffix}"
            chosen.append(it)
            i += 1
        lo, hi = PRICE[cat]
        for it in chosen:
            pid += 1
            price = round(rng.uniform(lo, hi), 2)
            stock = 0 if rng.random() < 0.06 else rng.randint(3, 60)
            bits = []
            if it["color"]:
                bits.append(f"Colour: {it['color']}.")
            if it["material"]:
                bits.append(f"Material: {it['material']}.")
            bits.append(rng.choice([
                "Ships in plain recyclable packaging.",
                "Backed by a 30-day return window.",
                "Restocked weekly.", "Popular in its category.",
                "Sold and dispatched from our own warehouse.",
                "Covered by the standard one-year guarantee."]))
            catalog.append(dict(
                id=pid, name=it["name"], category=cat, price=price,
                brand=it["brand"] or "Unbranded", stock=stock,
                description=" ".join(bits)))
            src = os.path.join(ABO_IMG, "small", img_path[it["mid"]])
            shutil.copyfile(src, os.path.join(OUT_IMG, f"p{pid}.jpg"))
            asset = os.path.join(ASSETS, f"{it['mid']}.jpg")
            if not os.path.exists(asset):
                shutil.copyfile(src, asset)
            man_rows.append([pid, it["name"], cat, it["item_id"], it["mid"],
                             img_path[it["mid"]], it["raw"][:90],
                             it["color"]])
        print(f"{cat:12s} {len(chosen):4d} products "
              f"({base_n} unique, {len(chosen)-base_n} variants)")

    with open(os.path.join(STORE, "catalog.json"), "w",
              encoding="utf-8") as f:
        json.dump(catalog, f, indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, "ATTRIBUTIONS.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["product_id", "name", "category", "abo_item_id",
                    "abo_image_id", "abo_image_path", "abo_original_name",
                    "abo_color", "license"])
        for r in man_rows:
            w.writerow(r + ["CC BY 4.0 — Amazon Berkeley Objects (ABO)"])
    print(f"catalog: {len(catalog)} products")


if __name__ == "__main__":
    main()
