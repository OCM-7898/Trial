import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(HERE, "ministore", "catalog.json")
TABLE = os.path.join(HERE, "hand_prices.json")
VARIANTS = {" Classic": 1.0, " Twin Pack": 1.8}


def price_for(table, name):
    if name in table:
        return table[name]
    for suf, mult in VARIANTS.items():
        if name.endswith(suf) and name[:-len(suf)] in table:
            base = table[name[:-len(suf)]]
            if mult == 1.0:
                return base
            return round(int(base * mult) + 0.99, 2)
    return None


def main():
    with open(TABLE, encoding="utf-8") as f:
        table = json.load(f)["prices"]
    with open(CATALOG, encoding="utf-8") as f:
        catalog = json.load(f)
    missing = []
    for c in catalog:
        p = price_for(table, c["name"])
        if p is None:
            missing.append(c["name"])
            continue
        c["price"] = p
    assert not missing, missing[:10]
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=1, ensure_ascii=False)
    print(f"repriced {len(catalog)} products from {len(table)} hand prices")


if __name__ == "__main__":
    main()
