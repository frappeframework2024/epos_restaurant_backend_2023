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
def submit_order(data=None,print_request_bill=False,print_server_url=None,print_setting=None):
    doc = data.get("doc")
    
    # get Submitted product 
    
    _new_products = [d for d in doc.get("sale_products") if not d.get("name") or d.get("sale_product_status") == 'New']
    
    sale_doc=None
    if doc:
        for sp in _new_products:
            if doc.get("sale_staus") not in ["Hold Order"]:
                sp["order_time"] = str(frappe.utils.now_datetime()) 
            sp["order_by"] = sp.get("order_by") or get_full_name() 
            sp["sale_product_status"] =  "Submitted" if sp.get("sale_product_status") == "New" and doc.get("sale_status") != 'Hold Order' else sp.get("sale_product_status") 


        if not doc.get("name"):
            sale_doc = frappe.get_doc(doc)
            if print_request_bill:
                sale_doc.sale_status = "Bill Requested"
                    
            sale_doc.insert()
        else:
            
            sale_doc = frappe.get_doc("Sale", doc["name"])
            
            _new_sale_products = [x for x in doc.get("sale_products") if not x.get("name")]
            doc["sale_products"] = [x for x in doc.get("sale_products") if x.get("name")]
            
            sale_doc.update(doc)
            for sp in _new_sale_products:
                sale_doc.append("sale_products",sp)

            if print_request_bill:
                sale_doc.sale_status = "Bill Requested"
            
            sale_doc.save()
            
            
    if sale_doc.sale_status == "Hold Order":
        _new_products = []

    deleted_products = data.get("deleted_products") or []
    if deleted_products:
        for x in deleted_products:
            x["is_deleted"] = 1
    


    if _new_products or len(deleted_products)>0:
        frappe.enqueue(
            "epos_restaurant_2023.api.sale.generate_print_queue",
            queue="short",
            doc=sale_doc,
            print_server_url = print_server_url,
            products=(_new_products or []) + (deleted_products or []) ,
            at_front=True
        )
        


    frappe.db.commit()
    
    if print_request_bill:
        frappe.enqueue(
            "epos_restaurant_2023.api.sale.print_bill",
            queue="short",
            sale_name= sale_doc.name,
            print_server_url = print_server_url,
            print_setting=print_setting

        )
        
    # enqueue add deleted product to Sale Product Deleted
    
    
    if len(deleted_products)>0:
        frappe.enqueue(
            "epos_restaurant_2023.api.sale.add_deleted_sale_products",
            queue="short",
            sale_doc=sale_doc,
            deleted_products=deleted_products,

        )
       

    

    return {"doc":sale_doc}
    
@frappe.whitelist(methods=["POST"])
def generate_print_queue(doc,products,print_server_url=None,run_commit = True):
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
                    
                    print_data["sale_products"] = [{**p,"quantity":1}]

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
    
 
    process_print(print_docs,print_server_url=print_server_url,run_commit = run_commit)

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

def get_printer_by_product(product_codes):
    sql = """
        SELECT
            GROUP_CONCAT(DISTINCT pp.printer ORDER BY pp.parent SEPARATOR ',') AS printer_ids,
            pp.parent as product_code
        FROM `tabProduct Printer` pp
        WHERE pp.parent IN %(product_codes)s
        GROUP BY
           pp.parent
    """
    return frappe.db.sql(sql,{"product_codes":product_codes},as_dict=1)



def get_full_name():
    return frappe.get_cached_value("User",frappe.session.user,"full_name")

    
