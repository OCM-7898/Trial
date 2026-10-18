import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(HERE, "cars")
DEST = os.path.join(ROOT, "sites", "visual", "gari", "static", "cars")


def main():
    n = 0
    for cid in sorted(os.listdir(SRC)):
        src_dir = os.path.join(SRC, cid)
        if not os.path.isdir(src_dir):
            continue
        dest_dir = os.path.join(DEST, cid)
        os.makedirs(dest_dir, exist_ok=True)
        for name in sorted(os.listdir(src_dir)):
            if name.endswith(".jpg"):
                shutil.copyfile(os.path.join(src_dir, name),
                                os.path.join(dest_dir, name))
                n += 1
    print(f"copied {n} car photos to {DEST}")


if __name__ == "__main__":
    main()
