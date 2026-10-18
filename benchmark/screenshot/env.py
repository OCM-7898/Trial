from dataclasses import dataclass

from ..env import BrowserEnv, Observation
from .render import screenshot


@dataclass
class ScreenshotObservation(Observation):
    screenshot: bytes = b""

    def render(self, max_chars=4000):
        note = ("SCREENSHOT: attached (yellow [N] = link N -> click N; green [fill N] = form N -> fill N)"
                if self.screenshot else "SCREENSHOT: (not available for this page)")
        return super().render(max_chars) + "\n" + note


class ScreenshotBrowserEnv(BrowserEnv):
    render_failures = 0

    def _observe(self, response):
        base = super()._observe(response)
        try:
            png = screenshot(self.last_html, self.current_url)
        except Exception as e:
            ScreenshotBrowserEnv.render_failures += 1
            print(f"    [screenshot failed: {str(e)[:160]}]", flush=True)
            png = b""
        obs = ScreenshotObservation(base.url, base.title, base.text, base.links, base.forms,
                                    screenshot=png)
        self._last_obs = obs
        return obs

    def step(self, action_str):
        a = action_str.strip()
        if a == "view" or a.startswith("view "):
            return self._last_obs, False, None
        return super().step(action_str)
