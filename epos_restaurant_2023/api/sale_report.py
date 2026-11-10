import frappe 
import requests
import json
from frappe import _


# source site
api_url ="http://192.168.10.19:1216"
token = "token c7988962eef0dcc:0985a51ea46c343"


headers = {
    "Authorization": token
}

@frappe.whitelist(methods=["POST"])
def send_sale_to_report_site(sale_ids: str):
    if isinstance(sale_ids, str):
        sale_ids = frappe.parse_json(sale_ids)

    validate_synced_sales(sale_ids)
    send_validate_product_codes(sale_ids)
    sync_sale_data(sale_ids)


@frappe.whitelist()
def validate_synced_sales(sale_ids):
    if isinstance(sale_ids, str):
        sale_ids = frappe.parse_json(sale_ids)

    if not sale_ids:
        frappe.throw(_("No sales selected."))

    sale_ids = list(dict.fromkeys(sale_ids))

    sales = frappe.get_all(
        "Sale",
        filters={"name": ["in", sale_ids]},
        fields=[
            "name",
            "docstatus",
            "sale_status",
            "custom_is_sync_to_report_site",
        ],
    )

    sales_by_name = {sale.name: sale for sale in sales}
    errors = []

    for sale_id in sale_ids:
        if sale_id not in sales_by_name:
            errors.append(f"{sale_id}: Sale does not exist.")

    for sale_id in sale_ids:
        sale = sales_by_name.get(sale_id)

        if not sale:
            continue

        if sale.custom_is_sync_to_report_site:
            errors.append(f"{sale_id}: Already synced to the report site.")

        if sale.docstatus != 1:
            errors.append(
                f"{sale_id}: DocStatus is not Submitted; must be Submitted."
            )

        if sale.sale_status != "Closed":
            errors.append(
                f"{sale_id}: Sale Status is not Closed; must be Closed."
            )

    if errors:
        message = "<br>".join(
            f"{i}. {frappe.utils.escape_html(error)}"
            for i, error in enumerate(errors, start=1)
        )

        frappe.throw(
            _("Cannot sync sales.<br>{0}").format(
                message
            ),
            title=_("Sales Validation Failed"),
        )


@frappe.whitelist()
def sync_customers(sale_ids):
    url = f"{api_url}/api/method/epos_restaurant_2023.api.sale_report.sync_and_create_customers"
    if isinstance(sale_ids, str):
        sale_ids = frappe.parse_json(sale_ids)
        
    if not sale_ids:
        frappe.throw(_("No sales selected"))

    customers = frappe.get_all(
        "Sale",
        filters={"name": ["in", sale_ids]},
        pluck="customer"
    )

    customer_list = list(set(filter(None, customers)))
    
    if not customer_list:
        frappe.throw(_("No customers found for the selected sales."))    
        
    try:
        response = requests.post(
            url,
            headers=headers,
            json={"customers": customer_list},
            timeout=120
        )
    except requests.exceptions.RequestException as e:
        frappe.throw(_("Unable to connect to report site. Please try again later. Details: {0}").format(str(e)))

    if response.status_code != 200:
        frappe.throw(_("Report site returned an error (Status {0}): {1}").format(response.status_code, response.text))

    res_data = json.loads(response.text)
    
    message = res_data.get("message", [])
    if isinstance(message, dict):
        missing_customers = message.get("missing_customers", [])
    elif isinstance(message, list):
        missing_customers = message
    else:
        missing_customers = frappe.parse_json(message) if message else []
    
    if missing_customers:

        customer_docs = []
        fields_to_remove = ["modified_by", "owner", "idx", "_user_tags", "_comments", "_assign", "_liked_by"]
        
        for cust_name in missing_customers:
            doc = frappe.get_doc("Customer", cust_name)
            doc_dict = frappe.parse_json(frappe.as_json(doc.as_dict()))
            
            for field in fields_to_remove:
                doc_dict.pop(field, None)
            customer_docs.append(doc_dict)
            
        create_url = f"{api_url}/api/method/epos_restaurant_2023.api.sale_report.bulk_create_customers"
        try:
            create_response = requests.post(
                create_url,
                headers=headers,
                json={"customer_data": customer_docs},
                timeout=120
            )
        except requests.exceptions.RequestException as e:
            frappe.throw(_("Failed to sync new customers: {0}").format(str(e)))
            
        if create_response.status_code != 200:
            frappe.throw(_("Failed to create customers on report site: {0}").format(create_response.text))


