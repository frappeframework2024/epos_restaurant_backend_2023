# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
class PriceRule(Document):
	def on_update(self):
		"""set default price rule"""
		if self.is_default:
			frappe.db.set_value('Price Rule', {'is_default': 1, 'name': ['!=', self.name]}, 'is_default', 0)
			frappe.db.set_value('Price Rule', self.name, 'is_default', 1)

@frappe.whitelist()
def verify_is_default(name,is_default):
	"""check if is default"""
	if is_default == "1":
		existed = (frappe.db.get_list('Price Rule',filters={'is_default': 1,'name':['!=',name]},fields=['name'],as_list=0) or [])
		if len(existed) > 0:
			return 'Price Rule <b>{}</b> is already set as default. Do you want to overwrite?'.format(existed[0].name)
		else:
			return ""
	else:
		return ""