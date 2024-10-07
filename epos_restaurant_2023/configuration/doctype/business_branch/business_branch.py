# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

 
from epos_restaurant_2023.api.cache_function import get_doctype_value_cache
import frappe
from frappe.model.document import Document

class BusinessBranch(Document):
	def on_update(self):
		frappe.clear_document_cache('Business Branch', self.name)
		get_doctype_value_cache.cache_clear()
		frappe.clear_document_cache("Business Branch", self.name)

	@frappe.whitelist()
	def update_to_transaction(self):
		data = {"property":self.name}
		frappe.db.sql("update `tabDaily Property Data` set property=%(property)s",data)
		frappe.db.sql("update `tabReservation` set property=%(property)s",data)
		frappe.db.sql("update `tabReservation Stay` set property=%(property)s",data)
		frappe.db.sql("update `tabReservation Stay Room` set property=%(property)s",data)
		frappe.db.sql("update `tabRoom Occupy` set property=%(property)s",data)
		frappe.db.sql("update `tabTemp Room Occupy` set property=%(property)s",data)
		
		frappe.db.sql("update `tabWorking Day` set business_branch=%(property)s",data)
		frappe.db.sql("update `tabCashier Shift` set business_branch=%(property)s",data)
		frappe.db.commit()

		frappe.msgprint("Update complete")