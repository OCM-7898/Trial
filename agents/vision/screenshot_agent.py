from agents.base import credentials_line
from agents.local_agent import SYSTEM as TEXT_SYSTEM
from agents.local_agent import _VERB, LocalAgent, parse_action

from .common import data_uri, load_task_photo

_ANCHOR = "Links and forms are numbered separately:"
assert _ANCHOR in TEXT_SYSTEM
SYSTEM = TEXT_SYSTEM.replace(_ANCHOR, (
    "Pictures: the TASK may come with a photo, shown first. Every step also comes with a\n"
    "SCREENSHOT of the whole page as a person sees it. In the screenshot, a yellow tag [N]\n"
    "marks link N (click N) and a green tag [fill N] marks form N (fill N) - the same\n"
    "numbers as under LINKS and FORMS.\n"
    "The page shows only part of the site; use the search box or the menus to find\n"
    "what the task names.\n\n" + _ANCHOR))


class ScreenshotAgent(LocalAgent):
    def begin(self, task):
        super().begin(task)
        self.system = SYSTEM.replace("{credentials}", credentials_line(task))
        self.task_photo = load_task_photo(task)

    def _parts(self, text, obs):
        parts = [{"type": "text", "text": text}]
        if self.task_photo is not None:
            parts.append({"type": "text", "text": "TASK PHOTO:"})
            parts.append({"type": "image_url", "image_url": {"url": data_uri(*self.task_photo)}})
        if getattr(obs, "screenshot", b""):
            parts.append({"type": "text", "text": "SCREENSHOT:"})
            parts.append({"type": "image_url", "image_url": {"url": data_uri(obs.screenshot, "image/png")}})
        return parts

    def act(self, task, obs):
        text = self.prompt_for(task, obs)
        turn = [{"role": "user", "content": self._parts(text, obs)}]
        resp, hist = self._call(list(self.history), turn)
        raw, n_reason = self._read(resp)
        if resp is not None and not raw.strip():
            self.usage["empty"] += 1
            print(f"    [empty reply (reasoning: {n_reason} chars) - asking once more]", flush=True)
            nudge = turn + [
                {"role": "assistant", "content": ""},
                {"role": "user", "content": "Your reply contained no action. Reply with exactly one action line."}]
            resp2, hist = self._call(hist, nudge)
            raw, _ = self._read(resp2)
        action, rescued = parse_action(raw, strict=self.strict)
        if raw.strip() and not _VERB.match(action or ""):
            print(f"    [no action line in reply: {raw.strip()[:200]!r}]", flush=True)
        self.usage["rescues"] += rescued
        self.history = (hist + [{"role": "user", "content": text},
                                {"role": "assistant", "content": action}])[-8:]
        return action
