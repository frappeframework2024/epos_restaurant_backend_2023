# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from py_linq import Enumerable
from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction,get_uom_conversion
from epos_restaurant_2023.api.product import get_currenct_cost
from epos_restaurant_2023.api.account import submit_general_ledger_entry

class SingleProductAdjustment(Document):
	def before_insert(self):
		update_current_product_info(self)

	def validate(self):
		epos_setting = frappe.get_doc('ePOS Settings')
		if self.is_inventory_product == 1 and epos_setting.allow_negative_stock == 0:
			if self.new_quantity < 0:
				frappe.throw(("Product <b>{0}</b> QTY Not Allow Negative".format(self.product_code)))			
		self.total_current_cost = self.current_quantity * self.current_cost
		self.total_new_cost =self.new_quantity * self.new_cost
		self.difference_quantity = self.new_quantity - self.current_quantity
		self.difference_amount = self.total_new_cost - self.total_current_cost
	
	def on_submit(self):
		update_inventory_on_submit(self)
		general_ledger(self)
			
def update_current_product_info(self):
	p = get_currenct_cost(self.product_code,self.stock_location,self.unit)
	self.current_cost = p["cost"]
	self.current_quantity = p["quantity"]
	self.total_current_cost = self.current_quantity * self.current_cost

@frappe.whitelist()
def update_inventory_on_submit(self):
	difference_qty = self.new_quantity - self.current_quantity
	add_to_inventory_transaction({
		'doctype': 'Inventory Transaction',
		'transaction_type':"Single Product Adjustment",
		'transaction_date':self.posting_date,
		'transaction_number':self.name,
		'product_code': self.product_code,
		'unit':self.unit,
		'stock_location':self.stock_location,
		'out_quantity': abs(difference_qty) if difference_qty < 0 else 0,
		'in_quantity': difference_qty if difference_qty >= 0 else 0,
		"price":self.new_cost,
		'note': 'New single product adjustment submitted.',
		"action":"Submit"
	})
	
@frappe.whitelist()
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
		"voucher_type":"Single Product Adjustment",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "Accounting For Single Product Adjustment"
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
        "voucher_type":"Single Product Adjustment",
        "voucher_number":self.name,
        "business_branch": self.business_branch,
		"remark": "Accounting For Single Product Adjustment"
    }
    docs.append(doc)
    submit_general_ledger_entry(docs=docs)
