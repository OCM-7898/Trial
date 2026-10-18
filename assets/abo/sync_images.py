import csv
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
IMAGES = os.path.join(HERE, "images")

SITES = [
    ("sites/visual/ATTRIBUTIONS.csv",
     "sites/visual/ministore/static/img/products"),
]


def main():
    for manifest, dest in SITES:
        man_path = os.path.join(ROOT, manifest)
        if not os.path.exists(man_path):
            print(f"skip (no manifest): {manifest}")
            continue
        dest_dir = os.path.join(ROOT, dest)
        os.makedirs(dest_dir, exist_ok=True)
        n = missing = 0
        with open(man_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                src = os.path.join(IMAGES, f"{r['abo_image_id']}.jpg")
                if not os.path.exists(src):
                    missing += 1
                    continue
                shutil.copyfile(src, os.path.join(
                    dest_dir, f"p{r['product_id']}.jpg"))
                n += 1
        print(f"{manifest}: {n} images synced"
              + (f", {missing} MISSING from assets" if missing else ""))


if __name__ == "__main__":
    main()