@frappe.whitelist()
def sync_sale_data(sale_ids): 
    url = f"{api_url}/api/method/epos_restaurant_2023.api.sale_report.create_sales"
    if isinstance(sale_ids, str):
        sale_ids = frappe.parse_json(sale_ids)
    if not sale_ids:
        frappe.throw(_("No sales selected for syncing."))
    sales_docs = frappe.get_all(
        "Sale",
        filters={"name": ["in", sale_ids], "docstatus": 1, "sale_status": "Closed"},
        fields=["name", "closed_date"]
    )
    if not sales_docs:
        frappe.throw(_("Selected sales must be Submitted (DocStatus 1) and have a Closed sale status."))      
        
    sales_docs = sorted(sales_docs, key=lambda k: (str(k.get("closed_date") or ""), str(k.get("name") or "")))
    
    sync_customers(sale_ids)
    sync_working_days(sale_ids)
    sync_cashier_shifts(sale_ids)
        
    ordered_sale_ids = [d["name"] for d in sales_docs]   
    sale_data = [] 
    for sale_id in ordered_sale_ids:
        doc = frappe.get_doc("Sale", sale_id)
        doc_dict = frappe.parse_json(frappe.as_json(doc.as_dict()))
        
        original_name = doc_dict.get("name")
        doc_dict["original_sale_name"] = original_name
        
        fields_to_remove = [
            "modified_by", "owner", "idx", "_user_tags", "_comments", "_assign", "_liked_by", "name"
        ]
        for field in fields_to_remove:
            doc_dict.pop(field, None) 
        for table_key in ["sale_products", "payment", "trade_in_products", "cash_coupon_items"]:
            if table_key in doc_dict and isinstance(doc_dict[table_key], list):
                cleaned_rows = []
                for row in doc_dict[table_key]:
                    row_dict = dict(row)
                    for field in fields_to_remove:
                        row_dict.pop(field, None)
                    row_dict.pop("name", None)
                    cleaned_rows.append(row_dict)
                doc_dict[table_key] = cleaned_rows
        sale_data.append(doc_dict)
    try:
        response = requests.post(
            url,
            headers=headers,
            json={"sale_data": sale_data},
            timeout=120
        )
    except requests.exceptions.RequestException as e:
        frappe.throw(_("Connection error while syncing sales: {0}").format(str(e)))
    if response.status_code != 200:
        frappe.throw(_("Sync failed with status code {0}: {1}").format(response.status_code, response.text))
    res_data = json.loads(response.text)
    success_sales = res_data.get("message", [])
    if success_sales:
        frappe.db.set_value(
            "Sale", 
            {"name": ["in", ordered_sale_ids]}, 
            "custom_is_sync_to_report_site", 
            1, 
            update_modified=False
        )
        frappe.db.commit()
    return {"status": "success", "synced_count": len(ordered_sale_ids)}


