# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesCouponPayment(Document):

	def validate(self):
		sale_coupon = frappe.get_doc("Sale Coupon", self.sale_coupon)
		if sale_coupon.docstatus != 1:
			frappe.throw("The sale coupon not yet submit.")

		