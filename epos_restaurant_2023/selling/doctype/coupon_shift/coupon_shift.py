# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CouponShift(Document):
	def validate(self):	

	

		full_name = frappe.utils.get_fullname(frappe.session.user)
 


		if not self.open_by :
			self.open_by = full_name