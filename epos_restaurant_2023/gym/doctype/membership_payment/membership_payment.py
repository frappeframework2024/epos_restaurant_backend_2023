# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MembershipPayment(Document):
	def validate(self):	

		if frappe.db.exists("Membership",{"name":self.membership,"docstatus":0}):
			frappe.throw("Please submit membership (#{}) first.".format(self.membership))
		
		doc = frappe.db.get_list('Membership Payment',filters=[
									{
										'docstatus': 0,
										'membership':self.membership
									},
									['name','!=',self.name]
								])
		if doc:
			frappe.throw("There are draft payment need to submit first.")

		if (self.input_amount or 0) ==0  or  (self.payment_amount or 0) == 0:
			frappe.throw("Input or Paymout amount not allow zero(0)")

		self.payment_amount = (self.input_amount or 0) / (self.exchange_rate or 0)

		if (self.payment_amount or 0) > ( self.balance or 0):
			frappe.throw("Payment amount cannot grater than balance")

	def on_submit(self):
		update_membership(self)
	
	def on_cancel(self):
		update_membership(self)


def update_membership(self):
	data = frappe.db.sql("select  ifnull(sum(payment_amount),0)  as total_paid from `tabMembership Payment` where docstatus=1 and membership='{}' and payment_amount>0".format(self.membership))
	membership_amount = frappe.db.get_value('Membership', self.membership, 'grand_total')
	
	currency_precision = frappe.db.get_single_value('System Settings', 'currency_precision')
	if currency_precision=='':
		currency_precision = "2"

	
	if data and membership_amount:
		balance =round(membership_amount  , int(currency_precision))-  round(data[0][0]    , int(currency_precision))  

		if balance<0:
			balance = 0

		frappe.db.set_value('Membership', self.membership,  {
			'total_paid': data[0][0],
			'balance': balance  
		})
	

	## update customer balance
	cancel = True if self.docstatus == 2 else False
	update_customer_membership_summary(self.member, cancel)
	

def update_customer_membership_summary(customer, cancel = False):

	## get customer sale credit balance
	sale_sql = """select
	 	coalesce(sum(s.balance),0) as total_sale_balance 
	   from `tabSale` s where s.customer = %(customer)s"""
	sale = frappe.db.sql(sale_sql,{"customer":customer}, as_dict = 1)
	total_sale_balance = 0
	if len(sale) > 0:
		total_sale_balance = sale[0]["total_sale_balance"] or 0

	balance = "c.balance = {} + c.total_coupon_balance +  _c.total_balance".format(total_sale_balance)
	if cancel:
		balance = "c.balance = {} + c.total_coupon_balance ".format(total_sale_balance)

	sql = """update `tabCustomer` c
			inner join (
				select 
					%(customer)s as customer,
					coalesce(sum(m.grand_total),0) as total_amount,
					coalesce(sum(m.total_paid),0) as total_paid,
					coalesce(sum(m.balance),0) as total_balance
				from `tabMembership` m 
				where m.docstatus = 1 
				and m.customer =  %(customer)s ) as _c on _c.customer = c.name
			set c.membership_amount = _c.total_amount,
			c.membership_paid = _c.total_paid,
			c.membership_balance = _c.total_balance,
			{}
			where c.name = %(customer)s""".format(balance)
	frappe.db.sql(sql,{"customer":customer})