@frappe.whitelist()
def send_validate_product_codes(sale_ids):
    url = f"{api_url}/api/method/epos_restaurant_2023.api.sale_report.validate_product_codes"
    if isinstance(sale_ids, str):
        sale_ids = frappe.parse_json(sale_ids)

    product_codes = []
    for sale_id in sale_ids:
        doc = frappe.get_doc("Sale", sale_id)
        for item in doc.get("sale_products", []):
            code = item.get("product_code")
            if code:
                product_codes.append(code)
    
    product_codes = list(set(filter(None, product_codes)))
    if not product_codes:
        return

    try:
        response = requests.post(
            url,
            headers=headers,
            json={"product_codes": product_codes},
            timeout=120
        )
    except requests.exceptions.RequestException as e:
        frappe.throw(f"Connection error during product validation: {str(e)}")
    
    if not response.ok:
        frappe.throw(f"Validation failed (Status {response.status_code}): {response.text}")
    res_json = response.json()
    missing_codes = res_json.get("message", []) if isinstance(res_json, dict) else res_json
    if missing_codes and len(missing_codes) > 0:
        placeholders = ", ".join(["%s"] * len(missing_codes))
        sql = f"""
            SELECT GROUP_CONCAT(CONCAT(name, ' - ', product_name_en) SEPARATOR ',') AS names
            FROM `tabProduct` WHERE name IN ({placeholders});
        """
        msg_result = frappe.db.sql(sql, tuple(missing_codes), as_dict=1)
        
        product_names = msg_result[0].get("names") if msg_result else None
        if not product_names:
            product_names = ", ".join(missing_codes)

        msg = "Products do not exist.<br>" + product_names.replace(",", "<br>")
        frappe.throw(str(msg))


@frappe.whitelist()
def sync_working_days(sale_ids):
    url = f"{api_url}/api/method/epos_restaurant_2023.api.sale_report.bulk_create_working_days"
    if isinstance(sale_ids, str):
        sale_ids = frappe.parse_json(sale_ids)
        
    working_days = []
    for sale_id in sale_ids:
        wd = frappe.db.get_value("Sale", sale_id, "working_day")
        if wd:
            working_days.append(wd)
            
    working_days = list(set(working_days))
    if not working_days:
        return

    docs = []
    fields_to_remove = ["modified_by", "owner", "idx", "_user_tags", "_comments", "_assign", "_liked_by"]
    for name in working_days:
        doc = frappe.get_doc("Working Day", name)
        doc_dict = frappe.parse_json(frappe.as_json(doc.as_dict()))
        for f in fields_to_remove:
            doc_dict.pop(f, None)
        docs.append(doc_dict)
        
    try:
        res = requests.post(url, headers=headers, json={"data": docs}, timeout=120)
    except requests.exceptions.RequestException as e:
        frappe.throw(_("Connection error during Working Day sync: {0}").format(str(e)))
        
    if res.status_code != 200:
        frappe.throw(_("Failed to sync Working Days on report site: {0}").format(res.text))


@frappe.whitelist()
def sync_cashier_shifts(sale_ids):
    url = f"{api_url}/api/method/epos_restaurant_2023.api.sale_report.bulk_create_cashier_shifts"
    if isinstance(sale_ids, str):
        sale_ids = frappe.parse_json(sale_ids)
        
    shifts = []
    for sale_id in sale_ids:
        sh = frappe.db.get_value("Sale", sale_id, "cashier_shift")
        if sh:
            shifts.append(sh)
            
    shifts = list(set(shifts))
    if not shifts:
        return

    docs = []
    fields_to_remove = ["modified_by", "owner", "idx", "_user_tags", "_comments", "_assign", "_liked_by"]
    for name in shifts:
        doc = frappe.get_doc("Cashier Shift", name)
        doc_dict = frappe.parse_json(frappe.as_json(doc.as_dict()))
        for f in fields_to_remove:
            doc_dict.pop(f, None)
        docs.append(doc_dict)
        
    try:
        res = requests.post(url, headers=headers, json={"data": docs}, timeout=120)
    except requests.exceptions.RequestException as e:
        frappe.throw(_("Connection error during Cashier Shift sync: {0}").format(str(e)))
        
    if res.status_code != 200:
        frappe.throw(_("Failed to sync Cashier Shifts on report site: {0}").format(res.text))



# target site
@frappe.whitelist(methods=["POST"])
def validate_product_codes():
    data = frappe.request.get_json() or frappe.form_dict
    product_codes = data.get("product_codes", [])
    
    if isinstance(product_codes, str):
        product_codes = frappe.parse_json(product_codes)
        
    if not product_codes:
        return []

    existing_products = frappe.get_all(
        "Product",
        filters={"name": ["in", product_codes]},
        pluck="name"
    )
    
    missing_codes = list(set(product_codes) - set(existing_products))
    return missing_codes

