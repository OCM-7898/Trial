import os
import re
import time

from .base import MAX_TOKENS, BaseAgent, credentials_line

SYSTEM = """You are a web agent completing tasks on simple websites.
You will be given a TASK and an OBSERVATION of the current page
(text, numbered links, numbered forms). Reply with EXACTLY ONE action:

goto <path>                       e.g. goto /login
click <link_index>                e.g. click 3
fill <form_index> <name>=<value>; <name>=<value>
                                  fills the form's fields then submits it
                                  (use the field names listed under FORMS,
                                  e.g. fill 1 username=alice; password=secret)
stop <answer>                     finish; include the answer if asked for one

Links and forms are numbered separately: "click N" follows LINK N.
To press a form's button, use "fill N" (with no fields for a
button-only form, e.g. fill 2 to press form 2 'Place order').

Credentials for this site if login is needed: {credentials}
Think silently; output only the single action line, nothing else."""

VERBS = ("goto", "click", "fill", "stop")
_THINK = re.compile(r"<think>.*?</think>", re.S | re.I)
_VERB = re.compile(r"^(goto|click|fill|stop)\b", re.I)
_LEAD = re.compile(r"^(?:[-*>•]\s+|\d+[.)]\s+|[`*]+)+")
_TRAIL = re.compile(r"[`*]+$")
_LABEL = re.compile(r"^[A-Za-z][A-Za-z ]{0,24}\s*[:\-]\s*")
_BRACKET = re.compile(r"^(click|fill)\s+\[(\d+)\]", re.I)
_CLICK = re.compile(r"^click\s+(\d+)\b")


def _first_line(text):
    lines = text.strip().splitlines()
    return lines[0].strip() if lines else ""


def _unquote(line):
    if len(line) >= 2 and line[0] == line[-1] and line[0] in "\"'":
        return line[1:-1].strip()
    return line


def _clean(line):
    line = _TRAIL.sub("", _LEAD.sub("", line.strip()))
    line = _unquote(line)
    if not _VERB.match(line):
        m = _LABEL.match(line)
        if m:
            line = _unquote(_TRAIL.sub("", _LEAD.sub("", line[m.end():])))
    if not _VERB.match(line):
        return None
    verb = _VERB.match(line).group(1).lower()
    line = verb + line[len(verb):]
    line = _BRACKET.sub(lambda m: f"{m.group(1).lower()} {m.group(2)}", line)
    if verb == "click":
        m = _CLICK.match(line)
        if m:
            line = f"click {m.group(1)}"
    return line.strip()


def parse_action(raw, strict=False):
    first = _first_line(raw)
    if strict:
        return (first or "stop"), False
    text = _THINK.sub("", raw)
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[1]
    for line in text.splitlines():
        act = _clean(line)
        if act:
            return act, act != first
    return (first or "stop"), False


