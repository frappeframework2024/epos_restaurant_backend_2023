# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, get_uom_conversion,get_stock_location_product,check_uom_conversion
from epos_restaurant_2023.api.product import get_currenct_cost
from epos_restaurant_2023.api.account import submit_general_ledger_entry
import frappe
from frappe import _
from frappe.model.document import Document
class StockTake(Document):
	def before_insert(self):
		update_current_product_info(self)

	def validate(self): 
		self.total_quantity = sum((a.quantity or 0) for a in self.stock_take_products)
		self.total_amount = sum((a.quantity or 0)* (a.cost or  0) for a in self.stock_take_products)
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			validate_account(self)
  
	def before_submit(self):
		for d in self.stock_take_products:
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
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			GL_Entry(self)
		update_inventory_on_submit(self)

	def on_cancel(self):
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			GL_Entry(self)
		update_inventory_on_cancel(self)

def update_inventory_on_submit(self):
	for p in self.stock_take_products:
		uom_conversion = get_uom_conversion(p.base_unit, p.unit)			
		add_to_inventory_transaction({
			'doctype': 'Inventory Transaction',
			'transaction_type':"Stock Take",
			'transaction_date':self.posting_date,
			'transaction_number':self.name,
			'product_code': p.product_code,
			'unit':p.unit,
			'stock_location':self.stock_location,
			'out_quantity':p.quantity / uom_conversion,
			"price":p.cost * uom_conversion,
			"previous_cost":p.cost * uom_conversion,
			'note': 'New stock take submitted.',
			"action": "Submit"
		})

def update_inventory_on_cancel(self):
	for p in self.stock_take_products:
		uom_conversion = get_uom_conversion(p.base_unit, p.unit)
		add_to_inventory_transaction({
			'doctype': 'Inventory Transaction',
			'transaction_type':"Stock Take",
			'transaction_date':self.posting_date,
			'transaction_number':self.name,
			'product_code': p.product_code,
			'unit':p.unit,
			'stock_location':self.stock_location,
			'in_quantity':p.quantity / uom_conversion,
			"price":p.cost * uom_conversion,
			"previous_cost":p.cost * uom_conversion,
			'note': 'Stock take cancelled.',
			"action": "Cancel"
		})

def validate_account(self):
	if not self.difference_account:
		self.difference_account = frappe.get_cached_value("Business Branch", self.business_branch, "stock_adjustment_account")
	if not self.default_inventory_account:
		self.default_inventory_account = frappe.get_cached_value("Business Branch", self.business_branch, "default_inventory_account")

def update_current_product_info(self):
	for a in self.stock_take_products:
		p = get_currenct_cost(a.product_code,self.stock_location,a.unit)
		a.cost = p["cost"]
		a.total_amount = a.quantity * a.cost

def GL_Entry(self):
    docs = [] 
    if self.total_amount > 0:
        doc_expenses = {
            "doctype": "General Ledger",
            "posting_date": self.posting_date,
            "account": self.default_inventory_account if self.docstatus == 1 else self.difference_account,
            "credit_amount": self.total_amount,
            "againt": self.difference_account if self.docstatus == 1 else self.default_inventory_account,
            "voucher_type": "Stock Take",
            "voucher_number": self.name,
            "business_branch": self.business_branch,
            "remark": "Accounting adjustment for Stock"
        }
        docs.append(doc_expenses)
        doc_assets = {
            "doctype": "General Ledger",
            "posting_date": self.posting_date,
            "account": self.difference_account if self.docstatus == 1 else self.default_inventory_account,
            "debit_amount": self.total_amount,
            "againt": self.default_inventory_account if self.docstatus == 1 else self.difference_account,
            "voucher_type": "Stock Take",
            "voucher_number": self.name,
            "business_branch": self.business_branch,
            "remark": "Accounting adjustment for Stock"
        }
        docs.append(doc_assets)

    submit_general_ledger_entry(docs=docs)