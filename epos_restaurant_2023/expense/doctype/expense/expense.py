# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import utils
from frappe import _
from frappe.model.document import Document
from epos_restaurant_2023.api.account import submit_general_ledger_entry
from collections import defaultdict
from frappe.utils import get_link_to_form

class Expense(Document):
	def validate(self):
		account_validation(self)
		
		total_amount = 0
		total_quantity = 0
		for d in self.expense_items:
			d.amount = d.price * d.quantity
			total_quantity = total_quantity + d.quantity
			total_amount = total_amount + d.amount

		self.total_quantity = total_quantity
		self.total_amount = total_amount
		self.balance = self.total_amount - self.total_paid

	def on_submit(self):
		GLEntry(self)

	def on_cancel(self):
		GLEntry(self)

def account_validation(self):
	invalid_modes=[]
	for a in self.expense_items:
		if a.expense_account is None or a.expense_account == "":
			invalid_modes.append(get_link_to_form("Expense Code", a.expense_code))
	if invalid_modes:
		msg = _("Please Select or Set Default Account For Expense Code {}")
		frappe.throw(msg.format(", ".join(invalid_modes)), title=_("Missing Account"))

	
	for a in self.payments:
		if a.default_account is None or a.default_account == "":
			invalid_modes.append(get_link_to_form("Payment Type", a.payment_type))
	if invalid_modes:
		msg = _("Please Set Default Account For Payment Type {}")
		frappe.throw(msg.format(", ".join(invalid_modes)), title=_("Missing Account"))

	expense = sum((a.amount or 0) for a in self.expense_items)
	payment = sum((b.amount or 0) for b in self.payments)
	if abs(expense - payment) != 0:
		frappe.throw("Expense Amount Must Be The Same As Payment Amount")
  
@frappe.whitelist(allow_guest=True)
def get_expense_code_account(expense_code,branch):
	accounts = frappe.db.sql("""select 
						  default_expense_account 
						  from `tabExpense Code Account` 
						  where parent = %(expense_code)s 
						  and business_branch = %(branch)s""",{'expense_code':expense_code,'branch':branch},as_dict=1)
	if len(accounts) == 0:
		accounts = "no_record"
	return accounts

@frappe.whitelist(allow_guest=True)
def get_payment_type_account(payment_type,branch):
	accounts = frappe.db.sql("""select 
						  account 
						  from `tabPayment Type Account` 
						  where parent = %(payment_type)s 
						  and business_branch = %(branch)s""",{'payment_type':payment_type,'branch':branch},as_dict=1)
	if len(accounts) == 0:
		accounts = "no_record"
	return accounts

def GLEntry(self):
	if self.docstatus == 1:
		expense_accounts = defaultdict(int)
		for a in self.expense_items:
			category = a.expense_account
			value = a.amount
			expense_accounts[category] += value
		expense_accounts = dict(expense_accounts)
		for a in expense_accounts:
			expense_general_ledger_debit(self,account = {"account":a,"amount":expense_accounts[a]})
		
		payment_accounts = defaultdict(int)
		for a in self.payments:
			category = a.default_account
			value = a.amount
			payment_accounts[category] += value
		payment_accounts = dict(payment_accounts)
		for a in payment_accounts:
			expense_general_ledger_credit(self,account = {"account":a,"amount":payment_accounts[a]})
	else:
		expense_accounts = defaultdict(int)
		for a in self.expense_items:
			category = a.expense_account
			value = a.amount
			expense_accounts[category] += value
		expense_accounts = dict(expense_accounts)
		for a in expense_accounts:
			expense_general_ledger_credit(self,account = {"account":a,"amount":expense_accounts[a]})
		
		payment_accounts = defaultdict(int)
		for a in self.payments:
			category = a.default_account
			value = a.amount
			payment_accounts[category] += value
		payment_accounts = dict(payment_accounts)
		for a in payment_accounts:
			expense_general_ledger_debit(self,account = {"account":a,"amount":payment_accounts[a]})


def expense_general_ledger_debit(self,account):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		"debit_amount":account["amount"],
		"voucher_type":"Expense",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "Expense {} On Account {}".format(account["amount"],account["account"])

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
        "voucher_type":"Expense",
        "voucher_number":self.name,
        "business_branch": self.business_branch,
		"remark": "Expense Payment {} On Account {}".format(account["amount"],account["account"])
    }
    docs.append(doc)
    submit_general_ledger_entry(docs=docs)