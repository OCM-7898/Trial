import argparse
import csv
import datetime
import json
import os
import random

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
CSV = os.path.join(ROOT, "marketplace_cars_final.csv")
FRAMES = os.path.join(ROOT, "frames")
SITE = os.path.join(HERE, "gari")
OUT_JSON = os.path.join(SITE, "listings.json")
IMG_ROOT = os.path.join(SITE, "static", "cars")

N_IMAGES = 6
MAX_DIM = 560
QUALITY = 72

BRAND_BASE = {
    "Aston Martin": 165_000, "Porsche": 107_000, "Hummer": 64_000,
    "Tesla": 61_000, "Land Rover": 79_000, "Lexus": 55_000,
    "Mercedes-Benz": 57_000, "BMW": 54_000, "Audi": 50_000,
    "Cadillac": 48_000, "Lincoln": 46_000, "Volvo": 45_000,
    "Infiniti": 43_000, "Jeep": 41_000, "MINI": 32_000,
    "Toyota": 29_500, "Honda": 27_000, "Subaru": 26_000,
    "Volkswagen": 25_000, "Ford": 25_000, "Mazda": 23_500,
    "Skoda": 23_000, "Buick": 23_000, "Chevrolet": 22_000,
    "Chrysler": 21_500, "Hyundai": 21_500, "Kia": 21_500,
    "Nissan": 21_000, "Mitsubishi": 20_000, "Peugeot": 19_500,
    "Citroen": 19_000, "Renault": 18_000, "smart": 15_000,
    "Suzuki": 13_000,
}
BODY_MULT = {"Sedan": 1.0, "SUV": 1.25, "Hatchback": 0.8,
             "Sports car": 1.8, "MPV": 1.1, "Van": 0.9}
CC_BY_BODY = {"Sedan": [1300, 1500, 1600, 1800, 2000],
              "SUV": [1500, 1800, 2000, 2400, 3000],
              "Hatchback": [1000, 1200, 1300, 1500],
              "Sports car": [3000, 4000, 5200],
              "MPV": [1500, 1800, 2000], "Van": [2000, 2700]}
CITIES = ["Karachi", "Lahore", "Islamabad", "Rawalpindi",
          "Faisalabad", "Multan", "Peshawar", "Sialkot"]
CITY_W = [25, 25, 15, 10, 8, 7, 5, 5]
LOCAL_ASSEMBLY = {"Toyota", "Honda", "Suzuki", "Hyundai", "Kia"}
LUXURY = {"Aston Martin", "Porsche", "Land Rover", "Mercedes-Benz", "BMW",
          "Audi", "Lexus", "Cadillac", "Lincoln", "Infiniti", "Volvo",
          "Tesla", "Hummer", "Jeep"}
INDIVIDUALS = [
    "Ahmed Khan", "Bilal Hussain", "Fatima Malik", "Usman Sheikh",
    "Ayesha Siddiqui", "Imran Qureshi", "Sana Tariq", "Hassan Raza",
    "Zainab Akhtar", "Kamran Baig", "Nadia Hussain", "Faisal Mahmood",
    "Rabia Anwar", "Tariq Jameel", "Mehwish Iqbal", "Salman Butt",
    "Hira Farooq", "Adeel Akram", "Saad Chaudhry", "Amna Javed",
]
DEALERS = [
    "Khan Motors", "City Auto Traders", "Prime Wheels",
    "Capital Car Point", "Star Motors", "Elite Auto Gallery",
    "Metro Cars", "Crescent Automobiles", "Highway Motors",
    "Galaxy Car Centre",
]
FEATURES = [
    "ABS", "Air Conditioning", "Power Steering", "Power Windows",
    "Airbags", "Alloy Rims", "Navigation", "Rear Camera",
    "Cruise Control", "Keyless Entry", "Sunroof", "Leather Seats",
    "Heated Seats", "Immobilizer", "Fog Lights", "Bluetooth",
    "USB Port", "Parking Sensors",
]
DESCRIPTIONS = [
    "Well-maintained family car with complete service history.",
    "Excellent condition inside and out, all original paint.",
    "Carefully driven, always garage kept and regularly serviced.",
    "First-class mechanical condition, new tyres fitted recently.",
    "Complete documents, token tax paid up to date.",
    "Non-accidental, engine and suspension in top shape.",
    "Urgent sale, serious buyers only, price slightly negotiable.",
    "Doctor-owned vehicle, used sparingly within the city.",
    "Company-maintained until last year, full record available.",
    "Immaculate interior, chilled AC, smooth long-route drive.",
]


