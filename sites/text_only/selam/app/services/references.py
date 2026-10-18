from __future__ import annotations

import threading

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

WIDTH = 6

PREFIXES = {
    "change": "CH-", "refund": "RF-", "baggage": "BG-", "upgrade": "UP-",
    "lounge": "LG-", "wifi": "WF-", "hotel": "HT-", "car": "CR-", "missing_miles": "MC-", "feedback": "FB-", "baggage_report": "PIR-",
    "assistance": "AS-", "group": "GR-", "cargo": "CG-", "medical": "MD-",
    "compensation": "CP-", "voucher": "VC-", "corporate": "CO-", "nominee": "NM-", "upgrade_bid": "UB-", "status_alert": "AL-", "buy_miles": "BM-",
    "stopover": "SB-", "hold": "HD-",
}

START = 100_000


def next_reference(session: Session, kind: str, column) -> str:
    prefix = PREFIXES[kind]
    highest = session.scalar(
        select(func.max(func.substr(column, len(prefix) + 1)))
        .where(column.like(f"{prefix}%"))
    )
    nxt = (int(highest) + 1) if highest and str(highest).isdigit() else START + 1
    return f"{prefix}{nxt:0{WIDTH}d}"


def membership_number(session: Session, column) -> str:
    highest = session.scalar(select(func.max(func.substr(column, 3))).where(column.like("SM%")))
    nxt = (int(highest) + 1) if highest and str(highest).isdigit() else 1
    return f"SM{nxt:08d}"


def draft_reference(session: Session, column) -> str:
    highest = session.scalar(
        select(func.max(func.substr(column, 3))).where(column.like("DR%")))
    nxt = (int(highest) + 1) if highest and str(highest).isdigit() else 1
    return f"DR{nxt:04d}"


ALLOCATED_COLUMNS = ("reference_no", "member_no", "pnr")


def _is_allocation_collision(error) -> bool:
    detail = str(getattr(error, "orig", error))
    return "UNIQUE" in detail.upper() and any(
        column in detail for column in ALLOCATED_COLUMNS)


def _reallocate(session, instance) -> bool:
    changed = False
    for name in ALLOCATED_COLUMNS:
        current = getattr(instance, name, None)
        if not isinstance(current, str) or not current:
            continue
        column = getattr(type(instance), name, None)
        if column is None:
            continue
        prefix = current[:-WIDTH] if "-" in current else current[:2]
        highest = session.scalar(
            select(func.max(func.substr(column, len(prefix) + 1)))
            .where(column.like(f"{prefix}%")))
        width = len(current) - len(prefix)
        nxt = (int(highest) + 1) if highest and str(highest).isdigit() else 1
        setattr(instance, name, f"{prefix}{nxt:0{width}d}")
        changed = True
    return changed


class AllocatingSession(Session):

    MAX_ATTEMPTS = 8

    _allocation_lock = threading.Lock()

    def _has_allocated_identifier(self) -> bool:
        return any(
            isinstance(getattr(obj, name, None), str) and getattr(obj, name)
            for obj in self.new for name in ALLOCATED_COLUMNS)

    def commit(self):
        if not self._has_allocated_identifier():
            return super().commit()
        with self._allocation_lock:
            return self._commit_with_retry()

    def _commit_with_retry(self):
        pending = list(self.new)
        for attempt in range(self.MAX_ATTEMPTS):
            try:
                return super().commit()
            except IntegrityError as error:
                if not _is_allocation_collision(error) or attempt == self.MAX_ATTEMPTS - 1:
                    raise
                self.rollback()
                for instance in pending:
                    _reallocate(self, instance)
                    self.add(instance)
