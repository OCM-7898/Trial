import base64
import mimetypes
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_task_photo(task):
    rel = task.get("image")
    if not rel:
        return None
    path = os.path.join(REPO, rel)
    with open(path, "rb") as f:
        data = f.read()
    return data, (mimetypes.guess_type(path)[0] or "image/jpeg")


def data_uri(data, mime):
    return f"data:{mime};base64," + base64.b64encode(data).decode()
