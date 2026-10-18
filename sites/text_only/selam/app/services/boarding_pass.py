from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from ..i18n import t

FONT_NAME = "NotoSansEthiopic"
FONT_PATH = Path(__file__).resolve().parent.parent / "static" / "fonts" / "NotoSansEthiopic.ttf"

BOARDING_OFFSET_MIN = 40

_font_registered = False


def _ensure_font() -> str:
    global _font_registered
    if not _font_registered:
        if not FONT_PATH.exists():
            raise FileNotFoundError(
                f"{FONT_PATH} is missing; the Amharic boarding pass cannot render"
            )
        pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))
        _font_registered = True
    return FONT_NAME


def barcode_payload(pnr: str, segment_id: int, sequence_no: int) -> str:
    return f"{pnr}|{segment_id}|{sequence_no}"


def boarding_time(dep_time) -> str:
    base = datetime.combine(datetime(2000, 1, 1).date(), dep_time)
    return (base - timedelta(minutes=BOARDING_OFFSET_MIN)).strftime("%H:%M")


def render(
    destination: Path,
    *,
    pnr: str,
    passenger_name: str,
    flight_no: str,
    origin_iata: str,
    origin_city: str,
    destination_iata: str,
    destination_city: str,
    date_label: str,
    dep_time_label: str,
    boarding_label: str,
    gate: str,
    terminal: str,
    seat_no: str,
    cabin_label: str,
    sequence_no: int,
    payload: str,
) -> Path:
    font = _ensure_font()
    destination.parent.mkdir(parents=True, exist_ok=True)

    width, height = landscape(A5)
    pdf = canvas.Canvas(str(destination), pagesize=landscape(A5))
    green = colors.HexColor("#0B5D51")
    gold = colors.HexColor("#E8A33D")

    pdf.setFillColor(green)
    pdf.rect(0, height - 26 * mm, width, 26 * mm, stroke=0, fill=1)
    pdf.setFillColor(gold)
    pdf.circle(18 * mm, height - 13 * mm, 7 * mm, stroke=0, fill=1)
    pdf.setFillColor(green)
    for index, bar_width in enumerate((9, 7, 5)):
        pdf.rect(14 * mm, height - 15 * mm + index * 2.2 * mm,
                 bar_width * mm * 0.55, 1.2 * mm, stroke=0, fill=1)

    pdf.setFillColor(colors.white)
    pdf.setFont(font, 15)
    pdf.drawString(30 * mm, height - 12 * mm, t("brand.airline"))
    pdf.setFont(font, 9)
    pdf.drawString(30 * mm, height - 18 * mm, t("boarding.title"))

    def field(x, y, label, value, size=13):
        pdf.setFillColor(colors.HexColor("#6B7B78"))
        pdf.setFont(font, 7.5)
        pdf.drawString(x, y + 6 * mm, label.upper())
        pdf.setFillColor(colors.HexColor("#12211F"))
        pdf.setFont(font, size)
        pdf.drawString(x, y, str(value))

    top = height - 42 * mm
    field(14 * mm, top, t("boarding.passenger"), passenger_name)
    field(14 * mm, top - 18 * mm, t("boarding.from"), f"{origin_city} ({origin_iata})", 11)
    field(14 * mm, top - 33 * mm, t("boarding.to"), f"{destination_city} ({destination_iata})", 11)

    field(95 * mm, top, t("boarding.flight"), flight_no)
    field(95 * mm, top - 18 * mm, t("boarding.date"), date_label, 11)
    field(95 * mm, top - 33 * mm, t("boarding.departs"), dep_time_label)

    field(150 * mm, top, t("boarding.seat"), seat_no or "--")
    field(150 * mm, top - 18 * mm, t("boarding.gate"), gate or "--")
    field(150 * mm, top - 33 * mm, t("boarding.boarding_time"), boarding_label)

    field(180 * mm, top, t("boarding.terminal"), terminal or "--")
    field(180 * mm, top - 18 * mm, t("boarding.sequence"), f"{sequence_no:03d}")

    pdf.setFillColor(colors.HexColor("#12211F"))
    pdf.setFont(font, 9)
    pdf.drawString(14 * mm, 24 * mm, f"{t('boarding.reference')}: {pnr}")
    pdf.drawString(14 * mm, 19 * mm, f"{t('boarding.cabin')}: {cabin_label}")

    x = 14 * mm
    pdf.setFillColor(colors.black)
    for index, char in enumerate(payload):
        bar = 0.35 * mm if ord(char) % 2 else 0.7 * mm
        pdf.rect(x, 5 * mm, bar, 10 * mm, stroke=0, fill=1)
        x += bar + 0.45 * mm
    pdf.setFont(font, 7)
    pdf.setFillColor(colors.HexColor("#6B7B78"))
    pdf.drawString(x + 3 * mm, 9 * mm, payload)

    pdf.showPage()
    pdf.save()
    return destination
