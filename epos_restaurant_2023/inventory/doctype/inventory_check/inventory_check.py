# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, calculate_average_cost, get_last_inventory_transaction, get_uom_conversion, update_inventory_transaction_status
import frappe
from frappe.model.document import Document
from epos_restaurant_2023.controllers.base_controller import BaseController
class InventoryCheck(BaseController):
	def validate(self):
		if self.is_new():
			data = frappe.db.sql("select name from `tabInventory Check` where stock_location='{}' and docstatus=0".format(self.stock_location),as_dict=1)
			if data:
				frappe.throw("Please submit your pending inventory check first before create new inventory check")
   
   
		if self.check_type == "Partially Check":
			if len(self.product_categories) == 0:
				frappe.throw("Please select product category")

		if self.items:
			for d in [x for x in self.items if 
          (x.opening_quantity if x.opening_quantity is not None else 0) + 
          (x.sale if x.sale is not None else 0) + 
          (x.purchase if x.purchase is not None else 0) + 
          (x.other_transaction if x.other_transaction is not None else 0) + 
          (x.actual_quantity if x.actual_quantity is not None else 0) > 0]:
				d.difference = d.actual_quantity or 0 - d.current_on_hand or 0
		
  
		if self.is_new() or not self.items:
			get_products(self)
		
	def before_submit(self):
		# update product cost
		sql = """
			update `tabInventory Check Items` a
			join `tabStock Location Product` b on b.product_code = a.product_code and b.stock_location=%(stock_location)s
			set
				a.cost = b.cost
			where
				a.parent = %(name)s

  		"""
		frappe.db.sql(sql,{"stock_location": self.stock_location, "name":self.name})
	def on_submit(self):
		update_inventory_on_submit(self)
		# frappe.enqueue("epos_restaurant_2023.inventory.doctype.inventory_check.inventory_check.update_inventory_on_submit", queue='short', self=self)
	def on_cancel(self):
		update_inventory_on_cancel(self)
	
@frappe.whitelist()
def get_product_quantity_information(product_code,date,stock_location):
	product_doc = frappe.get_doc("Product",product_code)
	# opening data
	sql = "select  sum(in_quantity - out_quantity) as quantity from `tabInventory Transaction` where stock_location=%(stock_location)s and  transaction_date<%(date)s and product_code = %(product_code)s"
	opening_data = frappe.db.sql(sql, {"date":date, "stock_location": stock_location ,"product_code":product_code},as_dict=1 )

	# current data 
	sql = "select coalesce(transaction_type,'Not Set') as transaction_type, sum(in_quantity - out_quantity) as quantity from `tabInventory Transaction` where stock_location=%(stock_location)s and  transaction_date=%(date)s and product_code =  %(product_code)s group by coalesce(transaction_type,'Not Set') "
	current_data = frappe.db.sql(sql, {"date":date, "stock_location":stock_location ,"product_code":product_code},as_dict=1 )
	


	result =  {
		"product_code":product_doc.name,
		"product_name":product_doc.product_name_en,
		"unit": product_doc.unit,
		"has_expired_date": product_doc.has_expired_date,
		"expired_date": product_doc.expired_date,
		"opening_quantity": opening_data[0]["quantity"] or 0,
		"sale": sum([d["quantity"] for d in current_data if d["transaction_type"] =='Sale']),
		"purchase": sum([d["quantity"] for d in current_data if d["transaction_type"] =='Purchase Order']),
		"other_transaction":sum([d["quantity"] for d in current_data if not d["transaction_type"]  in ('Purchase Order','Sale')]),
		

	}
	result["current_on_hand"] = (result["opening_quantity"] or 0)  +  (result["sale"] or 0) + (result["purchase"] or 0)  + (result["other_transaction"] or 0)

	return result
  
		


def update_inventory_on_submit(self):
	
	for p in [ x for x in self.items if x.difference!=0]:
		# uom_conversion = (1 if (get_uom_conversion(p.base_unit, p.unit) or 0) == 0 else get_uom_conversion(p.base_unit, p.unit))
		uom_conversion = 1
		add_to_inventory_transaction({
			'doctype': 'Inventory Transaction',
			'transaction_type':"Inventory Check",
			'transaction_date':self.posting_date,
			'transaction_number':self.name,
			'product_code': p.product_code,
			'unit':p.unit,
			'stock_location':self.stock_location,
			'in_quantity': 0 if p.difference<0 else  abs( p.difference) / uom_conversion,
			'out_quantity': 0 if p.difference>0 else  abs(p.difference) / uom_conversion,
			"uom_conversion":uom_conversion,
			"price":calculate_average_cost(p.product_code,self.stock_location,(p.difference / uom_conversion),p.cost*uom_conversion),
			'note': 'New Inventory Check submitted.',
			"has_expired_date":p.has_expired_date,
			"expired_date":p.expired_date,
			'action': 'Submit'
		})
	
def update_inventory_on_cancel(self):
	for p in [ x for x in self.items if x.difference!=0]:
		# uom_conversion = (1 if (get_uom_conversion(p.base_unit, p.unit) or 0) == 0 else get_uom_conversion(p.base_unit, p.unit))
		uom_conversion = 1
		add_to_inventory_transaction({
			'doctype': 'Inventory Transaction',
			'transaction_type':"Inventory Check",
			'transaction_date':self.posting_date,
			'transaction_number':self.name,
			'product_code': p.product_code,
			'unit':p.unit,
			'stock_location':self.stock_location,
			'out_quantity': 0 if p.difference<0 else  abs(p.difference) / uom_conversion,
			'in_quantity': 0 if p.difference>0 else  abs(p.difference) / uom_conversion,
			"price": get_last_inventory_transaction(p.product_code,self.stock_location,self.name),
			'note': 'Inventory Check cancelled.',
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
		child_doc.current_on_hand = child_doc.opening_quantity +  child_doc.purchase +   child_doc.sale + child_doc.other_transaction 
		child_doc.actual_quantity = child_doc.current_on_hand
  
  

  
		self.append("items", child_doc)
  

  
def get_opening_quantity(self,product_codes):
    sql = "select product_code, sum(in_quantity - out_quantity) as quantity from `tabInventory Transaction` where stock_location=%(stock_location)s and  transaction_date<%(date)s and product_code in %(product_codes)s group by product_code"
    data = frappe.db.sql(sql, {"date":self.posting_date, "stock_location": self.stock_location ,"product_codes":product_codes},as_dict=1 )
    
    return data
    
  
def get_current_quantity(self,product_codes):
    sql = "select product_code,coalesce(transaction_type,'Not Set') as transaction_type, sum(in_quantity - out_quantity) as quantity from `tabInventory Transaction` where stock_location=%(stock_location)s and  transaction_date=%(date)s and product_code in %(product_codes)s group by product_code,coalesce(transaction_type,'Not Set') "
    data = frappe.db.sql(sql, {"date":self.posting_date, "stock_location": self.stock_location ,"product_codes":product_codes},as_dict=1 )
    return data
    