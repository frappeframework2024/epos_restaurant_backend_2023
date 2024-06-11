# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, get_uom_conversion
import frappe
from frappe.model.document import Document


class InventoryCheck(Document):
	def validate(self):
		if self.check_type == "Partially Check":
			if len(self.product_categories) == 0:
				frappe.throw("Please select product category")

		if self.items:
			for d in [x for x in self.items if x.opening_quantity +  x.sale + x.purchase + x.other_transaction + x.actual_quantity > 0]:
				d.difference = d.actual_quantity - d.current_on_hand
		
  
		if self.is_new() or not self.items:
			get_products(self)

	# def before_submit(self):
	# 	# remove un change option
	# 	[self.remove(d) for d in  [x for x in self.items if x.actual_quantity == x.current_on_hand]]
	def on_submit(self):
		frappe.enqueue("epos_restaurant_2023.inventory.doctype.inventory_check.inventory_check.update_inventory_on_submit", queue='short', self=self)



def update_inventory_on_submit(self):
	
	for p in self.purchase_order_products:
		if p.is_inventory_product:
			uom_conversion = (1 if (get_uom_conversion(p.base_unit, p.unit) or 0) == 0 else get_uom_conversion(p.base_unit, p.unit))
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Purchase Order",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.product_code,
				'unit':p.unit,
				'stock_location':self.stock_location,
				'in_quantity':p.quantity / uom_conversion,
				"uom_conversion":uom_conversion,
				"price":calculate_average_cost(p.product_code,self.stock_location,(p.quantity / uom_conversion),p.cost*uom_conversion),
				'note': 'New purchase order submitted.',
				"has_expired_date":p.has_expired_date,
				"expired_date":p.expired_date,
    			'action': 'Submit'
			})

 
			
def update_inventory_on_cancel(self):
	for p in self.purchase_order_products:
		if p.is_inventory_product:
			uom_conversion = (1 if (get_uom_conversion(p.base_unit, p.unit) or 0) == 0 else get_uom_conversion(p.base_unit, p.unit))
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Purchase Order",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.product_code,
				'unit':p.unit,
				'stock_location':self.stock_location,
				'out_quantity':p.quantity / uom_conversion,
				"price": get_last_inventory_transaction(p.product_code,self.stock_location,self.name),
				'note': 'Purchase order cancelled.',
				'action': 'Cancel'
			})
			update_inventory_transaction_status(self.name)
		
  


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
		child_doc.sale = sum([x["quantity"] for x in current_data if x["product_code"] ==d["name"] and x["transaction_type"] == "Sale"])
		child_doc.purchase = sum([x["quantity"] for x in current_data if x["product_code"] ==d["name"] and x["transaction_type"] == "Purchase Order"])
		child_doc.other_transaction = sum([x["quantity"] for x in current_data if x["product_code"] ==d["name"] and not x["transaction_type"] in ["Purchase Order","Sale"]])
		child_doc.current_on_hand = (child_doc.opening_quantity+ child_doc.purchase)   -  child_doc.sale  
		child_doc.actual_quantity = child_doc.current_on_hand
  
  

  
		self.append("items", child_doc)
  

  
def get_opening_quantity(self,product_codes):
    sql = "select product_code, sum(in_quantity - out_quantity) as quantity from `tabInventory Transaction` where stock_location=%(stock_location)s and  transaction_date<%(date)s and product_code in %(product_codes)s group by product_code"
    data = frappe.db.sql(sql, {"date":self.posting_date, "stock_location": self.stock_location ,"product_codes":product_codes},as_dict=1 )
    
    return data
    
  
def get_current_quantity(self,product_codes):
    sql = "select product_code,transaction_type, sum(in_quantity - out_quantity) as quantity from `tabInventory Transaction` where stock_location=%(stock_location)s and  transaction_date=%(date)s and product_code in %(product_codes)s group by product_code,transaction_type"
    data = frappe.db.sql(sql, {"date":self.posting_date, "stock_location": self.stock_location ,"product_codes":product_codes},as_dict=1 )
    return data
    