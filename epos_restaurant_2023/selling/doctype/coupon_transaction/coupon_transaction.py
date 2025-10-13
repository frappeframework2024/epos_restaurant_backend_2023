# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from epos_restaurant_2023.api.account import submit_general_ledger_entry
from frappe import _

from frappe import conf
class CouponTransaction(Document):
	def validate(self):
		#validate exhcange rate change 
		if self.transaction_type != "Used":
			if self.currency != frappe.get_cached_value("ePOS Settings",None,"currency"):
				sql_exchange_rate = """select 
									exchange_rate,
									change_exchange_rate 
								from `tabCurrency Exchange` 
								where to_currency = %(to_currency)s and to_currency != from_currency
									and docstatus = 1 
								order by 
								posting_date desc, 
								modified desc limit 1"""
				exch = frappe.db.sql(sql_exchange_rate,{"to_currency":self.currency},as_dict=1) 
				self.exchange_rate = 1
				if exch:
					self.exchange_rate = exch[0].exchange_rate

				self.exchange_rate = self.exchange_rate or 1

		self.actual_amount = self.input_actual_amount / self.exchange_rate 
		if self.input_coupon_amount == 0 and self.actual_amount > 0:
			self.input_coupon_amount = self.actual_amount
		self.coupon_amount = self.input_coupon_amount / self.exchange_rate 
		if self.transaction_type == "Used":
			self.transaction_amount = self.actual_amount

		## calculate markup percentage
		if self.transaction_type != "Used":
			self.markup_percentage = ((self.coupon_amount - self.actual_amount)/(self.actual_amount or 1)) * 100
		
		if self.transaction_type =="Used":
			
			self.validate_account_code()
			

	def after_insert(self):
		if self.transaction_type == "Used":
			frappe.enqueue("epos_restaurant_2023.selling.doctype.coupon_transaction.coupon_transaction.update_coupon_transaction_after_insert", queue='default', self = self)

		frappe.enqueue("epos_restaurant_2023.api.supabase.send_coupon_data_to_supabase", queue='short', coupon_code = self.coupon_code, coupon_number=self.coupon_number,posting_date=self.posting_date)
		# from epos_restaurant_2023.api.supabase import send_coupon_data_to_supabase
		# send_coupon_data_to_supabase(self.coupon_code,self.coupon_number)

 
	def on_update(self):
		if self.has_value_changed("status") and self.status == "Deleted":
			frappe.db.sql("update `tabGeneral Ledger` set is_cancelled=1 where voucher_type='Coupon Transaction' and voucher_number='{}'".format(self.name))


	def validate_account_code(self):
		# Account Code Priority 
		# 1 from Coupon transaction with transaction Sale Coupon or Coupon Issue
		# 2. from POS Profile Use Coupon Account
		# 3. from business branch account setting
		
		# debit acocunt is account use for deduct use acoupon amount from liabilty account 
		# debit account be account payable or income account base on store owner, store rented or inteneral coupon using for managemnent team		
		debit_account = "" 

		# credit account 
		credit_account = ""


		


		if self.transaction_type =="Used":
			
			# 1 Check debit account code from coupon transaction
			sql="select  credit_account  from `tabCoupon Transaction` where coupon_code=%(coupon_code)s and coupon_number = %(coupon_number)s and transaction_type in ('Sale Coupon','Coupon Issue') and coalesce(credit_account,'')<> ''"
			account_data = frappe.db.sql(sql,{"coupon_code":self.coupon_code, "coupon_number":self.coupon_number},as_dict = 1)
			if account_data:
				debit_account = account_data[0].get("credit_account")
			
			#2. use account code from pos profile 
			# check account type type = Income set it to credit account => Income Increase
			# it account type = "Payable" set it  to Debit Account => Payable Decrease

			credit_account = frappe.get_cached_value("POS Profile",self.pos_profile,"coupon_use_account")
			
			#3. check from pos_config
			if not debit_account:
				debit_account = frappe.get_cached_value("Business Branch",self.business_branch, "default_unearned_revenue_account")

			if not credit_account:
				credit_account = frappe.get_cached_value("Business Branch",self.business_branch, "default_income_account")

		
		self.debit_account = debit_account
		self.credit_account = credit_account
		if not self.debit_account:
			frappe.throw(_("Please set debit account for " ) + self.pos_profile)
			
		if not self.credit_account:
			frappe.throw(_("Please set credit account for " ) + self.pos_profile)




@frappe.whitelist()
def update_coupon_transaction_after_insert(self):
	reference_doctype, reference_name = frappe.get_cached_value("Coupon Codes", self.coupon_code,["reference_doctype","reference_name"])
	sql = "update `tabCoupon Transaction` set reference_doctype=%(reference_doctype)s, reference_name=%(reference_name)s where name = %(name)s"
	frappe.db.sql(sql,{"reference_doctype":reference_doctype,"reference_name":reference_name,"name":self.name})
	# submit to gl entry
	submit_to_gl_entry(self)

@frappe.whitelist()
def submit_to_gl_entry(self):
	docs = []
	# debit account
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":self.debit_account,
		"debit_amount":abs(self.coupon_amount),
		"voucher_type":"Coupon Transaction",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "លុបការប្រើប្រាស់គូប៉ុង " + self.coupon_number if self.status == "Deleted" else "ប្រើប្រាស់គូប៉ុង " + self.coupon_number,
		"is_cancelled":1 if self.status == "Deleted" else 0
	}

	docs.append(doc)
	# debit account
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":self.credit_account,
		"credit_amount":abs(self.coupon_amount),
		"voucher_type":"Coupon Transaction",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "លុបការប្រើប្រាស់គូប៉ុង " + self.coupon_number if self.status == "Deleted" else "ប្រើប្រាស់គូប៉ុង " + self.coupon_number,
		"is_cancelled":1 if self.status == "Deleted" else 0
	}
	doc["party_type"] ="Vendor"
	doc["party"] = self.vendor
	doc["party_name"] = frappe.get_cached_value("Vendor", self.vendor,"vendor_name")

	docs.append(doc)



	submit_general_ledger_entry(docs = docs,commit = True)

 
 
 