import frappe

def submit_cash_transaction_expense_general_entry(self):
    from epos_restaurant_2023.api.account import submit_general_ledger_entry
 

    docs = []
 ##
    doc = {
        "doctype":"General Ledger",
        "posting_date":self.posting_date,
        "account":self.expense_to,
        "debit_amount":self.amount,
        "againt":self.created_by,
        "voucher_type":"Cash Transaction",
        "voucher_number":self.name,
        "business_branch": self.business_branch,       

    }
    doc["remark"] = "{} {}".format(self.transaction_status, frappe.format(self.amount,{"fieldtype":"Currency"}))
    docs.append(doc)


      ##   
    doc = {
        "doctype":"General Ledger",
        "posting_date":self.posting_date,
        "account":self.expense_from,
        "credit_amount":self.amount,
        "againt":self.created_by,
        "voucher_type":"Cash Transaction",
        "voucher_number":self.name,
        "business_branch": self.business_branch,

    }
    doc["remark"] = "{} {}".format(self.transaction_status, frappe.format(self.amount,{"fieldtype":"Currency"}))
    docs.append(doc)

    submit_general_ledger_entry(docs=docs)

    