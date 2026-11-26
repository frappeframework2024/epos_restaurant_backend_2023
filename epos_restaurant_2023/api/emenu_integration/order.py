from html import escape
from re import fullmatch

import frappe
import requests
import json
from .sync import _emenu_connection
from concurrent.futures import ThreadPoolExecutor
from epos_restaurant_2023.api.api import get_sale_list_table_badge
from epos_restaurant_2023.custom_socket_client import emit_event
from epos_restaurant_2023.api.emenu_integration.convert_to_sale import upsert_sale


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

    params = {
        "status": context.get("status", "submitted"),
        "page": context.get("page", 1),
        "page_size": context.get("page_size", 25),
    }
    posting_date = context.get("posting_date")
    if posting_date not in (None, ""):
        params["posting_date"] = posting_date

    result = _request("GET", ORDERS_PATH, params=params)
    orders = result.get("orders")
    total_record = result.get("total_record")
    if not isinstance(orders, list) or type(total_record) is not int or total_record < 0:
        frappe.throw(UNEXPECTED_RESPONSE)

    _enrich_accepted_orders_totals(orders)
    return result


@frappe.whitelist()
def update_order(payload):
    """Update the eMenu order status after the POS transaction commits."""
    if isinstance(payload, str):
        payload = frappe.parse_json(payload)
    if not isinstance(payload, dict):
        frappe.throw("Order update payload must be an object.")

    path = _order_path(payload.get("order_id"))
    status = payload.get("status")
    if status not in ("accepted", "completed", "cancelled"):
        frappe.throw("Order status must be accepted, completed, or cancelled.")

    body = {"status": status}
    products = payload.get("products")
    if isinstance(products, list):
        normalized_products = []
        for item in products:
            if not isinstance(item, dict) or not item.get("id"):
                continue
            raw_status = str(item.get("status") or "").strip().lower()

            item_status = "rejected" if raw_status in ("rejected", "reject") else "accepted"
            normalized_products.append({
                "id": item["id"],
                "status": item_status,
            })
        body["products"] = normalized_products

    result = _request("PATCH", path, json=body)
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


@frappe.whitelist()
def get_current_table_orders(pos_profile=None,table_id=None):
    if table_id:
        table_id = frappe.db.exists(
            "Tables Number",
            {"integration_id": table_id}
        )    
     
    
    if table_id:
        return [x for x in get_sale_list_table_badge({"pos_profile":pos_profile}) if x.get("table_id") == table_id]
    return []


@frappe.whitelist(methods=["POST"])
def confirm_order(context):
    if isinstance(context, str):
        context = frappe.parse_json(context)
    order = dict(context.get("order") or {})
    order_id = order.get("id")
    if not order_id:
        frappe.throw("Invalid order ID.")

    all_products = order.get("products") or []
    raw_selected_ids = context.get("selected_product_ids")
    selected_ids = (
        {str(x) for x in raw_selected_ids if x is not None}
        if raw_selected_ids is not None
        else None
    )
    accepted_products = []
    status_products = []

    for p in all_products:
        pid = p.get("id")
        if selected_ids is not None:
            is_accepted = pid is not None and str(pid) in selected_ids
        else:
            is_accepted = str(p.get("status") or "").strip().lower() == "accepted"


        item_status = "accepted" if is_accepted else "rejected"
        if pid is not None:
            status_products.append({
                "id": pid,
                "status": item_status,
            })

        if is_accepted:
            accepted_item = dict(p)
            accepted_item["status"] = "accepted"
            accepted_products.append(accepted_item)

    if not accepted_products:
        frappe.throw("Please select at least one product to confirm.")

    accepted_total = sum(
        float(p.get("amount") or (float(p.get("price") or 0) * float(p.get("qty") or 1)))
        for p in accepted_products
    )
    # only accept to sale
    sale_order = dict(order)
    sale_order["products"] = accepted_products
    sale_order["total"] = accepted_total
    sale_context = dict(context)
    sale_context["order"] = sale_order

    valid = upsert_sale(context=sale_context)
    if not isinstance(valid, dict) or not valid.get("sale"):
        frappe.throw("Failed to confirm order.")

    payload = {
        "order_id": order_id,
        "status": "accepted",
        "products": status_products,
    }
    update_order(payload)
    frappe.cache().set_value(
        f"emenu_accepted_total:{order_id}",
        round(float(accepted_total), 6),
        expires_in_sec=86400 * 7,
    )

    return valid





    
@frappe.whitelist(methods=["POST"])
def cancell_order(order_id,reason = None):
    res = update_order({"order_id":order_id,"status":"cancelled"})
    frappe.msgprint("Cancel order successfully")


@frappe.whitelist(allow_guest=True)
def notify_online_order(order_id,room=None):   
    if not room:
        room = frappe.site_config.get("notify_online_order_key") or None
        
    if room:    
        emit_event("NotifyOnlineOrder",{"order_id":order_id,"room":room})



#for accepted filter in order online
def _calc_accepted_products_total(products):
    total = 0.0
    for p in products or []:
        st = str(p.get("status") or "").strip().lower()
        if st in ("rejected", "reject"):
            continue
        raw_amount = p.get("amount") if p.get("amount") is not None else p.get("total_amount")
        if raw_amount is not None:
            total += float(raw_amount or 0)
        else:
            price = float(p.get("price") or p.get("unit_price") or 0)
            qty = float(p.get("qty") or p.get("quantity") or 1)
            total += price * qty
    return round(total, 6)


def _apply_accepted_total_to_order(order_dict, accepted_total):
    order_dict["accepted_total"] = accepted_total
    for key in ("total_amount", "total", "grand_total", "amount"):
        if key in order_dict and order_dict[key] is not None:
            order_dict[key] = accepted_total


def _enrich_accepted_orders_totals(orders):
    accepted_orders = [
        o for o in orders
        if isinstance(o, dict) and str(o.get("status") or "").strip().lower() == "accepted"
    ]
    if not accepted_orders:
        return

    missing = []
    for o in accepted_orders:
        if isinstance(o.get("products"), list) and o["products"]:
            _apply_accepted_total_to_order(o, _calc_accepted_products_total(o["products"]))
            continue
        oid = o.get("id")
        if not oid:
            continue
        cached = frappe.cache().get_value(f"emenu_accepted_total:{oid}")
        if cached is not None:
            _apply_accepted_total_to_order(o, float(cached))
        else:
            missing.append(o)
    if not missing:
        return
    api_url, api_key = _emenu_connection()
    def _fetch_detail_total(oid):
        try:
            path = _order_path(oid)
            resp = requests.request(
                "GET",
                api_url + path,
                headers={"Authorization": "Bearer " + api_key, "Accept": "application/json"},
                timeout=(5, 20),
                allow_redirects=False,
            )
            if 200 <= resp.status_code < 300:
                data = resp.json()
                if isinstance(data, dict) and isinstance(data.get("products"), list):
                    return oid, _calc_accepted_products_total(data["products"])
        except Exception:
            pass
        return oid, None
    with ThreadPoolExecutor(max_workers=min(8, len(missing))) as pool:
        results = list(pool.map(_fetch_detail_total, [o["id"] for o in missing]))
    totals_by_id = {oid: tot for oid, tot in results if tot is not None}
    for o in missing:
        oid = o.get("id")
        if oid in totals_by_id:
            tot = totals_by_id[oid]
            frappe.cache().set_value(f"emenu_accepted_total:{oid}", tot, expires_in_sec=86400 * 7)
            _apply_accepted_total_to_order(o, tot)

