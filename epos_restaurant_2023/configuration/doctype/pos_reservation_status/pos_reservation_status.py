# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class POSReservationStatus(Document):
	def on_update(self):
		frappe.clear_document_cache("POS Reservation Status",self.name)
