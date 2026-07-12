import frappe
from epos_restaurant_2023.api import sale
from epos_restaurant_2023.api.api import get_sale_list_table_badge
from epos_restaurant_2023.api.change_merge_table import on_merge_order 
from epos_restaurant_2023.api.split_bill import on_save as on_split_bill ,get_sales as _get_split_sub_bill_list


@frappe.whitelist(methods=["POST"])
def get_sale_detail(sale_name):
    return sale.get_sale_detail(sale_name)


@frappe.whitelist(methods="POST")
def submit_order(data=None,print_request_bill=False,print_server_url=None,print_setting=None):
    result = sale.submit_order(data=data,print_request_bill=print_request_bill,print_server_url=print_server_url,print_setting = print_setting)
    return result


@frappe.whitelist(methods="POST")
def get_pending_order(data): 
    return get_sale_list_table_badge(data)

@frappe.whitelist(methods=["POST","GET"])
def get_sale_product_printers(sale_products=None):
    sale_products = [sale_products]
    products = sale.get_products(sale_products)
    product_printers = sale.get_printer_by_product([x.get("product_code") for x in products])

    def get_printer_names(printers):
        _printers = []
        for p in printers:
            _printers.append(
                {
                    "printer": p ,
                    "printer_name": frappe.get_cached_value("Printer",p, "printer_name")
                })
        return _printers

    for pp in product_printers:
        _pro = next((p for p in products if p.get("product_code") == pp.get("product_code")), {})
        pp["printers"] = get_printer_names(pp.get("printer_ids").split(","))
        pp.update(_pro)

    return product_printers


@frappe.whitelist(methods=["POST","GET"])
def get_sale_product_printers_by_sale_name(sale_name):
    sale_doc = frappe.get_cached_doc("Sale",sale_name)
    result = {}
    for sp in sale_doc.sale_products:
        result[sp.name] = get_sale_product_printers(sp)

    return result
    

@frappe.whitelist(methods=["POST","GET"])
def submit_resend_to_printer(doc=None,data=None,print_server_url=None):    
    return sale.submit_resend_product_to_printer(doc = doc,data = data,print_server_url=print_server_url)
    
@frappe.whitelist(methods=["POST"])
def merge_bill(source_doc_name,target_doc_name):
    data = on_merge_order(old_sale = source_doc_name, new_sale = target_doc_name)
    return data.get("data")

@frappe.whitelist(methods="POST")
def bulk_request_print_bill(sale_names, print_server_url=None, print_setting=None):
    can_print_sales = []
    for s in sale_names:
        if frappe.db.get_value("Sale",s,"sale_status") == "Submitted":
            can_print_sales.append(s)
            sale_status= frappe.get_cached_doc("Sale Status","Bill Requested")
            frappe.db.set_value("Sale",s,"sale_status_color",sale_status.background_color)
            frappe.db.set_value("Sale",s,"sale_status","Bill Requested")
            frappe.db.set_value("Sale",s,"sale_status_priority",sale_status.priority)
    frappe.throw(str(can_print_sales))

    if len(can_print_sales)>0:
            frappe.enqueue(
                "epos_restaurant_2023.api.sale.print_bill",
                queue="short",
                at_front=True,
                sale_name= can_print_sales,
                print_server_url=print_server_url,
                print_setting = print_setting
            )
            
            
    frappe.db.commit()

    return "Done"

@frappe.whitelist(methods="POST")
def print_bill(sale_name="SINV2026-0790", print_server_url=None, print_setting=None,additional_info={} ):
    sale.print_bill(sale_name=sale_name, print_server_url = print_server_url, print_setting = print_setting,additional_info=additional_info)
    return "Success"

@frappe.whitelist(methods=["POST","GET"])
def split_bill(data,current_sale_id):
    return  on_split_bill(data,current_sale_id)

    


@frappe.whitelist(methods=["POST","GET"])
def get_split_sub_bills(sale_id):
    return _get_split_sub_bill_list(sale_id)

