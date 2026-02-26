# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class POSProfile(Document):
	def on_update(self):
		frappe.clear_document_cache('POS Profile', self.name)
