import frappe
from frappe import _

def submit_sale_to_general_ledger_entry(self):
	from epos_restaurant_2023.api.account import submit_general_ledger_entry
	docs = []
	# income account
	for acc in set([d.account for d in self.account_entries]):
		if not acc:
				frappe.throw(_("Please enter income account"))
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":acc,
			"debit":sum([d.debit for d in self.account_entries if d.account==acc]),
			"againt":self.customer + " - " + self.customer_name,
			"voucher_type":"Journal Entry",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"type":"Income"#not use in db
		}
	
		docs.append(doc)
  
	submit_general_ledger_entry(docs=docs)


 