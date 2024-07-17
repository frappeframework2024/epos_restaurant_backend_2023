import frappe
from frappe import _
def submit_stock_to_general_ledger_entry_on_submit(self):
    
	from epos_restaurant_2023.api.account import submit_general_ledger_entry
	entry_type =frappe.db.get_value("Stock Entry Type", self.entry_type, "purpose")
	docs = []
	
	if entry_type == 'Stock In':
		doc={
                  "doctype":"General Ledger",
                  "posting_date":self.posting_date,
                  "account":self.default_inventory_account,
                  "debit_amount":self.total_amount,
                  "againt":frappe.db.get_value("Business Branch", self.business_branch, "stock_adjustment_account"),
                  "againt_voucher_type":"Sale",
                  "againt_voucher_number": self.name,
                  "voucher_type":"Stock Entry",
                  "voucher_number":self.name,
                  "business_branch": self.business_branch,
            }
		docs.append(doc)
	


	submit_general_ledger_entry(docs=docs)