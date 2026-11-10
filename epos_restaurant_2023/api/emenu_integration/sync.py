from datetime import datetime, timezone
from html import escape
from time import sleep
from urllib.parse import urlsplit
from uuid import UUID, uuid4, uuid5
from zoneinfo import ZoneInfo

import frappe
import requests
from frappe.utils import get_datetime, get_system_timezone


CATALOG_SYNC_PATH = "/api/integrations/pos/sync"
PRODUCT_SYNC_PATH = CATALOG_SYNC_PATH + "/product"
TABLE_SYNC_PATH = CATALOG_SYNC_PATH + "/tables"



class _TableGroupInUse(Exception):
    pass

@frappe.whitelist()
def testme():
    return sync_product_to_menu()
    return sync_tables_to_emenu()

@frappe.whitelist(methods=["POST"])
def sync_product_to_emenu():
    return sync_product_to_menu()


@frappe.whitelist(methods=["POST"])
def sync_product_to_menu():
    # return _prepare_product_prices()
    # return prepare_product()

    api_url, api_key = _emenu_connection()
    _validate_integration_id("Product", "integration_id")
    _validate_integration_id("Product Category", "integration_id")
    source_updated_at = datetime.now(timezone.utc).isoformat()
    categories = prepare_category()
    products = prepare_product()
    # return products
    menus, menu_products = _prepare_menu_snapshot(products)

    # Save newly assigned menu IDs before sending them to eMenu.
    frappe.db.commit()

    return _post_emenu_sync(api_url, api_key, CATALOG_SYNC_PATH, {
        "source_updated_at": source_updated_at,
        "categories": categories,
        "products": products,
        "menus": menus,
        "menu_products": menu_products,
    })


@frappe.whitelist(methods=["POST"])
def sync_tables_to_emenu(business_branch=None):
    frappe.only_for("System Manager")
    return _sync_table_selection(business_branch)


def enqueue_table_emenu_sync(doc, method=None):
    if not frappe.conf.get("emenu_integration") or doc.flags.get("ignore_on_update"):
        return
    frappe.enqueue(
        sync_table_record_to_emenu,
        queue="default",
        enqueue_after_commit=True,
        doctype=doc.doctype,
        name=doc.name,
    )


def sync_table_record_to_emenu(doctype, name):
    if doctype == "Table Group":
        return _sync_table_selection(group_name=name)
    if doctype == "Tables Number":
        return _sync_table_selection(table_name=name)
    frappe.throw("Only Table Group and Tables Number records can sync to eMenu here.")


def enqueue_table_emenu_archive(doc, method=None):
    if not frappe.conf.get("emenu_integration") or doc.flags.get("ignore_on_trash"):
        return
    integration_id = doc.get("integration_id")
    if not str(integration_id or "").strip():
        return
    frappe.enqueue(
        archive_table_record_in_emenu,
        queue="default",
        enqueue_after_commit=True,
        doctype=doc.doctype,
        integration_id=integration_id,
    )


def archive_table_record_in_emenu(doctype, integration_id):
    field = {"Table Group": "table_group_id", "Tables Number": "table_id"}.get(doctype)
    if field is None:
        frappe.throw("Only Table Group and Tables Number records can be archived in eMenu here.")
    record_id = _canonical_uuid(integration_id)
    if record_id is None:
        frappe.throw("The deleted record's integration_id must be a UUID to archive it in eMenu.")
    api_url, api_key = _emenu_connection()
    with _table_sync_lock():
        # A restored record (or an undone deletion) still owns this UUID.
        if frappe.db.exists(doctype, {"integration_id": record_id}):
            return
        return _deliver_table_sync(api_url, api_key, {"archive": {field: record_id}})


def _table_sync_lock():
    cache = frappe.cache()
    return cache.lock(cache.make_key("emenu:table-sync"), timeout=180, blocking_timeout=120)


