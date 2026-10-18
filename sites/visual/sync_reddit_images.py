import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
GARI_IMG = os.path.join(HERE, "gari", "static", "cars")
MINI_IMG = os.path.join(HERE, "ministore", "static", "img", "products")
CONTENT = os.path.join(HERE, "reddit", "content.json")
IMG_OUT = os.path.join(HERE, "reddit", "static", "post_images")


def main():
    with open(CONTENT, encoding="utf-8") as f:
        posts = json.load(f)["posts"]
    os.makedirs(IMG_OUT, exist_ok=True)
    n = 0
    for p in posts:
        if not p["n_images"]:
            continue
        if p["kind"] == "car":
            for k in range(1, p["n_images"] + 1):
                shutil.copyfile(
                    os.path.join(GARI_IMG, str(p["src_id"]), f"{k}.jpg"),
                    os.path.join(IMG_OUT, f"{p['id']}_{k}.jpg"))
                n += 1
        else:
            shutil.copyfile(
                os.path.join(MINI_IMG, f"p{p['src_id']}.jpg"),
                os.path.join(IMG_OUT, f"{p['id']}_1.jpg"))
            n += 1
    print(f"copied {n} post images to {IMG_OUT}")


if __name__ == "__main__":
    main()
