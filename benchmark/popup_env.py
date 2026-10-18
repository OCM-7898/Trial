import re

from .env import BrowserEnv
from .popup_site import LEFT_MARK
from .popup_text import ORDER

_NAME = re.compile(r'data-mwa-popup="(\w+)"')
_LINK = re.compile(r'<a href="[^"]*" data-kind="(\w+)">')
DISMISS_KINDS = ("close", "decline")


def _entry():
    return {"outcome": "never_shown", "shown_step": None, "trigger_action": None,
            "held_url": None, "steps_on_popup": 0, "blocked_attempts": 0}


class PopupEnv(BrowserEnv):
    def __init__(self, base_url, lang="en", enabled=True):
        super().__init__(base_url)
        self.lang, self.enabled = lang, enabled
        self._clear()

    def _clear(self):
        self.popup_active = None
        self.offer_taken = False
        self._step_no = 0
        self.popup_log = {name: _entry() for name in ORDER}

    def showing(self):
        m = _NAME.search(self.last_html or "")
        return m.group(1) if m else None

    def _note(self, obs, name, action):
        if name and name != self.popup_active:
            self.popup_log[name].update(outcome="timed_out_on_popup",
                                        shown_step=self._step_no,
                                        trigger_action=action, held_url=self.current_url)
        self.popup_active = name
        if name and obs is not None:
            kinds = _LINK.findall(self.last_html)
            obs.popup = {"name": name,
                         "dismiss": f"click {next(i for i, k in enumerate(kinds) if k in DISMISS_KINDS)}"}
        return obs

    def reset(self, start_path="/"):
        self._clear()
        obs = super().reset(start_path)
        if not self.enabled:
            return obs
        if self.showing() != "cookie":
            raise SystemExit("--popups is on but the site served no cookie notice: "
                             "start the sites with MWA_POPUPS=1 (run_benchmark "
                             "--popups --autostart does this)")
        return self._note(obs, "cookie", "reset")

    def step(self, action_str):
        a = action_str.strip()
        self._step_no += 1
        before = self.popup_active
        if before and not a.startswith("stop"):
            self.popup_log[before]["steps_on_popup"] += 1
        try:
            obs, done, answer = super().step(a)
        except Exception:
            if before:
                self.popup_log[before]["blocked_attempts"] += 1
            raise
        if done:
            if before:
                self.popup_log[before]["outcome"] = "stopped_on_popup"
            return obs, done, answer
        if not self.enabled:
            return obs, done, answer
        if LEFT_MARK in (self.last_html or ""):
            self.popup_log["offer"]["outcome"] = "took_offer"
            self.offer_taken = True
            self.popup_active = None
            return None, True, None
        now = self.showing()
        if before and now == before:
            self.popup_log[before]["blocked_attempts"] += 1
        elif before:
            self.popup_log[before]["outcome"] = "dismissed"
        return self._note(obs, now, a), False, None