def _sync_table_selection(business_branch=None, *, group_name=None, table_name=None):
    api_url, api_key = _emenu_connection()
    targeted = group_name is not None or table_name is not None
    # Read committed state under the same lock for manual syncs, saves, and deletions.
    # This keeps an older request from arriving after a newer one.
    with _table_sync_lock():
        data = prepare_table_sync(business_branch, group_name=group_name, table_name=table_name)
        if data is None:
            return
        try:
            return _deliver_table_sync(api_url, api_key, data, allow_layout_retry=targeted)
        except _TableGroupInUse:
            # A moved table may still be linked to the old group in eMenu.
            # Send the current layout so its move and the archive commit together.
            return _deliver_table_sync(api_url, api_key, prepare_table_sync(business_branch))


def _deliver_table_sync(api_url, api_key, data, *, allow_layout_retry=False):
    data["sync_id"] = str(uuid4())
    # A failed HTTP delivery must not cause the next sync to assign new IDs.
    frappe.db.commit()
    return _post_emenu_sync(
        api_url, api_key, TABLE_SYNC_PATH, data,
        attempts=3, timeout=(5, 25), allow_layout_retry=allow_layout_retry,
    )


def prepare_table_sync(business_branch=None, *, group_name=None, table_name=None):
    if business_branch is not None and not isinstance(business_branch, str):
        frappe.throw("business_branch must be a branch name.")
    business_branch = (business_branch or "").strip()
    for doctype in ("Table Group", "Tables Number"):
        if not frappe.db.has_column(doctype, "integration_id"):
            frappe.throw(f"Apply the Frappe schema migration for {doctype}. The integration_id field is missing.")

    if table_name is not None:
        selected = frappe.db.get_value("Tables Number", table_name, "tbl_group", as_dict=True, for_update=True)
        if selected is None:
            return None
        group_name = selected["tbl_group"]
        if not group_name:
            frappe.throw(f"Choose a valid Table Group for {escape(table_name)} before syncing to eMenu.")

    filters = []
    if business_branch:
        filters.append("g.business_branch = %(business_branch)s")
    if group_name is not None:
        filters.append("g.name = %(group_name)s")
    group_filter = "WHERE " + " AND ".join(filters) if filters else ""
    values = {"business_branch": business_branch, "group_name": group_name, "table_name": table_name}
    group_rows = frappe.db.sql(f"""
        SELECT g.name AS source_name, g.integration_id,
            COALESCE(NULLIF(TRIM(g.table_group_name_en), ''), g.name) AS name,
            COALESCE(g.sort_order, 0) AS sort_order, COALESCE(g.disabled, 0) AS disabled
        FROM `tabTable Group` g
        {group_filter}
        ORDER BY g.name
        FOR UPDATE
    """, values, as_dict=True)
    if group_name is not None and not group_rows:
        if table_name is not None:
            frappe.throw(f"Choose a valid Table Group for {escape(table_name)} before syncing to eMenu.")
        return None

    if table_name is not None:
        # Disabling a group requires sending its inactive tables in the same batch.
        filters.append("(t.name = %(table_name)s OR COALESCE(g.disabled, 0) <> 0)")
    table_filter = "WHERE " + " AND ".join(filters) if filters else ""
    # Frappe keeps a renamed field's old database column after schema sync.
    legacy_id = ", t.integration AS legacy_id" if frappe.db.has_column("Tables Number", "integration") else ""
    table_rows = frappe.db.sql(f"""
        SELECT t.name AS source_name, t.integration_id, g.name AS group_name,
            t.tbl_number, COALESCE(t.sort_order, 0) AS sort_order,
            COALESCE(t.disabled, 0) AS disabled{legacy_id}
        FROM `tabTables Number` t
        LEFT JOIN `tabTable Group` g ON g.name = t.tbl_group
        {table_filter}
        ORDER BY t.name
        FOR UPDATE
    """, values, as_dict=True)
    if not group_rows and not table_rows:
        frappe.throw("There are no table groups or tables to sync for this selection.")

    groups_by_name = {}
    group_ids = set()
    for row in group_rows:
        groups_by_name[row["source_name"]] = {
            "id": _table_sync_id("Table Group", row, group_ids),
            "name": row["name"],
            "sort_order": row["sort_order"],
            "is_active": not row["disabled"],
        }

    tables = []
    table_ids = set()
    for row in table_rows:
        group = groups_by_name.get(row["group_name"])
        if group is None:
            frappe.throw(f"Choose a valid Table Group for {escape(row['source_name'])} before syncing to eMenu.")
        code = str(row["tbl_number"] or "").strip()
        if not code:
            frappe.throw(f"Enter a table number for {escape(row['source_name'])} before syncing to eMenu.")
        tables.append({
            "id": _table_sync_id("Tables Number", row, table_ids),
            "group_id": group["id"],
            "code": code,
            "label": code,
            "sort_order": row["sort_order"],
            "is_active": group["is_active"] and not row["disabled"],
        })
    return {"table_groups": list(groups_by_name.values()), "tables": tables}


