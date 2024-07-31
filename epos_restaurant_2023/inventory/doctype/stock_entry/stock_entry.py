# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, get_uom_conversion,get_stock_location_product
from epos_restaurant_2023.inventory.inventory import check_uom_conversion
import frappe
from frappe import _
from py_linq import Enumerable
from frappe.model.document import Document
from collections import defaultdict
from epos_restaurant_2023.api.account import submit_general_ledger_entry
from frappe.utils import get_link_to_form

class StockEntry(Document):
	def validate(self):
		self.total_quantity =  (sum((a.quantity or 0) for a in self.item) or 0)
		self.total_amount = (sum((a.quantity or 0) * (a.price or  0) for a in self.item) or 0)
		validate_expense_account(self)
  
	def before_submit(self):
		for d in self.items:
			if d.unit != d.base_unit:
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
			if not self.flags.ignore_post_general_ledger_entry:
				GLEntry(self)
		update_inventory_on_submit(self)
		#frappe.enqueue("epos_restaurant_2023.purchasing.doctype.purchase_order.purchase_order.update_inventory_on_submit", queue='short', self=self)
	
	def on_cancel(self):
		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature"):
			GLEntry(self)
		update_inventory_on_cancel(self)
		#frappe.enqueue("epos_restaurant_2023.purchasing.doctype.purchase_order.purchase_order.update_inventory_on_cancel", queue='short', self=self)
	
@frappe.whitelist(allow_guest=True)
def get_expense_account(product_code,branch):
	expense_account = frappe.db.get_value('Product Default Account', {'parent': product_code,'business_branch':branch}, 'default_adjustment_account')
	if (expense_account or "") == "":
		expense_account = frappe.db.get_value('Business Branch',branch,'stock_adjustment_account')
	return expense_account

def validate_expense_account(self):
	for a in self.items:
		if (a.expense_account or '') == "":
			a.expense_account = get_expense_account(a.product_code,self.business_branch)


def update_inventory_on_submit(self):
	entry_type =frappe.db.get_value("Stock Entry Type", self.entry_type, "purpose")
	for p in self.items:
		if p.is_inventory_product:
			uom_conversion = get_uom_conversion(p.base_unit, p.unit)			
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock Entry",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.product_code,
				'unit':p.unit,
				'stock_location':self.stock_location,
				'in_quantity':p.quantity / uom_conversion if entry_type == 'Stock In' else 0,
				'out_quantity':p.quantity / uom_conversion if entry_type == 'Stock Out' else 0,
				"price":p.base_cost,
				'note': 'New stock Entry submitted.',
				"stock_entry_type":self.entry_type,
				"action": "Submit"
			})

def update_inventory_on_cancel(self):
	entry_type =frappe.db.get_value("Stock Entry Type", self.entry_type, "purpose")
	for p in self.items:
		if p.is_inventory_product:
			uom_conversion = get_uom_conversion(p.base_unit, p.unit)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock Entry",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.product_code,
				'unit':p.unit,
				'stock_location':self.stock_location,
				'out_quantity':p.quantity / uom_conversion if entry_type == 'Stock In' else 0,
				'in_quantity':p.quantity / uom_conversion if entry_type == 'Stock Out' else 0,
				"price":p.base_cost,
				'note': 'Stock Entry cancelled.',
				"stock_entry_type":self.entry_type,
				"action": "Cancel"
			})
	
def GLEntry(self):
	inventory_account = frappe.db.get_value('Business Branch',self.business_branch,'default_inventory_account')
	if self.docstatus == 1:
		if self.purpose == "Stock In":
			expense_general_ledger_debit(self,account = {"account":inventory_account,"amount":self.total_amount})
		else:
			expense_general_ledger_credit(self,account = {"account":inventory_account,"amount":self.total_amount})

		expense_accounts = defaultdict(int)
		for a in self.items:
			category = a.expense_account
			value = a.amount
			expense_accounts[category] += value
		expense_accounts = dict(expense_accounts)
		for a in expense_accounts:
			if self.purpose == "Stock In":
				expense_general_ledger_credit(self,account = {"account":a,"amount":expense_accounts[a]})
			else:
				expense_general_ledger_debit(self,account = {"account":a,"amount":expense_accounts[a]})

	else:
		if self.purpose == "Stock In":
			expense_general_ledger_credit(self,account = {"account":inventory_account,"amount":self.total_amount})
		else:
			expense_general_ledger_debit(self,account = {"account":inventory_account,"amount":self.total_amount})

		expense_accounts = defaultdict(int)
		for a in self.items:
			category = a.expense_account
			value = a.amount
			expense_accounts[category] += value
		expense_accounts = dict(expense_accounts)
		for a in expense_accounts:
			if self.purpose == "Stock In":
				expense_general_ledger_debit(self,account = {"account":a,"amount":expense_accounts[a]})
			else:
				expense_general_ledger_credit(self,account = {"account":a,"amount":expense_accounts[a]})


def expense_general_ledger_debit(self,account):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		"debit_amount":account["amount"],
		"voucher_type":"Stock Entry",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "Stock Entry {} Entry Type {}".format(self.name,self.entry_type)

	}
	docs.append(doc)
	submit_general_ledger_entry(docs = docs)

def expense_general_ledger_credit(self,account):
    docs = []
    doc = {
        "doctype":"General Ledger",
        "posting_date":self.posting_date,
        "account":account["account"],
        "credit_amount":account["amount"],
        "voucher_type":"Stock Entry",
        "voucher_number":self.name,
        "business_branch": self.business_branch,
		"remark": "Stock Entry {} Entry Type {}".format(self.name,self.entry_type)
    }
    docs.append(doc)
    submit_general_ledger_entry(docs=docs)