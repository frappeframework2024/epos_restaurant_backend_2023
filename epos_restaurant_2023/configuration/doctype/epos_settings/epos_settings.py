# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt
from frappe.model import no_value_fields
import frappe
from frappe.model.document import Document
from py_linq import Enumerable
from epos_restaurant_2023.selling.doctype.sale.general_ledger_entry import submit_sale_to_general_ledger_entry
from epos_restaurant_2023.api.account import cancel_general_ledger_entery

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
	def generate_sale_general_ledger(self):
		if not self.business_branch:
			frappe.throw("Please Selecte Business Branch")

		frappe.publish_realtime("generate_sales_general_ledger", {"message": "Start Generating General Ledger"},user=frappe.session.user)

		frappe.db.sql("""UPDATE `tabPOS Sale Payment` a 
						inner JOIN `tabPayment Type Account` b ON b.parent = a.payment_type
						SET a.default_account = if(coalesce(a.default_account,'')='',b.account,a.default_account)
						WHERE b.business_branch = '{0}'""".format(self.business_branch))
		
		frappe.db.sql("""UPDATE `tabSale Product` a 
						inner JOIN `tabRevenue Group Default Account` b ON b.parent = a.revenue_group
						SET a.default_income_account = if(coalesce(a.default_income_account,'')='',b.default_income_account,a.default_income_account),
						a.default_discount_account = if(coalesce(a.default_discount_account,'')='',b.default_discount_account,a.default_discount_account)
						WHERE b.business_branch = '{0}'""".format(self.business_branch))
		
		frappe.db.sql("""UPDATE `tabSale` a
						INNER JOIN `tabBusiness Branch` b ON b.name = a.business_branch
						SET a.default_change_account = if(coalesce(a.default_change_account,'')='',b.default_change_account,a.default_change_account)
						WHERE business_branch = '{0}';""".format(self.business_branch))

		sales = frappe.db.sql("""select 
										name 
									from `tabSale` 
									where business_branch = '{0}' and 
									name not in (SELECT 
														voucher_number 
													FROM `tabGeneral Ledger` 
													WHERE voucher_type='Sale' 
													GROUP BY voucher_number)""".format(self.business_branch),as_dict=1)
		for a in sales:
			doc = frappe.get_doc("Sale",a["name"])
			submit_sale_to_general_ledger_entry(doc)

		cancelled_sales = frappe.db.sql("select name from `tabSale` where business_branch = '{0}' and docstatus = 2".format(self.business_branch),as_dict=1)
		for a in cancelled_sales:
			cancel_general_ledger_entery("Sale", a["name"])	
			
		frappe.publish_realtime("generate_sales_general_ledger", {"message": "General Ledger Generated"},user=frappe.session.user)

@frappe.whitelist(allow_guest=True)
def main_currency():
	setting = frappe.get_doc('ePOS Settings')
	main_currency = frappe.get_doc("Currency",setting.currency)
	return main_currency