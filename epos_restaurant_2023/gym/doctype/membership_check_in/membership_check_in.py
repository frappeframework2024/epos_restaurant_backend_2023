# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
import json
import frappe
from frappe.model.document import Document


class MembershipCheckIn(Document):
	def validate(self): 
		pass
 
	def on_submit(self):
		sql = """select count(`name`) as total_check_in from `tabMembership Check In Items` where membership = '{}' and docstatus = 1"""
		for m in self.membership_check_in_item:
			exec = frappe.db.sql(sql.format(m.membership), as_dict=1)
			if exec:
				m.check_in_number = (exec[0].total_check_in or 0) + 1
	