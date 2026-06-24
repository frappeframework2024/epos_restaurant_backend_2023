import frappe 
import json
from collections import defaultdict
from epos_restaurant_2023.api.printing import get_receipt_html,get_kitchen_order_template
from epos_restaurant_2023.custom_socket_client import emit_event
from  epos_restaurant_2023.api.print_server import process_print

@frappe.whitelist()
def runme():
 
    doc = frappe.as_json(frappe.get_cached_doc("Sale","SINV2026-0682"))
    doc = json.loads(doc)
    
    for sp in doc.get("sale_products"):
        sp["name"] =  ""

    return submit_order(data = { "doc": doc})



@frappe.whitelist(methods=["POST"])
def get_sale_detail(sale_name):
    return frappe.get_doc("Sale",sale_name)


@frappe.whitelist(methods="POST")
def submit_order(data=None,print_bill=False):
    doc = data.get("doc")
    
    
    # get Submitted product 
    
    _new_products = [d for d in doc.get("sale_products") if not d.get("name") or d.get("sale_product_status") == 'New']
    
    if doc:
        for sp in _new_products:
            sp["order_time"] = str(frappe.utils.now_datetime())

            sp["order_by"] = sp.get("order_by") or get_full_name() 
            sp["sale_product_status"] =  "Submitted" if sp.get("sale_product_status") == "New" else sp.get("sale_product_status") 


        if not doc.get("name"):
            doc = frappe.get_doc(doc)
            if print_bill:
                doc.sale_status = "Bill Requested"
                
            doc.insert()
        else:
            doc = frappe.get_doc(doc)
            if print_bill:
                doc.sale_status = "Bill Requested"
            
            doc.save()
    
             
    if _new_products:
        frappe.enqueue(
            "epos_restaurant_2023.api.sale.generate_print_queue",
            queue="short",
            doc=doc,
            products=_new_products,
            at_front=True
        )   

    
    frappe.db.commit()

    if data.get("print_bill_request"):
        frappe.throw("Print bill request")

    # enqueue add deleted product to Sale Product Deleted
    deleted_products = data.get("deleted_products") or []
    
    if len(deleted_products)>0:
        frappe.enqueue(
            "epos_restaurant_2023.api.sale.add_deleted_sale_products",
            queue="short",
            sale_doc=doc,
            deleted_products=deleted_products,
        )

    

    return {"doc":doc}
    
@frappe.whitelist(methods=["POST"])
def generate_print_queue(doc,products,run_commit = True):
    print_docs = []

    new_products = get_products(products)
    product_printers = get_product_pritners([x.get("product_code") for x in new_products])
    for pp in product_printers:
        printer_proucts = [d for d in new_products if d.get("product_code") in pp.get("product_codes").split(",")]
        print_data = {
            "printer_name":pp.get("printer_name"),
            "actual_printer_name":pp.get("actual_printer_name"),
            "ip_address":pp.get("ip_address"),
            "port":pp.get("port"),
            "sale":doc.get("name"),
            "tbl_number":doc.get("tbl_number"),
            "pos_station_name":doc.get("pos_station_name"),
            "pos_profile":doc.get("pos_profile"),
            "order_time": products[0].get("order_time"),
            "order_by": products[0].get("order_by") or get_full_name()
        }
        
        if pp.get("group_item_type") == "Printer cut by order":
            print_data["sale_products"] = printer_proucts

            queue_doc =  add_print_queue(doc.get("name"),print_data)
            print_docs.append(
                {
                    **queue_doc.data,
                    "print_queue": queue_doc.name,
                    "html":get_kitchen_order_template(doc=queue_doc),

                }
            )
            
        elif pp.get("group_item_type") == "Printer cut by order line":
            for p in printer_proucts:
                print_data["sale_products"] = [p]
                queue_doc =  add_print_queue(doc.get("name"),print_data)
                print_docs.append(
                    {
                        **queue_doc.data,
                        "print_queue": queue_doc.name,
                        "html":get_kitchen_order_template(doc=queue_doc),

                    }
                )
                
        else:
            for p in printer_proucts:
                for n in range(1,int(p.get("quantity") or 1) + 1):
                    print_data["index"] = n
                    print_data["sale_products"] = [p]
                    queue_doc =  add_print_queue(doc.get("name"),print_data)
                    print_docs.append(
                        {
                            **queue_doc.data,
                            "print_queue": queue_doc.name,
                            "html":get_kitchen_order_template(doc=queue_doc),

                        }
                    )
                    

    if run_commit:
        frappe.db.commit()
    
 
    process_print(print_docs,run_commit = run_commit)

    return print_docs


