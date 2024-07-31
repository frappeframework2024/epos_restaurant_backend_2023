# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, get_uom_conversion,calculate_average_cost,check_uom_conversion
import frappe
from frappe import _
from frappe.model.document import Document
from collections import defaultdict
from epos_restaurant_2023.api.account import submit_general_ledger_entry

class StockEntry(Document):
	def validate(self):
		self.total_quantity =  (sum((a.quantity or 0) for a in self.items) or 0)
		self.total_amount = (sum((a.quantity or 0) * (a.cost or  0) for a in self.items) or 0)
		validate_expense_account(self)
		validate_uom_conversion(self)
      
	def on_submit(self):
		use_basic_accounting_feature = frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature")
		if len(self.items)>=100:
			if use_basic_accounting_feature:
				if not self.flags.ignore_post_general_ledger_entry:
					frappe.enqueue("epos_restaurant_2023.inventory.doctype.stock_entry.stock_entry.GLEntry", queue='short', self=self)
			frappe.enqueue("epos_restaurant_2023.inventory.doctype.stock_entry.stock_entry.update_inventory", queue='short', self=self)
		else:
			if use_basic_accounting_feature:
				if not self.flags.ignore_post_general_ledger_entry:
					GLEntry(self)
			update_inventory(self)
	
	def on_cancel(self):
		use_basic_accounting_feature = frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature")
		if len(self.items)>=100:
			if use_basic_accounting_feature:
				frappe.enqueue("epos_restaurant_2023.inventory.doctype.stock_entry.stock_entry.GLEntry", queue='short', self=self)
			frappe.enqueue("epos_restaurant_2023.inventory.doctype.stock_entry.stock_entry.update_inventory", queue='short', self=self)
		else:
			if use_basic_accounting_feature:
				GLEntry(self)
			update_inventory(self)


def validate_uom_conversion(self):
	error=""
	for d in self.items:
		if d.unit != d.base_unit:
			if not check_uom_conversion(d.base_unit, d.unit):
				error += ("Row #{} There is no UoM conversion from {} to {}.</br>".format(d.idx,d.base_unit, d.unit))
	if error:
		frappe.throw(error)

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


def update_inventory(self):
	entry_type =frappe.db.get_value("Stock Entry Type", self.entry_type, "purpose")
	if self.docstatus == 1:
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
					'in_quantity':(p.quantity / uom_conversion) if entry_type == 'Stock In' else 0,
					'out_quantity':(p.quantity / uom_conversion) if entry_type == 'Stock Out' else 0,
					"price":calculate_average_cost(p.product_code,self.stock_location,(p.quantity / uom_conversion),(p.cost*uom_conversion)),
					'note': 'New stock Entry submitted.',
					"stock_entry_type":self.entry_type,
					"action": "Submit"
				})
	else:
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
					'out_quantity':(p.quantity / uom_conversion) if entry_type == 'Stock In' else 0,
					'in_quantity':(p.quantity / uom_conversion) if entry_type == 'Stock Out' else 0,
					"price":calculate_average_cost(p.product_code,self.stock_location,((p.quantity*-1) / uom_conversion),(p.cost*uom_conversion),self.name),
					'note': 'Stock Entry cancelled.',
					"stock_entry_type":self.entry_type,
					"action": "Cancel"
				})
	
def GLEntry(self):
	inventory_account = frappe.db.get_value('Business Branch',self.business_branch,'default_inventory_account')
	if self.docstatus == 1:
		if self.purpose == "Stock In":
			expense_general_ledger(self,account = {"account":inventory_account,"amount":self.total_amount},type = "dr")
		else:
			expense_general_ledger(self,account = {"account":inventory_account,"amount":self.total_amount},type = "cr")

		expense_accounts = defaultdict(int)
		for a in self.items:
			category = a.expense_account
			value = a.amount
			expense_accounts[category] += value
		expense_accounts = dict(expense_accounts)
		if self.purpose == "Stock In":
			for a in expense_accounts:
				expense_general_ledger(self,account = {"account":a,"amount":expense_accounts[a]},type = "cr")
		else:
			for a in expense_accounts:
				expense_general_ledger(self,account = {"account":a,"amount":expense_accounts[a]},type = "dr")

	else:
		if self.purpose == "Stock In":
			expense_general_ledger(self,account = {"account":inventory_account,"amount":self.total_amount},type = "cr")
		else:
			expense_general_ledger(self,account = {"account":inventory_account,"amount":self.total_amount},type = "dr")

		expense_accounts = defaultdict(int)
		for a in self.items:
			category = a.expense_account
			value = a.amount
			expense_accounts[category] += value
		expense_accounts = dict(expense_accounts)
		if self.purpose == "Stock In":
			for a in expense_accounts:
				expense_general_ledger(self,account = {"account":a,"amount":expense_accounts[a]},type = "dr")
		else:
			for a in expense_accounts:
				expense_general_ledger(self,account = {"account":a,"amount":expense_accounts[a]}, type = "cr")


def expense_general_ledger(self,account,type):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		"debit_amount":account["amount"] if type == "dr" else 0,
		"credit_amount":account["amount"]  if type == "cr" else 0,
		"voucher_type":"Stock Entry",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "Stock Entry {} Entry Type {}".format(self.name,self.entry_type) if self.docstatus == 1 else "Cancel Stock Entry {} Entry Type {}".format(self.name,self.entry_type)

	}
	docs.append(doc)
	submit_general_ledger_entry(docs = docs)