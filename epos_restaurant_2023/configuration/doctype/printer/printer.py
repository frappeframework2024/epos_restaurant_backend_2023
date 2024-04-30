# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from escpos.printer import Network
from frappe.model.document import Document
import json
class Printer(Document):
	def validate(self):
		self.business_branch_printer = "{} > {}".format(self.business_branch, self.printer_name)
  
  
@frappe.whitelist()
def update_printer_to_product():
    update_to_product()
    
    data =frappe.db.sql( "select name from `tabProduct`",as_dict=1)
    for d in data:
        product_doc = frappe.get_doc("Product",d["name"])
        if product_doc.printers:
            printers= json.dumps(get_printer(product_doc))
            
            frappe.db.sql("update `tabTemp Product Menu` set printers=%(printers)s where product_code=%(product_code)s",{
				"printers":printers,
    			"product_code":d["name"]
			}) 
    frappe.db.commit()
    

def update_to_product():
    pritners = frappe.db.sql("select * from `tabPrinter`",as_dict=1)
    for p in pritners:
        frappe.db.sql("""update `tabProduct Printer` 
                      	set 
                       printer_name=%(printer_name)s,
                       group_item_type=%(group_item_type)s,
                       ip_address=%(ip_address)s,
                       port=%(port)s,
                       is_label_printer=%(is_label_printer)s,
                       usb_printing=%(usb_printing)s
                       where 
							printer=%(name)s
                       """,{
						   "printer_name":p["printer_name"],
						   "group_item_type":p["group_item_type"],
						   "ip_address":p["ip_address"],
						   "port":p["port"],
						   "is_label_printer":p["is_label_printer"],
						   "usb_printing":p["usb_printing"],
							"name":p["name"]
					   })
    frappe.db.commit()
    
        
def get_printer(doc):
	printers = []
	for p in doc.printers:
		printers.append({
				"printer":p.printer_name,
				"group_item_type":p.group_item_type,
				"ip_address":p.ip_address,
				"port":int(p.port or 0),
				"is_label_printer":p.is_label_printer,
				"usb_printing":p.usb_printing,
	})
	return printers