def add_print_queue(sale, data = None):
    
    queue_doc = {
            "doctype":"Print Queue",
            "document_type":"Sale",
            "document_name":sale,
            "printer_name":data.get("printer_name"),
            "data":data or "{}"
    }
    
    doc = frappe.get_doc(queue_doc).insert(ignore_permissions = True)
    return doc



def get_product_pritners(product_codes):
    sql = """
        SELECT
            GROUP_CONCAT(DISTINCT pp.parent ORDER BY pp.parent SEPARATOR ',') AS product_codes,
            p.printer_name,
            p.ip_address,
            p.port,
            p.group_item_type,
            p.actual_printer_name
        FROM `tabProduct Printer` pp
        JOIN `tabPrinter` p
            ON p.name = pp.printer
        WHERE pp.parent IN %(product_codes)s
        GROUP BY
            p.printer_name,
            p.ip_address,
            p.port,
            p.group_item_type,
            p.actual_printer_name;
    """
    return frappe.db.sql(sql,{"product_codes":product_codes},as_dict=1)



def get_full_name():
    return frappe.get_cached_value("User",frappe.session.user,"full_name")

    
def get_products(sale_products):
    products =[] 
    for sp in sale_products:
        products.append({
            "product_code":sp.get("product_code"),
            "product_name":sp.get("product_name"),
            "quantity":sp.get("quantity"),
            "price":sp.get("price"),
            "unit":sp.get("unit"),
            "note":sp.get("note"),
            "portion":sp.get("note"),
            "modifiers":sp.get("modifiers"),
            

            
        })

        if sp.get("combo_menu_data"):
            combo_data = json.loads(sp.get("combo_menu_data"))
            for c in combo_data:
                products.append({
                    "product_code":c.get("product_code"),
                    "product_name":c.get("product_name"),
                    "quantity":c.get("quantity"),
                    "price":c.get("price"),
                    
                })  
    return products

def add_deleted_sale_products(sale_doc,deleted_products,run_commit=True):
    for sp in deleted_products:
        frappe.get_doc({
            "doctype":"Sale Product Deleted",
            "sale_doc":sale_doc.name,
            "sale_date":sale_doc.posting_date,
            "sale_product_id": sp.get("name"),
            "product_name":sp.get("product_name"),
            "product_name_kh":sp.get("product_name_kh"),
            "quantity":sp.get("quantity"),
            "amount":sp.get("amount"),
            "deleted_by":sp.get("deleted_by"),
            "deleted_note":sp.get("deleted_note"),
            "sale_product":sp,
            "order_by":sp.get("order_by"),
            "order_time":sp.get("order_time") or frappe.utils.now_datetime(),
            "hide_in_kod":sp.get("hide_in_kod"),
            "kod_status": sp.get("kod_status"),
            "printers":sp.get("printers"),
            "portion":sp.get("portion"),
            "modifiers":sp.get("modifiers"),
            "combo_menu_data":sp.get("combo_menu_data"),
            "combo_menu":sp.get("combo_menu"),
            "note":sp.get("note"),
            "is_free":sp.get("is_free") or 0
        }).insert(ignore_permissions = True)
    
    if run_commit:
        frappe.db.commit()

@frappe.whitelist(methods="POST")
def bulk_request_print_bill(sale_names):

    frappe.msgprint("u print bill")



@frappe.whitelist(methods=["POST","GET"])
def print_bill(sale_name="SINV2026-0790",printer_name="Cashier Printer"):
    html = get_receipt_html(sale_name, "Receipt En Test",include_css=True)
    process_print({"printer_name":printer_name,"copies":2, "html":html,})





    

