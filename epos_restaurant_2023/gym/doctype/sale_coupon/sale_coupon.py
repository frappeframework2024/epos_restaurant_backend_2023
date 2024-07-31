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

	def validate(self):
		for p in self.payments:
			p.payment_amount = p.input_amount / p.exchange_rate
		self.total_payment_amount = sum([d.payment_amount for d in self.payments])
		
		if self.price != self.total_payment_amount:
			frappe.throw("Total Payment must equal to Price.")
	def on_submit(self):
		if self.total_payment_amount < self.price:
			frappe.throw("Please enter payment")

@frappe.whitelist()
def get_recent_sold_coupon():
	sale_coupon = frappe.db.get_list("Member Coupon",order_by='creation desc')
	return sale_coupon

@frappe.whitelist()
def get_coupon_by_number(coupon_number):
	coupon = frappe.get_doc("Sale Coupon",coupon_number)
	return coupon

@frappe.whitelist()
def insert_sale_coupon(data,is_submit):
	doc = frappe.get_doc({
		'doctype':'Sale Coupon',
		'coupon_type':data['coupon_type'],
		'coupon_number':data['coupon_number'],
		'membership':data['membership'] if data.get('membership') else '',
		'member_name':data['member_name'] if data.get('member_name') else '',
		'phone_number':data['phone_number'] if data.get('phone_number') else '' ,
		'price':data['price'],
		'limit_visit':data['limit_visit'],
		'expiry_date':data['expiry_date']
	})
	
	if data.get("payments"):
		for payment in data["payments"]:
			doc.append("payments",{
				"input_amount":payment["input_amount"],
				"currency":payment["currency"],
				"payment_type":payment["payment_type"],
				"exchange_rate":payment["exchange_rate"]
			})
	doc.insert()
	if is_submit==1:
		doc.submit()

@frappe.whitelist()
def submit_sale_coupon(docname):
	doc = frappe.get_doc("Sale Coupon",docname)
	doc.submit()


@frappe.whitelist()
def get_sale_coupon_payment(docname):
	payments = frappe.db.get_all("Sale Coupon Payment",{"parent":docname},["*"])
	return payments