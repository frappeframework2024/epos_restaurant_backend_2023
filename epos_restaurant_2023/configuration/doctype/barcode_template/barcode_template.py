# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BarcodeTemplate(Document):
	def validate(self):
		if self.is_new():
			self.name = self.document_type + "-" + self.template_name
			if frappe.db.exists("Barcode Template", self.name):
				frappe.throw("Template name {} is already exist".format(self.template_name))

		if self.is_default ==1:
			frappe.db.sql("update `tabBarcode Template` set is_default=0 where document_type='{}'".format(self.document_type))
		 