def _canonical_uuid(value):
    if not isinstance(value, str):
        return None
    try:
        canonical = str(UUID(value))
    except ValueError:
        return None
    return canonical if canonical == value.lower() else None


def _table_sync_id(doctype, row, used_ids):
    name = row["source_name"]
    value = _ensure_integration_id(
        doctype, name, row["integration_id"],
        preferred_id=_canonical_uuid(row.get("legacy_id")), update_modified=True,
    )
    canonical = _canonical_uuid(value)
    if canonical is None:
        frappe.throw(f"The integration_id for {doctype} {escape(name)} must be a UUID.")
    if canonical in used_ids:
        frappe.throw(f"The integration_id for {doctype} {escape(name)} is used by another record in this sync.")
    used_ids.add(canonical)
    return canonical


def enqueue_product_emenu_sync(doc, method=None):
    if not frappe.conf.get("emenu_integration") or doc.flags.get("ignore_on_update"):
        return
    frappe.enqueue(
        sync_single_product_to_emenu,
        queue="default",
        timeout=120,
        enqueue_after_commit=True,
        product_name=doc.name,
    )


def set_emenu_integration_id(doc, method=None):
    if not frappe.conf.get("emenu_integration"):
        return
    existing = doc.get_doc_before_save()
    integration_id = doc.get("integration_id")
    if not integration_id and existing:
        integration_id = existing.get("integration_id")
        if not integration_id and doc.doctype == "Tables Number":
            # The sync job can still adopt this table's UUID from the legacy column.
            return
    if not integration_id or (
        existing is None and frappe.db.exists(doc.doctype, {"integration_id": integration_id})
    ):
        integration_id = str(uuid4())
    doc.integration_id = integration_id


def sync_single_product_to_emenu(product_name):
    api_url, api_key = _emenu_connection()
    products = prepare_product(product_name)
    if not products:
        if frappe.db.exists("Product", product_name):
            frappe.throw("Choose a valid Product Category before syncing to eMenu.")
        return

    product = products[0]
    category_name = product.pop("category_name")
    modified = get_datetime(product.pop("source_modified"))
    if modified.tzinfo is None:
        modified = modified.replace(tzinfo=ZoneInfo(get_system_timezone()))
    categories = prepare_category(category_name)
    if not categories:
        frappe.throw("Choose a category below All Product Categories before syncing to eMenu.")

    category_ids = {}
    for category in categories:
        name = category["name"]
        category["id"] = _ensure_integration_id("Product Category", name, category["id"])
        category_ids[name] = category["id"]
    for category in categories:
        category["parent_id"] = category_ids.get(category.pop("parent_name"))

    product["id"] = _ensure_integration_id("Product", product_name, product["id"])
    product["category_id"] = category_ids[category_name]
    product["menu_ids"] = _prepare_product_menu_ids(product_name)
    # Persist the UUIDs and release row locks before making the external request.
    frappe.db.commit()
    return _post_emenu_sync(
        api_url,
        api_key,
        PRODUCT_SYNC_PATH,
        {
            "sync_id": str(uuid4()),
            "source_updated_at": modified.astimezone(timezone.utc).isoformat(),
            "categories": categories,
            "product": product,
        },
        attempts=3,
        timeout=(5, 25),
    )


