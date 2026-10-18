import os
from urllib.parse import unquote

TOKEN_HEADER = "X-Harness-Token"


def token():
    return os.environ.get("MWA_HARNESS_TOKEN", "mwa-harness-2026")


def headers():
    return {TOKEN_HEADER: token()}


def is_harness_path(path):
    for _ in range(3):
        decoded = unquote(path)
        if decoded == path:
            break
        path = decoded
    return any(s.startswith("__") for s in path.split("/") if s)


def protect(app, endpoint_prefixes=("harness.",)):
    from flask import abort, request

    @app.before_request
    def _harness_gate():
        ep = request.endpoint or ""
        if is_harness_path(request.path) or ep.startswith(endpoint_prefixes):
            if request.headers.get(TOKEN_HEADER) != token():
                abort(404)
    from .popup_site import maybe_install
    maybe_install(app)
    return app
