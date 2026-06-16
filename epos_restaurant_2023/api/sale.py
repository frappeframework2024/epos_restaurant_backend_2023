import frappe 
import json
from collections import defaultdict
from epos_restaurant_2023.api.printing import get_kitchen_order_template
from epos_restaurant_2023.custom_socket_client import emit_event
            
@frappe.whitelist()
def runme():
    
    doc = frappe.as_json(frappe.get_cached_doc("Sale","SINV2026-0527"))
    doc = json.loads(doc)
    
    for sp in doc.get("sale_products"):
        sp["name"] =  ""

    return submit_order(data = { "doc": doc})

@frappe.whitelist(methods="POST")
def submit_order(data):
    doc = data.get("doc")
    
    # get submited product 
    _new_products = [d for d in doc.get("sale_products") if not d.get("name") or d.get("sale_product_status") == 'New']
    


    if doc:
        for sp in [x for x in doc.get("sale_products") if  not x.get("name") or x.get("sale_product_status") == 'New']:
            sp["order_time"] = str(frappe.utils.now_datetime())

        if doc.get("name"):
            doc = frappe.get_doc(doc)
            doc.insert()
        else:
            doc = frappe.get_doc(doc)
            doc.save()
    # return "done"
  
    
    pdf_data  = []
    print_docs= None
    if _new_products:
        
        frappe.enqueue(
            "epos_restaurant_2023.api.sale.generate_print_queue",
            queue="short",
            doc=doc,
            products=_new_products
        )
        
        # print_docs =  generate_print_queue(doc,_new_products)
        # for p in print_docs:
        #     pdf_data.append({
        #         "printer":p.get("printer_name"),
        #         "base64_data":get_kitchen_order_pdf(doc = p)
        #     })


    
    frappe.db.commit()

    
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
            # print_docs.append(print_data)
            emit_event("PrintKitchenOrderOnDesktop",{**queue_doc.data,"html":get_kitchen_order_template(doc=queue_doc)})

            

            
        elif pp.get("group_item_type") == "Printer cut by order line":
            for p in printer_proucts:
                print_data["sale_products"] = [p]
                queue_doc =  add_print_queue(doc.get("name"),print_data)
                # print_docs.append(print_data)
                emit_event("PrintKitchenOrderOnDesktop",{**queue_doc.data,"html":get_kitchen_order_template(doc=queue_doc)})

                
        else:
            for p in printer_proucts:
                for n in range(1,int(p.get("quantity") or 1) + 1):
                    print_data["index"] = n
                    print_data["sale_products"] = [p]
                    queue_doc =  add_print_queue(doc.get("name"),print_data)
                    # print_docs.append(print_data)
                    emit_event("PrintKitchenOrderOnDesktop",{**queue_doc.data,"html":get_kitchen_order_template(doc=queue_doc)})

                    

    if run_commit:
        frappe.db.commit()


def add_print_queue(sale, data):
    
    queue_doc = {
            "doctype":"Print Queue",
            "document_type":"Sale",
            "document_name":sale,
            "printer_name":data.get("printer_name"),
            "data":data
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
    return frappe.cached_value("User",frappe.session.user,"full_name")

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


 

    

