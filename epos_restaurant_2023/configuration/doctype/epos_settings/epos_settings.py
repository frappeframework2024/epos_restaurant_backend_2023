# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt
from frappe.model import no_value_fields
import frappe
from frappe.model.document import Document
from py_linq import Enumerable
from epos_restaurant_2023.selling.doctype.sale.general_ledger_entry import submit_sale_to_general_ledger_entry

class ePOSSettings(Document):
	def validate(self):
		if self.specific_pos_profile:
			self.specific_business_branch = self.specific_pos_profile

	def on_update(self):
		frappe.clear_document_cache('ePOS Settings', None)
		for df in self.meta.get("fields"):
			if df.fieldtype not in no_value_fields and self.has_value_changed(df.fieldname):
				frappe.db.set_default(df.fieldname, self.get(df.fieldname))
	
	@frappe.whitelist()
	def get_site_id(self):
		import hashlib
		site_name = frappe.local.site
		site_name =  hashlib.sha256(site_name.encode()).hexdigest()
		return site_name
	
	@frappe.whitelist()
	def generate_sale_general_ledger(self):
		frappe.publish_realtime("generate_sales_general_ledger", {"message": "Start Generating General Ledger"},user=frappe.session.user)
		sales = frappe.db.sql("select name from `tabSale` where name not in (SELECT voucher_number FROM `tabGeneral Ledger` WHERE voucher_type='Sale' AND is_cancelled=0 GROUP BY voucher_number)",as_dict=1)
		for a in sales:
			doc = frappe.get_doc("Sale",a["name"])
			submit_sale_to_general_ledger_entry(doc)
		frappe.publish_realtime("generate_sales_general_ledger", {"message": "General Ledger Generated"},user=frappe.session.user)

@frappe.whitelist(allow_guest=True)
def main_currency():
	setting = frappe.get_doc('ePOS Settings')
	main_currency = frappe.get_doc("Currency",setting.currency)
	return main_currency