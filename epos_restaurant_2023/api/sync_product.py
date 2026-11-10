import frappe 
import requests
import json

api_url ="http://192.168.10.19:1216"
token = "token fdad19c1e00297c:83531648ff79a04"

headers = {
    "Authorization": token
}

batch_size = 10

# source site
@frappe.whitelist(methods=["POST"])
def send_product_to_report_site(product_ids=None):
    is_sync_all = False

    if product_ids:
        if isinstance(product_ids, str):
            product_ids = frappe.parse_json(product_ids)
    else:
        is_sync_all = True
        product_ids = frappe.get_all("Product", pluck="name")

    if not product_ids:
        frappe.throw("No products found to sync.")

    missing_product_ids = validate_product_codes(product_ids)
    if not missing_product_ids:
        if is_sync_all:
            frappe.throw("All products already exist on the target site.")
        else:
            frappe.throw("All selected products already exist on the target site.")

    sync_missing_product_categories(missing_product_ids)
    sync_missing_pos_menus(missing_product_ids)
    synced_count = sync_product(missing_product_ids)

    return {
        "status": "success",
        "total_checked": len(product_ids),
        "already_existed": len(product_ids) - len(missing_product_ids),
        "synced_count": synced_count,
    }


def validate_product_codes(product_ids):
    url = f"{api_url}/api/method/epos_restaurant_2023.api.sync_product.get_missing_product_codes"
    res = requests.post(
        url,
        headers=headers,
        json={"product_ids": product_ids},
        timeout=30,
    )
    _raise_for_frappe_error(res)
    return res.json().get("message", [])


def sync_missing_product_categories(product_ids):
    product_categories = frappe.get_all(
        "Product",
        filters={"name": ["in", product_ids]},
        pluck="product_category",
        distinct=True,
    )
    product_categories = [c for c in product_categories if c]
    if not product_categories:
        return

    ordered_categories = _get_ordered_tree_docs(
        "Product Category", product_categories, "parent_product_category"
    )

    check_url = f"{api_url}/api/method/epos_restaurant_2023.api.sync_product.get_missing_product_categories"
    res = requests.post(
        check_url,
        headers=headers,
        json={"product_categories": ordered_categories},
        timeout=30,
    )
    _raise_for_frappe_error(res)
    missing_categories = set(res.json().get("message", []))

    if not missing_categories:
        return

    categories_to_sync = [c for c in ordered_categories if c in missing_categories]
    payload = [
        _prepare_doc_payload("Product Category", cat, extra_exclude=("lft", "rgt", "old_parent"))
        for cat in categories_to_sync
    ]

    create_url = f"{api_url}/api/method/epos_restaurant_2023.api.sync_product.bulk_create_product_categories"
    res = requests.post(
        create_url,
        headers=headers,
        json={"categories": payload},
        timeout=60,
    )
    _raise_for_frappe_error(res)


def sync_missing_pos_menus(product_ids):
    pos_menus = _get_pos_menus_for_products(product_ids)
    if not pos_menus:
        return

    ordered_menus = _get_ordered_tree_docs("POS Menu", pos_menus, "parent_pos_menu")

    check_url = f"{api_url}/api/method/epos_restaurant_2023.api.sync_product.get_missing_pos_menus"
    res = requests.post(
        check_url,
        headers=headers,
        json={"pos_menus": ordered_menus},
        timeout=30,
    )
    _raise_for_frappe_error(res)
    missing_menus = set(res.json().get("message", []))

    if not missing_menus:
        return

    menus_to_sync = [m for m in ordered_menus if m in missing_menus]
    payload = [
        _prepare_doc_payload("POS Menu", menu, extra_exclude=("lft", "rgt", "old_parent", "products"))
        for menu in menus_to_sync
    ]

    create_url = f"{api_url}/api/method/epos_restaurant_2023.api.sync_product.bulk_create_pos_menus"
    res = requests.post(
        create_url,
        headers=headers,
        json={"pos_menus": payload},
        timeout=60,
    )
    _raise_for_frappe_error(res)


def _get_pos_menus_for_products(product_ids):
    menus = set()
    product_meta = frappe.get_meta("Product")

    link_fields = [
        df.fieldname
        for df in product_meta.fields
        if df.fieldtype == "Link" and df.options == "POS Menu"
    ]
    if link_fields:
        rows = frappe.get_all(
            "Product",
            filters={"name": ["in", product_ids]},
            fields=link_fields,
        )
        for row in rows:
            for field in link_fields:
                if row.get(field):
                    menus.add(row.get(field))

    for df in product_meta.get_table_fields():
        child_meta = frappe.get_meta(df.options)
        child_menu_fields = [
            cdf.fieldname
            for cdf in child_meta.fields
            if cdf.fieldtype == "Link" and cdf.options == "POS Menu"
        ]
        if child_menu_fields:
            child_rows = frappe.get_all(
                df.options,
                filters={
                    "parent": ["in", product_ids],
                    "parenttype": "Product",
                    "parentfield": df.fieldname,
                },
                fields=child_menu_fields,
            )
            for row in child_rows:
                for field in child_menu_fields:
                    if row.get(field):
                        menus.add(row.get(field))

    pos_menu_meta = frappe.get_meta("POS Menu")
    products_table_df = pos_menu_meta.get_field("products")
    if products_table_df and products_table_df.options:
        child_meta = frappe.get_meta(products_table_df.options)
        product_link_fields = [
            cdf.fieldname
            for cdf in child_meta.fields
            if cdf.fieldtype == "Link" and cdf.options == "Product"
        ]
        for field in product_link_fields:
            parent_menus = frappe.get_all(
                products_table_df.options,
                filters={
                    field: ["in", product_ids],
                    "parenttype": "POS Menu",
                    "parentfield": "products",
                },
                pluck="parent",
                distinct=True,
            )
            menus.update(m for m in parent_menus if m)

    return list(menus)


