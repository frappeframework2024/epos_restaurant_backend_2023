# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesCouponPayment(Document):

	def validate(self):
		if not self.sale_coupon:
			frappe.throw("Sale Coupon cannot be blank")	
		
		sale_coupon = frappe.get_doc("Sale Coupon", self.sale_coupon)
		if sale_coupon.docstatus != 1:
			frappe.throw("The sale coupon not yet submit.")
		
		self.payment_amount = self.input_amount / (self.exchange_rate or 1)	

		currency_precision = frappe.db.get_single_value('System Settings', 'currency_precision')
		if currency_precision=='':
			currency_precision = "2"			 

		balance = round(self.sale_amount  , int(currency_precision))  - round(self.payment_amount  , int(currency_precision)) 
		if balance < 0:
			frappe.throw("Payment amount cannot greater sale amount") 

	def on_submit(self):
		update_payment_balance(self)
	
	def on_cancel(self):
		update_payment_balance(self)


def update_payment_balance(self):
	sql = """update `tabSale Coupon` s
			inner join (
				select 
					p.sale_coupon,  
					coalesce(sum(p.payment_amount) ,0) as total_payment 
				from `tabSales Coupon Payment` p
				where docstatus = 1 
				and p.sale_coupon = %(coupon_number)s 
				group by p.sale_coupon 
			) sp on sp.sale_coupon =  %(coupon_number)s
			set 
				s.payment_balance = s.grand_total - sp.total_payment,
				s.total_payment_amount = sp.total_payment
			"""
	frappe.db.sql(sql,{"coupon_number":self.sale_coupon})

	## update customer on total sale coupon payment balance
	sale_coupon = frappe.get_doc("Sale Coupon", self.sale_coupon)
	if not sale_coupon.member_type  is "Individual":
		customer_sql = """update `tabCustomer` c
						inner join (
							select 
								s.member,  
								coalesce(sum(s.payment_balance) ,0) as total_payment_balance 
							from `tabSale Coupon` s
							where docstatus = 1 
							and s.member = %(customer_code)s
							group by s.member 
						) sp on sp.member =  %(customer_code)s
						set c.total_sale_coupon_payment_balance = sp.total_payment_balance"""
		frappe.db.sql(customer_sql,{"customer_code":sale_coupon.member})