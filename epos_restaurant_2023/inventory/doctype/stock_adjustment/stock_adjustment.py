# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, get_stock_location_product,get_uom_conversion
from epos_restaurant_2023.api.product import get_currenct_cost
import frappe
from frappe import _
from frappe.model.document import Document
from py_linq import Enumerable
from epos_restaurant_2023.inventory.doctype.stock_adjustment.general_ledger_entry import submit_stock_adjustment_general_ledger_entry_on_submit

class StockAdjustment(Document):
	def validate(self):
		if frappe.db.get_single_value("ePOS Settings","use_basic_accounting_feature"):
			validate_account(self)
		not_inventory_product =  Enumerable(self.products).where(lambda x: x.is_inventory_product==0).first_or_default()
		if not_inventory_product:
			frappe.throw(_("Product {} - {} is not an inventory product".format(not_inventory_product.product_code, not_inventory_product.product_name )))
			total_quantity = Enumerable(self.products).sum(lambda x: x.quantity or 0)
			total_cost = Enumerable(self.products).sum(lambda x: x.cost or 0)
			total_current_quantity = Enumerable(self.products).sum(lambda x: x.current_quantity or 0)
			total_current_cost = Enumerable(self.products).sum(lambda x: x.current_cost or 0)
			self.total_current_quantity = total_current_quantity
			self.total_current_cost = total_current_cost
			self.total_quantity = total_quantity
			self.total_cost = total_cost

	def on_submit(self):
		if frappe.db.get_single_value("ePOS Settings","use_basic_accounting_feature"):
			submit_stock_adjustment_general_ledger_entry_on_submit(self)
		if len(self.products)>=10:
			update_inventory_on_submit(self)
		else:
			frappe.enqueue("epos_restaurant_2023.inventory.doctype.stock_adjustment.stock_adjustment.update_inventory_on_submit", queue='short', self=self)
	
	def before_cancel(self):
		frappe.throw(_("Stock adjustment transaction is not allow to cancel."))
		#frappe.enqueue("epos_restaurant_2023.inventory.doctype.stock_adjustment.stock_adjustment.update_inventory_on_cancel", queue='short', self=self)
  
def update_inventory_on_submit(self):
	for p in self.products:
		if p.is_inventory_product:
			uom_conversion = (1 if (get_uom_conversion(p.base_unit, p.unit) or 0) == 0 else get_uom_conversion(p.base_unit, p.unit))
			defference_qty = (p.quantity - p.current_quantity) / uom_conversion
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock Adjustment",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.product_code,
				'unit':p.unit,
				'stock_location':self.stock_location,
				'out_quantity': abs(defference_qty) if defference_qty < 0 else 0,
				'in_quantity': defference_qty if defference_qty >= 0 else 0,
				"price":p.cost * uom_conversion,
				'note': 'New Stock adjustment submitted.',
				"action":"Submit"
			})
def validate_account(self):
    # set default account
		if not self.difference_account:
			self.difference_account = frappe.db.get_value("Business Branch",self.business_branch,"stock_adjustment_account")

	# for p in self.products:
	# 	if p.is_inventory_product:
	# 		defference_qty = p.quantity - p.current_quantity
	# 		add_to_inventory_transaction({
	# 			'doctype': 'Inventory Transaction',
	# 			'transaction_type':"Stock adjustment",
	# 			'transaction_date':self.posting_date,
	# 			'transaction_number':self.name,
	# 			'product_code': p.product_code,
	# 			'unit':p.unit,
	# 			'stock_location':self.stock_location,
	# 			'out_quantity': defference_qty if defference_qty >= 0 else 0,
	# 			'in_quantity': abs(defference_qty) if defference_qty < 0 else 0,
	# 			"price":p.current_cost,
	# 			'note': 'Stock adjustment cancelled.',
    # 			"action":"Cancel"	
	# 		})