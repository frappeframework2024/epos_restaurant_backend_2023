# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class POSProfile(Document):
	def on_update(self):
		frappe.clear_document_cache('POS Profile', self.name)
		frappe.cache().delete_keys(f"api.sale.get_default_print_template::{self.pos_config}")
		frappe.cache.delete_keys("system_settings:*")

