import frappe
from frappe import _
from epos_restaurant_2023.api.account import submit_general_ledger_entry
def submit_sale_to_general_ledger_entry(self):
	
	docs = []
	# income account
	for acc in self.account_entries:
		doc = {
			"doctype":"General Ledger",
			"posting_date":self.posting_date,
			"account":acc.account,
			"debit_amount":acc.debit,
			"credit_amount":acc.credit,
			"againt":acc.party + " - " + acc.party_name,
			"voucher_type":"Journal Entry",
			"voucher_number":self.name,
			"business_branch": self.business_branch,
			"party_type":acc.party_type,
			"party":acc.party,
			"remark":acc.note
		}
	
		docs.append(doc)
  
	submit_general_ledger_entry(docs=docs)


 