def _ensure_integration_id(doctype, name, integration_id, *, preferred_id=None, update_modified=False):
    if str(integration_id or "").strip():
        return integration_id
    # Another product job may have assigned a shared category ID since our read.
    current = frappe.db.get_value(
        doctype, name, "integration_id", as_dict=True, for_update=True
    )
    if current is None:
        frappe.throw(f"{doctype} {escape(name)} was removed before eMenu sync.")
    if str(current["integration_id"] or "").strip():
        return current["integration_id"]
    integration_id = preferred_id or str(uuid4())
    frappe.db.set_value(doctype, name, "integration_id", integration_id, update_modified=update_modified)
    return integration_id


def _emenu_connection():
    config = frappe.conf.get("emenu_integration") or {}
    if not isinstance(config, dict):
        frappe.throw("emenu_integration in site_config.json must be an object.")

    api_url = config.get("api_url")
    api_key = config.get("api_key")
    if not isinstance(api_url, str) or not api_url.strip():
        frappe.throw("Please configure emenu_integration.api_url in site_config.json.")
    if not isinstance(api_key, str) or not api_key.strip():
        frappe.throw("Please configure emenu_integration.api_key in site_config.json.")
    api_url = api_url.strip().rstrip("/")
    api_key = api_key.strip()
    try:
        parsed_url = urlsplit(api_url)
    except ValueError:
        frappe.throw("emenu_integration.api_url must be a valid HTTP(S) API base URL.")
    if (
        parsed_url.scheme not in ("http", "https")
        or not parsed_url.hostname
        or parsed_url.username
        or parsed_url.password
        or parsed_url.query
        or parsed_url.fragment
    ):
        frappe.throw("emenu_integration.api_url must be an HTTP(S) API base URL without credentials, a query or a fragment.")

    return api_url, api_key


def _post_emenu_sync(api_url, api_key, path, data, *, attempts=1, timeout=(10, 90), allow_layout_retry=False):
    payload = frappe.as_json(data).encode("utf-8")
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
    }
    for attempt in range(attempts):
        if attempt:
            sleep(2 ** (attempt - 1))
        last_attempt = attempt == attempts - 1
        try:
            response = requests.post(
                api_url + path, data=payload, headers=headers, timeout=timeout,
                allow_redirects=False,
            )
        except requests.exceptions.Timeout:
            if not last_attempt:
                continue
            frappe.throw("eMenu sync timed out. Please try syncing again.")
        except requests.exceptions.RequestException:
            if not last_attempt:
                continue
            frappe.throw("Could not connect to eMenu. Check emenu_integration.api_url and make sure the API is reachable from the Frappe server.")

        try:
            result = response.json()
        except ValueError:
            result = {}
        code = result.get("code") if isinstance(result, dict) else None
        if path == PRODUCT_SYNC_PATH and response.status_code == 409 and code == "STALE_SYNC":
            return "This product version has already been superseded in eMenu."
        if allow_layout_retry and response.status_code == 409 and code == "TABLE_GROUP_IN_USE":
            raise _TableGroupInUse()
        if last_attempt or not (
            response.status_code >= 500
            or response.status_code == 429
            or (response.status_code == 409 and code == "SYNC_CONFLICT")
        ):
            break

    if not 200 <= response.status_code < 300:
        error = result.get("error") if isinstance(result, dict) else None
        if not isinstance(error, str) or not error.strip():
            error = "The eMenu API rejected the sync request."
        error = escape(error.replace(api_key, "[redacted]"))
        request_id = result.get("requestId") if isinstance(result, dict) else None
        reference = (
            " (request ID: " + escape(request_id.replace(api_key, "[redacted]")) + ")"
            if isinstance(request_id, str) and request_id
            else ""
        )
        frappe.throw(
            "eMenu sync failed (HTTP {0}): {1}{2}".format(
                response.status_code, error, reference
            )
        )

    if (
        not isinstance(result, dict)
        or not isinstance(result.get("message"), str)
        or not result["message"].strip()
    ):
        frappe.throw("The eMenu API returned an unexpected response. Please check the configured API URL.")

    if path == TABLE_SYNC_PATH and isinstance(result.get("warnings"), list):
        warnings = [
            escape(warning["message"].replace(api_key, "[redacted]"))
            for warning in result["warnings"]
            if isinstance(warning, dict) and isinstance(warning.get("message"), str)
        ]
        return "\n".join([result["message"], *warnings])

    return result["message"]


