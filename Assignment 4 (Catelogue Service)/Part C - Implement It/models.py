"""
Record classes for the Catalogue Service.

Each class holds the full stored record, including internal-only fields
that must never reach a client. as_json() is the one place that decides
what a caller is allowed to see — it is deliberately not just "the record,
serialised": it drops fields that are internal bookkeeping (see C2).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Outlet:
    outlet_id: int
    name: str
    address: str
    phone: Optional[str]
    is_active: bool
    created_at: str
    # Internal only: which admin session registered this outlet. Useful for
    # an internal audit trail; not part of the public Outlet representation
    # and must never be echoed back to a caller.
    registered_by: Optional[str] = None

    def as_json(self) -> dict:
        return {
            "outlet_id": self.outlet_id,
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }


@dataclass
class MenuItem:
    menu_item_id: int
    outlet_id: int
    name: str
    description: Optional[str]
    price: float
    is_available: bool
    created_at: str
    # Internal only: which staff session created the item, and the raw
    # idempotency key (if any) the create request arrived with. Neither is
    # part of the public MenuItem representation.
    created_by_staff: Optional[str] = None
    idempotency_key: Optional[str] = None

    def as_json(self) -> dict:
        return {
            "menu_item_id": self.menu_item_id,
            "outlet_id": self.outlet_id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "is_available": self.is_available,
            "created_at": self.created_at,
        }
