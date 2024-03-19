import os
import numpy as np
import base64
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
def get_bill_template(station, name,template, reprint=0):
    doc = frappe.get_doc("Sale", name)
    data_template,css = frappe.db.get_value("POS Receipt Template","Receipt En",["template","style"])
    html= frappe.render_template(data_template, get_print_context(doc))
    return {"html":html,"css":css}

## END WINDOW SERVER PRINTING GENERATE HTML