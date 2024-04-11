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
@frappe.whitelist()
def dome():
    return print_from_print_format(data = {
                "action" : "print_report",                
                "doc": "Working Day",
                "name":"WD2024-0008",
                "print_format": "Working Day Sale Summary",
                "pos_profile":"Main POS Profile",
                "outlet":"Main Outlet"
            })
    

## WINDOW SERVER PRINTING GENERATE HTML
@frappe.whitelist(allow_guest=True, methods="POST")
def get_bill_template(name,template, reprint=0):
    if not frappe.db.exists("Sale",name):
        return ""    
    doc = frappe.get_doc("Sale", name) 
    data_template,css = frappe.db.get_value("POS Receipt Template",template,["template","style"])
    html= frappe.render_template(data_template, get_print_context(doc,reprint))
    return {"html":html,"css":css}


## print waiting slip
@frappe.whitelist(allow_guest=True,methods='POST')
def get_waiting_slip_template(name):
    if not frappe.db.exists("Sale",name):
        return ""    
    doc = frappe.get_doc("Sale", name)
    data_template,css = frappe.db.get_value("POS Receipt Template","Waiting Slip",["template","style"])
    html= frappe.render_template(data_template, get_print_context(doc))
    return {"html":html,"css":css}


@frappe.whitelist(allow_guest=True, methods="POST")
def get_voucher_template(name):
    if not frappe.db.exists("Voucher",name):
        return ""    
    doc = frappe.get_doc("Voucher", name) 
    working_day = frappe.get_doc("Working Day",doc.working_day)

    doc.pos_profile = working_day.pos_profile
    data_template,css = frappe.db.get_value("POS Receipt Template","Voucher Reciept",["template","style"])
    html= frappe.render_template(data_template, get_print_context(doc))
    return {"html":html,"css":css}


@frappe.whitelist(allow_guest=True,methods='POST')
def get_kot_template(sale, printer_name, products): 
    if not frappe.db.exists("Sale",sale):
        return ""    
    doc_sale = frappe.get_doc("Sale", sale)
    _products = products
    if type(products) is str:
        _products  = json.loads(products)
    data_template,css = frappe.db.get_value("POS Receipt Template","Kitchen Order",["template","style"])   
    html = frappe.render_template(data_template, get_print_context(doc=doc_sale,sale_products = _products,printer_name=printer_name))    
    return {"html":html,"css":css}


## get Sticker Lable 
@frappe.whitelist(allow_guest=True,methods='POST')
def get_lable_order_template(sale, printer_name, products): 
    if not frappe.db.exists("Sale",sale):
        return ""    
    doc_sale = frappe.get_doc("Sale", sale)
    _products = products
    if type(products) is str:
        _products  = json.loads(products)
    data_template,css = frappe.db.get_value("POS Receipt Template","Lable Sticker",["template","style"])   
    html = frappe.render_template(data_template, get_print_context(doc=doc_sale,sale_products = _products,printer_name=printer_name))    
    return {"html":html,"css":css}

## print waiting slip
@frappe.whitelist(allow_guest=True,methods='POST')
def get_wifi_template(password):    
    data_template,css = frappe.db.get_value("POS Receipt Template","WiFi",["template","style"]) 
    html= frappe.render_template(data_template, {"password":password})
    return {"html":html,"css":css}

## print report Print Format
@frappe.whitelist(allow_guest=True,methods='POST')
def get_report_from_print_format_template(data):    
    return print_from_print_format(data,is_html=True)


## END WINDOW SERVER PRINTING GENERATE HTML