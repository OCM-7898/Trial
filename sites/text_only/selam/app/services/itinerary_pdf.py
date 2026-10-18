from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from ..i18n import t
from .boarding_pass import _ensure_font

GREEN = colors.HexColor("#0B5D51")
GOLD = colors.HexColor("#E8A33D")
MUTED = colors.HexColor("#6B7B78")
INK = colors.HexColor("#12211F")


@dataclass(frozen=True)
class ItineraryLeg:
    flight_no: str
    date_label: str
    origin: str
    destination: str
    dep_time: str
    arr_time: str
    cabin_label: str
    seat_labels: str


def render(destination: Path, *, pnr: str, passenger_names: list[str],
           legs: list[ItineraryLeg], total_label: str) -> Path:
    font = _ensure_font()
    destination.parent.mkdir(parents=True, exist_ok=True)

    width, height = A4
    pdf = canvas.Canvas(str(destination), pagesize=A4)

    pdf.setFillColor(GREEN)
    pdf.rect(0, height - 30 * mm, width, 30 * mm, stroke=0, fill=1)
    pdf.setFillColor(GOLD)
    pdf.circle(20 * mm, height - 15 * mm, 7 * mm, stroke=0, fill=1)
    pdf.setFillColor(colors.white)
    pdf.setFont(font, 16)
    pdf.drawString(32 * mm, height - 13 * mm, t("brand.airline"))
    pdf.setFont(font, 10)
    pdf.drawString(32 * mm, height - 20 * mm, t("itinerary.title"))

    def label_value(x, y, label, value, size=11):
        pdf.setFillColor(MUTED)
        pdf.setFont(font, 7.5)
        pdf.drawString(x, y + 5.5 * mm, label.upper())
        pdf.setFillColor(INK)
        pdf.setFont(font, size)
        pdf.drawString(x, y, str(value))

    cursor = height - 48 * mm
    label_value(18 * mm, cursor, t("boarding.reference"), pnr, 14)
    label_value(70 * mm, cursor, t("itinerary.passengers"),
                ", ".join(passenger_names)[:70])
    label_value(18 * mm, cursor - 16 * mm, t("review.total_due"), total_label)

    cursor -= 34 * mm
    pdf.setFillColor(MUTED)
    pdf.setFont(font, 8)
    headings = ((18, t("boarding.flight")), (42, t("boarding.date")),
                (80, t("boarding.from")), (108, t("boarding.to")),
                (136, t("boarding.departs")), (158, t("itinerary.arrives")),
                (178, t("boarding.seat")))
    for x, heading in headings:
        pdf.drawString(x * mm, cursor, heading.upper()[:12])
    cursor -= 2 * mm
    pdf.setStrokeColor(GOLD)
    pdf.line(18 * mm, cursor, width - 18 * mm, cursor)

    pdf.setFillColor(INK)
    for leg in legs:
        cursor -= 9 * mm
        pdf.setFont(font, 9)
        for x, value in ((18, leg.flight_no), (42, leg.date_label),
                         (80, leg.origin), (108, leg.destination),
                         (136, leg.dep_time), (158, leg.arr_time),
                         (178, leg.seat_labels or "--")):
            pdf.drawString(x * mm, cursor, str(value)[:16])
        cursor -= 4.5 * mm
        pdf.setFillColor(MUTED)
        pdf.setFont(font, 7.5)
        pdf.drawString(18 * mm, cursor, leg.cabin_label)
        pdf.setFillColor(INK)

    pdf.setFillColor(MUTED)
    pdf.setFont(font, 8)
    pdf.drawString(18 * mm, 18 * mm, t("itinerary.not_a_boarding_pass"))
    pdf.showPage()
    pdf.save()
    return destination
