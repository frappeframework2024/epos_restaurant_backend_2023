# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CouponTransaction(Document):
	def validate(self):
		
		#validate exhcange rate change 
		if self.transaction_type != "Use":
			sql_exchange_rate = """select 
								exchange_rate,
								change_exchange_rate 
							from `tabCurrency Exchange` 
							where to_currency = %(to_currency)s and to_currency != from_currency
								and docstatus = 1 
							order by 
							posting_date desc, 
							modified desc limit 1"""
			exch = frappe.db.sql(sql_exchange_rate,{"to_currency":self.currency},as_dict=1) 
			self.exchange_rate = 1
			if exch:
				self.exchange_rate = exch[0].exchange_rate

			self.exchange_rate = self.exchange_rate or 1

		self.actual_amount = self.input_actual_amount / self.exchange_rate 
		if self.input_coupon_amount == 0 and self.actual_amount > 0:
			self.input_coupon_amount = self.actual_amount
		self.coupon_amount = self.input_coupon_amount / self.exchange_rate 


		## calculate markup percentage
		if self.transaction_type != "Use":
			self.markup_percentage = ((self.coupon_amount - self.actual_amount)/self.actual_amount) * 100
		


		
