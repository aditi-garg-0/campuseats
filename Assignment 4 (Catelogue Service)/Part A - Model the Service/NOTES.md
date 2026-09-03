# CampusEats — Assignment 4: Catalogue Service in REST

**Team ID: 7** — Aditi Garg (20251651008), Neha Nupur (20251651064), Shivam Kumar Soni (20251651084)

**Course:** CS543, Web Services · 

**Assignment 4** · 

Instructor: Dr. Pramit Mazumdar


**Service rebuilt:** Catalogue Service (owns `Outlet`, `Menu Item` — Assignment 2's boundary, unchanged)

---

## Part A — Modelling the service

### A2. Operations as they would have been written as SOAP (starting point only)

- `registerOutlet(adminId, name, address, phone)` → outletRef
- `getOutletMenu(outletRef)` → outlet details + menu items
- `addMenuItem(outletRef, staffId, name, description, price)` → menuItemRef
- `setItemAvailability(menuItemRef, staffId, availabilityFlag)` → confirmed availability
- `checkItemsAvailability(outletRef, items[])` → per-item availability (folded into the filtered list below rather than kept as a separate endpoint — see A5)

### A3. Nouns

`Outlets`, `MenuItems`. `register`, `get`, `add`, `set`, `check` do not survive into any URL.

### A4. Resource table

| Method | URL | What it does | Success | Failure |
|---|---|---|---|---|
| POST | `/outlets` | Create an outlet (`registerOutlet`) | 201 | 400, 422 |
| GET | `/outlets/{outletId}` | Read a single outlet | 200 | 404 |
| POST | `/outlets/{outletId}/menu-items` | Add a menu item to an outlet (`addMenuItem`); safely retryable via `Idempotency-Key` | 201 | 400, 404, 422 |
| GET | `/outlets/{outletId}/menu-items?available=true\|false` | List an outlet's menu items, filtered by availability | 200 | 404 |
| PATCH | `/menu-items/{menuItemId}/availability` | Change a menu item's availability (`setItemAvailability`) — sub-resource, state-changing | 200 | 404, 409, 422 |

### A5. The hard choice — `setItemAvailability`

`setItemAvailability` mapped least comfortably onto a resource, because it is fundamentally a verb — "flip this flag" — not a noun. The obvious shortcut was `PATCH /menu-items/{id}` with `{"is_available": false}` in the body, alongside any other field. That was rejected: a plain PATCH on the whole item blurs together two very different concerns (an outlet editing its own name/price/description versus a staff member marking something sold out), gives no natural place to attach a `reason`, and offers no seam for the audit/warning behaviour Part D needed. Instead, availability is modelled as its own sub-resource, `PATCH /menu-items/{id}/availability`, mirroring the assignment's own `/orders/42/cancellation` example: it treats the flip as a discrete, addressable state transition with its own semantics (it can conflict — see A4 — in a way a generic field update conceptually shouldn't), even though underneath the store only touches one field.

---

## Part D — Surviving the network

### D1–D2. The call and its hardening

Catalogue Service was the *one* service in Assignment 2 (Task 6) that never called out to anything else — that was exactly what made all five service properties pass for it without qualification. Assignment 4 forces one real outbound call, so `PATCH /menu-items/{id}/availability` — specifically when marking an item **unavailable** — now calls Order Service's existing `listOrdersForOutlet` operation (already in its Task 3 contract; nothing about Order Service was redesigned to support this) to report how many `placed` orders are currently open for that outlet, as an advisory `active_order_warning` on the response.

The call (`order_client.py`) is a single `GET`, so every attempt is inherently safe to retry: a 2s timeout, up to 3 attempts, exponential backoff (`0.2s, 0.4s, ...`) with jitter, and a 4xx response stops retrying immediately since retrying our own bad request changes nothing. The Order Service address is read from `ORDER_SERVICE_URL`, never hard-coded.

### D3. Fallback

**Chosen fallback: degrade, don't fail.** If Order Service is unreachable, the availability change still succeeds; `active_order_warning` is simply returned as `{"checked": false, ...}`. Failing the whole request instead would have been the wrong call: marking an item unavailable is itself a safety operation — it exists to *stop* students from ordering something the kitchen can no longer make — so gating it on an unrelated service's uptime would mean an Order Service outage forces staff to keep selling a sold-out item. That would directly undo the independence Task 6 already established for Catalogue Service; the warning is a nice-to-have, not a precondition, and code and tests treat it that way.

---

## Answers

**Q1.** *Count the lines in your Assignment 3 WSDL and in your `openapi.yaml`. What is the difference actually made of? Name two things the WSDL declared that the OpenAPI file does not need to.*

