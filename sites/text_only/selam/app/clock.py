from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Africa/Addis_Ababa")

FROZEN_TODAY = date(2026, 3, 16)
FROZEN_NOW = datetime(2026, 3, 16, 9, 0, 0, tzinfo=TZ)

assert FROZEN_TODAY.weekday() == 0, "FROZEN_TODAY must be a Monday (SPEC.md 7.1)"
assert FROZEN_NOW.date() == FROZEN_TODAY, "FROZEN_NOW and FROZEN_TODAY must agree"

WINDOW_DAYS_BACK = 90
WINDOW_DAYS_FORWARD = 90
WINDOW_START = FROZEN_TODAY - timedelta(days=WINDOW_DAYS_BACK)
WINDOW_END = FROZEN_TODAY + timedelta(days=WINDOW_DAYS_FORWARD)


def today() -> date:
    return FROZEN_TODAY


def now() -> datetime:
    return FROZEN_NOW


def is_past(when: date | datetime) -> bool:
    if isinstance(when, datetime):
        return _aware(when) < FROZEN_NOW
    return when < FROZEN_TODAY


def hours_until(when: datetime) -> float:
    return (_aware(when) - FROZEN_NOW).total_seconds() / 3600.0


def in_window(day: date) -> bool:
    return WINDOW_START <= day <= WINDOW_END


def _aware(when: datetime) -> datetime:
    return when if when.tzinfo else when.replace(tzinfo=TZ)
