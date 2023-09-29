# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
# from datetime import timedelta, date
from frappe.model.document import Document


class Membership(Document):
	def validate(self):
		if self.discount_type=="Percent":
			self.grand_total = self.price - ((self.price or 0) * (self.discount or 0)/100)
		else:
			self.grand_total = self.price - (self.price or 0) - (self.discount or 0)
		
		#update date balance
		self.balance = self.grand_total - self.total_paid
		

	def on_submit(self):

		# doc = frappe.get_doc('Customer')
		pass

