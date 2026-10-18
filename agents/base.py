import os

MAX_TOKENS = int(os.environ.get("MWA_MAX_TOKENS") or 4096)


class BaseAgent:

    def begin(self, task):
        pass

    def act(self, task, obs):
        raise NotImplementedError

    _pending_error = None

    def on_error(self, message):
        self._pending_error = message

    def prompt_for(self, task, obs):
        err, self._pending_error = self._pending_error, None
        head = (f"That action failed: {err}. Choose a different valid "
                f"action.\n\n" if err else "")
        return (head + f"TASK: {task['intent']}\n\n"
                f"OBSERVATION:\n{obs.render()}\n\n"
                "Your single action line:")


CREDENTIALS = {
    "ministore": "username=agent_smith password=password123",
    "reddit": "username=agent_smith password=password123",
    "gari": "email=ahmed.raza@garibazaar.test password=garibazaar2026",
    "portal": "citizen id 9999708182203 password=citizen1234",
    "rail": "username=priya_sharma password=travel123",
    "selam": "there is no account login; bookings are opened with the "
             "PNR + surname and loyalty pages with the member number + "
             "surname given in the task",
}


def credentials_line(task):
    site = task.get("site", "")
    return CREDENTIALS.get(site, "given in the task if needed")
