from __future__ import annotations

import json
from pathlib import Path

from ..brand import BRANDS
from ..lang import LANGS, active, set_active as _set_active

_HERE = Path(__file__).parent

_catalogues: dict[str, dict[str, str]] = {}


class MissingTranslation(KeyError):
    pass


def load(lang: str) -> dict[str, str]:
    if lang not in LANGS:
        raise ValueError(f"unknown language {lang!r}")
    if lang not in _catalogues:
        catalogue = json.loads((_HERE / f"{lang}.json").read_text("utf-8"))
        for key, value in BRANDS.items():
            catalogue.setdefault(f"brand.{key}", value[lang])
        _catalogues[lang] = catalogue
    return _catalogues[lang]


def set_language(lang: str) -> None:
    load(lang)
    _set_active(lang)


def current_language() -> str:
    return active()


def t(key: str, **fmt: object) -> str:
    catalogue = load(active())
    try:
        value = catalogue[key]
    except KeyError:
        raise MissingTranslation(
            f"key {key!r} missing from {active()}.json -- add it rather than "
            f"letting another language leak into this build"
        ) from None
    return value.format(**fmt) if fmt else value


def all_keys() -> set[str]:
    return set().union(*(load(l).keys() for l in LANGS))
