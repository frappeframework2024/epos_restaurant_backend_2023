# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VoucherPayment(Document):
	def on_submit(self):
		sql = """
			SELECT 
				SUM(credit_amount) credit_amount,
				SUM(actual_amount) actual_amount,
				SUM(balance)  balance FROM `tabVoucher`
			WHERE customer = {} and docstatus = 1
			GROUP BY customer
		""".format(self.customer)
		customer_voucher_amount = frappe.db.sql(sql)