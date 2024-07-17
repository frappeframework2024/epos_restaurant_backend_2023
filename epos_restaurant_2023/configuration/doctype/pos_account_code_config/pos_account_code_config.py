# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class POSAccountCodeConfig(Document):
	def validate(self):
		self.name = self.outlet + "-" + self.shift_name 

	def on_update(self):
		frappe.clear_document_cache('POS Account Code Config', self.name)