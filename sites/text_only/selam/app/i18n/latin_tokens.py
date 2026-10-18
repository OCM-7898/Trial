GENERAL = {"SM", "USD", "PNR", "IATA", "ICAO", "USB", "PDF", "Wi", "Fi"}

PARTNER_MARKS = {"ZT", "EV", "ER", "RD", "SV"}

SERVICE_CODES = {
    "WCHR", "WCHS", "WCHC", "WCHP", "WCBD", "WCBW",
    "MEDA", "DEAF", "BLND", "DPNA", "UMNR", "STCR", "OXYG",
}

MEAL_CODES = {
    "VGML", "VJML", "AVML", "GFML", "LFML", "LSML", "DBML",
    "HNML", "MOML", "KSML", "ORML", "CHML", "BBML", "FPML",
}

ALLOWED = GENERAL | PARTNER_MARKS | SERVICE_CODES | MEAL_CODES

IDENTIFIER_PATTERN = r"^[A-Za-z0-9-]*[0-9][A-Za-z0-9-]*$"

EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

URL_PATH_PATTERN = r"/[A-Za-z0-9._~:@+-]+(?:/[A-Za-z0-9._~:@+*<>-]*)+"
