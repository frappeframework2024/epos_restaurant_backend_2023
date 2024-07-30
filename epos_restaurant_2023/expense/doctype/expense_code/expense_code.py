# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ExpenseCode(Document):
	pass

@frappe.whitelist(allow_guest=True)
def get_branches():
	branches = frappe.db.get_list('Business Branch',filters={'disabled': 0},fields=['name'],as_list=False)
	return branches