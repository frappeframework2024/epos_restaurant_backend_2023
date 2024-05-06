# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
class TaxInvoice(Document):
	def get_print_settings(self):
		if hasattr(self,"print_settings"):
			
			return self.print_settings.split(",")
		else:
			return []

	def after_delete(self):
		if self.document_type in ["Reservation Folio","Desk Folio"]:
			frappe.db.sql("update `tab{}` set is_generate_tax_invoice=0, tax_invoice_number = '' where name='{}'".format(self.document_type, self.document_name))
			frappe.db.commit()