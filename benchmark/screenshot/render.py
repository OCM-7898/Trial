import io
import os
import shutil
import subprocess
import tempfile

from bs4 import BeautifulSoup
from PIL import Image


def _find_chrome():
    if os.environ.get("MWA_CHROME"):
        return os.environ["MWA_CHROME"]
    for name in ("chrome-headless-shell", "google-chrome", "google-chrome-stable", "chromium",
                 "chromium-browser", "chrome"):
        if shutil.which(name):
            return shutil.which(name)
    mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(mac):
        return mac
    raise SystemExit("no Chrome found: install chrome-headless-shell (or Chrome/Chromium) "
                     "or set MWA_CHROME to its path")


CHROME = None
WIDTH = 1280
MAX_HEIGHT = 8000
TAG_CSS = """
.mwa-tag{display:inline-block;font:bold 12px/14px monospace;padding:0 3px;margin:0 3px 0 0;
  border:1px solid #000;border-radius:3px;vertical-align:middle;direction:ltr;unicode-bidi:isolate;
  white-space:nowrap}
.mwa-link{background:#ffe14d;color:#000}
.mwa-form{background:#7ee08a;color:#000}
"""


def tag_html(html, url):
    soup = BeautifulSoup(html, "html.parser")
    skipped = {id(a) for t in soup(["script", "style"]) for a in t.find_all("a", href=True)}
    links = [a for a in soup.find_all("a", href=True) if id(a) not in skipped]
    skipped = {id(f) for t in soup(["script", "style"]) for f in t.find_all("form")}
    forms = [f for f in soup.find_all("form") if id(f) not in skipped]
    for i, a in enumerate(links):
        tag = soup.new_tag("span", attrs={"class": "mwa-tag mwa-link"})
        tag.string = f"[{i}]"
        a.insert(0, tag)
    for i, f in enumerate(forms):
        tag = soup.new_tag("span", attrs={"class": "mwa-tag mwa-form"})
        tag.string = f"[fill {i}]"
        f.insert(0, tag)
    head = soup.head or soup.new_tag("head")
    if soup.head is None:
        (soup.html or soup).insert(0, head)
    base = soup.new_tag("base", href=url)
    head.insert(0, base)
    style = soup.new_tag("style")
    style.string = TAG_CSS
    head.append(style)
    return str(soup)


def _crop(img):
    bg = img.getpixel((img.width - 1, img.height - 1))
    px = img.load()
    for y in range(img.height - 1, 0, -1):
        if any(px[x, y] != bg for x in range(0, img.width, 4)):
            return img.crop((0, 0, img.width, min(img.height, y + 16)))
    return img


def screenshot(html, url, out=None):
    with tempfile.TemporaryDirectory() as d:
        page, png = os.path.join(d, "page.html"), os.path.join(d, "page.png")
        with open(page, "w", encoding="utf-8") as f:
            f.write(tag_html(html, url))
        global CHROME
        CHROME = CHROME or _find_chrome()
        headless = [] if "headless-shell" in os.path.basename(CHROME) else ["--headless=new"]
        subprocess.run([CHROME, *headless, "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={WIDTH},{MAX_HEIGHT}", f"--screenshot={png}",
                        f"file://{page}"], check=True, capture_output=True, timeout=60)
        img = _crop(Image.open(png).convert("RGB"))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    data = buf.getvalue()
    if out:
        with open(out, "wb") as f:
            f.write(data)
    return data
