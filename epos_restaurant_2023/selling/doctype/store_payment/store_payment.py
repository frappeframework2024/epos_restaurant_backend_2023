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

@frappe.whitelist()
def get_vendor_credit_balance(pos_profile):
	account_code = frappe.get_cached_doc("POS Profile",pos_profile,"default_credit_account")
	sql = "select sum(debit_amount-credit_amount) as total from `tabGeneral Ledger` where account = %(account)s"

	data = frappe.db.sql(sql,{"account":account_code},as_dict = 1)
	if data:
		return {"balance":data[0].get("total") or 0}

	return {"balance":0} 

