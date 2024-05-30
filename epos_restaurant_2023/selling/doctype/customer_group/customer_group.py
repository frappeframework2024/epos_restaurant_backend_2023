# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CustomerGroup(Document):
	def validate(self):
		if not self.customer_group_kh:
			self.customer_group_kh = self.name
		if self.has_value_changed('allow_earn_point'):
			customers = frappe.db.get_all("Customer",filters={
        		'customer_group': self.name
    		},) 
			if len(customers) > 0:
				for c in customers:
					 frappe.db.set_value("Customer",c.name,'allow_earn_point',self.allow_earn_point)