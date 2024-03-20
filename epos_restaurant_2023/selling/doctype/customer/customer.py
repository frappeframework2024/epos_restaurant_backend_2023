# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import utils
from frappe import _
from datetime import datetime
from frappe.utils.data import strip

class Customer(Document):
	def validate(self):
		
		if self.flags.ignore_validate == True:
			return
		if self.date_of_birth:
			if datetime.strptime(str(self.date_of_birth), "%Y-%m-%d").date() >datetime.strptime(utils.today(), "%Y-%m-%d").date():
				frappe.throw(_("Date of birth cannot be greater than the current time"))

		if not self.customer_name_kh:
			self.customer_name_kh = self.customer_name_en

		self.customer_code_name = "{} - {}".format(self.name,self.customer_name_en)
	# def on_update(self):
	# 	if hasattr(self,'attach'):
	# 		if self.attach and self.is_new():
	# 			file = frappe.get_doc('File', self.attach)
	# 			file.attached_to_name = self.name
	# 			file.attached_to_field = ''
	# 			file = file.save()
	# 			frappe.db.set_value('Customer', self.name,{'photo':file.file_url})
	# 			frappe.db.commit()
	# 		else:
	# 			# remove profile
	# 			frappe.db.set_value('Customer', self.name,{'photo':''})

	def autoname(self):
		if self.flags.ignore_autoname == True:
			return
		
		from frappe.model.naming import set_name_by_naming_series, get_default_naming_series,make_autoname

		if strip(self.customer_code) =="":
			set_name_by_naming_series(self)
			self.customer_code = self.name	

		self.customer_code = strip(self.customer_code)
		self.name = self.customer_code


	def after_rename(self, old_name,new_name,merge):  
		if self.flags.ignore_after_rename == True:
			return
		frappe.db.set_value('Customer', new_name, {
			'customer_code_name': "{} - {}".format(new_name,self.customer_name_en),
			'customer_code': new_name		
		}) 
		
  
@frappe.whitelist()
def get_customer_order_summary(customer):
	total_visit = 0
	total_order = 0
	total_annual_order = 0
	sql = "select count(name) as total_visit, sum(grand_total) as total_amount from `tabSale` where customer='{}' and docstatus=1".format(customer)
	data = frappe.db.sql(sql, as_dict=1)
	today = datetime.today()  
	year = today.strftime("%Y")
	
	
	if data:
		total_visit = data[0]["total_visit"]
		total_order = data[0]["total_amount"]

		
	sql = "select  sum(grand_total) as total_amount from `tabSale` where posting_date >= '{}-01-01' and customer='{}' and docstatus=1".format(year,customer)
	data = frappe.db.sql(sql, as_dict=1)
	if data:
		total_annual_order = data[0].total_amount
	voucher_balance = frappe.db.get_value("Customer",customer,'voucher_balance')
	return {
		"total_visit":int(total_visit or 0),
		"total_order":float( total_order or 0),
		"total_annual_order": float(total_annual_order  or 0),
		"voucher_balance": float( voucher_balance or 0)
	}

@frappe.whitelist()
def get_voucher_list_per_customer(customer):
	vouchers = frappe.db.get_list("Voucher",
		order_by='modified desc',
		fields=['name', 'credit_amount','actual_amount'],
		filters={
			'customer': customer,
			'docstatus':['!=','2']
		},
		page_length=5000)
	for v in vouchers:
		payments = frappe.db.get_list("Voucher Payment",
			fields=['name', 'payment_type','payment_amount'],
			filters={
				'customer': customer,
				'voucher': v.name,
				'docstatus':['!=','2']
			})
		v['payments'] = payments or []
	return vouchers
	