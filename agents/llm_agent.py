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


class LLMAgent(BaseAgent):
    def __init__(self, model="claude-sonnet-4-5"):
        try:
            import anthropic
        except ImportError as e:
            raise SystemExit("pip install anthropic to use the LLM agent") from e
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = os.environ.get("MWA_ANTHROPIC_MODEL", model)
        tb = int(os.environ.get("MWA_THINK_BUDGET") or 0)
        self.think_budget = max(tb, 1024) if tb > 0 else None
        if 0 < tb < 1024:
            print(f"[llm agent] MWA_THINK_BUDGET={tb} clamped to the "
                  "API minimum 1024")
        self.usage = {"calls": 0, "in": 0, "out": 0, "think": 0}
        self.history = []

    def begin(self, task):
        self.system = SYSTEM.replace("{credentials}", credentials_line(task))
        self.history = []
        self._pending_error = None

    def _complete(self, prompt):
        kwargs = dict(
            model=self.model,
            max_tokens=MAX_TOKENS,
            system=self.system,
            messages=self.history + [{"role": "user", "content": prompt}],
        )
        if self.think_budget:
            kwargs["thinking"] = {"type": "enabled",
                                  "budget_tokens": self.think_budget}
            kwargs["max_tokens"] = max(MAX_TOKENS, self.think_budget + 500)
        msg = self.client.messages.create(**kwargs)
        u = getattr(msg, "usage", None)
        if u is not None:
            self.usage["calls"] += 1
            self.usage["in"] += u.input_tokens or 0
            self.usage["out"] += u.output_tokens or 0
        block = next((b for b in msg.content
                      if getattr(b, "type", "") == "text"), None)
        lines = (block.text if block else "").strip().splitlines()
        text = lines[0] if lines else "stop"
        self.history += [{"role": "user", "content": prompt},
                         {"role": "assistant", "content": text}]
        self.history = self.history[-8:]
        return text

    def act(self, task, obs):
        return self._complete(self.prompt_for(task, obs))
