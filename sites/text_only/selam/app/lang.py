from __future__ import annotations

from contextvars import ContextVar

LANGS = ("en", "am", "bn", "hi", "ur")

ACTIVE = "en"

_CURRENT: ContextVar[str | None] = ContextVar("selam_language", default=None)


def set_active(lang: str) -> None:
    global ACTIVE
    if lang not in LANGS:
        raise ValueError(f"unknown language {lang!r}")
    ACTIVE = lang


def bind(lang: str):
    if lang not in LANGS:
        raise ValueError(f"unknown language {lang!r}")
    return _CURRENT.set(lang)


def unbind(token) -> None:
    _CURRENT.reset(token)


def active() -> str:
    current = _CURRENT.get()
    if current is not None:
        return current
    app_language = _app_language()
    return app_language if app_language is not None else ACTIVE


def _app_language() -> str | None:
    try:
        from flask import current_app, has_app_context
    except ImportError:
        return None
    if not has_app_context():
        return None
    language = current_app.config.get("LANGUAGE")
    return language if language in LANGS else None


def col(field: str) -> str:
    return f"{field}_{active()}"
