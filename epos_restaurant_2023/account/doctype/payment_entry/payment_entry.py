# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PaymentEntry(Document):
	pass

@frappe.whitelist()
def get_mode_of_payment_detail(branch="",mode_of_payment="",party_type=""):
	party_account = ""
	mode_of_payment_account = ""

	if mode_of_payment:
		mode_of_payment_account = frappe.db.get_value('Payment Type Account', {'parent': mode_of_payment,'business_branch':branch}, ['account'])

	if party_type == "Customer":
		party_account = frappe.db.get_value('Business Branch', {'name':branch}, ['default_receivable_account'])
	elif party_type == "Vendor":
		party_account = frappe.db.get_value('Business Branch', {'name':branch}, ['default_credit_account'])
	else:
		party_account = ""
	return{"mode_of_payment_account":mode_of_payment_account,"mode_of_payment_balance":0,"party_account":party_account,"party_balance":0}

@frappe.whitelist()
def get_party_detail(party_type,party,posting_date):
	fields = []
	name = ""
	if party_type == "Customer":
		fields.append("customer_name_en")
	elif party_type == "Employee":
		fields.append("employee_name")
	else:
		fields.append("vendor_name")
	party = frappe.db.get_value(party_type,{'name':party},fields,as_dict=1)
	if party_type == "Customer":
		name = party.customer_name_en
	elif party_type == "Employee":
		name = party.employee_name
	else:
		name = party.vendor_name
	return {"name":name,"balance":0}


	