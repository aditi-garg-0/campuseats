"""
Stand-in for Order Service, exposing just enough of its existing
listOrdersForOutlet contract (Assignment 2, Task 3, Section 2.1) for
Catalogue Service's outbound call (order_client.py) to have something real
to talk to. Not part of the Catalogue Service submission itself — it plays
the role Order Service will play for real once it exists as its own
Tutorial 4 style implementation.

Run alongside app.py:
    python3 stub_order_service.py            # listens on :5001
    ORDER_SERVICE_URL=http://localhost:5001 python3 app.py   # listens on :5000
"""

from flask import Flask, request, jsonify

stub = Flask(__name__)

# A couple of canned "placed" orders for outlet 1, so the warning has
# something non-trivial to report during the curl demo.
_FAKE_ORDERS = {
    1: [
        {"order_id": 501, "status": "placed"},
        {"order_id": 502, "status": "placed"},
    ]
}


@stub.get("/outlets/<int:outlet_id>/orders")
def list_orders_for_outlet(outlet_id: int):
    status = request.args.get("status")
    orders = _FAKE_ORDERS.get(outlet_id, [])
    if status:
        orders = [o for o in orders if o["status"] == status]
    return jsonify({"orders": orders}), 200


if __name__ == "__main__":
    stub.run(port=5001, debug=False)
