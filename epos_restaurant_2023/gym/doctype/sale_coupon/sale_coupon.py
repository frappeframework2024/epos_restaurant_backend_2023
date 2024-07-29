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
def save_coupon_and_files(file,file_name,sale_coupon=None):
	import base64
	saved_file = save_file(file_name, content=base64.b64decode(file), dt="Sale Coupon", dn='52854', is_private=0)
	return saved_file