# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class StorePayment(Document):
	def validate(self):
		#remote record empty
		self.payments = [d for d in self.payments if   d.payment_type and (d.input_amount or 0)>0]
		if sum([d.input_amount for d in self.payments]) == 0:
			frappe.throw(_("Please enter payment amount"))
		# update payment with commar separated values
		self.payment_types = ", ".join(set(str(d.payment_type) for d in self.payments))
		for p in self.payments:
			p.payment_amount = p.input_amount / (p.exchange_rate or 1)
		self.payment_amount = sum(d.payment_amount for d in self.payments)

	def before_submit(self):
		if (self.payment_amount or 0)  == 0:
			frappe.throw(_("Please enter payment amount"))

	def on_submit(self):
		add_GL_Entry(self)

@frappe.whitelist()
def get_vendor_credit_balance(pos_profile):
	account_code = frappe.get_cached_doc("POS Profile",pos_profile,"default_credit_account")
	sql = "select sum(debit_amount-credit_amount) as total from `tabGeneral Ledger` where account = %(account)s"

	data = frappe.db.sql(sql,{"account":account_code},as_dict = 1)
	if data:
		return {"balance":data[0].get("total") or 0}

	return {"balance":0} 

@frappe.whitelist(allow_guest=True)
def get_payment_type_account(payment_type,branch):
	accounts = frappe.db.sql("""select 
						a.account,
						b.exchange_rate,
						b.change_exchange_rate
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
			"remark": "Payment to store",
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