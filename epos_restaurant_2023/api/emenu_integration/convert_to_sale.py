import frappe
import json
import re

@frappe.whitelist()
def upsert_sale(**args):
    
    args.pop("cmd",None)
    ctx = args.get("context") or {}
    sale = ctx.get("sale") or {}
    order = ctx.get("order") or {}
    pos_profile = ctx.get("pos_profile") or ""
    pos_station = ctx.get("pos_station") or ""
    curr_usr = _get_current_user()
    now = frappe.utils.now() 
    
    def _sale_products():
        sale_products = []
          
        for product_data in order.get("products", []):                
            sale_product = _prepare_sale_product(product_data)
            sale_product.update({  
                "pos_profile": pos_profile,
                "order_by":curr_usr.get("employee_name"),
                "order_time": now,
                "time_in": now
            })            
            sale_products.append(sale_product)
            
        return sale_products
 
    if sale:
        doc_sale = frappe.get_doc("Sale", sale.get("name")) if sale.get("name") else None
        if doc_sale:      
            if doc_sale.docstatus != 0:
                frappe.throw("Cannot modify a submitted sale.")       
                
            doc_sale.sale_status = "Hold Order"
            doc_sale.extend("sale_products", _sale_products())                
            doc_sale.save()

        return {
            "sale": doc_sale,
            "message": "Order product was convert to sale: {}".format(doc_sale.name)
        }
        
    else:
        prepared = _prepare_new_sale(pos_profile, order)
        prepared.update({
            "created_by": curr_usr.get("employee_name"),
            "pos_station_name": pos_station,
            "sale_products": _sale_products()
        })
        
        doc = frappe.get_doc(prepared)
        doc.insert()  
        return  {
            "sale": doc,
            "message": "Order product was convert to new sale"
        }

def _prepare_new_sale(pos_profile, data):
    # get doc pos profile
    doc_profile = frappe.get_doc("POS Profile", pos_profile)
    stock_location = doc_profile.stock_location
    default_customer = doc_profile.default_customer
    price_rule = doc_profile.price_rule
    business_branch = doc_profile.business_branch
    outlet = doc_profile.outlet
    sale_type = doc_profile.default_sale_type
    
    # get table
    doc_table = frappe.get_doc("Tables Number", {"integration_id": data.get("table_id")}) if data.get("table_id") else None
    table_id = doc_table.name if doc_table else None
    tbl_number = doc_table.tbl_number if doc_table else None   
    
    # get customer
    doc_customer = frappe.get_cached_doc("Customer", default_customer) if default_customer else None
    
    # get currency cashier shift
    cashier_shift = frappe.db.get_value(
    "Cashier Shift",
        {
            "pos_profile": pos_profile,
            "is_closed": 0
        },
        "*",
        as_dict=True
    )

    doc = {
        "doctype": "Sale",
        "sale_status": "Hold Order",
        "cashier_shift": cashier_shift.name,
        "shift_name": cashier_shift.shift_name,
        "working_day": cashier_shift.working_day,
        "outlet": outlet,
        "stock_location": stock_location,
        "table_id": table_id,
        "tbl_number": tbl_number,
        "pos_profile": pos_profile,
        "customer": default_customer,
        "customer_photo": doc_customer.photo if doc_customer else None,
        "customer_name": doc_customer.customer_name_en if doc_customer else None,
        "customer_group": doc_customer.customer_group if doc_customer else None,
        "price_rule": price_rule,
        "business_branch": business_branch,
        "sale_products": [],
        "product_variants": [],
        "sale_type": sale_type,
        "discount_type": "Percent",
        "grand_total": 0,
        "guest_cover": 1,
        "discount": 0,
        "sub_total": 0,
        "deposit": 0,
        "payment": [],
        "commission_type": "Percent",
        "commission": 0,
        "commission_note": '',
        "commission_amount": 0, 
        "new_sale_default_pos_menu": "",
        "submitted_default_pos_menu": ""
    }
    return doc

