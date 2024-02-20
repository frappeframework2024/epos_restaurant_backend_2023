# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Voucher(Document):
	pass

@frappe.whitelist()
def insert_voucher_multiple_row(vouchers):
	for v in vouchers:
		doc = frappe.get_doc({
				"doctype": "Voucher",
				"customer": v["customer"],
				"working_day": v["working_day"],
				"cashier_shift": v["cashier_shift"],
				"posting_date": v["posting_date"],
				"actual_amount": v["actual_amount"],
				"credit_amount": v["credit_amount"],
				"balance": v["credit_amount"],
			})
		doc.insert()
	frappe.db.commit()
		