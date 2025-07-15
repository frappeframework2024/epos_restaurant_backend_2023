# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class StorePayment(Document):
	def validate(self):
		#remote record empty
		self.payments = [d for d in self.payments if d.payment_type and (d.input_amount or 0)>0]
		if sum([d.input_amount for d in self.payments]) == 0:
			frappe.throw(_("Please enter payment amount"))
		
		# update payment with commar separated values
		self.payment_types = ", ".join(set(str(d.payment_type) for d in self.payments))

		get_accounts(self)
		self.credit_amount = get_vendor_credit_balance(self.pos_profile)["balance"]
		self.payment_amount = sum(d.payment_amount for d in self.payments)

	def before_submit(self):
		if self.credit_amount < self.payment_amount:
			if self.credit_amount == 0:
				frappe.throw(_("Credit amount is zero"))
			else:
				frappe.throw(_("Credit amount is less than payment amount"))

	def on_submit(self):
		add_GL_Entry(self)
	
	def on_cancel(self):
		cancel_GL_Entry(self)

def get_accounts(self):
	error = ""
	if (self.account_code or "") == "":
		self.account_code = frappe.db.get_value("POS Profile",self.pos_profile,"default_credit_account")

	for a in self.payments:
		if a.payment_type:
			account = get_payment_type_account(a.payment_type,self.business_branch)
			if account != "no_record":
				a.account_code = account[0].account
				a.exchange_rate = account[0].exchange_rate
				a.payment_amount = a.input_amount / (a.exchange_rate or 1)
			else:
				error += "Row <b>{}</b> Payment Type <b>{}</b> does not have account code</br>".format(a.idx,a.payment_type)
	if error:
		frappe.throw(error)

@frappe.whitelist()
def get_vendor_credit_balance(pos_profile):
	pos_profile = frappe.get_doc("POS Profile",pos_profile)
	sql = "select abs(sum(debit_amount-credit_amount)) as total from `tabGeneral Ledger` where account = %(account)s"
	data = frappe.db.sql(sql,{"account":pos_profile.default_credit_account},as_dict=1)
	if data:
		return {"balance":data[0].get("total") or 0}
	return {"balance":0} 

@frappe.whitelist()
def get_payment_type_account(payment_type,branch):
	accounts = frappe.db.sql("""select 
						a.account,
						b.exchange_rate
						from `tabPayment Type Account` a
						inner join `tabPayment Type` b on b.name = a.parent
						where parent = %(payment_type)s 
						and business_branch = %(branch)s""",{'payment_type':payment_type,'branch':branch},as_dict=1)
	if len(accounts) == 0:
		accounts = "no_record"
	return accounts

def add_GL_Entry(self):
	from epos_restaurant_2023.api.account import submit_general_ledger_entry
	docs = []
	for a in set([d.account_code for d in self.payments]):
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":a,
			"credit_amount":sum([d.payment_amount for d in self.payments if d.account_code == a]),
			"againt": self.account_code,
			"voucher_type":"Store Payment",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"remark": "Payment to store"
		}
		docs.append(doc)
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":self.account_code,
		"debit_amount": sum([d.payment_amount for d in self.payments]),
		"voucher_type":"Store Payment",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark" : "Payment to store",
		"party_type" : "Vendor",
		"party":self.vendor,
		"party_name":self.vendor_name
		}
	docs.append(doc)
	submit_general_ledger_entry(docs=docs)

def cancel_GL_Entry(self):
	from epos_restaurant_2023.api.account import submit_general_ledger_entry
	frappe.db.sql("update `tabGeneral Ledger` set is_cancelled=1 where voucher_type='Store Payment' and voucher_number = '{0}'".format(self.name))
	docs = []
	for a in set([d.account_code for d in self.payments]):
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":a,
			"debit_amount":sum([d.payment_amount for d in self.payments if d.account_code == a]),
			"againt": self.account_code,
			"voucher_type":"Store Payment",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"remark": "Payment to store",
			"party_type" : "Vendor",
			"party":self.vendor,
			"party_name":self.vendor_name,
			"is_cancelled":1
		}
		docs.append(doc)
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":self.account_code,
		"credit_amount": sum([d.payment_amount for d in self.payments]),
		"voucher_type":"Store Payment",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark" : "Payment to store",
		"is_cancelled":1
		}
	docs.append(doc)
	submit_general_ledger_entry(docs=docs)