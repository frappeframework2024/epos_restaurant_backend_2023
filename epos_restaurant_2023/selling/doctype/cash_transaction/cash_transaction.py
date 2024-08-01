# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CashTransaction(Document):
	def validate(self):
		if self.flags.ignore_validate:
			return
		self.amount = self.input_amount / self.exchange_currency
		if not self.created_by:
			self.created_by = frappe.get_user().doc.full_name

		if frappe.get_cached_value("ePOS Settings",None,"use_basic_accounting_feature") and self.transaction_type == "Expense":			
			if self.transaction_status == "Cash In":
				if not self.expense_from:
					default_cash_transaction_expense_account = frappe.get_cached_value("Business Branch",self.business_branch, "default_cash_transaction_expense_account")
					frappe.throw(default_cash_transaction_expense_account)
					
					self.expense_from = default_cash_transaction_expense_account


				
				if not self.expense_to: 
					sql = "select account from `tabPayment Type Account` where business_branch=%(business_branch)s and parent=%(payment_type)s limit 1"
					data = frappe.db.sql(sql,{"business_branch":self.business_branch,"payment_type":self.payment_type},as_dict=1)
					if data: 
						self.expense_to =  data[0]["account"]
					
				if not self.expense_to:
					branch = frappe.db.get_value('Business Branch', self.business_branch,  ['default_cash_account'], as_dict=1)
					branch.default_cash_account
			else:
				pass

