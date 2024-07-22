# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SaleCoupon(Document):
	pass

@frappe.whitelist()
def get_recent_sold_coupon():
	sale_coupon = frappe.db.get_list("Member Coupon",order_by='creation desc')
	return sale_coupon
