# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate
class SaleCoupon(Document): 
	def validate(self): 

		if self.is_new():
			self.posting_date = getdate() if not self.posting_date else self.posting_date
			self.visited_count = 0
			

		if len( self.items) <=0:
			frappe.throw(_("Sale coupon items not allow empty record"))

		if len( [d for d in self.items if d.quantity <= 0]) >0:
			frappe.throw(_("Please check quantity agian"))

		if  self.member_type != "Individual":
			if not self.member:
				frappe.throw("Please select member to continue")	
			m = frappe.get_doc("Customer", self.member)
			self.gender = m.gender
			self.member_name = m.customer_name_en
			self.member_name_kh = m.customer_name_kh
			self.phone_number = m.phone_number
			self.phone_number_2 = m.phone_number_2

		else:
			if not self.member_name:
				frappe.throw("Please enter member name")	
			if not self.member_name_kh:
				self.member_name_kh = self.member_name
		self.balance = self.limit_visit - self.visited_count
		validate_sale_coupon_payment(self)

		if self.payment_balance < 0:
			frappe.throw("You cannot settle with over grand total amount")
		

	def on_submit(self):
		for p in self.payments:
			doc = frappe.get_doc({
				"doctype":"Sales Coupon Payment",
				"payment_type":p.payment_type,
				"currency":p.currency,
				"sale_coupon":self.name,
				"sale_amount":self.grand_total,
				"input_amount":p.input_amount,
				"payment_amount":p.payment_amount,
				"exchange_rate":p.exchange_rate,
			}).insert()
			doc.submit()

		update_customer_relate_sale_coupon(self)

#
def update_customer_relate_sale_coupon(self):
	if  self.member_type != "Individual":
		sql = """update `tabCustomer` c
				inner join (
					select 
						%(customer_code)s as member,
						coalesce(sum(s.limit_visit),0) as total_limit_visit,
						coalesce(sum(s.visited_count),0) as total_visited_count,
						coalesce(sum(s.balance),0) as total_visited_balance
					from `tabSale Coupon` s
					where s.docstatus = 1 
					and s.member = %(customer_code)s
				) sc on c.name = sc.member
					set c.total_limit_visit = sc.total_limit_visit,
					c.total_visited_count = sc.total_visited_count,
					c.total_visited_balance = sc.total_visited_balance
				where c.name = %(customer_code)s"""	
		frappe.db.sql(sql, {"customer_code": self.member })		


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
		doc.gender=data['gender']
		doc.price=data['price']
		doc.grand_total=data['grand_total']
		doc.discount_value=data['discount_value']
		doc.discount_type=data['discount_type']
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
			'gender':data['gender'],
			'price':data['price'],
			'grand_total':data['grand_total'],
			'discount_value':data['discount_value'],
			'discount_type':data['discount_type'],
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
		if doc.total_payment_amount != doc.grand_total:
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

@frappe.whitelist()
def validate_sale_coupon_payment(self):
	for p in self.payments:
		p.payment_amount = p.input_amount / p.exchange_rate

	self.total_payment_amount = sum([d.payment_amount for d in self.payments])
	self.payment_balance = self.grand_total - self.total_payment_amount