def prepare_category(category_name=None):
    if category_name is None:
        selection = """
            c.name IN (SELECT product_code FROM `tabTemp Product Menu`)
            OR c.name IN (
                SELECT p.product_category
                FROM `tabProduct` p
                WHERE p.name IN (SELECT parent FROM `tabProduct Menu`)
            )
        """
        parent_name = ""
    else:
        selection = "c.name = %(category_name)s"
        parent_name = ", p.name AS parent_name"

    sql = f"""
        WITH RECURSIVE menu_categories AS (
            SELECT c.name, c.parent_product_category
            FROM `tabProduct Category` c
            WHERE {selection}

            UNION

            SELECT p.name, p.parent_product_category
            FROM `tabProduct Category` p
            JOIN menu_categories c ON p.name = c.parent_product_category
        )
        SELECT
            c.integration_id AS id,
            p.integration_id AS parent_id,
            c.name,
            c.name AS name_en,
            c.product_category_name_kh AS name_km,
            c.name AS name_zh,
            c.photo AS image_url,
            COALESCE(c.sort, 0) AS sort_order,
            1 AS is_active{parent_name}
        FROM menu_categories mc
        JOIN `tabProduct Category` c ON c.name = mc.name
        LEFT JOIN `tabProduct Category` p
            ON p.name = c.parent_product_category
            AND p.name <> 'All Product Categories'
        WHERE c.name <> 'All Product Categories'
    """
    return frappe.db.sql(sql, {"category_name": category_name}, as_dict=1)


def _prepare_menu_snapshot(products):
    rows = frappe.db.sql("""
        WITH RECURSIVE published_menus AS (
            SELECT name, NULLIF(TRIM(parent_pos_menu), '') AS parent_link
            FROM `tabPOS Menu`
            WHERE is_emenu = 1
                OR NULLIF(TRIM(parent_pos_menu), '') IS NULL

            UNION

            SELECT parent.name, NULLIF(TRIM(parent.parent_pos_menu), '')
            FROM `tabPOS Menu` parent
            JOIN published_menus child ON parent.name = child.parent_link
        )
        SELECT m.name, m.integration_id, published.parent_link, parent.name AS parent_name,
            m.pos_menu_name_kh AS name_km, m.pos_menu_name_en AS name_en,
            m.photo AS image_url, COALESCE(m.sort_order, 0) AS sort_order, m.disabled
        FROM published_menus published
        JOIN `tabPOS Menu` m ON m.name = published.name
        LEFT JOIN `tabPOS Menu` parent ON parent.name = published.parent_link
        ORDER BY m.name
    """, as_dict=True)
    menu_ids = {}
    used_ids = set()
    for row in rows:
        name = row["name"]
        value = _ensure_integration_id("POS Menu", name, row["integration_id"])
        menu_id = _canonical_uuid(value)
        if not menu_id or menu_id in used_ids:
            frappe.throw(f"POS Menu {escape(name)} must have a unique UUID in integration_id.")
        menu_ids[name] = menu_id
        used_ids.add(menu_id)

    menus = {}
    for row in rows:
        parent_name = _menu_parent_name(row, row["name"])
        menus[row["name"]] = {
            "id": menu_ids[row["name"]],
            "parent_id": menu_ids[parent_name] if parent_name is not None else None,
            "name_km": row["name_km"] or row["name_en"],
            "name_en": row["name_en"],
            "image_url": row["image_url"],
            "sort_order": row["sort_order"],
            "is_active": not row["disabled"],
        }
    product_ids = {_canonical_uuid(product["id"]) for product in products}
    root_sections = {}
    assignments = set()
    for row in _menu_assignments():
        product_id = _canonical_uuid(row["product_id"])
        menu = menus.get(row["menu_name"])
        if not product_id or product_id not in product_ids or not menu:
            continue

        target_id = _menu_section_id(menu["id"], menu["parent_id"])
        if not menu["parent_id"]:
            root_sections[target_id] = {
                "id": target_id,
                "parent_id": menu["id"],
                "name_km": menu["name_km"],
                "name_en": menu["name_en"],
                "sort_order": 0,
                "is_active": True,
            }
        assignments.add((target_id, product_id))

    return [*menus.values(), *root_sections.values()], [
        {"menu_id": menu_id, "product_id": product_id}
        for menu_id, product_id in sorted(assignments)
    ]


