# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction,get_uom_conversion
from epos_restaurant_2023.api.product import get_currenct_cost
from epos_restaurant_2023.api.account import submit_general_ledger_entry
import frappe
from frappe import _
from frappe.model.document import Document
from py_linq import Enumerable

class StockAdjustment(Document):
	def before_insert(self):
		update_current_product_info(self)

	def validate(self):
		total_quantity = Enumerable(self.products).sum(lambda x: x.quantity or 0)
		total_cost = Enumerable(self.products).sum(lambda x: x.total_amount or 0)
		total_current_quantity = Enumerable(self.products).sum(lambda x: x.current_quantity or 0)
		total_current_cost = Enumerable(self.products).sum(lambda x: x.total_current_cost or 0)

		self.total_quantity = total_quantity
		self.total_cost = total_cost

		self.total_current_quantity = total_current_quantity
		self.total_current_cost = total_current_cost
		
		self.difference_quantity = self.total_quantity - self.total_current_quantity; 
		self.difference_cost = self.total_cost - self.total_current_cost; 
		self.difference_amount = self.difference_cost

	def on_submit(self):
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			if self.difference_amount > 0:
				general_ledger(self)
   
		if len(self.products)<=10:
			if self.difference_amount > 0:
				update_inventory_on_submit(self)
			else:
				frappe.msgprint("No Stocks Changed")
		else:
			frappe.enqueue("epos_restaurant_2023.inventory.doctype.stock_adjustment.stock_adjustment.update_inventory_on_submit", queue='short', self=self)
	
	def before_cancel(self):
		frappe.throw(_("Stock adjustment transaction is not allow to cancel."))
		#frappe.enqueue("epos_restaurant_2023.inventory.doctype.stock_adjustment.stock_adjustment.update_inventory_on_cancel", queue='short', self=self)

def update_current_product_info(self):
	for a in self.products:
		p = get_currenct_cost(a.product_code,self.stock_location,a.unit)
		a.current_quantity = p["quantity"]
		a.cost = p["cost"]
		a.current_cost = a.cost
		a.total_amount = a.current_quantity * a.cost
		a.total_current_cost = a.total_amount

def update_inventory_on_submit(self):
	for p in self.products:
		if p.is_inventory_product:
			defference_qty = p.quantity - p.current_quantity
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
				"price":p.cost,
				'note': 'New Stock adjustment submitted.',
				"action":"Submit"
			})

def general_ledger(self):
	stock_in_hand = frappe.db.get_value("Business Branch",self.business_branch,"default_inventory_account")
	if self.difference_amount > 0:
		general_ledger_debit(self,{"account":stock_in_hand,"amount":abs(self.difference_amount)})
		general_ledger_credit(self,{"account":self.difference_account,"amount":abs(self.difference_amount)})
	else:
		general_ledger_debit(self,{"account":self.difference_account,"amount":abs(self.difference_amount)})
		general_ledger_credit(self,{"account":stock_in_hand,"amount":abs(self.difference_amount)})

def general_ledger_debit(self,account):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		"debit_amount":account["amount"],
		"voucher_type":"Stock Adjustment",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "Accounting For Stock Adjustment"
	}
	docs.append(doc)
	submit_general_ledger_entry(docs = docs)

def general_ledger_credit(self,account):
    docs = []
    doc = {
        "doctype":"General Ledger",
        "posting_date":self.posting_date,
        "account":account["account"],
        "credit_amount":account["amount"],
        "voucher_type":"Stock Adjustment",
        "voucher_number":self.name,
        "business_branch": self.business_branch,
		"remark": "Accounting For Stock Adjustment"
    }
    docs.append(doc)
    submit_general_ledger_entry(docs=docs)