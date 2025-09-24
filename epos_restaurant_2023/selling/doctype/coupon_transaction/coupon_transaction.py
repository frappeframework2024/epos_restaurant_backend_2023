# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from epos_restaurant_2023.api.account import submit_general_ledger_entry

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

		

	def after_insert(self):

		if self.transaction_type == "Used":
			#add GL entry
			unearned_revenue = frappe.get_cached_value("Business Branch",self.business_branch, "default_unearned_revenue_account")
			income_account = frappe.get_cached_value("Business Branch",self.business_branch, "default_income_account")
			pos_profile =  frappe.db.get_value("POS Profile",self.pos_profile,["pos_config","coupon_use_account"],as_dict=1)
			income_account = pos_profile.coupon_use_account if pos_profile.coupon_use_account != "" else income_account
			pos_config_accounts = (frappe.db.sql("""select 
												default_unearned_revenue_account,
												default_income_account 
										from `tabPOS Config Default Account` 
										where parent = %(pos_config)s and business_branch = %(business_branch)s""",{
				"pos_config":pos_profile.pos_config,
				"business_branch":self.business_branch
				}, as_dict=1) or [])
			
			if len(pos_config_accounts) > 0:
				account = pos_config_accounts[0]
				unearned_revenue = account.get("default_unearned_revenue_account","") if account.get("default_unearned_revenue_account","") != "" else unearned_revenue
				income_account = account.get("default_income_account","") if account.get("default_income_account","") != "" else income_account
 

			general_ledger_debit(self,account = {"account":unearned_revenue,"amount":abs(self.coupon_amount)})
			general_ledger_credit(self,account = {"account":income_account,"amount":abs(self.coupon_amount)})


	def on_update(self):

		if self.has_value_changed("status") and self.status == "Deleted":
			#add GL entry
			unearned_revenue = frappe.get_cached_value("Business Branch",self.business_branch, "default_unearned_revenue_account")
			income_account = frappe.get_cached_value("Business Branch",self.business_branch, "default_income_account")
			pos_profile =  frappe.db.get_value("POS Profile",self.pos_profile,["pos_config","coupon_use_account"],as_dict=1)
			income_account = pos_profile.coupon_use_account if pos_profile.coupon_use_account != "" else income_account
			pos_config_accounts = (frappe.db.sql("""select 
												default_unearned_revenue_account,
												default_income_account 
										from `tabPOS Config Default Account` 
										where parent = %(pos_config)s and business_branch = %(business_branch)s""",{
				"pos_config":pos_profile.pos_config,
				"business_branch":self.business_branch
				}, as_dict=1) or [])
			
			if len(pos_config_accounts) > 0:
				account = pos_config_accounts[0]
				unearned_revenue = account.get("default_unearned_revenue_account","") if account.get("default_unearned_revenue_account","") != "" else unearned_revenue
				income_account = account.get("default_income_account","") if account.get("default_income_account","") != "" else income_account
 
 

			tranactions = (frappe.db.sql("""select 
							transaction_type
							from `tabCoupon Transaction` 
							where name != %(name)s and coupon_code = %(coupon_code)s 
							and creation > %(creation)s and status in ('Active','Locked') 
							order by creation desc""",{"name":self.name,"coupon_code":self.coupon_code,"creation":self.creation},as_dict=1))
			if len(tranactions) > 0:
				if tranactions[0]["transaction_type"] == "Redeem":
					frappe.throw(("Coupon has already been redeemed for cash"))
				else:
					frappe.throw(("Can not delete coupon transaction"))
			general_ledger_credit(self,account = {"account":unearned_revenue,"amount":abs(self.coupon_amount)})
			general_ledger_debit(self,account = {"account":income_account,"amount":abs(self.coupon_amount)})
			frappe.db.sql("update `tabGeneral Ledger` set is_cancelled=1 where voucher_type='Coupon Transaction' and voucher_number='{}'".format(self.name))


def general_ledger_debit(self,account):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		"debit_amount":account["amount"],
		"voucher_type":"Coupon Transaction",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "លុបការប្រើប្រាស់គូប៉ុង " + self.coupon_number if self.status == "Deleted" else "ប្រើប្រាស់គូប៉ុង " + self.coupon_number,
		"is_cancelled":1 if self.status == "Deleted" else 0
	}

	# if self.transaction_type == "Used" :
	# 	doc["party_type"] ="Vendor"
	# 	doc["party"] = self.vendor
	# 	doc["party_name"] = frappe.get_cached_value("Vendor", self.vendor,"vendor_name")
		

	docs.append(doc)
	submit_general_ledger_entry(docs = docs,commit = False)

def general_ledger_credit(self,account):
	docs = []
	doc = {
		"doctype":"General Ledger",
		"posting_date":self.posting_date,
		"account":account["account"],
		
		"credit_amount":account["amount"],
		"voucher_type":"Coupon Transaction",
		"voucher_number":self.name,
		"business_branch": self.business_branch,
		"remark": "លុបការប្រើប្រាស់គូប៉ុង " + self.coupon_number if self.status == "Deleted" else "ប្រើប្រាស់គូប៉ុង " + self.coupon_number,
		"is_cancelled":1 if self.status == "Deleted" else 0
	}
	
	if self.transaction_type == "Used" :
		doc["party_type"] ="Vendor"
		doc["party"] = self.vendor
		doc["party_name"] = frappe.get_cached_value("Vendor", self.vendor,"vendor_name")

	docs.append(doc)
	submit_general_ledger_entry(docs=docs,commit=False)
		
