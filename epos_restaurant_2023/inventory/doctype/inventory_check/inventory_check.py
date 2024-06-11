# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InventoryCheck(Document):
	def validate(self):
		if self.check_type == "Partially Check":
			if len(self.product_categories) == 0:
				frappe.throw("Please select product category")
		get_products(self)

def get_products(self):
	data = []
	if self.check_type=="Partially Check":
		data =frappe.db.sql( "select name,product_name_en  from `tabProduct` where disabled=0 and is_inventory_product=1 and product_category in %(product_categories)s",{"product_categories":[d.product_category for d in self.product_categories]},as_dict=1)
	else:
		data =frappe.db.sql( "select name,product_name_en  from `tabProduct` where disabled=0 and is_inventory_product=1",as_dict=1)
	
	opening_data = get_opening_quantity(self, [d["name"] for d in data])
	current_data = get_current_quantity(self, [d["name"] for d in data])
	frappe.msgprint(str(current_data))
	for d in data:
		child_doc = frappe.new_doc("Inventory Check Items")
		child_doc.product_code = d["name"] 
		child_doc.product_name = d["product_name_en"] 
		child_doc.opening_quantity = sum([x["quantity"] for x in opening_data if x["product_code"] ==d["name"]])
		self.append("items", child_doc)
  

  
def get_opening_quantity(self,product_codes):
    sql = "select product_code, sum(in_quantity - out_quantity) as quantity from `tabInventory Transaction` where stock_location=%(stock_location)s and  transaction_date<%(date)s and product_code in %(product_codes)s group by product_code"
    data = frappe.db.sql(sql, {"date":self.posting_date, "stock_location": self.stock_location ,"product_codes":product_codes},as_dict=1 )
    
    return data
    
  
def get_current_quantity(self,product_codes):
    sql = "select product_code,transaction_type, sum(in_quantity - out_quantity) as quantity from `tabInventory Transaction` where stock_location=%(stock_location)s and  transaction_date=%(date)s and product_code in %(product_codes)s group by product_code,transaction_type"
    data = frappe.db.sql(sql, {"date":self.posting_date, "stock_location": self.stock_location ,"product_codes":product_codes},as_dict=1 )
    return data
    