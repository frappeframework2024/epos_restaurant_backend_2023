# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import utils
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import getdate

class Expense(Document):
	def validate(self):
		
		#validate expense dsate
		if getdate(self.posting_date)>getdate(utils.today()):
			frappe.throw(_("Expense date cannot greater than current date"))

		#validate amount
		total_amount = 0
		total_quantity = 0
		for d in self.expense_items:
			d.amount = d.price * d.quantity
			total_quantity = total_quantity + d.quantity
			total_amount = total_amount + d.amount

		self.total_quantity = total_quantity
		self.total_amount = total_amount

		self.balance = self.total_amount
  
@frappe.whitelist(allow_guest=True)
def get_expense_code_account(expense_code,branch):
	accounts = frappe.db.sql("""select 
						  default_expense_account 
						  from `tabExpense Code Account` 
						  where parent = %(expense_code)s 
						  and business_branch = %(branch)s""",{'expense_code':expense_code,'branch':branch},as_dict=1)
	return accounts


		
