import json
import time
import frappe
import base64
from py_linq import Enumerable
from frappe.utils import today, add_to_date
from datetime import datetime, timedelta
from frappe import _


@frappe.whitelist()
def on_save(data,current_sale_id ): 
    
    for d in [ r for r in data if not r["temp_deleted"]]:       
            doc = frappe.get_doc(d)
            doc.save() 

    for d in [ r for r in data if r["temp_deleted"]]:  
        if d["name"]: 
            frappe.delete_doc("Sale", str(d["name"]))
            # # Fetch the document
            # doc = frappe.get_doc("Sale", str(d["name"]))

            # # Manually clear the sale_products child table
            # # doc.sale_products = []

            # # Update the other fields
            # doc.db_set('deleted_by', 'Split Bill')
            # doc.db_set('deleted_note', 'Auto Delete by Split Bill')
            # doc.db_set('status', 'Cancelled')
            
            # # Transition the document to Cancelled directly (docstatus = 2)
            # doc.db_set('docstatus', 2)  # This bypasses workflow restrictions, use cautiously

            # # Save the document
            # # doc.save()

            # # Reload the document to ensure changes are reflected
            # doc.reload()


    frappe.db.commit()

    _current_sale = frappe.get_doc("Sale",str(current_sale_id))

    return _current_sale


@frappe.whitelist()
def get_sales(sale_id ): 
    sale = frappe.get_doc("Sale", str(sale_id))
    sales = []
     
    sale_list = frappe.get_list("Sale",
                                limit_page_length=100,
                                filters={
                                    'name':['!=',sale.name], 
                                    'table_id':sale.table_id,
                                    'cashier_shift':sale.cashier_shift,
                                    'docstatus':0
                                })
    for s in sale_list:
        doc = frappe.get_doc("Sale", str(s.name))
        sales.append(doc)

    return sales