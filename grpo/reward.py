import json
import os
import re
import sys
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agents.local_agent import parse_action
from benchmark.env import _unwrap
from benchmark.evaluator import _norm, evaluate

_FIELD = re.compile(r"^([^=\s']+)='(.*)'$", re.S)


def _addr(url):
    u = urlsplit(url.strip())
    path = unquote(u.path).rstrip("/") or "/"
    q = sorted(parse_qsl(u.query, keep_blank_values=True))
    return path + ("?" + urlencode(q) if q else "")


def _target(action, links):
    if action.startswith("goto "):
        return _addr(action[5:])
    if action.startswith("click "):
        href = links.get(action[6:].strip())
        return _addr(href) if href else None
    return None


def _fill(action, forms):
    rest = action[5:].strip()
    idx, _, kv = rest.partition(" ")
    if idx not in forms:
        return None
    current = {}
    for f in forms[idx]:
        m = _FIELD.match(f)
        if m:
            current[m.group(1)] = _norm(m.group(2))
    fields = {}
    for pair in kv.split(";"):
        if "=" in pair:
            k, _, v = pair.partition("=")
            k, v = k.strip(), _norm(_unwrap(v.strip()))
            if current.get(k) != v:
                fields[k] = v
    return idx, fields


def score_action(action, ref, links, forms, answer_checks):
    action, ref = action.strip(), ref.strip()
    if ref.startswith("stop"):
        if not action.startswith("stop"):
            return 0.0
        if not answer_checks:
            return 1.0
        ok, _ = evaluate({"eval": answer_checks}, "", action[4:].strip())
        return 1.0 if ok else 0.0
    if ref.startswith(("goto ", "click ")):
        want = _target(ref, links)
        got = _target(action, links)
        return 1.0 if want is not None and got == want else 0.0
    if ref.startswith("fill "):
        if not action.startswith("fill "):
            return 0.0
        want, got = _fill(ref, forms), _fill(action, forms)
        return 1.0 if want is not None and got == want else 0.0
    return 0.0


def compute_score(data_source, solution_str, ground_truth, extra_info=None):
    gt = json.loads(ground_truth)
    action, _ = parse_action(solution_str or "")
    if not action:
        return 0.0
    return score_action(action, gt["reference"], gt["links"], gt["forms"],
                        gt.get("answer_checks") or [])
