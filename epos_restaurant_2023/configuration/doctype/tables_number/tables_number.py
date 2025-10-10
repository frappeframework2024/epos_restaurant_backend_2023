# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TablesNumber(Document):
	def validate(self):
		pass
		# if not frappe.db.exists('ePOS Table Position', {'tbl_number': self.tbl_number, 'table_group': self.tbl_group}):
   		# 	frappe.throw("Table number {} is already exist in group {}".format(self.tbl_number, self.tbl_group))
	def on_update(self):
		frappe.clear_document_cache("Tables Number",self.name)

@frappe.whitelist()
def get_table_number_list(txt,table_group='Rooms'):
	data = frappe.db.get_list("Tables Number",filters=[[
    'tbl_number', 'like', "%"+ txt +"%"
	]],
		fields=['name','tbl_number', 'tbl_group']
	)
	return data