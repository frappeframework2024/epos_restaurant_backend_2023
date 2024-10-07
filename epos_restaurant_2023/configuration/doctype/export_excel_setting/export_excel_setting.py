# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ExportExcelSetting(Document):
	def on_update(self):
		frappe.clear_document_cache('Export Excel Setting', None)
