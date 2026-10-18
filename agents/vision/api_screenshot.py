import time

from agents.base import MAX_TOKENS, credentials_line
from agents.gemini_agent import GeminiAgent
from agents.openai_agent import OpenAIAgent

from .common import data_uri, load_task_photo
from .screenshot_agent import SYSTEM


def _images(agent, obs):
    out = []
    if agent.task_photo is not None:
        out.append(("TASK PHOTO:", *agent.task_photo))
    if getattr(obs, "screenshot", b""):
        out.append(("SCREENSHOT:", obs.screenshot, "image/png"))
    return out


class GeminiScreenshotAgent(GeminiAgent):
    def begin(self, task):
        super().begin(task)
        self.system = SYSTEM.replace("{credentials}", credentials_line(task))
        self.task_photo = load_task_photo(task)

    def act(self, task, obs):
        prompt = self.prompt_for(task, obs)
        parts = [{"text": prompt}]
        for label, data, mime in _images(self, obs):
            parts += [{"text": label}, {"inline_data": {"mime_type": mime, "data": data}}]
        config = {"system_instruction": self.system, "max_output_tokens": MAX_TOKENS}
        if self.think_budget is not None:
            config["thinking_config"] = {"thinking_budget": self.think_budget}
        contents = self.history + [{"role": "user", "parts": parts}]
        text = ""
        for attempt in range(5):
            try:
                resp = self.client.models.generate_content(model=self.model, contents=contents, config=config)
            except Exception as e:
                wait = 2 ** attempt * 5
                print(f"    [gemini API error, retry in {wait}s: {str(e)[:120]}]", flush=True)
                time.sleep(wait)
                continue
            u = getattr(resp, "usage_metadata", None)
            if u is not None:
                self.usage["calls"] += 1
                self.usage["in"] += u.prompt_token_count or 0
                self.usage["out"] += u.candidates_token_count or 0
                self.usage["think"] += getattr(u, "thoughts_token_count", 0) or 0
            lines = (resp.text or "").strip().splitlines()
            if lines:
                text = lines[0]
                break
        text = text or "stop"
        self.history = (self.history + [{"role": "user", "parts": [{"text": prompt}]},
                                        {"role": "model", "parts": [{"text": text}]}])[-8:]
        return text


class OpenAIScreenshotAgent(OpenAIAgent):
    def begin(self, task):
        super().begin(task)
        self.system = SYSTEM.replace("{credentials}", credentials_line(task))
        self.task_photo = load_task_photo(task)

    def act(self, task, obs):
        prompt = self.prompt_for(task, obs)
        content = [{"type": "text", "text": prompt}]
        for label, data, mime in _images(self, obs):
            content += [{"type": "text", "text": label},
                        {"type": "image_url", "image_url": {"url": data_uri(data, mime)}}]
        messages = [{"role": "system", "content": self.system}] + self.history + \
            [{"role": "user", "content": content}]
        kwargs = dict(model=self.model, messages=messages)
        if self.effort:
            kwargs["reasoning_effort"] = self.effort
            kwargs["max_completion_tokens"] = MAX_TOKENS
        else:
            kwargs["max_tokens"] = MAX_TOKENS
        resp = None
        for attempt in range(5):
            try:
                resp = self.client.chat.completions.create(**kwargs)
                break
            except Exception as e:
                if "max_tokens" in str(e) and "max_tokens" in kwargs:
                    kwargs["max_completion_tokens"] = kwargs.pop("max_tokens")
                    continue
                wait = 2 ** attempt * 5
                print(f"    [openai API error, retry in {wait}s: {str(e)[:120]}]", flush=True)
                time.sleep(wait)
        text = "stop"
        if resp is not None:
            u = getattr(resp, "usage", None)
            if u is not None:
                self.usage["calls"] += 1
                self.usage["in"] += u.prompt_tokens or 0
                self.usage["out"] += u.completion_tokens or 0
                det = getattr(u, "completion_tokens_details", None)
                self.usage["think"] += getattr(det, "reasoning_tokens", 0) or 0
            lines = (resp.choices[0].message.content or "").strip().splitlines()
            text = lines[0] if lines else "stop"
        self.history = (self.history + [{"role": "user", "content": prompt},
                                        {"role": "assistant", "content": text}])[-8:]
        return text
