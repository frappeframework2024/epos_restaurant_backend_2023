# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from epos_restaurant_2023.api.account import submit_general_ledger_entry

class CouponTransaction(Document):
	def validate(self):
		#validate exhcange rate change 
		if self.transaction_type != "Use":
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


		## calculate markup percentage
		if self.transaction_type != "Use":
			self.markup_percentage = ((self.coupon_amount - self.actual_amount)/self.actual_amount) * 100

		#add GL entry
		if self.is_new():
			if self.transaction_type == "Use":
				unearned_revenue = frappe.get_cached_value("Business Branch",self.business_branch, "default_unearned_revenue")
				general_ledger_credit(self,account = {"account":unearned_revenue,"amount":abs(self.coupon_amount)})
				income_account = frappe.get_cached_value("Business Branch",self.business_branch, "default_income_account")
				general_ledger_debit(self,account = {"account":income_account,"amount":abs(self.coupon_amount)})
		else:
			if self.status == "Deleted":
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
				unearned_revenue = frappe.get_cached_value("Business Branch",self.business_branch, "default_unearned_revenue")
				general_ledger_debit(self,account = {"account":unearned_revenue,"amount":abs(self.coupon_amount)})
				income_account = frappe.get_cached_value("Business Branch",self.business_branch, "default_income_account")
				general_ledger_credit(self,account = {"account":income_account,"amount":abs(self.coupon_amount)})
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
		"remark": "Delete Coupon Transaction" if self.status == "Deleted" else "",
		"is_cancelled":1 if self.status == "Deleted" else 0
	}
	docs.append(doc)
	submit_general_ledger_entry(docs = docs)

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
		"remark": "Delete Coupon Transaction" if self.status == "Deleted" else "",
		"is_cancelled":1 if self.status == "Deleted" else 0
    }
    docs.append(doc)
    submit_general_ledger_entry(docs=docs)
		
