"""
Outbound call from Catalogue Service to Order Service.

This call does not exist in the Assignment 2 design (Catalogue Service was
the one service that never called out — Task 6, Section 4.2). It is added
here purely to satisfy Part D of Assignment 4, and is deliberately kept
best-effort and non-blocking, in the same spirit as the non-blocking calls
Order Service itself makes to Review Service and Notification Service in
Task 4: it must never be able to stop setItemAvailability from doing its own
job, because that would compromise the independence Catalogue Service was
built to have.

Address is resolved from an environment variable, never hard-coded, per D1.
"""

import os
import random
import time

import requests

ORDER_SERVICE_URL_ENV = "ORDER_SERVICE_URL"
DEFAULT_TIMEOUT_SECONDS = 2.0
MAX_ATTEMPTS = 3
BASE_BACKOFF_SECONDS = 0.2


def _order_service_base_url() -> str:
    return os.environ.get(ORDER_SERVICE_URL_ENV, "http://localhost:5001")


def get_active_order_warning(outlet_id: int) -> dict:
    """
    Best-effort check: are there any currently-placed orders for this
    outlet? Calls Order Service's listOrdersForOutlet (an operation that
    already exists in its Task 3 contract — no redesign of Order Service is
    required), filtered to status=placed.

    This is a read-only, idempotent GET, so every attempt is safe to retry.
    A 4xx from Order Service (a client-side problem on our end) is not
    retried, since retrying an already-known-bad request only wastes time
    and would never itself change the response — only transient failures
    (timeouts, connection errors, 5xx) are retried. On exhausted retries,
    this degrades to an "unknown" result rather than raising, so the caller
    (app.py) never has to treat Order Service's availability as a
    precondition for its own write. See NOTES.md Part D3 for why degrading,
    not failing, is the correct choice here.
    """
    base_url = _order_service_base_url()
    url = f"{base_url}/outlets/{outlet_id}/orders"
    params = {"status": "placed"}

    last_error = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            last_error = str(exc)
        else:
            if response.status_code < 400:
                orders = response.json().get("orders", [])
                return {
                    "checked": True,
                    "active_order_count": len(orders),
                    "note": f"{len(orders)} placed order(s) currently open for this outlet.",
                }
            if response.status_code < 500:
                # A 4xx is our own request being wrong — retrying it changes
                # nothing, so stop immediately instead of burning attempts.
                last_error = f"Order Service returned {response.status_code}"
                break
            last_error = f"Order Service returned {response.status_code}"

        if attempt < MAX_ATTEMPTS - 1:
            backoff = BASE_BACKOFF_SECONDS * (2 ** attempt)
            jitter = random.uniform(0, backoff * 0.5)
            time.sleep(backoff + jitter)

    return {
        "checked": False,
        "active_order_count": None,
        "note": f"Order Service unavailable, warning skipped ({last_error}).",
    }
