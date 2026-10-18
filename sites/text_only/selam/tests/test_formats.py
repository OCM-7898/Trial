from datetime import date, datetime, time

import pytest

from app.i18n.formats import format_date, format_money, format_time, format_weekday


@pytest.mark.parametrize("value", [
    time(15, 10),
    time(15, 10, 0),
    datetime(2026, 3, 16, 15, 10),
    "15:10:00",
    "15:10",
])
def test_time_always_renders_as_hh_mm(value):
    assert format_time(value) == "15:10"


def test_date_formats_are_symmetric():
    day = date(2026, 3, 16)
    english, amharic = format_date(day, "en"), format_date(day, "am")
    assert english == "16 March 2026"
    assert amharic.startswith("16 ") and amharic.endswith(" 2026")
    assert english.split()[0] == amharic.split()[0]
    assert english.split()[-1] == amharic.split()[-1]


def test_weekday_names_differ_but_index_matches():
    day = date(2026, 3, 16)
    assert format_weekday(day, "en") == "Monday"
    assert format_weekday(day, "am") == "ሰኞ"


def test_money_is_identical_in_both_builds():
    assert format_money(412) == "USD 412"
    assert format_money(1234.5) == "USD 1,234.50"


def test_money_range_prints_the_currency_once():
    from app.i18n.formats import format_money_range

    assert format_money_range(10, 18) == "USD 10–18"
    assert format_money_range(18, 18) == "USD 18"
    assert format_money_range(10.5, 18) == "USD 10.50–18"
