from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .harness import headers as harness_headers, is_harness_path


def _unwrap(v):
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    return v


@dataclass
class Observation:
    url: str
    title: str
    text: str
    links: list = field(default_factory=list)
    forms: list = field(default_factory=list)

    def render(self, max_chars=4000):
        lines = [f"URL: {self.url}", f"TITLE: {self.title}", "", "PAGE TEXT:",
                 self.text[:max_chars], "", "LINKS:"]
        for i, txt, href in self.links:
            lines.append(f"  [{i}] {txt}  -> {href}")
        lines.append("FORMS:")
        for i, action, method, fields in self.forms:
            fstr = ", ".join(fields) if fields else "(no visible fields)"
            lines.append(f"  [{i}] {method.upper()} {action}  fields: {fstr}"
                         f"  -> press with: fill {i}")
        return "\n".join(lines)


class BrowserEnv:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.current_url = None
        self.last_html = ""
        self._soup = None

    def reset(self, start_path="/"):
        self.session = requests.Session()
        try:
            self.session.post(self.base_url + "/__reset__", timeout=10,
                              headers=harness_headers())
        except requests.RequestException:
            pass
        return self.goto(start_path)

    def _absolutize(self, path):
        if path.startswith("http"):
            return path
        return urljoin(self.base_url + "/", path.lstrip("/")) \
            if not path.startswith("/") else self.base_url + path

    def _guard(self, url):
        if is_harness_path(urlparse(url).path):
            raise ValueError(
                "blocked path: harness endpoints are not part of the site")

    def _observe(self, response):
        self.current_url = response.url
        self.last_html = response.text
        soup = BeautifulSoup(response.text, "html.parser")
        self._soup = soup
        for tag in soup(["script", "style"]):
            tag.decompose()
        title = soup.title.get_text(strip=True) if soup.title else ""
        text = " ".join(soup.get_text(" ", strip=True).split())
        links = []
        for i, a in enumerate(soup.find_all("a", href=True)):
            links.append((i, a.get_text(" ", strip=True) or a["href"], a["href"]))
        forms = []
        for i, f in enumerate(soup.find_all("form")):
            action = f.get("action") or self.current_url
            method = (f.get("method") or "get").lower()
            fields = []
            for inp in f.find_all(["input", "textarea", "select"]):
                name = inp.get("name")
                if not name or inp.get("type") == "hidden":
                    continue
                if inp.name == "textarea":
                    val = inp.get_text(strip=True)
                elif inp.name == "select":
                    opt = inp.find("option", selected=True) \
                        or inp.find("option")
                    val = (opt.get("value") or
                           opt.get_text(strip=True)) if opt else ""
                else:
                    val = inp.get("value", "")
                kind = (inp.get("type") or "").lower()
                if kind in ("checkbox", "radio"):
                    state = "checked" if inp.has_attr("checked") else "unchecked"
                    fields.append(f"{name}='{val or 'on'}' ({kind}, {state})")
                    continue
                fields.append(f"{name}='{val}'" if val else name)
            groups = {}
            for btn in f.find_all("button", attrs={"name": True}):
                groups.setdefault(btn["name"], []).append(
                    (btn.get("value", ""), btn.get_text(" ", strip=True)))
            for bname, opts in groups.items():
                if len(opts) == 1:
                    fields.append(f"{bname}='{opts[0][0]}'")
                    continue
                labels = {lbl for _, lbl in opts}
                shown = " | ".join(
                    f"'{v}'" if len(labels) <= 1 else f"'{v}' ({lbl[:24]})"
                    for v, lbl in opts[:40])
                more = f" … +{len(opts) - 40} more" if len(opts) > 40 else ""
                fields.append(f"{bname}=[{shown}{more}] "
                              "(submit buttons, page order)")
            labels = [b.get_text(" ", strip=True)
                      for b in f.find_all("button") if not b.get("name")]
            labels += [inp["value"] for inp in
                       f.find_all("input", attrs={"type": "submit"})
                       if inp.get("value") and not inp.get("name")]
            labels = [l for l in labels if l]
            if labels:
                fields.append("button=" + "/".join(
                    f"'{l[:30]}'" for l in labels[:3]))
            forms.append((i, action, method, fields))
        return Observation(self.current_url, title, text, links, forms)

    def goto(self, path):
        url = self._absolutize(path)
        self._guard(url)
        r = self.session.get(url, timeout=10)
        self._guard(r.url)
        return self._observe(r)

    def click(self, link_index):
        obs_links = self._soup.find_all("a", href=True) if self._soup else []
        if not (0 <= link_index < len(obs_links)):
            raise ValueError(f"No link with index {link_index}")
        return self.goto(obs_links[link_index]["href"])

    def submit_form(self, form_index, fields):
        soup_forms = self._soup.find_all("form") if self._soup else []
        if not (0 <= form_index < len(soup_forms)):
            raise ValueError(f"No form with index {form_index}")
        form = soup_forms[form_index]
        action = self._absolutize(form.get("action") or self.current_url)
        self._guard(action)
        method = (form.get("method") or "get").lower()

        data = {}
        for inp in form.find_all(["input", "textarea", "select"]):
            name = inp.get("name")
            if not name:
                continue
            if inp.name == "select":
                opt = inp.find("option", selected=True) or inp.find("option")
                data[name] = opt.get("value", opt.get_text(strip=True)) if opt else ""
            elif inp.name == "textarea":
                data[name] = inp.get_text()
            elif (inp.get("type") or "").lower() in ("checkbox", "radio"):
                if inp.has_attr("checked"):
                    data[name] = inp.get("value", "on")
            else:
                data[name] = inp.get("value", "")
        btn = form.find("button", attrs={"name": True})
        if btn is not None and btn["name"] not in data:
            data[btn["name"]] = btn.get("value", "")
        data.update(fields)

        if method == "post":
            r = self.session.post(action, data=data, timeout=10)
        else:
            r = self.session.get(action, params=data, timeout=10)
        self._guard(r.url)
        return self._observe(r)

    def step(self, action_str):
        action_str = action_str.strip()
        if action_str.startswith("goto "):
            return self.goto(action_str[5:].strip()), False, None
        if action_str.startswith("click "):
            return self.click(int(action_str[6:].strip())), False, None
        if action_str.startswith("fill "):
            rest = action_str[5:].strip()
            idx_str, _, kv = rest.partition(" ")
            fields = {}
            for pair in kv.split(";"):
                if "=" in pair:
                    k, _, v = pair.partition("=")
                    fields[k.strip()] = _unwrap(v.strip())
            return self.submit_form(int(idx_str), fields), False, None
        if action_str.startswith("stop"):
            answer = action_str[4:].strip()
            return None, True, answer
        raise ValueError(f"Unknown action: {action_str!r}")
