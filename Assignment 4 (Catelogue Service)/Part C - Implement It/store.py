"""
In-process storage for the Catalogue Service.

No other service may import this module (Task 6 of Assignment 2 already
established Catalogue Service as self-contained; this file is what keeps
that true in code — Order Service, or anything else, reaches this data only
through app.py's HTTP contract, never by importing Store directly).
"""

from threading import Lock
from typing import Dict, Optional

from models import Outlet, MenuItem


class Store:
    def __init__(self) -> None:
        self._lock = Lock()
        self.outlets: Dict[int, Outlet] = {}
        self.menu_items: Dict[int, MenuItem] = {}
        self._next_outlet_id = 1
        self._next_menu_item_id = 1
        # Idempotency-Key -> the (status_code, body, location) already
        # returned for that key, so a repeated create returns the original
        # result instead of doing the work again.
        self.idempotency: Dict[str, dict] = {}

    def next_outlet_id(self) -> int:
        with self._lock:
            oid = self._next_outlet_id
            self._next_outlet_id += 1
            return oid

    def next_menu_item_id(self) -> int:
        with self._lock:
            mid = self._next_menu_item_id
            self._next_menu_item_id += 1
            return mid

    def get_outlet(self, outlet_id: int) -> Optional[Outlet]:
        return self.outlets.get(outlet_id)

    def get_menu_item(self, menu_item_id: int) -> Optional[MenuItem]:
        return self.menu_items.get(menu_item_id)

    def menu_items_for_outlet(self, outlet_id: int):
        return [m for m in self.menu_items.values() if m.outlet_id == outlet_id]

    def get_idempotent_result(self, key: str) -> Optional[dict]:
        return self.idempotency.get(key)

    def save_idempotent_result(self, key: str, result: dict) -> None:
        self.idempotency[key] = result


# Module-level singleton, mirroring the Tutorial 4 shape (a single in-process
# store the app module wires up on startup).
store = Store()
