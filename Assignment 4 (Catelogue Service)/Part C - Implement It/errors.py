"""
Errors and request validation for the Catalogue Service.

Every failure response, regardless of which endpoint raised it, is built by
problem() — this is the single error shape required by C6. validate_*()
functions are the hand-written replacement for the XML Schema validation
Assignment 3's WSDL got for free (see NOTES.md Part 4).
"""


class DomainError(Exception):
    """Base class for errors that map to a specific HTTP status code."""
    status_code = 400
    code = "domain_error"

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class MalformedBody(DomainError):
    status_code = 400
    code = "malformed_body"


class ValidationFailed(DomainError):
    status_code = 422
    code = "validation_failed"


class NotFound(DomainError):
    status_code = 404
    code = "not_found"


class Conflict(DomainError):
    status_code = 409
    code = "conflict"


def problem(status: int, title: str, detail: str, code: str) -> tuple:
    """
    The one error shape every endpoint uses. Returns (body_dict, status)
    so a Flask view can do `return problem(...)` directly.
    """
    body = {
        "type": f"https://campuseats.example/errors/{code}",
        "title": title,
        "status": status,
        "detail": detail,
        "code": code,
    }
    return body, status


def error_response(exc: DomainError):
    titles = {
        400: "Malformed request",
        404: "Not found",
        409: "Conflict",
        422: "Unprocessable request",
    }
    return problem(exc.status_code, titles.get(exc.status_code, "Error"), exc.detail, exc.code)


# ---- Validation functions -------------------------------------------------
# These are what now carries the responsibility the Assignment 3 XML Schema
# used to carry automatically: nothing below this point is allowed to touch
# raw request fields without having passed through one of these first.

def validate_outlet_create(body) -> dict:
    if not isinstance(body, dict):
        raise MalformedBody("Request body must be a JSON object.")

    name = body.get("name")
    address = body.get("address")
    phone = body.get("phone")

    if not isinstance(name, str) or not isinstance(address, str):
        raise MalformedBody("'name' and 'address' must be strings.")
    if phone is not None and not isinstance(phone, str):
        raise MalformedBody("'phone' must be a string if provided.")

    if not name.strip():
        raise ValidationFailed("'name' must not be blank.")
    if not address.strip():
        raise ValidationFailed("'address' must not be blank.")

    return {"name": name.strip(), "address": address.strip(), "phone": phone}


def validate_menu_item_create(body) -> dict:
    if not isinstance(body, dict):
        raise MalformedBody("Request body must be a JSON object.")

    name = body.get("name")
    description = body.get("description")
    price = body.get("price")

    if not isinstance(name, str):
        raise MalformedBody("'name' must be a string.")
    if description is not None and not isinstance(description, str):
        raise MalformedBody("'description' must be a string if provided.")
    # bool is a subclass of int in Python — explicitly reject it so
    # {"price": true} is not silently accepted as price=1.
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        raise MalformedBody("'price' must be a number.")

    if not name.strip():
        raise ValidationFailed("'name' must not be blank.")
    if price <= 0:
        raise ValidationFailed("'price' must be a positive number.")

    return {"name": name.strip(), "description": description, "price": float(price)}


def validate_availability_update(body) -> dict:
    if not isinstance(body, dict):
        raise MalformedBody("Request body must be a JSON object.")

    available = body.get("available")
    reason = body.get("reason")

    if isinstance(available, bool) is False:
        raise ValidationFailed("'available' must be a boolean.")
    if reason is not None and not isinstance(reason, str):
        raise MalformedBody("'reason' must be a string if provided.")

    return {"available": available, "reason": reason}
