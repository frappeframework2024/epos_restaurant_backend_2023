# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class CouponCodes(Document):
	pass

@frappe.whitelist()
def check_coupon_code(coupon):
	if not coupon:
		frappe.throw(_("Please scan the QR code of the coupon"))
	data = frappe.db.sql("select name, coupon,coupon_status from `tabCoupon Codes` where coupon = %(coupon)s",{"coupon":coupon},as_dict=1)
	if not data:
		frappe.throw(_("Coupon code not found"))
	if data:
		if len([d for d in data if d.get("coupon_status") == "Unused"]) == 0:
			frappe.throw(_("Coupon code is already used"))
	return [d for d in data if d.get("coupon_status") =="Unused"][0]

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
