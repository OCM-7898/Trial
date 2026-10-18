from datetime import date, datetime, time

MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
    "am": ["ጃንዩወሪ", "ፌብሩወሪ", "ማርች", "ኤፕሪል", "ሜይ", "ጁን", "ጁላይ",
           "ኦገስት", "ሴፕቴምበር", "ኦክቶበር", "ኖቬምበር", "ዲሴምበር"],
    "bn": ["জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন", "জুলাই",
           "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"],
    "hi": ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई",
           "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"],
    "ur": ["جنوری", "فروری", "مارچ", "اپریل", "مئی", "جون", "جولائی",
           "اگست", "ستمبر", "اکتوبر", "نومبر", "دسمبر"],
}
WEEKDAYS = {
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "am": ["ሰኞ", "ማክሰኞ", "ረቡዕ", "ሐሙስ", "ዓርብ", "ቅዳሜ", "እሁድ"],
    "bn": ["সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার", "শনিবার", "রবিবার"],
    "hi": ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"],
    "ur": ["پیر", "منگل", "بدھ", "جمعرات", "جمعہ", "ہفتہ", "اتوار"],
}


def format_date(d: date, lang: str) -> str:
    return f"{d.day} {MONTHS[lang][d.month - 1]} {d.year}"


def format_weekday(d: date, lang: str) -> str:
    return WEEKDAYS[lang][d.weekday()]


def format_time(value: datetime | time | str) -> str:
    if isinstance(value, (datetime, time)):
        return value.strftime("%H:%M")
    return str(value)[:5]


def format_money_range(low: float, high: float, currency: str = "USD") -> str:
    if low == high:
        return format_money(low, currency)
    return f"{format_money(low, currency)}\u2013{_amount(high)}"


def _amount(value: float) -> str:
    return f"{value:,.0f}" if float(value).is_integer() else f"{value:,.2f}"


def format_money(amount: float, currency: str = "USD") -> str:
    return f"{currency} {_amount(amount)}"
