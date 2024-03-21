import numpy as np
import json
from PIL import Image

from epos_restaurant_2023.api.product import get_product_by_menu
from epos_restaurant_2023.api.api import get_system_settings
from epos_restaurant_2023.api.printing import (
    get_print_context, 
    print_bill,
    print_kitchen_order,
    print_waiting_slip,
    print_voucher_invoice,
    print_from_print_format
    )
import frappe

## WINDOW SERVER PRINTING GENERATE HTML
@frappe.whitelist(allow_guest=True)
def get_bill_template(name,template, reprint=0):
    doc = frappe.get_doc("Sale", name) 
    data_template,css = frappe.db.get_value("POS Receipt Template",template,["template","style"])
    html= frappe.render_template(data_template, get_print_context(doc,reprint))
    return {"html":html,"css":css}

@frappe.whitelist(allow_guest=True,methods='POST')
def get_kot_template(sale, products): 
    if not frappe.db.exists("Sale",sale):
        return ""    
    doc_sale = frappe.get_doc("Sale", sale)
    _products = products
    if type(products) is str:
        _products  = json.loads(products)
    data_template,css = frappe.db.get_value("POS Receipt Template","Kitchen Order",["template","style"])   
    html = frappe.render_template(data_template, get_print_context(doc=doc_sale,sale_products = _products))    
    return {"html":html,"css":css}

## END WINDOW SERVER PRINTING GENERATE HTML