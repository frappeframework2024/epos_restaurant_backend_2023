# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from frappe import _
import frappe
from epos_restaurant_2023.api.cache_function import get_default_account_from_pos_config
from frappe.model.document import Document 


class POSConfig(Document):
	def validate(self):		
		self.validate_form()
		

	def on_update(self):
		self.validate_form()
		frappe.clear_document_cache("POS Config",self.name)
		cache = frappe.cache()
		cache.delete_keys("system_settings:*")
  
		get_default_account_from_pos_config.cache_clear()  


	def validate_form(self):
		pass