def _get_ordered_tree_docs(doctype, names, parent_field):
    ordered = []
    visited = set()

    def visit(name):
        if not name or name in visited:
            return
        visited.add(name)
        parent = frappe.db.get_value(doctype, name, parent_field)
        if parent:
            visit(parent)
        ordered.append(name)

    for name in names:
        visit(name)

    return ordered


def sync_product(product_ids):
    url = f"{api_url}/api/method/epos_restaurant_2023.api.sync_product.bulk_create_products"
    total_synced = 0

    for i in range(0, len(product_ids), batch_size):
        batch_ids = product_ids[i : i + batch_size]
        products_payload = [
            _prepare_doc_payload("Product", pid, extra_exclude=("printers",))
            for pid in batch_ids
        ]

        res = requests.post(
            url,
            headers=headers,
            json={"products": products_payload},
            timeout=60,
        )
        _raise_for_frappe_error(res)
        total_synced += len(batch_ids)

    return total_synced


def _prepare_doc_payload(doctype, name, extra_exclude=()):
    doc = frappe.get_doc(doctype, name).as_dict()
    exclude_fields = ("creation", "modified", "modified_by", "owner", "docstatus", "idx") + tuple(extra_exclude)
    for field in exclude_fields:
        doc.pop(field, None)

    for value in doc.values():
        if isinstance(value, list):
            for row in value:
                if isinstance(row, dict):
                    for field in ("name", "creation", "modified", "modified_by", "owner", "parent"):
                        row.pop(field, None)
    return doc


def _raise_for_frappe_error(res):
    if not res.ok:
        try:
            err_data = res.json()
            server_msgs = err_data.get("_server_messages")
            if server_msgs:
                msgs = [json.loads(m).get("message") for m in json.loads(server_msgs)]
                frappe.throw("Target Site Error: " + "; ".join(filter(None, msgs)))
            frappe.throw(f"Target Site Error ({res.status_code}): {err_data.get('exception') or res.text}")
        except ValueError:
            frappe.throw(f"Target Site Error ({res.status_code}): {res.text}")






# target site
@frappe.whitelist(methods=["POST"])
def get_missing_product_codes(product_ids):
    if isinstance(product_ids, str):
        product_ids = frappe.parse_json(product_ids)
    if not product_ids:
        return []
    existing = set(
        frappe.get_all("Product", filters={"name": ["in", product_ids]}, pluck="name")
    )
    return [pid for pid in product_ids if pid not in existing]

@frappe.whitelist(methods=["POST"])
def get_missing_product_categories(product_categories):
    if isinstance(product_categories, str):
        product_categories = frappe.parse_json(product_categories)
    if not product_categories:
        return []
    existing = set(
        frappe.get_all("Product Category", filters={"name": ["in", product_categories]}, pluck="name")
    )
    return [cat for cat in product_categories if cat not in existing]

@frappe.whitelist(methods=["POST"])
def bulk_create_product_categories(categories):
    if isinstance(categories, str):
        categories = frappe.parse_json(categories)
    if not categories:
        return {"created": 0}
    created = 0
    for data in categories:
        cat_name = data.get("name")
        if cat_name and frappe.db.exists("Product Category", cat_name):
            continue
        data["doctype"] = "Product Category"
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True, set_name=cat_name)
        created += 1
    frappe.db.commit()
    return {"created": created}

@frappe.whitelist(methods=["POST"])
def get_missing_pos_menus(pos_menus):
    if isinstance(pos_menus, str):
        pos_menus = frappe.parse_json(pos_menus)
    if not pos_menus:
        return []
    existing = set(
        frappe.get_all("POS Menu", filters={"name": ["in", pos_menus]}, pluck="name")
    )
    return [menu for menu in pos_menus if menu not in existing]

@frappe.whitelist(methods=["POST"])
def bulk_create_pos_menus(pos_menus):
    if isinstance(pos_menus, str):
        pos_menus = frappe.parse_json(pos_menus)
    if not pos_menus:
        return {"created": 0}
    created = 0
    for data in pos_menus:
        menu_name = data.get("name")
        if menu_name and frappe.db.exists("POS Menu", menu_name):
            continue

        data.pop("products", None)
        data["doctype"] = "POS Menu"
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True, set_name=menu_name)
        created += 1
    frappe.db.commit()
    return {"created": created}

@frappe.whitelist(methods=["POST"])
def bulk_create_products(products):
    if isinstance(products, str):
        products = frappe.parse_json(products)
    if not products:
        return {"created": 0}
    created = 0
    for data in products:
        product_name = data.get("name")
        if product_name and frappe.db.exists("Product", product_name):
            continue
        data.pop("printers", None)
        data["doctype"] = "Product"
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True, set_name=product_name)
        created += 1
    frappe.db.commit()
    return {"created": created}