**A1.** `Assignment 3/partner.wsdl`: 140 lines, 2 operations. `Assignment 4/openapi.yaml`: 317 lines, 5 operations. Per-operation this is actually comparable (~70 vs ~63 lines/operation) — the raw count doesn't shrink the way a first guess might suggest. What differs is *what* those lines encode. The WSDL's lines are dominated by transport and envelope plumbing that has no REST equivalent: a `<binding>` block per operation restating `soap:operation`/`soap:body use="literal"` that OpenAPI never needs, because the HTTP method and path in a `paths:` entry *are* the binding — there is no separate transport-declaration layer to write. Two concrete things the WSDL declares that `openapi.yaml` does not need: (a) a `<message>` wrapper per direction (`chargeRequestMessage`, `chargeResponseMessage`, `chargeFaultMessage`) that exists purely to name and group parts for the SOAP envelope — OpenAPI's `requestBody`/`responses` reference a schema directly, with no message-envelope indirection; (b) the `<service>`/`<port>`/`soap:address` block that binds an operation to one specific transport endpoint — OpenAPI's `servers:` list is a plain array of base URLs, not a per-operation binding declaration.

---

**Q2.** *Quote one `soap:Fault` from your Assignment 3 work and show the status code and problem body that replaced it. Why is returning that error inside a `200 OK` a problem for the network in between?*

**A2.** From `Assignment 3/soap-fault.xml`: `faultcode` `soap:Client`, `faultstring` "Charge declined by issuing bank", `detail/pb:error/code` `TXN_DECLINED`. The REST replacement (same shape used throughout this service) is a `422` with a problem body: `{"type": "https://campuseats.example/errors/payment_declined", "title": "Unprocessable request", "status": 422, "detail": "The issuing bank declined this charge and no funds were captured.", "code": "payment_declined"}` — 422 because the request was well-formed, it's the domain (the bank) that refuses it. Returning that same fault inside an HTTP `200 OK` — which is how a naive SOAP-over-HTTP integration can end up behaving if the transport status is treated as a formality — is a problem for everything sitting between the two endpoints: caches and CDNs are entitled to store and replay a `200` response indefinitely, a load balancer's health check sees "success", and any generic retry/circuit-breaker logic that keys off status codes never fires, even though the business operation genuinely failed. The status code is the one signal every intermediary on the path can read without understanding the payload; burying the real outcome inside a `200` body throws that signal away.

---

**Q3.** *Which of UDDI's three moves — publish, find, bind — still exist in your new setup, and which disappeared? Explain what took over the job.*

**A3.** *Bind* survives essentially unchanged: a consumer still needs a resolved base URL to actually call, it's just resolved from `ORDER_SERVICE_URL` (an environment variable) rather than a WSDL `<soap:address>`. *Publish* survives in a lightweight form: `openapi.yaml` committed to the repo *is* the publication, just without a registry to publish it into. *Find* is what actually disappeared — there is no runtime lookup step where Catalogue Service asks a UDDI-style registry "who implements the Order contract?" Environment configuration (and, in a real deployment, DNS or a service mesh) took over that job ahead of time, at deploy/config time, rather than at call time.

---

**Q4.** *Your XML Schema was enforced before your code ran; your OpenAPI schema is not. Name the specific function in your code that now carries that responsibility, and one failure that would get through if you had not written it.*

**A4.** `validate_availability_update()` (and its siblings `validate_outlet_create()`, `validate_menu_item_create()` in `errors.py`) is the specific function that now does, by hand, what `partner.wsdl`'s XML Schema `<types>` block did automatically for AasaanPay. Concretely: without it, `PATCH /menu-items/{id}/availability` with a body like `{"available": "false"}` (a string, not a boolean) would sail straight into `item.is_available = requested`, silently storing a truthy string instead of `False` — the item would still show as available in `as_json()` (since a non-empty string is truthy in Python), the opposite of what the caller asked for, and no exception would ever surface to explain why.

---

**Q5.** *Name one part of your service where you would still choose the SOAP stack over REST, and state exactly what guarantee you would be buying. Answering "nowhere" needs a stronger argument than answering "somewhere".*

**A5.** Nowhere inside Catalogue Service itself — but one edge, unchanged from Assignment 3: **Payment Service's own call out to AasaanPay.** That edge crosses into a system CampusEats does not control, moving actual money, through however many intermediaries a bank's network puts in the path. There, WS-Security's message-level signing buys something a REST/HTTPS call plain cannot: the signature travels *with the envelope itself*, so the charge stays verifiable and tamper-evident even if it passes through a proxy or queue that TLS's point-to-point encryption doesn't cover. Any REST replacement for that specific edge would need to reinvent that guarantee at the application layer — plain HTTPS alone gives you a secure pipe between two points, not a signed document that survives leaving it. ("Nowhere" would need to explain away that specific guarantee; it's the one place in this whole design where the partner, not CampusEats, dictates the protocol.)

---

## Files

- `openapi.yaml` — contract, validated with `openapi-spec-validator` (see `openapi-validation.txt`)
- `models.py`, `store.py`, `errors.py`, `order_client.py`, `app.py` — implementation
- `stub_order_service.py` — minimal stand-in for Order Service's `listOrdersForOutlet`, used only so Part D's outbound call has something real to talk to
- `tests/test_catalogue.py` — 7 tests (the 4 required, plus 3 covering the filter, the 409 conflict, and the degrade-on-outage path); see `pytest-output.txt`
- `curl-transcript.txt` — full `curl -i` transcript against the live service, including the successful create, the idempotent repeat, the 422, the 404, the 409, and the live outbound call to Order Service
