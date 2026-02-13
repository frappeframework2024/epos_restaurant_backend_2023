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
		currency_precision = frappe.db.get_single_value('System Settings', 'currency_precision')
		total_amount = 0
		total_quantity = 0
		for d in self.expense_items:
			d.amount =d.price * d.quantity
			total_quantity += d.quantity
			total_amount += d.amount
		self.total_quantity = total_quantity
		self.total_amount = round(total_amount,int(currency_precision))
		self.balance = round(self.total_amount - self.total_paid,int(currency_precision))
		self.remaining_cash_float = round(self.remaining_cash_float,int(currency_precision))

	def on_submit(self):
		GLEntry(self,"submit")

	def on_cancel(self):
		GLEntry(self,"cancel")
		update_cancelled_gl(self.name)

@frappe.whitelist()
def generate_expense_gl():
	expenses = frappe.db.sql("""select 
						  name 
						  from `tabExpense` 
						  where docstatus in (1,2) and 
						  name not in (SELECT 
						  voucher_number 
						  FROM `tabGeneral Ledger` 
						  WHERE voucher_type='Expense' 
						  GROUP BY voucher_number)""",as_dict=1)
	for a in expenses:
		manual_generate_expense_gl(a["name"])

@frappe.whitelist()
def manual_generate_expense_gl(name):
	doc = frappe.get_doc("Expense",name)
	GLEntry(doc,"submit")
	if doc.docstatus == 2:
		GLEntry(doc,"cancel")
		update_cancelled_gl(name)
		return "done"

def account_validation(self):
	invalid_modes=[]
	for a in self.expense_items:
		if (a.expense_account or "") == "":
			invalid_modes.append(get_link_to_form("Expense Code", a.expense_code))
	if invalid_modes:
		msg = _("Please Select or Set Default Account For Expense Code {}")
		frappe.throw(msg.format(", ".join(invalid_modes)), title=_("Missing Account"))
	
	for a in self.payments:
		if (a.default_account or "") == "":
			invalid_modes.append(get_link_to_form("Payment Type", a.payment_type))
	if invalid_modes:
		msg = _("Please Set Default Account For Payment Type {}")
		frappe.throw(msg.format(", ".join(invalid_modes)), title=_("Missing Account"))
	currency_precision = frappe.db.get_single_value('System Settings', 'currency_precision')
	expense = sum((a.amount or 0) for a in self.expense_items)
	payment = sum((b.amount or 0) for b in self.payments)
	if abs(round(expense,int(currency_precision)) -  round(payment,int(currency_precision))) != 0:
		frappe.throw("Expense Amount Must Be The Same As Payment Amount")
  
@frappe.whitelist()
def get_expense_code_account(expense_code,branch):
	accounts = frappe.db.sql("""select 
						  default_expense_account 
						  from `tabExpense Code Account` 
						  where parent = %(expense_code)s 
						  and business_branch = %(branch)s""",{'expense_code':expense_code,'branch':branch},as_dict=1)
	if len(accounts) == 0:
		accounts = "no_record"
	return accounts

@frappe.whitelist()
def get_payment_type_account(payment_type,branch):
	accounts = frappe.db.sql("""select 
						  account 
						  from `tabPayment Type Account` 
						  where parent = %(payment_type)s 
						  and business_branch = %(branch)s""",{'payment_type':payment_type,'branch':branch},as_dict=1)
	if len(accounts) == 0:
		accounts = "no_record"
	return accounts

def GLEntry(self,status):
	expense_accounts = defaultdict(int)
	for a in self.expense_items:
		category = a.expense_account
		value = a.amount
		expense_accounts[category] += value
	expense_accounts = dict(expense_accounts)
	if status == "submit":
		for a in expense_accounts:
			expense_general_ledger_debit(self,account = {"account":a,"amount":expense_accounts[a]},status=status)
	else:
		for a in expense_accounts:
			expense_general_ledger_credit(self,account = {"account":a,"amount":expense_accounts[a]},status=status)
	
	payment_accounts = defaultdict(int)
	for a in self.payments:
		category = a.default_account
		value = a.amount
		payment_accounts[category] += value
	payment_accounts = dict(payment_accounts)
	if status == "submit":
		for a in payment_accounts:
			expense_general_ledger_credit(self,account = {"account":a,"amount":payment_accounts[a]},status=status)
	else:
		for a in payment_accounts:
			expense_general_ledger_debit(self,account = {"account":a,"amount":payment_accounts[a]},status=status)

def expense_general_ledger_debit(self,account,status):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		"debit_amount":account["amount"],
		"voucher_type":"Expense",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"is_cancelled": (1 if status == "cancel" else 0),
		"remark": "Expense {} On Account {}".format(self.name,account["account"]) if self.docstatus == 1 else "Cancel Expense {} On Account {}".format(self.name,account["account"])
	}
	docs.append(doc)
	submit_general_ledger_entry(docs = docs)
	
def expense_general_ledger_credit(self,account,status):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		"credit_amount":account["amount"],
		"voucher_type":"Expense",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"is_cancelled":(1 if status == "cancel" else 0),
		"remark": "Expense Payment {} On Account {}".format(self.name,account["account"]) if self.docstatus == 1 else "Cancel Expense Payment {} On Account {}".format(self.name,account["account"])
	}
	docs.append(doc)
	submit_general_ledger_entry(docs=docs)

def update_cancelled_gl(name):
	frappe.db.sql("update `tabGeneral Ledger` set is_cancelled=1 where voucher_type='Expense' and voucher_number='{}'".format(name))
	frappe.db.commit()