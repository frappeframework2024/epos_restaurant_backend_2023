# Copyright (c) 2026, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import json
import frappe

class QuickbooksSyncQueues(Document):
	def on_update(self):
		previous_doc = self.get_doc_before_save()
		if self.status == "Completed" and previous_doc.status != "Completed":
			if self.reference_gl_entries:
				gl_entries = json.loads(self.reference_gl_entries)
				sql = "update `tabGeneral Ledger` set qb_synced = 1 where name in ({0})".format(",".join(["'{}'".format(d["name"]) for d in gl_entries]))
				frappe.db.sql(sql)