class LocalAgent(BaseAgent):
    def __init__(self):
        try:
            import openai
        except ImportError as e:
            raise SystemExit("pip install openai to use the local agent") from e
        base = os.environ.get("MWA_LOCAL_BASE_URL", "http://127.0.0.1:8000/v1")
        self.client = openai.OpenAI(base_url=base, api_key="EMPTY",
                                    max_retries=0)
        self.model = os.environ.get("MWA_LOCAL_MODEL") or \
            self.client.models.list().data[0].id
        self.strict = os.environ.get("MWA_STRICT_PARSE") == "1"
        self.max_tokens = int(os.environ.get("MWA_LOCAL_MAX_TOKENS")
                              or MAX_TOKENS)
        self.effort = os.environ.get("MWA_REASONING_EFFORT") or None
        tb = os.environ.get("MWA_THINK_BUDGET")
        self.template_kwargs = None
        if tb is not None:
            tb = int(tb)
            self.template_kwargs = {"enable_thinking": tb > 0}
            if tb > 0:
                self.max_tokens = max(self.max_tokens, tb + 512)
        print(f"[local agent] model={self.model} base={base} "
              f"parser={'strict' if self.strict else 'forgiving'} "
              f"max_tokens={self.max_tokens} "
              f"reasoning_effort={self.effort} "
              f"template_kwargs={self.template_kwargs}", flush=True)
        self.usage = {"calls": 0, "in": 0, "out": 0, "think": 0,
                      "rescues": 0, "trims": 0, "empty": 0, "harmony": 0}
        self.history = []

    def begin(self, task):
        self.system = SYSTEM.replace("{credentials}", credentials_line(task))
        self.history = []
        self._pending_error = None

    def _create(self, messages):
        kwargs = dict(model=self.model, messages=messages,
                      max_tokens=self.max_tokens, temperature=0.0)
        if self.template_kwargs is not None:
            kwargs["extra_body"] = {
                "chat_template_kwargs": self.template_kwargs}
        if self.effort:
            kwargs["reasoning_effort"] = self.effort
        return self.client.chat.completions.create(**kwargs)

    def _call(self, hist, turns):
        import openai
        resp = None
        for attempt in range(6):
            messages = [{"role": "system", "content": self.system}] + \
                hist + turns
            try:
                resp = self._create(messages)
                break
            except openai.BadRequestError as e:
                if hist and ("context" in str(e).lower()
                             or "maximum" in str(e).lower()):
                    hist = hist[2:]
                    self.usage["trims"] += 1
                    continue
                print(f"    [local server rejected the call: "
                      f"{str(e)[:160]}]", flush=True)
                break
            except openai.InternalServerError as e:
                msg = str(e).lower()
                if ("unexpected token" in msg or "start token" in msg
                        or "harmony" in msg):
                    self.usage["harmony"] += 1
                    print(f"    [malformed reply (Harmony parse error) - "
                          f"treated as empty]", flush=True)
                    return self._EMPTY, hist
                wait = 2 ** attempt * 5
                print(f"    [local server error, retry in {wait}s: "
                      f"{str(e)[:120]}]", flush=True)
                time.sleep(wait)
            except (openai.APIConnectionError, openai.APITimeoutError) as e:
                wait = 2 ** attempt * 5
                print(f"    [local server error, retry in {wait}s: "
                      f"{str(e)[:120]}]", flush=True)
                time.sleep(wait)
        return resp, hist

    _EMPTY = object()

    def _read(self, resp):
        if resp is None or resp is self._EMPTY:
            return "", 0
        u = getattr(resp, "usage", None)
        if u is not None:
            self.usage["calls"] += 1
            self.usage["in"] += u.prompt_tokens or 0
            self.usage["out"] += u.completion_tokens or 0
            det = getattr(u, "completion_tokens_details", None)
            self.usage["think"] += getattr(det, "reasoning_tokens", 0) or 0
        msg = resp.choices[0].message
        reasoning = (getattr(msg, "reasoning_content", None)
                     or getattr(msg, "reasoning", None) or "")
        return msg.content or "", len(reasoning)

    def _complete(self, prompt):
        turn = [{"role": "user", "content": prompt}]
        resp, hist = self._call(list(self.history), turn)
        raw, n_reason = self._read(resp)
        if resp is not None and not raw.strip():
            self.usage["empty"] += 1
            print(f"    [empty reply (reasoning: {n_reason} chars) - "
                  f"asking once more]", flush=True)
            nudge = turn + [
                {"role": "assistant", "content": ""},
                {"role": "user", "content": "Your reply contained no "
                 "action. Reply with exactly one action line."}]
            resp2, hist = self._call(hist, nudge)
            raw, _ = self._read(resp2)
        text, rescued = parse_action(raw, strict=self.strict)
        if raw.strip() and not _VERB.match(text):
            print(f"    [no action line in reply: {raw.strip()[:200]!r}]",
                  flush=True)
        self.usage["rescues"] += rescued
        self.history = hist + [{"role": "user", "content": prompt},
                               {"role": "assistant", "content": text}]
        self.history = self.history[-8:]
        return text

    def act(self, task, obs):
        return self._complete(self.prompt_for(task, obs))
