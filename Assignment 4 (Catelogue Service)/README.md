# CampusEats — Assignment 4: Catalogue Service in REST

This rebuilds the Catalogue Service (Outlet, Menu Item — Assignment 2's
cleanest, fully self-contained service) as a REST API, following the
assignment's own Part A → B → C → D structure. This README explains how the
files fit together and how to actually run the thing.

---

## 1. Folder-by-folder: what each part contains

```
Assignment 4/
├── Part A - Model the Service/
│   └── NOTES.md              ← the design: resource table, hard-choice
│                                justification, D3 fallback reasoning, and
│                                the 5 closing Q&A answers all live here
├── Part B - Publish the Contract/
│   ├── openapi.yaml          ← the API contract (written BEFORE any code)
│   └── openapi-validation.txt← proof it validates with zero errors
├── Part C - Implement It/
│   ├── app.py                ← the Flask app; the only file that touches
│   │                            HTTP requests/responses directly
│   ├── models.py             ← Outlet / MenuItem record classes
│   ├── store.py              ← in-memory storage (only app.py imports this)
│   ├── errors.py             ← validation functions + the one error shape
│   ├── tests/test_catalogue.py ← 7 automated tests
│   └── pytest-output.txt     ← proof all 7 pass
├── Part D - Survive the Network/
│   ├── order_client.py       ← hardened outbound call to Order Service
│   └── stub_order_service.py ← throwaway stand-in for the real Order
│                                Service, so the outbound call has something
│                                real to talk to
├── Evidence/
│   └── curl-transcript.txt   ← a real curl -i session against the live
│                                service (spans Parts C and D — not one part)
├── requirements.txt
├── setup.bat, run_order_service.bat,
│   run_catalogue_service.bat, run_tests.bat   ← Windows one-click scripts
└── RUNME.md                  ← quick reference for the .bat scripts
```

---

## 2. How the files talk to each other (the call graph)

```
tests/test_catalogue.py
        │  (drives requests through Flask's test client)
        ▼
      app.py  ───imports───►  errors.py   (validate_*() functions, problem())
        │
        ├──imports───►  models.py   (Outlet, MenuItem — as_json() strips
        │                            internal-only fields before they reach
        │                            a client)
        │
        ├──imports───►  store.py    (in-memory dict; the ONLY place data
        │                            lives; no other file may import it)
        │
        └──imports───►  order_client.py   (Part D — lives in a *different*
                          │                 folder; app.py adds that folder
                          │                 to sys.path before importing it)
                          ▼
                    stub_order_service.py   (a SEPARATE running process,
                                              not imported — reached only
                                              over real HTTP)
```

**What actually happens on a request**, e.g. `PATCH /menu-items/1/availability`:
1. `app.py` receives the request.
2. It calls a `validate_*()` function from `errors.py`. Bad input → raises an
   exception → `app.py`'s error handler turns it into the one shared JSON
   error shape via `errors.problem()`.
3. It reads/writes the record through `store.py`.
4. If the update is "mark unavailable", it also calls
   `order_client.get_active_order_warning()` (Part D) — a real `GET` to
   whatever process is listening on `ORDER_SERVICE_URL` (the stub, in your
   local setup). This call can never fail the request — if it's
   unreachable, the write still succeeds and the warning just says
   `"checked": false`.
5. The response is built by the record's own `as_json()` method in
   `models.py`, never by hand — that's what keeps internal-only fields
   (like which staff member created something) out of every response.

---

## 3. How to run it

You need **two terminal windows running at once**, plus a third for testing.

### One-time setup
Double-click `setup.bat`. It creates a `.venv` folder and installs
Flask, requests, pytest, and openapi-spec-validator into it.

### Every time you want to run the service
- **Window 1:** double-click `run_order_service.bat` → wait for
  `Running on http://127.0.0.1:5001`. Leave it open.
- **Window 2:** double-click `run_catalogue_service.bat` → wait for
  `Running on http://127.0.0.1:5000`. Leave it open too.

### Try it (a third, normal terminal)
```
curl -i -X POST http://localhost:5000/outlets -H "Content-Type: application/json" -d "{\"name\": \"Tandoori Corner\", \"address\": \"Block C\"}"
```
(Windows curl needs the quotes backslash-escaped like that.)

### Run the automated tests (independent of the two windows above)
Double-click `run_tests.bat`.

---

## 4. What you should see (expected output)

**`run_order_service.bat`** — a window that prints and then sits idle,
waiting for requests:
```
* Serving Flask app 'stub_order_service'
* Running on http://127.0.0.1:5001
```

**`run_catalogue_service.bat`** — same idea, on port 5000:
```
* Serving Flask app 'app'
* Debug mode: on
* Running on http://127.0.0.1:5000
* Debugger PIN: ###-###-###
```

**`run_tests.bat`** — runs once and exits:
```
collected 7 items
tests/test_catalogue.py::test_create_succeeds_with_right_code_and_location_header PASSED
tests/test_catalogue.py::test_idempotent_repeat_returns_original_result PASSED
tests/test_catalogue.py::test_malformed_body_returns_422 PASSED
tests/test_catalogue.py::test_unknown_id_returns_404 PASSED
tests/test_catalogue.py::test_state_conflict_returns_409 PASSED
tests/test_catalogue.py::test_filtered_list_by_query_string PASSED
tests/test_catalogue.py::test_availability_change_degrades_when_order_service_unreachable PASSED
======================== 7 passed in 0.3xs ========================
```

**Creating an outlet** (`POST /outlets`):
```
HTTP/1.1 201 CREATED
Location: /outlets/1

{
  "outlet_id": 1,
  "name": "Tandoori Corner",
  "address": "Block C",
  "phone": null,
  "is_active": true,
  "created_at": "..."
}
```

**Creating a menu item, then repeating the exact request with the same
`Idempotency-Key`** — both return `201`, but the **second response has the
identical `created_at` timestamp as the first**. That's the proof nothing
was created twice.

**Marking an item unavailable** (`PATCH /menu-items/1/availability` with
`{"available": false}`) — `200 OK`, with an extra field:
```json
"active_order_warning": {
  "checked": true,
  "active_order_count": 2,
  "note": "2 placed order(s) currently open for this outlet."
}
```
`active_order_count: 2` only appears if `run_order_service.bat` is running
— that number comes from a real HTTP call to it. If that window isn't
running, you'll instead see `"checked": false` and a note that it was
unreachable, and the availability change **still succeeds** either way.

**Repeating that same PATCH a second time** (item is already unavailable)
→ `409 Conflict` instead of `200` — proof the state-conflict check works.

---

## 5. Where to look for more detail

- **Why things are designed this way** (the reasoning behind each choice) →
  `Part A - Model the Service/NOTES.md`
- **The exact API shape** (every endpoint, every status code) →
  `Part B - Publish the Contract/openapi.yaml`
- **A full real transcript** of everything above, already run once → 
  `Evidence/curl-transcript.txt`