def build_listing(row):
    car_no = int(row["car_no"])
    rng = random.Random(20260316 * 1000 + car_no)
    brand, model = row["brand"], row["model"]
    body, color = row["body_type"], row["color"]

    year = rng.choices(range(2013, 2025),
                       weights=[2, 3, 4, 5, 7, 9, 11, 12, 12, 12, 12, 11])[0]
    age = 2026 - year
    mileage = round(age * rng.randint(8000, 18000), -3)
    price = (BRAND_BASE[brand] * BODY_MULT[body] * (0.88 ** age)
             * rng.uniform(0.92, 1.08))
    price = max(3_000, int(round(price / 100) * 100))

    if brand == "Tesla":
        fuel, transmission, engine_cc = "Electric", "Automatic", 0
    else:
        engine_cc = rng.choice(CC_BY_BODY[body])
        hybrid_w = 30 if brand in ("Toyota", "Honda", "Lexus") else 8
        fuel = rng.choices(["Petrol", "Hybrid", "Diesel"],
                           weights=[80, hybrid_w, 10])[0]
        if brand in LUXURY:
            transmission = "Automatic"
        else:
            manual_w = 55 if body == "Hatchback" else 35
            transmission = rng.choices(["Automatic", "Manual"],
                                       weights=[100 - manual_w, manual_w])[0]

    city = rng.choices(CITIES, weights=CITY_W)[0]
    reg_city = rng.choice([city, city, city, "Karachi", "Lahore", "Islamabad"])
    assembly = "Local" if brand in LOCAL_ASSEMBLY else "Imported"
    owners = rng.choices([1, 2, 3], weights=[50, 35, 15])[0]
    if rng.random() < 0.30:
        seller_name, seller_type = rng.choice(DEALERS), "Dealer"
    else:
        seller_name, seller_type = rng.choice(INDIVIDUALS), "Individual"
    day = rng.randint(0, 42)
    posted_on = (f"2026-02-{day + 1:02d}" if day < 28
                 else f"2026-03-{day - 27:02d}")
    status = "sold" if rng.random() < 0.05 else "active"
    n_feat = rng.randint(6, 9) if brand in LUXURY else rng.randint(4, 7)
    features = sorted(rng.sample(FEATURES, n_feat))
    desc = rng.choice(DESCRIPTIONS)

    return {
        "id": car_no, "brand": brand, "model": model, "year": year,
        "price": price, "mileage_km": mileage, "color": color,
        "body_type": body, "transmission": transmission, "fuel": fuel,
        "engine_cc": engine_cc, "city": city, "reg_city": reg_city,
        "assembly": assembly, "owners": owners,
        "seller_name": seller_name, "seller_type": seller_type,
        "posted_on": posted_on, "status": status,
        "features": ", ".join(features), "description": desc,
        "n_images": N_IMAGES, "frames_folder": row["frames_folder"],
    }


def enrich(listing):
    rng = random.Random(777_000 + listing["id"])
    posted = datetime.date.fromisoformat(listing["posted_on"])
    listing["days_listed"] = (datetime.date(2026, 3, 16) - posted).days
    if rng.random() < 0.40:
        t = [rng.randint(50, 96) for _ in range(4)]
        listing["inspection"] = {
            "engine": t[0] / 10, "body": t[1] / 10,
            "interior": t[2] / 10, "tires": t[3] / 10,
            "overall": ((sum(t) + 2) // 4) / 10,
        }
    else:
        listing["inspection"] = None
    if rng.random() < 0.35:
        drops = [x for x in (200, 300, 500, 800, 1200, 2000, 3000, 5000)
                 if x <= listing["price"] * 12 // 100]
        listing["prev_price"] = listing["price"] + rng.choice(drops)
    else:
        listing["prev_price"] = None
    return listing


def export_images(listing):
    src_dir = os.path.join(FRAMES, listing["frames_folder"])
    jpgs = sorted(f for f in os.listdir(src_dir)
                  if f.lower().endswith((".jpg", ".jpeg", ".png")))
    assert jpgs, src_dir
    picks = [jpgs[round(i * (len(jpgs) - 1) / (N_IMAGES - 1))]
             for i in range(N_IMAGES)]
    out_dir = os.path.join(IMG_ROOT, str(listing["id"]))
    os.makedirs(out_dir, exist_ok=True)
    for k, name in enumerate(picks, 1):
        img = Image.open(os.path.join(src_dir, name)).convert("RGB")
        img.thumbnail((MAX_DIM, MAX_DIM))
        img.save(os.path.join(out_dir, f"{k}.jpg"), "JPEG",
                 quality=QUALITY, optimize=True)


def main(images=True):
    with open(CSV, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    listings = [enrich(build_listing(r)) for r in rows]
    n_sold = sum(1 for l in listings if l["status"] == "sold")
    os.makedirs(SITE, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(listings, f, indent=1, ensure_ascii=False)
    print(f"wrote {len(listings)} listings ({n_sold} sold) to {OUT_JSON}")
    if images:
        for i, l in enumerate(listings, 1):
            export_images(l)
            if i % 100 == 0:
                print(f"  images: {i}/{len(listings)}")
        print(f"exported {len(listings) * N_IMAGES} images to {IMG_ROOT}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-images", action="store_true")
    main(images=not ap.parse_args().no_images)
