import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT_FIELDS = ("color", "city", "reg_city", "body_type", "transmission",
               "fuel", "assembly")


def load_table(lang):
    with open(os.path.join(HERE, "hand_gari", f"{lang}.json"),
              encoding="utf-8") as f:
        return json.load(f)


def localize_listing(l, T):
    out = dict(l)
    for k in TEXT_FIELDS:
        key = "city" if k == "reg_city" else k
        out[k] = T[key][l[k]]
    out["features"] = ", ".join(T["features"][f]
                                for f in l["features"].split(", "))
    out["description"] = T["description"][l["description"]]
    out["seller_name"] = (T["dealers"] if l["seller_type"] == "Dealer"
                          else T["sellers"])[l["seller_name"]]
    return out


def main(lang):
    T = load_table(lang)
    with open(os.path.join(HERE, "gari", "listings.json"),
              encoding="utf-8") as f:
        L = json.load(f)
    keys = ("color", "city", "reg_city", "body_type", "transmission",
            "fuel", "assembly", "features", "description", "seller_name")
    overlay = {}
    for l in L:
        o = localize_listing(l, T)
        overlay[str(l["id"])] = {k: o[k] for k in keys}
    out = os.path.join(HERE, "gari", f"listings_{lang}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(overlay, f, ensure_ascii=False, indent=1)
    print(f"wrote {len(overlay)} localized listings to {out}")


if __name__ == "__main__":
    main(sys.argv[1])
