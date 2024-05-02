# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BulkSalePayment(Document):
	pass

@frappe.whitelist()
def get_sale_by_customer(customer,payment_type):
	sales = frappe.db.sql("select name sale,'{1}' payment_type,grand_total amount,total_paid payment_amount,balance from `tabSale` where customer = '{0}' and docstatus=1 and balance > 0".format(customer,payment_type),as_dict=1)
	return sales