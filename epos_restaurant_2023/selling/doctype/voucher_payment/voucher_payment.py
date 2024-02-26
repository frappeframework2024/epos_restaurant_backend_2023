# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VoucherPayment(Document):
	def on_submit(self):
		self.update_customer_voucher_balance()
	def on_cancel(self):
		self.update_customer_voucher_balance()

	def update_customer_voucher_balance(self):
		sql = """
			SELECT 
				SUM(credit_amount) credit_amount,
				SUM(actual_amount) actual_amount
			FROM `tabVoucher`
			WHERE customer = '{}' and docstatus = 1
			GROUP BY customer
			""".format(self.customer)
		customer_voucher_amount = frappe.db.sql(sql,as_dict=1)
			
		# get customer voucher balance 
		voucher_balance =frappe.db.get_value("Customer",self.customer,"voucher_balance")
		if len(customer_voucher_amount) > 0:
			frappe.db.set_value('Customer', self.customer, {
				'voucher_actual_amount': customer_voucher_amount[0].actual_amount,
				'voucher_credit_amount': customer_voucher_amount[0].credit_amount,
				'voucher_balance': (voucher_balance or 0) + self.credit_amount
			})