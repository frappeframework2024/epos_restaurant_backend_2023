# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
class SaleCoupon(Document):
	def before_save(self):
		self.posting_date = getdate()
		self.visited_count = 0
		self.balance = self.limit_visit - self.visited_count

	def validate(self): 
		if  self.member_type != "Individual":
			if not self.member:
				frappe.throw("Please select member to continue")	
			m = frappe.get_doc("Customer", self.member)
			self.gender = m.gender
			self.member_name = m.member_name
			self.member_name_kh = m.member_name_kh
			self.phone_number = m.phone_number
			self.phone_number_2 = m.phone_number_2

		else:
			if not self.member_name:
				frappe.throw("Please enter member name")	
			if not self.member_name_kh:
				self.member_name_kh = self.member_name


		for p in self.payments:
			p.payment_amount = p.input_amount / p.exchange_rate
		self.total_payment_amount = sum([d.payment_amount for d in self.payments])
		
		

	def on_submit(self):
		if self.price != self.total_payment_amount:
			frappe.throw("Total Payment must equal to Price.")

		for p in self.payments:
			doc = frappe.get_doc({
				"doctype":"Sales Coupon Payment",
				"payment_type":p.payment_type,
				"currency":p.currency,
				"sale_coupon":self.name,
				"sale_amount":self.price,
				"input_amount":p.input_amount,
				"payment_amount":p.payment_amount,
				"exchange_rate":p.payment_amount,
			}).insert()
			doc.submit()


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
	if data.get("name"):
		doc = frappe.get_doc('Sale Coupon',data.get("name"))
		doc.coupon_type=data['coupon_type']
		if data.get('coupon_type') != "Individual":
			doc.membership=data['membership'] or data['membership'] if data.get('membership') else ''
		doc.member_name=data['member_name'] if data.get('member_name') else ''
		doc.phone_number=data['phone_number'] if data.get('phone_number') else '' 
		doc.price=data['price']
		doc.limit_visit=data['limit_visit']
		doc.expiry_date=data['expiry_date']
		if data.get("payments"):
			doc.payments=[]
			for payment in data["payments"]:
				doc.append("payments",{
					"input_amount":payment["input_amount"],
					"currency":payment["currency"],
					"payment_type":payment["payment_type"],
					"exchange_rate":payment["exchange_rate"]
				})
		for p in doc.payments:
			p.payment_amount = p.input_amount / p.exchange_rate
		doc.total_payment_amount = sum([d.payment_amount for d in doc.payments])
		doc.save()
		
	else:
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
		if doc.total_payment_amount != doc.price:
			frappe.throw("Total Payment must equal to Price.")
		doc.submit()
	return doc

@frappe.whitelist()
def submit_sale_coupon(docname):
	doc = frappe.get_doc("Sale Coupon",docname)
	doc.submit()


@frappe.whitelist()
def get_sale_coupon_payment(docname):
	payments = frappe.db.get_all("Sale Coupon Payment",{"parent":docname},["*"])
	return payments
