# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
import calendar
from datetime import datetime, timedelta
# from datetime import timedelta, date
from frappe.model.document import Document


class Membership(Document):
	def validate(self):
		if self.is_new():
			self.old_crypto_amount = 0		

		if self.membership_type =="Family Shared":
			if self.count_members <=0:
				frappe.throw("Your counter member not allow value less than zero(0).")
			
			if not self.membership_family_table and self.count_members > 1:
				frappe.throw("Please add members to list for Family Shared")

			elif len(self.membership_family_table) >= self.count_members:
				frappe.throw("List of members cannot allow more than {}".format(self.count_members - 1))
			elif len(self.membership_family_table) < (self.count_members - 1):
				frappe.throw("Member list not enough, please add more")	


		if self.discount_type=="Percent":
			self.total_discount = ((self.price or 0) * (self.discount or 0)/100)
			self.grand_total = (self.price or 0) - self.total_discount
		else:
			self.total_discount =  (self.discount or 0)
			self.grand_total = (self.price or 0) - self.total_discount
		
		#update date balance
		self.balance = self.grand_total - (self.total_paid or 0)
		

	def on_submit(self):
		update_customer_membership_summary(self)


	def before_update_after_submit(self):
		self.flags.old_customer = None
		old_member_sql = "select customer from `tabMembership` where name = %(membership)s"
		doc = frappe.db.sql(old_member_sql,{"membership":self.name}, as_dict=1)
		if len(doc)>0:
			if doc[0]["customer"] != self.customer:
				self.flags.old_customer = doc[0]["customer"]

	def on_update_after_submit(self):
		update_customer_membership_summary(self,old_customer=self.flags.old_customer)
	
	def on_cancel(self):
		_update_customer_membership_summary(self.customer,default_discount=self.default_discount, cancel=True )

	
def update_customer_membership_summary(self, old_customer=None):
	_update_customer_membership_summary(self.customer , default_discount=self.default_discount)
	if old_customer:
		_update_customer_membership_summary(old_customer,default_discount=0,cancel=True )

def _update_customer_membership_summary(customer,default_discount = 0, cancel = False):
	## update default discount to customer
	update_sql = "update `tabCustomer` set default_discount = %(default_discount)s where name = %(member)s"
	frappe.db.sql(update_sql,{"default_discount":default_discount,"member":customer})
	## end update default discount to customer

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
				and m.customer =  %(customer)s) as _c on _c.customer = c.name

				set c.membership_amount = _c.total_amount,
				c.membership_paid = _c.total_paid,
				c.membership_balance = _c.total_balance,
				{}
			where c.name = %(customer)s""".format(balance)
	frappe.db.sql(sql,{"customer":customer})


@frappe.whitelist( methods="POST")
def upgrade_membership_option(param):	
	p = json.loads(param)
	doc = frappe.get_doc("Membership", p["membership"])
	old_option = frappe.get_doc("Membership Options", p["old_membership_option"])	
	option = frappe.get_doc("Membership Options", p["new_membership_option"])	
	

	total_discount = 0
	grand_total = 0
	if doc.discount_type == "Percent":
		total_discount = (option.cost * (doc.discount or 0)/100)
		grand_total = (option.cost or 0) - total_discount
	else:
		total_discount =  (doc.discount or 0)
		grand_total = (option.cost or 0) - total_discount

	if doc.total_paid > grand_total:
		frappe.throw(_("Membership option not allow to down grade"))

	if old_option.tracking_limited :
		check_access_sql = """select 
							count(`name`) as total_check_in 
						from `tabMembership Check In Items` 
						where docstatus = 1 
						and parenttype = 'Membership Check In' 
						and membership = %(membership)s"""
		check_access = frappe.db.sql(check_access_sql, {"membership":doc.name}, as_dict = 1)

		if option.max_access < check_access[0]["total_check_in"]:
			frappe.throw(_("Membership option not allow down grade"))


	frappe.db.set_value("Membership",p["membership"],{"docstatus":0})
	new_doc = frappe.get_doc("Membership", p["membership"])

	if new_doc.duration_type == "Limited Duration":
		_duration =   option.membership_duration; 	
		_end_date = new_doc.end_date

		if new_doc.duration_base_on == "Day(s)":
			_end_date = new_doc.start_date + timedelta(days=_duration)
		elif new_doc.duration_base_on == "Week(s)":
			_end_date = new_doc.start_date + timedelta(weeks=_duration)
		elif new_doc.duration_base_on == "Month(s)":
			_end_date = add_months(new_doc.start_date,_duration)
		elif new_doc.duration_base_on == "Year(s)":
			_end_date = add_years(new_doc.start_date,_duration)
		else:
			_end_date = new_doc.start_date


	new_doc.old_membership_option = p["old_membership_option"] if not doc.old_membership_option else doc.old_membership_option
	new_doc.membership = p["new_membership_option"]
	new_doc.regular_end_date = _end_date
	new_doc.end_date = _end_date

	new_doc.regular_price = option.cost
	new_doc.price = option.cost
	new_doc.total_discount = total_discount
	new_doc.grand_total = grand_total
	new_doc.balance = grand_total - doc.total_paid
	new_doc.default_discount = option.default_discount
	new_doc.crypto_amount = option.crypto_amount
	new_doc.old_crypto_amount = old_option.crypto_amount
	new_doc.docstatus = 1
	new_doc.save()
	return True


def update_customer_saving_crypto(self):
	pass


def add_months(start_date, months):
    # Calculate the new month and year
    new_month = start_date.month + months
    new_year = start_date.year + (new_month - 1) // 12
    new_month = (new_month - 1) % 12 + 1
    
    # Determine the day in the new month
    day =start_date.day 
    try:
        new_date = datetime(new_year, new_month, day)
    except ValueError:
        next_month = new_month % 12 + 1
        next_year = new_year + (new_month // 12)
        new_date = datetime(next_year, next_month, 1) - timedelta(days=1)    
	
    return new_date

def add_years(start_date, years):
    # Calculate the new month and year
    new_month = start_date.month
    new_year = start_date.year + years
    new_month = (new_month - 1) % 12 + 1
    
    # Determine the day in the new month
    day =start_date.day 
    try:
        new_date = datetime(new_year, new_month, day)
    except ValueError:
        next_month = new_month % 12 + 1
        next_year = new_year + (new_month // 12)
        new_date = datetime(next_year, next_month, 1) - timedelta(days=1)    
	
    return new_date