def _prepare_sale_product( data):
    product_code = data.get("product_code")
    p = _prepare_product(product_code)        
   
    modifier = _get_choosed_modifier(data.get("modifiers", []))
    total_modifier_price= modifier.get("amount") or 0
    item_price =  (data.get("price") or 0) - total_modifier_price
    portion_name = "" if data.get("portion_name") is None or data.get("portion_name") == "Normal" else data.get("portion_name")
    p.update({
        "quantity": data.get("quantity", 1) or 1,
        "note": data.get("note", ""),
        "regular_price": item_price,
        "price": 0 if p.get("is_timer_product") else item_price,
        "sub_total": 0,
        "total_discount": 0,
        "total_tax": 0,
        "discount_amount": 0,
        "sale_discount_amount": 0,                
        "modifiers_price": total_modifier_price,      
        "kitchen_group_sort_order": p.get("kitchen_group_sort_order") or 0,
        "portion": portion_name,
        "is_free": 0,
        "discount_type": "Percent",   
        "discount":0,
        "sale_product_status": "New",
        "time_stop":0,
        "kod_status": "Pending",
        "is_newly_added":1,
    })
    
    return {**p, **modifier}
    

def _prepare_product( name):
    pro = frappe.get_doc("Product", name)
    printers = _get_product_printers(pro.printers)            
    return {
        "product_code": name,
        "product_name":pro.product_name_en,
        "product_name_kh":pro.product_name_kh,
        "revenue_group":pro.revenue_group,
        "unit":pro.unit,
        "product_tax_rule": "" if pro.tax_rule == "None" else (pro.tax_rule or ""),
        "product_variants":[],
        "use_combo_group": pro.use_combo_group,
        "combo_menu":"",
        "combo_menu_data":None,
        "is_require_employee": pro.is_require_employee,
        "is_timer_product": pro.is_timer_product,
        "rate_include_tax": pro.rate_include_tax,
        "variant_of":pro.variant_of,
        "is_variant": pro.is_variant,
        "pos_note": pro.pos_note,
        "printers": json.dumps(printers),        
        "append_quantity": pro.get("append_quantity") or 0,
        "allow_discount": pro.get("allow_discount") or 0,
        "allow_free":    pro.get("allow_free") or 0,
        "allow_change_price": pro.get("allow_change_price") or 0,
        "allow_crypto_claim": pro.get("allow_crypto_claim") or 0,
        "is_open_product": pro.get("is_open_product") or 0,
        "kitchen_group": pro.get("kitchen_group"),
    }

def _get_choosed_modifier(modifiers):
    json_modifiers = [
        {
            "idx": idx,
            "category": row.get("prefix") or None,
            "prefix": row.get("prefix") or None,
            "name": None,
            "modifier": row.get("label_en"),
            "price": row.get("price") or 0
        }
        for idx, row in enumerate(modifiers)
    ]

    modifier_names = ", ".join(
        "{}{}".format(
            row["prefix"] + " " if row["prefix"] else "",
            row["modifier"] or ""
        )
        for row in json_modifiers
    )

    return {
        "modifiers": modifier_names,
        "modifiers_data": json.dumps(json_modifiers, ensure_ascii=False),
        "amount": sum(row["price"] for row in json_modifiers)
    }

def _get_product_printers(printers):
    printers = [
        {
            "printer": row.printer_name,
            "actual_printer_name": row.actual_printer_name,
            "group_item_type": row.group_item_type,
            "ip_address": row.ip_address,
            "port": int(row.port or 9100),
            "is_label_printer": row.is_label_printer,
            "usb_printing": row.usb_printing
        }
        for row in printers
    ]
    
    return printers

def _get_current_user():
    curr_user = None
    if frappe.session.user and frappe.session.user != "Guest":
        curr_user = frappe.db.get_value(
            "Employee",
            {"user_id": frappe.session.user},
            ["name", "employee_name", "user_id","username"],
            as_dict=True
        )
    return curr_user

