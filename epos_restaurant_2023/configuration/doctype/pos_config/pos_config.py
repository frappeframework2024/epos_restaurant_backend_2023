# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from epos_restaurant_2023.api.cache_function import get_default_account_from_pos_config
from frappe.model.document import Document

class POSConfig(Document):
	def on_update(self):
		get_default_account_from_pos_config.cache_clear()
		frappe.clear_document_cache('POS Config', self.name)
