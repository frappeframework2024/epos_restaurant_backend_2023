# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class QuickBooksConfiguration(Document):
	def validate(self):
		if not self.refresh_token:
			self.access_token = None
			self.connected = 0
			self.qb_company_name = None
	
