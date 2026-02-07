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
		get_default_account_from_pos_config.cache_clear()  


	def validate_form(self):
		if self.enable_aba_integration and (
			(self.merchant_id or "") == ""  
			or (self.api_key or "") == "" 
			or (self.aba_qr_api_endpoint or "") ==""
			or (self.check_transaction_endpoint or "") == ""
			or (self.payment_gateway_callback or "") == "" ):
			frappe.throw(_("Fields of integration not allow blank"))
