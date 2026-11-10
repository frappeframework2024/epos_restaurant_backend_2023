from html import escape
from re import fullmatch

import frappe
import requests

from .sync import _emenu_connection


ORDERS_PATH = "/api/integrations/pos/orders"
UNEXPECTED_RESPONSE = "The eMenu order API returned an unexpected response."

@frappe.whitelist()
def get_order(context=None):
    """List orders for review, or fetch details when context includes order_id."""
    if context is None:
        context = {}
    if not isinstance(context, dict):
        frappe.throw("Order context must be an object.")

    order_id = context.get("order_id")
    if order_id is not None:
        result = _request("GET", _order_path(order_id))
        if not isinstance(result.get("order"), dict) or not isinstance(result.get("products"), list):
            frappe.throw(UNEXPECTED_RESPONSE)
        return result

    result = _request("GET", ORDERS_PATH, params={
        "status": context.get("status", "submitted"),
        "page": context.get("page", 1),
        "page_size": context.get("page_size", 25),
    })
    orders = result.get("orders")
    if not isinstance(orders, list):
        frappe.throw(UNEXPECTED_RESPONSE)
    return orders

@frappe.whitelist()
def update_order(payload):
    """Update the eMenu order status after the POS transaction commits."""
    if not isinstance(payload, dict):
        frappe.throw("Order update payload must be an object.")

    path = _order_path(payload.get("order_id"))
    status = payload.get("status")
    if status not in ("accepted", "completed", "cancelled"):
        frappe.throw("Order status must be accepted, completed, or cancelled.")

    result = _request("PATCH", path, json={"status": status})
    if result.get("id") != payload["order_id"] or result.get("status") != status:
        frappe.throw(UNEXPECTED_RESPONSE)
    return result


def _order_path(order_id):
    if not isinstance(order_id, str) or not fullmatch(r"ord_[0-9a-f]{32}", order_id):
        frappe.throw("Provide a valid eMenu order_id.")
    return ORDERS_PATH + "/" + order_id


def _request(method, path, **kwargs):
    api_url, api_key = _emenu_connection()
    try:
        response = requests.request(
            method, api_url + path,
            headers={"Authorization": "Bearer " + api_key, "Accept": "application/json"},
            timeout=(5, 20), allow_redirects=False, **kwargs,
        )
    except requests.exceptions.Timeout:
        frappe.throw("The eMenu order request timed out. Please try again.")
    except requests.exceptions.RequestException:
        frappe.throw("Could not connect to eMenu. Check emenu_integration.api_url from the Frappe server.")

    try:
        result = response.json()
    except ValueError:
        result = None

    if not 200 <= response.status_code < 300:
        error = result.get("error") if isinstance(result, dict) else None
        if not isinstance(error, str) or not error.strip():
            error = "The eMenu API rejected the order request."
        error = escape(error.replace(api_key, "[redacted]"))
        frappe.throw(f"eMenu order request failed (HTTP {response.status_code}): {error}")

    if not isinstance(result, dict):
        frappe.throw(UNEXPECTED_RESPONSE)
    return result
