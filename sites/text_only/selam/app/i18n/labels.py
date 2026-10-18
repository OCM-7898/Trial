from __future__ import annotations

from . import t


def checkin_label(code: str | None) -> str:
    if code is None:
        return t("checkin.open")
    return {
        "TOO_EARLY": t("checkin.code_too_early"),
        "CLOSED": t("checkin.code_closed"),
        "INFANT_ON_LAP": t("checkin.code_infant_on_lap"),
        "SPECIAL_ASSISTANCE_REQUIRED": t("checkin.code_special_assistance"),
        "UNACCOMPANIED_MINOR": t("checkin.code_unaccompanied_minor"),
        "DOCUMENT_CHECK_REQUIRED": t("checkin.code_document_check"),
        "CODESHARE_OPERATED_BY_PARTNER": t("checkin.code_codeshare"),
        "GROUP_BOOKING": t("checkin.code_group_booking"),
    }[code]


def flight_status_label(status: str) -> str:
    return {
        "scheduled": t("status.scheduled"),
        "delayed": t("status.delayed"),
        "cancelled": t("status.cancelled"),
        "departed": t("status.departed"),
    }[status]


def channel_label(channel: str) -> str:
    return {
        "website": t("manage.channel_website"),
        "agent": t("manage.channel_agent"),
        "call_centre": t("manage.channel_call_centre"),
        "corporate": t("manage.channel_corporate"),
    }[channel]


def pax_type_label(pax_type: str) -> str:
    return {
        "adult": t("pax.adult"),
        "child": t("pax.child"),
        "infant": t("pax.infant"),
    }[pax_type]


def refund_label(code: str | None) -> str:
    if code is None:
        return t("refund.eligible_hint")
    return {
        "FARE_NON_REFUNDABLE": t("refund.code_fare_non_refundable"),
        "OFFLINE_CHANNEL_ONLY": t("refund.code_offline_channel_only"),
    }[code]


def change_label(code: str | None) -> str:
    if code is None:
        return t("change.eligible")
    return {
        "FARE_NOT_CHANGEABLE": t("change.code_fare_not_changeable"),
        "TOO_LATE_TO_CHANGE": t("change.code_too_late"),
    }[code]


def upgrade_label(code: str | None) -> str:
    if code is None:
        return t("upgrade.offer_available")
    return {
        "FARE_CLASS_EXCLUDED": t("upgrade.code_fare_excluded"),
        "CABIN_FULL": t("upgrade.code_cabin_full"),
        "NO_BUSINESS_CABIN": t("upgrade.code_no_business_cabin"),
    }[code]


def region_label(region: str) -> str:
    return {
        "domestic": t("region.domestic"),
        "africa": t("region.africa"),
        "europe": t("region.europe"),
        "middle_east": t("region.middle_east"),
        "asia": t("region.asia"),
        "north_america": t("region.north_america"),
        "south_america": t("region.south_america"),
    }[region]


def content_category_label(category: str) -> str:
    return {
        "booking-help": t("category.booking_help"),
        "baggage": t("category.baggage"),
        "travel-info": t("category.travel_info"),
        "health": t("category.health"),
        "onboard": t("category.onboard"),
        "loyalty": t("category.loyalty"),
        "policies": t("category.policies"),
    }.get(category, category)


def lounge_access_label(reason: str) -> str:
    return {
        "cabin": t("lounge.free_by_cabin"),
        "tier": t("lounge.free_by_tier"),
        "paid": t("lounge.paid_entry"),
        "none": t("lounge.no_entry"),
    }[reason]


def stopover_category_label(category: str) -> str:
    return {
        "hotel": t("stopover.category_hotel"),
        "transfer": t("stopover.category_transfer"),
        "lounge": t("stopover.category_lounge"),
        "tour": t("stopover.category_tour"),
    }.get(category, category)


def special_baggage_category_label(category: str) -> str:
    return {
        "sport": t("special_bag.cat_sport"),
        "music": t("special_bag.cat_music"),
        "medical": t("special_bag.cat_medical"),
        "outsize": t("special_bag.cat_outsize"),
        "restricted": t("special_bag.cat_restricted"),
    }.get(category, category)


def seat_position_label(seat) -> str:
    parts = []
    if seat.is_window:
        parts.append(t("seats.window"))
    if seat.is_aisle:
        parts.append(t("seats.aisle"))
    if not parts:
        parts.append(t("seats.middle"))
    if seat.extra_legroom:
        parts.append(t("seats.extra_legroom"))
    return ", ".join(parts)
