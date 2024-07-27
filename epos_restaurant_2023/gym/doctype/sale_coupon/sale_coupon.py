# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate
from frappe.model.document import Document
from frappe.utils.file_manager import save_file


class SaleCoupon(Document):
	def before_insert(self):
		self.posting_date = getdate()
		self.visit_count = 0
		self.balance = self.limit_visit - self.visit_count 


@frappe.whitelist()
def get_recent_sold_coupon():
	sale_coupon = frappe.db.get_list("Member Coupon",order_by='creation desc')
	return sale_coupon

@frappe.whitelist()
def save_coupon_and_files(files=[],sale_coupon=None):
	import base64
	for img in files:
		saved_file = save_file("Hello.jpg", content=img, dt="Sale Coupon", dn='52854', is_private=0)
	return saved_file