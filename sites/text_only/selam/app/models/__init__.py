from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase

from ..lang import LANGS, active


class Base(DeclarativeBase):
    pass


def translated(field: str) -> property:

    def getter(self):
        column = f"{field}_{active()}"
        try:
            return getattr(self, column)
        except AttributeError:
            raise AttributeError(
                f"{type(self).__name__} has no {column!r}; seed.py must write "
                f"both {field}_en and {field}_am"
            ) from None

    getter.__name__ = field
    return property(getter)


def translated_column(model, field: str):
    column = getattr(model, f"{field}_{active()}", None)
    if column is None:
        raise AttributeError(
            f"{model.__name__} has no {field}_{active()}; seed.py must write both "
            f"halves and export.py must keep this build's")
    return column


def translated_kwargs(model, field: str, value) -> dict:
    columns = model.__table__.columns
    present = {f"{field}_{half}": value for half in LANGS
               if f"{field}_{half}" in columns}
    if not present:
        raise AttributeError(
            f"{model.__name__} has neither {field}_en nor {field}_am")
    return present


def set_translated(instance, field: str, value) -> None:
    for key, item in translated_kwargs(type(instance), field, value).items():
        setattr(instance, key, item)


from .network import (
    Aircraft, Airport, FareClass, Fare, Flight, Route, SeatMapSeat,
)
from .booking import (
    Booking, Passenger, SeatAssignment, Segment,
)
from .checkin import BoardingPass, Checkin
from .ancillary import (
    BaggagePurchase, BaggageRule, ChangeRequest, LoungePurchase, RefundRequest,
    UpgradePurchase,
)
from .loyalty import (
    AwardInventory, LoyaltyMember, MilesTransaction, MissingMilesClaim,
)
from .draft import DraftBooking, DraftPassenger
from .requests import ServiceRequest
from .partners import (
    CarBooking, CarOffer, HotelBooking, HotelRoom, InsuranceProduct,
    RailConnection, VisaType,
)
from .onboard import (
    MealMenu, MealRequest, SpecialMealCode, WifiPackage, WifiPurchase,
)
from .content import (
    ContactOffice, ContentPage, EntertainmentItem, Lounge, Promotion,
    SpecialBaggageItem, StopoverPackage, TravelRequirement,
)

__all__ = [
    "Base", "translated",
    "Airport", "Route", "Aircraft", "Flight", "FareClass", "Fare", "SeatMapSeat",
    "Booking", "Passenger", "Segment", "SeatAssignment",
    "Checkin", "BoardingPass",
    "ChangeRequest", "RefundRequest", "BaggagePurchase", "UpgradePurchase",
    "BaggageRule",
    "ContentPage", "SpecialBaggageItem", "ContactOffice", "Lounge",
    "StopoverPackage", "Promotion", "EntertainmentItem", "TravelRequirement",
    "LoungePurchase",
    "LoyaltyMember", "MilesTransaction", "AwardInventory", "MissingMilesClaim",
    "WifiPackage", "WifiPurchase", "SpecialMealCode", "MealMenu", "MealRequest",
    "DraftBooking", "DraftPassenger", "ServiceRequest",
    "HotelRoom", "HotelBooking", "VisaType", "RailConnection", "CarOffer",
    "CarBooking", "InsuranceProduct",
]
