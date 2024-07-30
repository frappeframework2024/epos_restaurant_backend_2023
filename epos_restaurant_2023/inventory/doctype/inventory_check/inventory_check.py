# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, calculate_average_cost, get_last_inventory_transaction, get_uom_conversion, update_inventory_transaction_status
import frappe
from frappe.model.document import Document
from epos_restaurant_2023.controllers.base_controller import BaseController
from epos_restaurant_2023.inventory.doctype.inventory_check.general_ledger_entry import submit_inventory_check_general_ledger_entry
class InventoryCheck(BaseController):
	def validate(self):
		# validate date with inventory transaction
		# inventory check date master be greater than or equal to last inventory transaction
		last_inventory_transaction  =frappe.db.sql( "select max(transaction_date) as date from `tabInventory Transaction`",as_dict=1)
		if last_inventory_transaction:
			if frappe.utils.getdate(self.posting_date)<frappe.utils.getdate(last_inventory_transaction[0]["date"]):
				frappe.throw("Inventory check date must be greater than or equal to last inventory transaction date")
  
		if self.is_new():
			data = frappe.db.sql("select name from `tabInventory Check` where stock_location='{}' and docstatus=0".format(self.stock_location),as_dict=1)
			if data:
				frappe.throw("Please submit your pending inventory check first before create new inventory check")

		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			validate_account(self)
   
   
		if self.check_type == "Partially Check":
			if len(self.product_categories) == 0:
				frappe.throw("Please select product category")

		if self.items:
			for d in [x for x in self.items if x.actual_quantity!=x.current_on_hand]:
				d.difference = (d.actual_quantity or 0) - (d.current_on_hand or 0)
			
			for d in [x for x in  self.items  if ( x.current_on_hand * x.original_cost) != (x.actual_quantity * x.cost) ]:
				d.total_difference_cost = (d.actual_quantity * d.cost) - (d.current_on_hand * d.original_cost)
		
  
		if self.is_new() or not self.items:
			get_products(self)
   
		# validate duplcate item
		if len(self.items) != len(set([d.product_code for d in self.items])):
			is_valid, product_code,product_name = validate_no_duplicate_codes(self.items)
			if not is_valid:
				frappe.throw("Product {} - {} is duplicated".format(product_code, product_name))
    
		
	def before_submit(self):
		sql  = """update `tabStock Location Product` s 
				inner join `tabInventory Check Items` i on i.product_code = s.product_code and s.stock_location = %(stock_location)s
					set s.cost = i.cost,
					s.total_cost = i.original_cost * s.quantity
				where i.parent = %(inventory_check)s and i.product_code in %(product_code)s"""
		
		products = [d.product_code for d in self.items if d.cost != d.original_cost]
		if len(products)>0:
			frappe.db.sql(sql,{
				"inventory_check":self.name,
				"stock_location":self.stock_location,
				"product_code": products
			})

	def on_submit(self):
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			submit_inventory_check_general_ledger_entry(self)

		update_inventory_on_submit(self)


		# frappe.enqueue("epos_restaurant_2023.inventory.doctype.inventory_check.inventory_check.update_inventory_on_submit", queue='short', self=self)
	def on_cancel(self):
		sql  = """update `tabStock Location Product` s 
				inner join `tabInventory Check Items` i on i.product_code = s.product_code and s.stock_location = %(stock_location)s
					set s.cost = i.original_cost,
					s.total_cost = i.original_cost * s.quantity
				where i.parent = %(inventory_check)s and i.product_code in %(product_code)s"""	
		products = [d.product_code for d in self.items if d.cost != d.original_cost]
		if len(products)>0:
			frappe.db.sql(sql,{
				"inventory_check":self.name,
				"stock_location":self.stock_location,
				"product_code": products
			})

		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			submit_inventory_check_general_ledger_entry(self, on_cancel=True)

		update_inventory_on_cancel(self)

def validate_no_duplicate_codes(dict_list):
    seen_codes = set()
    for item in dict_list:
        code = item.product_code

        if code in seen_codes:
            return False, code, item.product_name  # Duplicate code found
        seen_codes.add(code)
    return True, None , None # No duplicates found

def validate_account(self):
	if not self.is_new():
		inventory_check = frappe.db.sql("select business_branch from `tabInventory Check` where name = %(name)s", {"name":self.name}, as_dict=1)
		if  inventory_check[0].business_branch !=  self.business_branch:
			self.default_inventory_account = None
			self.default_adjustment_account = None

	if not self.default_inventory_account:
		self.default_inventory_account = frappe.get_cached_value("Business Branch", self.business_branch, "default_inventory_account")
	
	if not self.default_adjustment_account:
		self.default_adjustment_account = frappe.get_cached_value("Business Branch", self.business_branch, "stock_adjustment_account") 
	

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
			'note': 'New Inventory Check submitted. {}'.format(p.note or ""),
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

	sql = """
		select 
			b.product_code,
			b.cost 
		from  `tabStock Location Product` b 
		where
			b.product_code in %(product_code)s
			and b.stock_location=%(stock_location)s
	"""
	product_cost = frappe.db.sql(sql,{"stock_location": self.stock_location, "product_code":[d["name"] for d in data ]}, as_dict=1)
	


	
	for d in data:
		child_doc = frappe.new_doc("Inventory Check Items")
		child_doc.product_code = d["name"] 
		child_doc.product_name = d["product_name_en"] 
		child_doc.opening_quantity = sum([x["quantity"] for x in opening_data if x["product_code"] ==d["name"]])
		child_doc.sale = sum([x["quantity"] for x in current_data if x["product_code"] ==d["name"] and x["transaction_type"] == "Sale"])
		child_doc.purchase = sum([x["quantity"] for x in current_data if x["product_code"] ==d["name"] and x["transaction_type"] == "Purchase Order"])
		child_doc.other_transaction = sum([x["quantity"] for x in current_data if x["product_code"] ==d["name"] and not x["transaction_type"] in ["Purchase Order","Sale"]])
		child_doc.current_on_hand = child_doc.opening_quantity +  child_doc.purchase +   child_doc.sale + child_doc.other_transaction 
		child_doc.actual_quantity = 0 if  child_doc.current_on_hand <= 0 else child_doc.current_on_hand
		child_doc.original_cost = sum([x["cost"] for x in product_cost if x["product_code"]==d["name"]])
		child_doc.cost = sum([x["cost"] for x in product_cost if x["product_code"]==d["name"]])

		self.append("items", child_doc)
  

  
def get_opening_quantity(self,product_codes):
    sql = "select product_code, sum(in_quantity - out_quantity) as quantity from `tabInventory Transaction` where stock_location=%(stock_location)s and  transaction_date<%(date)s and product_code in %(product_codes)s group by product_code"
    data = frappe.db.sql(sql, {"date":self.posting_date, "stock_location": self.stock_location ,"product_codes":product_codes},as_dict=1 )
    
    return data
    
  
def get_current_quantity(self,product_codes):
    sql = "select product_code,coalesce(transaction_type,'Not Set') as transaction_type, sum(in_quantity - out_quantity) as quantity from `tabInventory Transaction` where stock_location=%(stock_location)s and  transaction_date=%(date)s and product_code in %(product_codes)s group by product_code,coalesce(transaction_type,'Not Set') "
    data = frappe.db.sql(sql, {"date":self.posting_date, "stock_location": self.stock_location ,"product_codes":product_codes},as_dict=1 )
    return data
    