def get_products(sale_products):
    products =[] 
    for sp in sale_products:
        products.append({
            "parent_product_name":sp.get("product_name"),
            "parent_product_kh":sp.get("product_name_kh"),
            "parent_quantity":sp.get("quantity"),
            "sale_product_id":sp.get("name"),
            "product_code":sp.get("product_code"),
            "product_name":sp.get("product_name"),
            "product_name_kh":sp.get("product_name_kh") or sp.get("product_name"),
            "quantity":sp.get("quantity"),
            "price":sp.get("price"),
            "unit":sp.get("unit"),
            "note":sp.get("note"),
            "portion":sp.get("portion"),
            "modifiers":sp.get("modifiers"),
            "order_by":sp.get("order_by"),
            "order_time":sp.get("order_time"),
            "is_deleted": sp.get("is_deleted") or 0,
            "deleted_by": sp.get("deleted_by") if sp.get("deleted_by") else get_full_name(),
            "deleted_note": sp.get("deleted_note") or "",
             
        })

        if sp.get("combo_menu_data"):
            combo_menu_data = sp.get("combo_menu_data").replace(":None", ":null")
            combo_data = json.loads(combo_menu_data )
  
            for c in combo_data:
                products.append({
                    "sale_product_id":sp.get("name"),
                    "product_code":c.get("product_code"),
                    "product_name":c.get("product_name"),
                    "product_name_kh": c.get("product_name_kh") or c.get("product_name"),
                    "quantity":(c.get("quantity") or 1) * (sp.get("quantity") or 1),
                    "price":c.get("price"),
                    "order_by": sp.get("order_by"),
                    "order_time": sp.get("order_time"),
                    "is_deleted": sp.get("is_deleted") or 0,
                    "deleted_by": sp.get("deleted_by") if sp.get("deleted_by") else get_full_name(),
                    "deleted_note": sp.get("deleted_note") or "",
                    
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




@frappe.whitelist(methods=["POST","GET"])
def print_bill(sale_name="SINV2026-0790", print_server_url=None, print_setting=None ):
    
    if not print_setting:
        print_setting = get_default_receipt_print_setting(frappe.get_cached_value("Sale", sale_name, "pos_profile"))
        
    if isinstance(sale_name,str):
        sale_name = [sale_name]

    
    print_data = []
    for s in sale_name:
        html = get_receipt_html(sale_name, print_setting.get("print_template") or "Default POS Receipt",include_css=True)
        print_data.append({
               
                    "printer_name":print_setting.get("printer") or "Cashier Printer",
                    "copies": print_setting.get("copies") or 1, 
                    "html":html
        })
    if print_data:
        process_print(data = print_data,print_server_url=print_server_url, retry = 4) #retry > 3 disable retry




def get_default_receipt_print_setting(pos_profile):
    cache = frappe.cache()
    key = f"api.sale.get_default_print_template::{pos_profile}"
    if not frappe.conf.developer_mode:
        cached = cache.get_value(key)
        if cached:
            return cached
    

    pos_config =  frappe.get_cached_value("POS Profile",pos_profile,"pos_config")
    sql = "select a.print_template,b.printer_name as printer, a.copies from `tabPOS Config Print Setting` a join `tabPrinter` b where a.parent = %(pos_config)s and a.print_type='Sale' limit 1"
    data = frappe.db.sql(sql,{"pos_config":pos_config},as_dict = 1)
    if data:
        data = data[0]
    cache.set_value(key, data, expires_in_sec=86400)
    return data



def submit_resend_product_to_printer(doc,data,print_server_url=None):
    print_docs = []
    printer_names  = set({
        printer.strip()
        for item in data
        for printer in item["printers"].split(",")
    })
    

    def expand_printers():
        result = []
        for d in data:
            printers = d.get("printers", "").split(",")
            for printer in printers:
                item = d.copy()
                item.pop("printers", None)
                item["printer"] = printer.strip()
                result.append(item)
        return result
    
    data_expand_printer =  expand_printers()


    def get_print_data(printer,products):

        data = {
            "actual_printer_name": printer.actual_printer_name,
            "is_reprint":1,
            "ip_address": printer.ip_address,
            "order_by": products[0].get("order_by"),
            "order_time": products[0].get("order_time"),
            "port": printer.port,
            "pos_profile": doc.get("pos_profile"),
            "pos_station_name": doc.get("pos_station_name"),
            "printer_name": printer.printer_name,
            "sale": doc.get("name"),
            "sale_products":  products,
            "tbl_number": doc.get("tbl_number")
        }
        return data
        

    def print_by_order(printer):
        print_docs.append( get_print_data(printer, [x for x in data_expand_printer if x.get("printer") == printer.name]))


    def print_by_order_line(printer):
        _products = [x for x in data_expand_printer if x.get("printer") == printer.name]
        for _p in _products:
            print_docs.append( get_print_data(printer, [_p]))


    def print_by_order_quantity(printer):
        _products = [x for x in data_expand_printer if x.get("printer") == printer.name]
        for _p in _products:
            for n in range(1,int(_p.get("quantity") or 1) + 1):
                _print_doc = get_print_data(printer, [{**_p,"quantity":1}])
                _print_doc["index"] = n
            print_docs.append( _print_doc)



    for _p in printer_names:
        _printer = frappe.get_cached_doc("Printer", _p)
        if _printer.group_item_type == "Printer cut by order":
            print_by_order(printer=_printer)
        elif _printer.group_item_type == "Printer cut by order line":
            print_by_order_line( printer=_printer)
        else:
            print_by_order_quantity(printer=_printer)

    print_jobs = []
    for pd in print_docs:
        queue_doc  = add_print_queue(doc.get("name"), pd)
        print_jobs.append(
            {
                **queue_doc.data,
                "print_queue": queue_doc.name,
                "html":get_kitchen_order_template(doc=queue_doc),
            }
        )

    frappe.db.commit()
    frappe.enqueue("epos_restaurant_2023.api.print_server.process_print",
        queue="short",
        at_front=True,
        data=print_jobs,
        print_server_url=print_server_url

    )
    

    
    return print_jobs





    