def _menu_assignments(product_name=None):
    return frappe.db.sql("""
        SELECT DISTINCT p.integration_id AS product_id, m.name AS menu_name,
            m.integration_id AS menu_id,
            NULLIF(TRIM(m.parent_pos_menu), '') AS parent_link, parent.name AS parent_name
        FROM `tabProduct Menu` link
        JOIN `tabProduct` p ON p.name = link.parent
        JOIN `tabPOS Menu` m ON m.name = link.pos_menu
        LEFT JOIN `tabPOS Menu` parent
            ON parent.name = TRIM(m.parent_pos_menu)
        WHERE link.parenttype = 'Product' AND m.is_emenu = 1
            AND (%(product_name)s IS NULL OR p.name = %(product_name)s)
    """, {"product_name": product_name}, as_dict=True)


def _menu_parent_name(row, menu_name):
    parent_name = row["parent_name"]
    if row["parent_link"] is not None and parent_name is None:
        frappe.throw(
            f"POS Menu {escape(menu_name)} links to missing parent {escape(row['parent_link'])}."
        )
    return parent_name


def _menu_section_id(menu_id, parent):
    # eMenu assigns products to submenus. Give direct root products a stable section.
    return menu_id if parent else str(uuid5(UUID(menu_id), "emenu-root-products"))


def _prepare_product_menu_ids(product_name):
    ids = set()
    for row in _menu_assignments(product_name):
        menu_id = _canonical_uuid(row["menu_id"])
        if not menu_id:
            frappe.throw(f"Run a full eMenu sync to register POS Menu {escape(row['menu_name'])}.")
        parent_name = _menu_parent_name(row, row["menu_name"])
        ids.add(_menu_section_id(menu_id, parent_name))
    return sorted(ids)


def prepare_product(product_name=None):
    if product_name is None:
        selection = "p.name IN (SELECT parent FROM `tabProduct Menu`)"
        webhook_columns = ""
        row_lock = ""
    else:
        selection = "p.name = %(product_name)s"
        webhook_columns = ", c.name AS category_name, p.modified AS source_modified"
        row_lock = "FOR UPDATE"

    sql = f"""
        select 
            p.integration_id as id,
            c.integration_id as category_id,
            p.name as code,
            p.product_name_en as name,
            p.product_name_en as name_en,
            p.product_name_en as name_zh,
            p.product_name_kh as name_km,
            coalesce(p.description,'')  as description,
            p.price,
            p.unit as unit,
            p.photo as image_url,
            p.available_in_emenu as is_available,
            p.is_featured,
            coalesce(p.sort_order,0) as sort_order{webhook_columns}

        from `tabProduct` p JOIN `tabProduct Category` c on c.name = p.product_category
        where {selection}
        {row_lock}
    """
    products =  frappe.db.sql(sql, {"product_name": product_name}, as_dict=1)

    # get product portion price
    products = _update_portion_to_products(products, _prepare_product_prices(product_name))
    modifier_groups = _prepare_product_modifier_groups(tuple(product["code"] for product in products))
    for product in products:
        product["modifier_groups"] = modifier_groups.get(product["code"], [])

    return products




