from __future__ import annotations

import math

SQLITE_MAX_INT = 2 ** 63 - 1


def row_id(raw) -> int | None:
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    if not 0 < value <= SQLITE_MAX_INT:
        return None
    return value


def bounded_int(raw, *, low: int, high: int, default: int) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, value))


def bounded_float(raw, *, low: float, high: float, default: float = 0.0) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(value):
        return default
    return max(low, min(high, value))


def get_row(session, model, raw):
    identifier = row_id(raw)
    if identifier is None:
        return None
    return session.get(model, identifier)
