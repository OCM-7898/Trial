import os

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


class GeminiAgent(BaseAgent):
    def __init__(self, model="gemini-3.1-flash-lite"):
        try:
            from google import genai
        except ImportError as e:
            raise SystemExit("pip install google-genai to use the Gemini agent") from e
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise SystemExit("set GEMINI_API_KEY (or GOOGLE_API_KEY) to use the Gemini agent")
        self.client = genai.Client(api_key=api_key)
        self.model = os.environ.get("MWA_GEMINI_MODEL", model)
        tb = os.environ.get("MWA_THINK_BUDGET")
        self.think_budget = int(tb) if tb is not None else None
        self.usage = {"calls": 0, "in": 0, "out": 0, "think": 0}
        self.history = []

    def begin(self, task):
        self.system = SYSTEM.replace("{credentials}", credentials_line(task))
        self.history = []
        self._pending_error = None

    def _complete(self, prompt):
        import time
        contents = self.history + [{"role": "user", "parts": [{"text": prompt}]}]
        config = {"system_instruction": self.system,
                  "max_output_tokens": MAX_TOKENS}
        if self.think_budget is not None:
            config["thinking_config"] = {
                "thinking_budget": self.think_budget}
        text = ""
        for attempt in range(5):
            try:
                resp = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )
            except Exception as e:
                wait = 2 ** attempt * 5
                print(f"    [gemini API error, retry in {wait}s: "
                      f"{str(e)[:120]}]", flush=True)
                time.sleep(wait)
                continue
            u = getattr(resp, "usage_metadata", None)
            if u is not None:
                self.usage["calls"] += 1
                self.usage["in"] += u.prompt_token_count or 0
                self.usage["out"] += u.candidates_token_count or 0
                self.usage["think"] += getattr(
                    u, "thoughts_token_count", 0) or 0
            lines = (resp.text or "").strip().splitlines()
            if lines:
                text = lines[0]
                break
        if not text:
            text = "stop"
        self.history += [{"role": "user", "parts": [{"text": prompt}]},
                         {"role": "model", "parts": [{"text": text}]}]
        self.history = self.history[-8:]
        return text

    def act(self, task, obs):
        return self._complete(self.prompt_for(task, obs))
