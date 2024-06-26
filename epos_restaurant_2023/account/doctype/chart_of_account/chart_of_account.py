# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet


class ChartOfAccount(NestedSet):
	def validate(self):
		if self.is_new():
			self.name = self.account_code + " - " + self.account_name
