# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
# from datetime import timedelta, date
from frappe.model.document import Document


class Membership(Document):
	def validate(self):
		if self.discount_type=="Percent":
			self.grand_total = (self.price or 0) - ((self.price or 0) * (self.discount or 0)/100)
		else:
			self.grand_total = (self.price or 0) - (self.price or 0) - (self.discount or 0)
		
		#update date balance
		self.balance = self.grand_total - (self.total_paid or 0)
		

	def on_submit(self):
		update_membership(self)
	
	def on_cancel(self):
		update_membership(self)


def update_membership(self):
	data = frappe.db.sql("select ifnull(sum(balance),0)  as total_balance from `tabMembership` where docstatus=1 and customer='{}' and balance>0".format(self.customer))
	frappe.db.set_value('Customer', self.customer,  {
		'balance': data[0][0]
	})

