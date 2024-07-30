# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate
from frappe.model.document import Document
from frappe.utils.file_manager import save_file


class SaleCoupon(Document):
	def before_insert(self):
		self.posting_date = getdate()
		self.visited_count = 0
		self.balance = self.limit_visit - self.visited_count 


@frappe.whitelist()
def get_recent_sold_coupon():
	sale_coupon = frappe.db.get_list("Member Coupon",order_by='creation desc')
	return sale_coupon

@frappe.whitelist()
def get_coupon_by_number(coupon_number):
	coupon = frappe.get_doc("Sale Coupon",coupon_number)
	return coupon