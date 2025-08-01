# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import datetime
from frappe.utils import get_datetime
class CouponCodes(Document):
	def validate(self):
		# validate coupon exist with status Unused
		if self.coupon:
		 
			if self.is_new():

				if frappe.db.exists("Coupon Codes",{"coupon":self.coupon,"coupon_status":["in",["Unused","Used"]]}):
					frappe.throw(_("Coupon {} code already exist").format(self.coupon))
			else:
				if frappe.db.exists("Coupon Codes",{"coupon":self.coupon,"coupon_status":["in",["Unused","Used"]],"name":["!=",self.name]}):
					frappe.throw(_("Coupon {} code already exist").format(self.coupon))

	def on_trash(self):
		if frappe.db.exists("Coupon Transaction",{"coupon_code":self.name}):
			frappe.throw(_("Cannot delete coupon code as it has transactions"))

		frappe.msgprint(_("Delete coupon code successfully"))

@frappe.whitelist()
def check_coupon_code(coupon):
	if not coupon:
		frappe.throw(_("Please scan the QR code of the coupon"))
	data = frappe.db.sql("select name, coupon,coupon_status,expired_date from `tabCoupon Codes` where coupon = %(coupon)s order by creation desc limit 1",{"coupon":coupon},as_dict=1)
	if not data:
		frappe.throw(_("This coupon is not exist in the system"))
	 
	if data[0].get("coupon_status") == "Redeemed":
		frappe.throw(_("Coupon code is already redeem"))

	if data[0].get("coupon_status") == "Expired":
		frappe.throw(_("This coupon code is already expired"))
	if data[0].get("coupon_status") == "Used":
		if datetime.datetime.now() > get_datetime(data[0].expired_date):
			frappe.throw(_("This coupon code is expired"))   

		frappe.throw(_("Coupon code is already used"))
	
	if data[0].get("coupon_status") == "Redeemed":
		frappe.throw(_("Coupon code is already redeem"))
	
	
	

	return data[0]

@frappe.whitelist()
def get_coupon_info(coupon):
	coupon_codes = frappe.db.sql("select name,coupon,creation,owner,coupon_status,sale_date from `tabCoupon Codes` where coupon = %(coupon)s",{"coupon":coupon},as_dict=1)

	if not coupon_codes:
		frappe.throw(_("Coupon code not found"))

	sql="""
		select 
			coupon_code,
			ct.coupon_number,
			ct.posting_date,
			ct.sale,
			ct.transaction_type,
			ct.customer,
			ct.customer_name,
			ct.actual_amount,
			ct.coupon_amount,
			ct.input_actual_amount,
			ct.currency,
			ct.exchange_rate


		from `tabCoupon Transaction` ct
		where
			ct.coupon_code in %(coupon_codes)s
		order by
			ct.posting_date,
			ct.creation
	"""
	coupon_transactions = frappe.db.sql(sql,{"coupon_codes":[d.get("name") for d in coupon_codes]},as_dict=1)


	return {
		"coupon_number":coupon,
		"coupon_info":coupon_codes,
		"coupon_transactions":coupon_transactions
	}