@frappe.whitelist(methods=["POST"])
def sync_and_create_customers(*args, **kwargs):
    data = frappe.request.get_json(silent=True) or frappe.form_dict or kwargs
    customers = data.get("customers", [])
    
    if isinstance(customers, str):
        customers = frappe.parse_json(customers)
        
    if not customers:
        return []

    existing_customers = frappe.get_all(
        "Customer",
        filters={"name": ["in", customers]},
        pluck="name"
    )
    
    missing_customers = list(set(customers) - set(existing_customers))
    return missing_customers


@frappe.whitelist(methods=["POST"])
def bulk_create_customers(*args, **kwargs):
    data = frappe.request.get_json(silent=True) or frappe.form_dict or kwargs
    customer_data = data.get("customer_data", [])
    if isinstance(customer_data, str):
        customer_data = frappe.parse_json(customer_data)
    created_customers = []
    
    for c in customer_data:
        try:
            c_name = c.get("name")
            if c_name and frappe.db.exists("Customer", c_name):
                continue
                
            # c.pop("name", None)
            doc = frappe.get_doc(c)
            doc.flags.ignore_permissions = True
            doc.flags.ignore_mandatory = True
            doc.flags.ignore_validate = True
            doc.insert(ignore_permissions=True)
            created_customers.append(doc.name)
        except Exception as e:
            frappe.db.rollback()
            frappe.local.response["http_status_code"] = 500
            return {"exc": str(frappe.get_traceback())}
    frappe.db.commit()
    return {"status": "success", "created": created_customers}



@frappe.whitelist(methods=["POST"])
def sync_and_create_working_days(*args, **kwargs):
    data = frappe.request.get_json(silent=True) or frappe.form_dict or kwargs
    working_days = data.get("working_days", [])
    if isinstance(working_days, str):
        working_days = frappe.parse_json(working_days)
    if not working_days:
        return []

    existing = frappe.get_all("Working Day", filters={"name": ["in", working_days]}, pluck="name")
    missing = list(set(working_days) - set(existing))
    return missing


@frappe.whitelist(methods=["POST"])
def bulk_create_working_days(*args, **kwargs):
    data = frappe.request.get_json(silent=True) or frappe.form_dict or kwargs
    doc_data = data.get("data", [])
    if isinstance(doc_data, str):
        doc_data = frappe.parse_json(doc_data)
        
    for d in doc_data:
        try:
            d_name = d.get("name")
            if d_name and frappe.db.exists("Working Day", d_name):
                doc = frappe.get_doc("Working Day", d_name)
                doc.update(d)
                doc.flags.ignore_permissions = True
                doc.flags.ignore_version = True
                doc.db_update()
            else:
                doc = frappe.get_doc(d)
                doc.flags.ignore_permissions = True
                doc.flags.ignore_version = True
                doc.db_insert()
        except Exception as e:
            frappe.db.rollback()
            frappe.local.response["http_status_code"] = 500
            return {"exc": str(frappe.get_traceback())}
            
    frappe.db.commit()
    return {"status": "success"}


@frappe.whitelist(methods=["POST"])
def sync_and_create_cashier_shifts(*args, **kwargs):
    data = frappe.request.get_json(silent=True) or frappe.form_dict or kwargs
    shifts = data.get("shifts", [])
    if isinstance(shifts, str):
        shifts = frappe.parse_json(shifts)
    if not shifts:
        return []
    existing = frappe.get_all("Cashier Shift", filters={"name": ["in", shifts]}, pluck="name")
    missing = list(set(shifts) - set(existing))
    return missing


