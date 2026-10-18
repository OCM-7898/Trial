from .base import BaseAgent


class ScriptedAgent(BaseAgent):
    def begin(self, task):
        self.script = list(task.get("solution", []))

    def act(self, task, obs):
        popup = getattr(obs, "popup", None)
        if popup:
            return popup["dismiss"]
        if self.script:
            return self.script.pop(0)
        return "stop"

    def on_error(self, message):
        print(f"    scripted agent action failed: {message}")
