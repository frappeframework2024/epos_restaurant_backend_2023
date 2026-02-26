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
		voucher_payment_sql = """
				select coalesce(sum(payment_amount),0) payment_amount from `tabSale Payment`
				where customer = '{0}' and payment_type_group = 'Voucher' and docstatus = 1
			""".format(self.customer) 
		total_voucher_payment = frappe.db.sql(voucher_payment_sql,as_dict=1)
		if len(customer_voucher_amount) > 0:
			frappe.db.set_value('Customer', self.customer, {
				'voucher_actual_amount': customer_voucher_amount[0].actual_amount,
				'voucher_credit_amount': customer_voucher_amount[0].credit_amount,
				'voucher_balance': customer_voucher_amount[0].credit_amount - total_voucher_payment[0].payment_amount
			})