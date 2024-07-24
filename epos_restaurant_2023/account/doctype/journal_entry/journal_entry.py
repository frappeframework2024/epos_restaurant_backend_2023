# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class JournalEntry(Document):
	def validate(self):
		self.total_credit = sum(d.credit for d in self.get("account_entries"))
		self.total_debit = sum(d.debit for d in self.get("account_entries"))
		for d in self.get("account_entries"):
			if d.debit == d.credit:
				frappe.throw(_("You cannot credit and debit same account at the same time"))
		if self.total_credit != self.total_debit:
			 frappe.throw("Credit amount must equal to Debit amount.")

	def on_submit(self):
		for account in self.account_entries:
			pass