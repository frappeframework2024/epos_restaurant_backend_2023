# Copyright (c) 2026, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PrintQueue(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		if self.document_name:
			self.name = make_autoname(f"KO.{self.document_name}.-.##")
