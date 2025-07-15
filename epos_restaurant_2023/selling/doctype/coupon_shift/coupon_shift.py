# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from epos_restaurant_2023.api.account import submit_general_ledger_entry

class CouponShift(Document):
	def validate(self):		
		full_name = frappe.utils.get_fullname(frappe.session.user)
		if not self.open_by :
			self.open_by = full_name

		if (self.is_new() or 0) == 0:
			if has_value_changed(self,'posting_date') or has_value_changed(self,'pos_profile') or has_value_changed(self,'vendor') or has_value_changed(self,'is_closed'):
				if self.is_closed == 1:
					submit_Gl_Entry(self)
				else:
					if check_for_existing_GL_Entry(self) == 1:
						cancel_Gl_Entry(self)
		else:
			if self.is_closed == 1:
				submit_Gl_Entry(self)
			else:
				if check_for_existing_GL_Entry(self) == 1:
					cancel_Gl_Entry(self)

def has_value_changed(self, fieldname):
	previous = self.get_doc_before_save()
	return str(previous.get(fieldname)) != str(self.get(fieldname)) if previous else True

def check_for_existing_GL_Entry(self):
	sql = "select name from `tabGeneral Ledger` where voucher_type='Coupon Shift' and voucher_number='{0}'".format(self.name)
	data = (frappe.db.sql(sql,as_dict=1) or [])
	if len(data)>0:
		return 1
	else:
		return 0

def getCouponShiftAmount(self):
	credit_account = ""
	payment_account = ""
	pos_profile = frappe.db.get_value("POS Profile",self.pos_profile,["pos_config","default_credit_account","coupon_posting_type"],as_dict=1)
	pos_config = frappe.db.get_value("POS Config",pos_profile.pos_config,["business_branch","name"],as_dict=1)

	branch = frappe.get_doc("Business Branch",pos_config.business_branch)
	credit_account = branch.default_credit_account
	payment_account = branch.default_coupon_payment_expense_account
	
	pos_config_account = (frappe.db.sql("""select default_credit_account,default_coupon_payment_expense_account from `tabPOS Config Default Account` where parent = %(pos_config)s and business_branch = %(business_branch)s""",{"pos_config":pos_config.name,"business_branch":pos_config.business_branch},as_dict=1) or [])
	if len(pos_config_account)>0:
		if pos_config_account[0].default_credit_account:
			credit_account = pos_config_account[0].default_credit_account
		if pos_config_account[0].default_coupon_payment_expense_account:
			payment_account = pos_config_account[0].default_coupon_payment_expense_account

	if pos_profile.default_credit_account:
		credit_account = pos_profile.default_credit_account

	coupon_transaction = (frappe.db.sql("""select sum(abs(actual_amount)) actual_amount,sum(abs(coupon_amount)) coupon_amount from `tabCoupon Transaction` where transaction_type = 'Use' and pos_profile = %(pos_profile)s and coupon_shift = %(coupon_shift)s""",{"pos_profile":self.pos_profile,"coupon_shift":self.name},as_dict=1) or [])
	return {
			"actual_amount":coupon_transaction[0].actual_amount,
			"coupon_amount":coupon_transaction[0].coupon_amount,
			"credit_account":credit_account,
			"payment_account":payment_account,
			"coupon_posting_type":pos_profile.coupon_posting_type
	}
	
def submit_Gl_Entry(self):
	coupon_shift = getCouponShiftAmount(self)
	docs = []
	amount = coupon_shift.get("actual_amount",0) if coupon_shift.get("coupon_posting_type","") == "Actual Amount" else coupon_shift.get("coupon_amount",0)
	if (amount or 0) > 0:
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":coupon_shift.get("credit_account",""),
			"credit_amount": amount,
			"againt":coupon_shift.get("payment_account",""),
			"voucher_type":"Coupon Shift",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"remark" : "Transfer from coupon expense payment account to payable account",
			"party_type" : "Vendor",
			"party":self.vendor,
			"party_name":self.vendor_name
		}
		docs.append(doc)
	
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":coupon_shift.get("payment_account",""),
			"debit_amount": amount,
			"againt": coupon_shift.get("credit_account",""),
			"voucher_type":"Coupon Shift",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"remark" : "Transfer to payable account"
			}
		docs.append(doc)
	submit_general_ledger_entry(docs=docs)
 
def cancel_Gl_Entry(self):
	coupon_shift = getCouponShiftAmount(self)
	amount = coupon_shift.get("actual_amount",0) if coupon_shift.get("coupon_posting_type","") == "Actual Amount" else coupon_shift.get("coupon_amount",0)
	frappe.db.sql("update `tabGeneral Ledger` set is_cancelled=1 where voucher_type='Coupon Shift' and voucher_number = '{0}'".format(self.name))
	docs = []
	if (amount or 0) > 0:
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":coupon_shift.get("credit_account",""),
			"debit_amount":amount,
			"againt":coupon_shift.get("payment_account",""),
			"voucher_type":"Coupon Shift",
			"voucher_number":self.name,
			"is_cancelled":1,
			"business_branch": self.business_branch,
			"remark" : "Cancelled Coupon Shift",
			"party_type" : "Vendor",
			"party":self.vendor,
			"party_name":self.vendor_name
		}
		docs.append(doc)
	
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":coupon_shift.get("payment_account",""),
			"credit_amount": amount,
			"againt": coupon_shift.get("credit_account",""),
			"voucher_type":"Coupon Shift",
			"voucher_number":self.name,
			"is_cancelled":1,
			"business_branch": self.business_branch,
			"remark" : "Cancelled Coupon Shift",
			"party_type" : "Vendor",
			"party":self.vendor,
			"party_name":self.vendor_name
			}
		docs.append(doc)
	submit_general_ledger_entry(docs=docs)