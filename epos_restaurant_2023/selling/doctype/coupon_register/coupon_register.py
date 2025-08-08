# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CouponRegister(Document):
	def before_submit(self):
		self.update_total_coupons()

	def update_total_coupons(self):
		data = frappe.db.sql("select count(*) as total from `tabCoupon Codes` where coupon_register=%(name)s",{"name":self.name},as_dict = 1)
		if(data):
			self.total_coupons = data[0].get("total")
		