@frappe.whitelist(methods=["POST"])
def bulk_create_cashier_shifts(*args, **kwargs):
    data = frappe.request.get_json(silent=True) or frappe.form_dict or kwargs
    doc_data = data.get("data", [])
    if isinstance(doc_data, str):
        doc_data = frappe.parse_json(doc_data) 
        
    for d in doc_data:
        try:
            d_name = d.get("name")
            if d_name and frappe.db.exists("Cashier Shift", d_name):
                doc = frappe.get_doc("Cashier Shift", d_name)
                doc.update(d)
                doc.flags.ignore_permissions = True
                doc.flags.ignore_version = True
                doc.db_update()
            else:
                doc = frappe.get_doc(d)
                doc.flags.ignore_permissions = True
                doc.flags.ignore_version = True
                doc.db_insert()
        except Exception as e:
            frappe.db.rollback()
            frappe.local.response["http_status_code"] = 500
            return {"exc": str(frappe.get_traceback())}   
            
    frappe.db.commit()
    return {"status": "success"}


@frappe.whitelist(methods=["POST"])
def create_sales(*args, **kwargs): 
    data = frappe.request.get_json(silent=True) or {}
    sale_data = data.get("sale_data", [])
    if isinstance(sale_data, str):
        sale_data = frappe.parse_json(sale_data)
        
    success_sales = []
    for s in sale_data:
        try:
            original_name = s.get("original_sale_name") or "Unknown"
            source_url = s.get("source_url") or ""
            
            working_day = s.get("working_day")
            cashier_shift = s.get("cashier_shift")
            
            s.pop("original_sale_name", None)
            s.pop("source_url", None)
            s.pop("name", None)
            
            s.pop("custom_bill_number", None)
            s.pop("custom_bill_number_prefix", None)
            
            orig_creation = s.get("creation")
            orig_modified = s.get("modified")
            orig_posting_date = s.get("posting_date")
            
            s["docstatus"] = 0
            
            doc = frappe.get_doc(s)
            
            if working_day:
                doc.working_day = working_day
            if cashier_shift:
                doc.cashier_shift = cashier_shift
                
            doc.flags.ignore_links = True
            doc.flags.ignore_mandatory = True
            doc.flags.ignore_validate = True #False
            doc.flags.ignore_version = True
            doc.flags.ignore_permissions = True
            
            doc.insert(ignore_permissions=True)
            
            if working_day or cashier_shift:
                frappe.db.set_value("Sale", doc.name, {
                    "working_day": working_day,
                    "cashier_shift": cashier_shift
                }, update_modified=False)
                doc.reload()

            # EXECUTE BILL NUMBER GENERATION, match Server Script logic
            if not doc.custom_bill_number and doc.pos_profile:
                pos_config_name = frappe.db.get_value("POS Profile", doc.pos_profile, "pos_config")
                if pos_config_name:
                    pos_config = frappe.db.get_value(
                        "POS Config", 
                        pos_config_name, 
                        ["pos_bill_number_prefix", "generate_bill_number_on_create"], 
                        as_dict=1
                    )
                    if pos_config and pos_config.pos_bill_number_prefix:
                        doc.custom_bill_number_prefix = pos_config.pos_bill_number_prefix

                        if hasattr(doc, "get_auto_name"):
                            doc.custom_bill_number = doc.get_auto_name()
                        doc.db_set("custom_bill_number_prefix", doc.custom_bill_number_prefix, update_modified=False)
                        doc.db_set("custom_bill_number", doc.custom_bill_number, update_modified=False)

            doc.submit()
            
            update_fields = {}
            if orig_creation:
                update_fields["creation"] = orig_creation
            if orig_modified:
                update_fields["modified"] = orig_modified
            if orig_posting_date:
                update_fields["posting_date"] = orig_posting_date
                
            if update_fields:
                frappe.db.set_value("Sale", doc.name, update_fields, update_modified=False)
                
            if source_url:
                sale_link = f"{source_url}/app/sale/{original_name}"
                source_display = f'<a href="{sale_link}" target="_blank">{source_url}</a>'
            else:
                source_display = "Source Site"

            target_doc = frappe.get_doc("Sale", doc.name)
            target_doc.add_comment(
                "Comment", 
                text=f"<b>Synced from source site.</b> Original Sale ID: {original_name}"
            )
            success_sales.append(doc.name)
        except Exception as e:
            frappe.db.rollback()
            frappe.local.response["http_status_code"] = 500
            return {"exc": str(frappe.get_traceback())}
            
    frappe.db.commit()
    return success_sales

