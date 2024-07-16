# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeCommissionPayment(Document):
	def on_submit(self):
		for a in self.employee_commission_sale:
			doc = frappe.get_doc("Sale",a.sale)
			paid_amount = doc.sale_commission_paid_amount + float(a.paid_amount)
			balance = float(doc.sale_commission_balance) - float(a.paid_amount)
			frappe.db.sql("update `tabSale` set sale_commission_paid_amount = {}, sale_commission_balance = {} where name = '{}'".format(paid_amount,balance,doc.name))
	def on_cancel(self):
		for a in self.employee_commission_sale:
			doc = frappe.get_doc("Sale",a.sale)
			paid_amount = doc.sale_commission_paid_amount - float(a.paid_amount)
			balance = float(doc.sale_commission_balance) + float(a.paid_amount)
			frappe.db.sql("update `tabSale` set sale_commission_paid_amount = {}, sale_commission_balance = {} where name = '{}'".format(paid_amount,balance,doc.name))

	@frappe.whitelist()
	def get_sale_commission(doc):
		sales=[]
		data = frappe.db.sql("""
					   select name,
					   sale_commission_amount,
					   sale_commission_paid_amount,
					   sale_commission_balance,
					   posting_date
					   from `tabSale` 
					   where sale_commission_to = '{0}' and 
					   sale_commission_balance > 0 and
					   posting_date between '{1}' and '{2}'
					   """.format(doc.employee,doc.sale_start_date,doc.sale_end_date),as_dict=1)
		for a in data:
			sales.append({"sale":a.name,"commission_amount":a.sale_commission_amount,"paid_amount":a.sale_commission_paid_amount,"balance":a.sale_commission_balance,"posting_date":a.posting_date})
		if len(data) == 0:
			frappe.throw("No Record")
		else:
			return sales