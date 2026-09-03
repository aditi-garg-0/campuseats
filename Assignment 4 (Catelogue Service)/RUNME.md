# How to run this project (Windows)

Four double-click scripts do everything. Run them in this order.

## 1. First time only: `setup.bat`
Double-click it. It creates a `.venv` folder right here and installs
Flask, requests, pytest, and openapi-spec-validator into it. Wait for
"Setup complete." Close the window (or press any key).

## 2. Every time you want to run the service: two windows

**Window 1** — double-click `run_order_service.bat`.
Wait until it says `Running on http://127.0.0.1:5001`. Leave this window open.

**Window 2** — double-click `run_catalogue_service.bat`.
Wait until it says `Running on http://127.0.0.1:5000`. Leave this window open too.

Both windows must stay open at the same time — closing either one stops
that service.

## 3. Try it

Open a third, normal terminal (or PowerShell) anywhere and run:

```
curl -i -X POST http://localhost:5000/outlets -H "Content-Type: application/json" -d "{\"name\": \"Tandoori Corner\", \"address\": \"Block C\"}"
```

(Note: on Windows, curl needs the JSON quotes escaped with backslashes,
as shown above — that's a Windows/curl quirk, not a bug in the service.)

You should get back a `201` with a `Location` header. More example requests,
copy-pasted from a real run, are in `Evidence/curl-transcript.txt` — those
use Mac/Linux-style quoting, so adjust the quotes the same way if you copy
them into a Windows terminal.

## 4. Run the automated tests any time

Close nothing — double-click `run_tests.bat`. It doesn't need the two
services running (the Order Service call is mocked in tests), and should
finish with `7 passed`.

## If something goes wrong

- **"python is not recognized"** — Python itself isn't on your PATH.
  Reinstall Python from python.org and check "Add Python to PATH", or
  use an Anaconda Prompt instead of a plain terminal.
- **A batch file closes instantly with no message** — right-click it and
  choose "Edit" (or open it in VSCode) to read what it says instead of
  double-clicking, or run it from inside a terminal instead: `setup.bat`.
- **Port 5000 or 5001 already in use** — something else on your machine
  is already using that port. Close it, or edit the port number in
  `Part C - Implement It/app.py` (and `stub_order_service.py` for 5001)
  and update `run_catalogue_service.bat`'s `ORDER_SERVICE_URL` to match.
