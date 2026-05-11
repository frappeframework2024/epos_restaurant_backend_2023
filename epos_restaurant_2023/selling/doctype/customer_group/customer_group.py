# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import time

class CustomerGroup(Document):
	def validate(self):
		if not self.customer_group_kh:
			self.customer_group_kh = self.name
		if self.has_value_changed('allow_earn_point'):
			queue_update_allow_earn_point(self.name, self.allow_earn_point)
		
def queue_update_allow_earn_point(group_name, allow_earn_point):
	frappe.publish_realtime("update_allow_earn_point", {"message": "Updating allow earn point", "color": "green"},user=frappe.session.user)
	frappe.enqueue(update_allow_earn_point, group_name=group_name, allow_earn_point=allow_earn_point, timeout=3000)

def update_allow_earn_point(group_name, allow_earn_point):
	customers = frappe.db.get_all("Customer",filters={'customer_group': group_name}) 
	if len(customers) > 0:
		for c in customers:
			frappe.db.set_value("Customer",c.name,'allow_earn_point',allow_earn_point)
	time.sleep(3) 
	frappe.publish_realtime("update_allow_earn_point", {"message": "Finished updating allow earn point", "color": "blue"},user=frappe.session.user)