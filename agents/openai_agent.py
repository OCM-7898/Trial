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


class OpenAIAgent(BaseAgent):
    def __init__(self, model="gpt-4o-mini"):
        try:
            import openai
        except ImportError as e:
            raise SystemExit("pip install openai to use the OpenAI agent") from e
        self.client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = os.environ.get("MWA_OPENAI_MODEL", model)
        self.effort = os.environ.get("MWA_REASONING_EFFORT")
        tb = os.environ.get("MWA_THINK_BUDGET")
        if self.effort is None and tb is not None:
            n = int(tb)
            self.effort = ("minimal" if n <= 0 else
                           "low" if n <= 1024 else
                           "medium" if n <= 4096 else "high")
            print(f"[openai agent] MWA_THINK_BUDGET={n} -> "
                  f"reasoning_effort={self.effort}")
        self.usage = {"calls": 0, "in": 0, "out": 0, "think": 0}
        self.history = []

    def begin(self, task):
        self.system = SYSTEM.replace("{credentials}", credentials_line(task))
        self.history = []
        self._pending_error = None

    def _complete(self, prompt):
        messages = [{"role": "system", "content": self.system}] + self.history + \
            [{"role": "user", "content": prompt}]
        kwargs = dict(model=self.model, messages=messages)
        if self.effort:
            kwargs["reasoning_effort"] = self.effort
            kwargs["max_completion_tokens"] = MAX_TOKENS
        else:
            kwargs["max_tokens"] = MAX_TOKENS
        try:
            resp = self.client.chat.completions.create(**kwargs)
        except Exception as e:
            if "max_tokens" in str(e) and "max_tokens" in kwargs:
                kwargs["max_completion_tokens"] = kwargs.pop("max_tokens")
                resp = self.client.chat.completions.create(**kwargs)
            else:
                raise
        u = getattr(resp, "usage", None)
        if u is not None:
            self.usage["calls"] += 1
            self.usage["in"] += u.prompt_tokens or 0
            self.usage["out"] += u.completion_tokens or 0
            det = getattr(u, "completion_tokens_details", None)
            self.usage["think"] += getattr(
                det, "reasoning_tokens", 0) or 0
        lines = (resp.choices[0].message.content or "").strip().splitlines()
        text = lines[0] if lines else "stop"
        self.history += [{"role": "user", "content": prompt},
                         {"role": "assistant", "content": text}]
        self.history = self.history[-8:]
        return text

    def act(self, task, obs):
        return self._complete(self.prompt_for(task, obs))
