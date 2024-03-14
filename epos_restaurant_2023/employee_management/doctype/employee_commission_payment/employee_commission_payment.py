# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeCommissionPayment(Document):
	def on_submit(self):
		doc = frappe.get_doc("Sale",self.sale)
		paid_amount = doc.sale_commission_paid_amount + float(self.paid_amount)
		balance = float(doc.sale_commission_balance) - float(self.paid_amount)
		frappe.db.sql("update `tabSale` set sale_commission_paid_amount = {}, sale_commission_balance = {} where name = '{}'".format(paid_amount,balance,doc.name))
	def on_cancel(self):
		doc = frappe.get_doc("Sale",self.sale)
		paid_amount = doc.sale_commission_paid_amount - float(self.paid_amount)
		balance = float(doc.sale_commission_balance) + float(self.paid_amount)
		frappe.db.sql("update `tabSale` set sale_commission_paid_amount = {}, sale_commission_balance = {} where name = '{}'".format(paid_amount,balance,doc.name))