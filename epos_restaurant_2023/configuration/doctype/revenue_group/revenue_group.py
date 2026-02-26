# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from epos_restaurant_2023.api.cache_function import get_default_account_from_revenue_group
from frappe.model.document import Document

class RevenueGroup(Document):
	def on_update(self):
		get_default_account_from_revenue_group.cache_clear()