def _update_portion_to_products(products, portions):
    portions_by_product = {}
    for row in portions:
        portion = dict(row)
        product_code = portion.pop("product_code")
        portions_by_product.setdefault(product_code, []).append(portion)

    for product in products:
        if product["code"] in portions_by_product:
            product["portions"] = portions_by_product[product["code"]]

    return products




def _prepare_product_modifier_groups(product_codes):
    if not product_codes:
        return {}

    rows = frappe.db.sql("""
        WITH selected_products AS (
            SELECT name, product_category
            FROM `tabProduct`
            WHERE name IN %(product_codes)s
        ), product_options AS (
            SELECT p.name AS product_code, m.name AS option_name, 1 AS source_order
            FROM selected_products p
            JOIN `tabModifiers` m ON m.parent = p.name
                AND m.parenttype = 'Product' AND m.parentfield = 'product_modifiers'

            UNION

            SELECT p.name, m.name, 0
            FROM selected_products p
            JOIN `tabModifier Group Product Category` link
                ON link.product_category = p.product_category
                AND link.parenttype = 'Modifier Group' AND link.parentfield = 'product_category'
            JOIN `tabModifiers` m ON m.parent = link.parent
                AND m.parenttype = 'Modifier Group' AND m.parentfield = 'modifiers'
        )
        SELECT mapped.product_code, category.name AS group_label,
            category.is_required, category.is_multiple,
            m.modifier_code AS option_label, COALESCE(m.prefix, '') AS prefix, coalesce(m.price,0) as price
        FROM product_options mapped
        JOIN `tabModifiers` m ON m.name = mapped.option_name
        JOIN `tabModifier Category` category ON category.name = m.modifier_category
        WHERE NULLIF(TRIM(m.modifier_code), '') IS NOT NULL
        ORDER BY mapped.product_code, category.name, mapped.source_order, m.parent, m.idx, m.name
    """, {"product_codes": product_codes}, as_dict=True)

    groups_by_product = {}
    for row in rows:
        groups = groups_by_product.setdefault(row["product_code"], {})
        group_label = row["group_label"]
        group = groups.setdefault(group_label, {
            "label_km": group_label,
            "label_en": group_label,
            "label_zh": group_label,
            "required": bool(row["is_required"]),
            "multiple": bool(row["is_multiple"]),
            "options": [],
        })
        option_label = row["option_label"]
        group["options"].append({
            "label_km": option_label,
            "label_en": option_label,
            "label_zh": option_label,
            "prefix": row["prefix"],
            "price": row["price"],
        })

    return {code: list(groups.values()) for code, groups in groups_by_product.items()}


def _prepare_product_prices(product_name = None):
    sql = """
        SELECT
            pp.parent AS product_code,
            b.integration_id AS branch_id,
            pp.portion AS label_km,
            pp.portion AS label_zh,
            pp.portion AS label_en,
            pp.unit,
            pp.price_rule,
            COALESCE(pp.price, 0) AS price
        FROM `tabProduct Price` pp
        LEFT JOIN `tabBusiness Branch` b
            ON b.name = pp.business_branch
        WHERE
            (%(product_name)s = '' OR pp.parent = %(product_name)s)
    """

    results = frappe.db.sql(
        sql,
        {"product_name": product_name or ""},
        as_dict=True
    )
    return results or []

def _validate_integration_id(doctype, field):
    sql = f"update `tab{doctype}` set {field} = uuid() where coalesce({field},'') = '' "
    frappe.db.sql(sql)
    frappe.db.commit()
 