# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, get_product_cost, get_uom_conversion,get_stock_location_product,update_product_quantity
from epos_restaurant_2023.inventory.inventory import check_uom_conversion
import frappe
from frappe import _
from py_linq import Enumerable
from frappe.model.document import Document
from epos_restaurant_2023.inventory.doctype.stock_entry.general_ledger_entry import submit_stock_to_general_ledger_entry
from  epos_restaurant_2023.api.cache_function import get_default_account_from_pos_config, get_default_account_from_revenue_group, get_doctype_value_cache
import json

class StockEntry(Document):
	def validate(self):
		total_quantity = Enumerable(self.items).sum(lambda x: x.quantity or 0)
		total_amount = Enumerable(self.items).sum(lambda x: (x.quantity or 0)* (x.price or  0))

		self.total_quantity = total_quantity
		self.total_amount = total_amount
		# update default accunt
		update_default_account(self)
  
	def before_submit(self):
		for d in self.items:
			if d.unit !=d.base_unit:
				if not check_uom_conversion(d.base_unit, d.unit):
					frappe.throw(_("There is no UoM conversion from {} to {}".format(d.base_unit, d.unit)))

				current_stock = get_stock_location_product(self.stock_location, d.product_code)
				
				if current_stock is None or current_stock.quantity <= 0:
					frappe.throw(_("{} is not available in stock".format(d.product_code)))
				else:
					uom_conversion = get_uom_conversion(current_stock.unit, d.unit)
					if current_stock.quantity * uom_conversion < d.quantity:
						frappe.throw(_("{} is available only {} {} in stock".format(d.product_code, current_stock.quantity,current_stock.unit)))
      
	def on_submit(self):

		if frappe.db.get_single_value("ePOS Settings","use_basic_accounting_feature"):
			submit_stock_to_general_ledger_entry(self)
		#frappe.enqueue("epos_restaurant_2023.purchasing.doctype.purchase_order.purchase_order.update_inventory_on_submit", queue='short', self=self)
	
	# def on_cancel(self):
	# 	update_inventory_on_cancel(self)
		#frappe.enqueue("epos_restaurant_2023.purchasing.doctype.purchase_order.purchase_order.update_inventory_on_cancel", queue='short', self=self)
  

def update_default_account(self):
 
	# 1 get from product
	if [x for x in self.items if not x.default_account]:
		# get product default account_code from product
		sql="select distinct parent as product_code, default_adjustment_account from `tabProduct Default Account` where parent in %(parents)s and business_branch =%(business_branch)s"

		 
		product_account_codes = frappe.db.sql(sql, {"parents":[x.product_code for x in self.items if not x.default_account], "business_branch":self.business_branch},as_dict=1)
		product_has_default_account = [d["product_code"] for d in product_account_codes]
		
		
		for sp in [x for x in self.items if not x.default_account and x.product_code in product_has_default_account]:
			sp.default_account = [d for d in product_account_codes if d["product_code"] == sp.product_code][0]["default_account"] 

	# 4 get account code from Business Branch
	if [x for x in self.items if not x.default_account]:
		for sp in [x for x in self.items if not x.default_account]:
			sp.default_account = get_doctype_value_cache("Business Branch",self.business_branch, "stock_adjustment_account")