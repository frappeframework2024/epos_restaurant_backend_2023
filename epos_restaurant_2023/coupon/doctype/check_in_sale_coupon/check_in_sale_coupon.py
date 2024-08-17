# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today,getdate
from frappe.model.document import Document


class CheckInSaleCoupon(Document):
	def validate(self):
		sale_coupon = frappe.get_doc("Sale Coupon",self.coupon_number)
		# if getdate(sale_coupon.expiry_date) < getdate(today()):
		# 	frappe.throw(_("Coupon was expired"))

		if sale_coupon.balance < int(self.visited_count):
			frappe.throw(_("Remaining visit not enough to Check In"))
			
		if int(self.visited_count) <= 0:
			frappe.throw(_("Invalid to Check In"))
	
	def after_insert(self):
		self.submit()

	def on_submit(self):
		coupon_number = frappe.db.get_value("Sale Coupon",self.coupon_number,['name','docstatus'],as_dict=1)
		if coupon_number.docstatus != 1:
			frappe.throw("Please submit coupon first.")

		update_visited(self)
	
	def on_cancel(self):
		update_visited(self)


def update_visited(self):
	frappe.db.sql("""
			UPDATE `tabSale Coupon` a
			JOIN (
				SELECT SUM(visited_count) AS total_visit,
				 %(coupon_number)s as coupon_number
				FROM `tabCheck In Sale Coupon`
				where docstatus = 1 and coupon_number = %(coupon_number)s
			) AS sub ON a.name = sub.coupon_number
			SET a.visited_count = sub.total_visit,
				a.balance = a.limit_visit - sub.total_visit
			WHERE a.name = %(coupon_number)s;
		""",{"coupon_number":self.coupon_number})
	frappe.db.commit()