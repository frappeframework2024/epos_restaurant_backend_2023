# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CashCoupon(Document):

	def validate(self):
		for d in self.items:
			d.claim_amount = 0
			d.balance = d.amount - d.claim_amount
			d.unlimited = self.unlimited
			d.expiry_date = self.expiry_date 
			d.member = self.member

		self.total_coupon = len(self.items)
		self.total_amount = sum([d.amount for d in self.items])
		self.total_claim = sum([d.claim_amount for d in self.items])
		self.total_balance = sum([d.balance for d in self.items])


	def on_submit(self): 
		on_update_to_customer([self.member])

	def on_update_after_submit(self):
		sql = """update `tabCash Coupon Items` i set i.unlimited = %(unlimited)s , i.expiry_date = %(expiry_date)s where parent = %(parent)s"""
		frappe.db.sql(sql,{"parent":self.name ,"unlimited": self.unlimited, "expiry_date": self.expiry_date}) 
		frappe.db.commit()

		on_update_to_customer([self.member])

	def on_cancel(self):
		sql = """select name from `tabSale Cash Coupon Claim` where docstatus != 1 and coupon_code in %(coupon_codes)s"""
		data = frappe.db.sql(sql,{"coupon_codes":[c.code for c in self.items]}, as_dict=1)
		if len(data) > 0:
			frappe.throw("There are coupon in sale trainsaction claim")

		on_update_to_customer([self.member])

def on_update_to_customer(members):
	from epos_restaurant_2023.api.api import update_cash_coupon_summary_to_customer
	update_cash_coupon_summary_to_customer(members)