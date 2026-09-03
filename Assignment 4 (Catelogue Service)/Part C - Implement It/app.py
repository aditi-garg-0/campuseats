"""
CampusEats Catalogue Service — REST implementation for Assignment 4.

Rebuilds the Catalogue Service (Outlet, Menu Item — Assignment 2's cleanest,
fully self-contained service) as REST, matching the resource table in
NOTES.md Part A4 and the contract in openapi.yaml.
"""

import os
import sys

from flask import Flask, request, jsonify

from models import Outlet, MenuItem, now_iso
from store import store
from errors import (
    DomainError,
    NotFound,
    Conflict,
    error_response,
    validate_outlet_create,
    validate_menu_item_create,
    validate_availability_update,
)

# order_client.py lives in the sibling "Part D - Survive the Network" folder
# (this project is organised by assignment part, not by Python package), so
# it isn't found by a plain `import` unless its folder is added to sys.path
# first. Resolved relative to this file's own location, so it works no
# matter which directory you launch app.py or pytest from.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PART_D_DIR = os.path.join(_THIS_DIR, "..", "Part D - Survive the Network")
sys.path.insert(0, _PART_D_DIR)

from order_client import get_active_order_warning  # noqa: E402

app = Flask(__name__)


@app.errorhandler(DomainError)
def handle_domain_error(exc: DomainError):
    body, status = error_response(exc)
    return jsonify(body), status


# ---------------------------------------------------------------- /outlets

@app.post("/outlets")
def create_outlet():
    body = request.get_json(silent=True)
    fields = validate_outlet_create(body)

    outlet_id = store.next_outlet_id()
    outlet = Outlet(
        outlet_id=outlet_id,
        name=fields["name"],
        address=fields["address"],
        phone=fields["phone"],
        is_active=True,
        created_at=now_iso(),
    )
    store.outlets[outlet_id] = outlet

    response = jsonify(outlet.as_json())
    response.status_code = 201
    response.headers["Location"] = f"/outlets/{outlet_id}"
    return response


@app.get("/outlets/<int:outlet_id>")
def get_outlet(outlet_id: int):
    outlet = store.get_outlet(outlet_id)
    if outlet is None:
        raise NotFound(f"No outlet with id {outlet_id}.")
    return jsonify(outlet.as_json()), 200


# ------------------------------------------------- /outlets/{id}/menu-items

@app.post("/outlets/<int:outlet_id>/menu-items")
def add_menu_item(outlet_id: int):
    outlet = store.get_outlet(outlet_id)
    if outlet is None:
        raise NotFound(f"No outlet with id {outlet_id}.")

    idempotency_key = request.headers.get("Idempotency-Key")
    if idempotency_key:
        cached = store.get_idempotent_result(idempotency_key)
        if cached is not None:
            response = jsonify(cached["body"])
            response.status_code = cached["status_code"]
            response.headers["Location"] = cached["location"]
            return response

    body = request.get_json(silent=True)
    fields = validate_menu_item_create(body)

    menu_item_id = store.next_menu_item_id()
    item = MenuItem(
        menu_item_id=menu_item_id,
        outlet_id=outlet_id,
        name=fields["name"],
        description=fields["description"],
        price=fields["price"],
        is_available=True,
        created_at=now_iso(),
        idempotency_key=idempotency_key,
    )
    store.menu_items[menu_item_id] = item

    body_json = item.as_json()
    location = f"/menu-items/{menu_item_id}"

    if idempotency_key:
        store.save_idempotent_result(
            idempotency_key,
            {"status_code": 201, "body": body_json, "location": location},
        )

    response = jsonify(body_json)
    response.status_code = 201
    response.headers["Location"] = location
    return response


@app.get("/outlets/<int:outlet_id>/menu-items")
def get_outlet_menu(outlet_id: int):
    outlet = store.get_outlet(outlet_id)
    if outlet is None:
        raise NotFound(f"No outlet with id {outlet_id}.")

    items = store.menu_items_for_outlet(outlet_id)

    available_param = request.args.get("available")
    if available_param is not None:
        want_available = available_param.lower() == "true"
        items = [i for i in items if i.is_available == want_available]

    return jsonify([i.as_json() for i in items]), 200


# ------------------------------------------ /menu-items/{id}/availability

@app.patch("/menu-items/<int:menu_item_id>/availability")
def set_item_availability(menu_item_id: int):
    item = store.get_menu_item(menu_item_id)
    if item is None:
        raise NotFound(f"No menu item with id {menu_item_id}.")

    body = request.get_json(silent=True)
    fields = validate_availability_update(body)
    requested = fields["available"]

    if item.is_available == requested:
        raise Conflict(
            f"Menu item {menu_item_id} is already "
            f"{'available' if requested else 'unavailable'}."
        )

    item.is_available = requested

    warning = None
    if requested is False:
        # Best-effort only; see order_client.py and NOTES.md Part D3. This
        # call can never undo the write above or block this response.
        warning = get_active_order_warning(item.outlet_id)

    result = item.as_json()
    result["active_order_warning"] = warning
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)