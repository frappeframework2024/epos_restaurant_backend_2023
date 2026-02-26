# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

from epos_restaurant_2023.account.doctype.journal_entry.general_ledger_entry import submit_sale_to_general_ledger_entry
import frappe
from frappe import _
from frappe.model.document import Document


class JournalEntry(Document):
	def validate(self):
		self.total_credit = sum(d.credit for d in self.get("account_entries"))
		self.total_debit = sum(d.debit for d in self.get("account_entries"))
		if len([d for d in self.account_entries if d.debit==d.credit and d.debit>0 and d.credit>0]):
			frappe.throw(_("You cannot credit and debit same account at the same time"))
		
		if self.total_credit != self.total_debit:
			frappe.throw(_("Credit amount must equal to Debit amount."))
		for d in [x for x in self.account_entries if x.party]:
			
			d.party_name = frappe.get_cached_value(d.party_type, d.party, frappe.get_cached_value("Reference Doctype",d.party_type, "title_field"))

	def before_submit(self):
		if self.party:
			for d in [x for x in self.account_entries if not x.party]: 
				d.party_type = self.party_type
				d.party = self.party
				d.party_name = frappe.get_cached_value(d.party_type, d.party_name, frappe.get_cached_value("Reference Doctype",d.party_type, "title_field"))
   
   
	def on_submit(self):
		submit_sale_to_general_ledger_entry(self)	
  
	def on_cancel(self):
		from epos_restaurant_2023.api.account import cancel_general_ledger_entery
		cancel_general_ledger_entery("Journal Entry", self.name)
  