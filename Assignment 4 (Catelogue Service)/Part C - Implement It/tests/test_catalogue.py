import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app as flask_app  # noqa: E402
from store import store  # noqa: E402


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    # Fresh store per test so tests don't leak state into each other.
    store.outlets.clear()
    store.menu_items.clear()
    store.idempotency.clear()
    store._next_outlet_id = 1
    store._next_menu_item_id = 1
    with flask_app.test_client() as c:
        yield c


def _make_outlet(client, name="Tandoori Corner", address="Block C, Ground Floor"):
    resp = client.post("/outlets", json={"name": name, "address": address})
    assert resp.status_code == 201
    return resp.get_json()["outlet_id"]


def test_create_succeeds_with_right_code_and_location_header(client):
    resp = client.post(
        "/outlets/{}/menu-items".format(_make_outlet(client)),
        json={"name": "Paneer Roll", "price": 90},
        headers={"Idempotency-Key": "test-key-1"},
    )
    assert resp.status_code == 201
    assert resp.headers["Location"] == "/menu-items/1"
    body = resp.get_json()
    assert body["name"] == "Paneer Roll"
    assert body["price"] == 90
    assert body["is_available"] is True
    # internal-only fields must never leak into the representation
    assert "created_by_staff" not in body
    assert "idempotency_key" not in body


def test_idempotent_repeat_returns_original_result(client):
    outlet_id = _make_outlet(client)
    payload = {"name": "Paneer Roll", "price": 90}
    headers = {"Idempotency-Key": "same-key"}

    first = client.post(f"/outlets/{outlet_id}/menu-items", json=payload, headers=headers)
    # Change the payload on the retry to prove the ORIGINAL result is
    # returned, not a re-run against the new body.
    second = client.post(
        f"/outlets/{outlet_id}/menu-items",
        json={"name": "Different Item", "price": 999},
        headers=headers,
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.get_json() == second.get_json()
    assert second.get_json()["name"] == "Paneer Roll"
    # No second item was actually created.
    assert len(store.menu_items) == 1


def test_malformed_body_returns_422(client):
    outlet_id = _make_outlet(client)
    resp = client.post(
        f"/outlets/{outlet_id}/menu-items",
        json={"name": "Free Water", "price": -5},
    )
    assert resp.status_code == 422
    body = resp.get_json()
    assert body["status"] == 422
    assert body["code"] == "validation_failed"
    assert "type" in body and "title" in body and "detail" in body


def test_unknown_id_returns_404(client):
    resp = client.get("/outlets/999")
    assert resp.status_code == 404
    body = resp.get_json()
    assert body["status"] == 404
    assert body["code"] == "not_found"


def test_state_conflict_returns_409(client):
    outlet_id = _make_outlet(client)
    item_resp = client.post(
        f"/outlets/{outlet_id}/menu-items", json={"name": "Cold Coffee", "price": 60}
    )
    item_id = item_resp.get_json()["menu_item_id"]

    # Item starts available; setting it to available again is a conflict.
    resp = client.patch(f"/menu-items/{item_id}/availability", json={"available": True})
    assert resp.status_code == 409
    assert resp.get_json()["code"] == "conflict"


def test_filtered_list_by_query_string(client):
    outlet_id = _make_outlet(client)
    client.post(f"/outlets/{outlet_id}/menu-items", json={"name": "Item A", "price": 10})
    b = client.post(f"/outlets/{outlet_id}/menu-items", json={"name": "Item B", "price": 20})
    item_b_id = b.get_json()["menu_item_id"]

    with patch("app.get_active_order_warning", return_value={"checked": False, "active_order_count": None, "note": "stubbed"}):
        client.patch(f"/menu-items/{item_b_id}/availability", json={"available": False})

    resp = client.get(f"/outlets/{outlet_id}/menu-items?available=true")
    names = [i["name"] for i in resp.get_json()]
    assert names == ["Item A"]


def test_availability_change_degrades_when_order_service_unreachable(client):
    """Part D3: Order Service being down must not block the write."""
    outlet_id = _make_outlet(client)
    item_resp = client.post(
        f"/outlets/{outlet_id}/menu-items", json={"name": "Samosa", "price": 25}
    )
    item_id = item_resp.get_json()["menu_item_id"]

    with patch(
        "app.get_active_order_warning",
        return_value={"checked": False, "active_order_count": None, "note": "Order Service unavailable, warning skipped."},
    ):
        resp = client.patch(f"/menu-items/{item_id}/availability", json={"available": False})

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["is_available"] is False
    assert body["active_order_warning"]["checked"] is False
