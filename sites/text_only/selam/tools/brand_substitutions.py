import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app.brand import BRANDS

TASK_TEXT_SUBSTITUTIONS = {
    "en": {
        "Ethiopian Airlines":                        BRANDS["airline"]["en"],
        "ShebaMiles":                                BRANDS["loyalty"]["en"],
        "Cloud Nine":                                BRANDS["cabin_business"]["en"],
        "Ethiopian Skylight In-Terminal Hotel":      BRANDS["hotel"]["en"],
        "Ethiopian e-VISA":                          BRANDS["evisa"]["en"],
        "Rail & Fly":                                BRANDS["rail"]["en"],
    },
    "am": {
        "የኢትዮጵያ አየር መንገድ":                            BRANDS["airline"]["am"],
        "ኢትዮጵያ አየር መንገድ":                             BRANDS["airline"]["am"],
        "የሸባማይልስ":                                    BRANDS["loyalty"]["am"],
        "ሸባማይልስ":                                     BRANDS["loyalty"]["am"],
        "ክላውድ ናይን":                                   BRANDS["cabin_business"]["am"],
        "በኢትዮጵያን ስካይላይት የተርሚናል ውስጥ ሆቴል":              BRANDS["hotel"]["am"],
        "የኢትዮጵያ ኢ-ቪዛ":                                BRANDS["evisa"]["am"],
    },
}


