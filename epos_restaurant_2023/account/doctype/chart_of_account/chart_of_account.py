# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet

class ChartOfAccount(NestedSet):
	def validate(self):
		prefix = frappe.db.get_value("Business Branch",self.business_branch,"chart_of_account_prefix")
		if self.is_new():
			if self.account_code:
				if prefix:
					self.name = prefix + " - " +self.account_code + " - " + self.account_name
				else:
					self.name = self.account_code + " - " + self.account_name
			else:
				if prefix:
					self.name = prefix + " - " + self.account_name
				else:
					self.name = self.account_name
		if self.parent_chart_of_account:
			self.root_tye = frappe.db.get_value("Chart Of Account",self.parent_chart_of_account,"root_type")