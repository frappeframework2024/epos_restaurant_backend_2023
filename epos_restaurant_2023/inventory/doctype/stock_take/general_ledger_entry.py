import frappe

def submit_stock_take_general_ledger_entry_on_submit(self):
    from epos_restaurant_2023.api.account import submit_general_ledger_entry
    docs = [] 
    # Expenses account
    if self.total_amount > 0:
        doc_expenses = {
            "doctype": "General Ledger",
            "posting_date": self.posting_date,
            "account": self.difference_account,
            "credit_amount": self.total_amount,
            "againt": self.default_inventory_account,
            "voucher_type": "Stock Take",
            "voucher_number": self.name,
            "business_branch": self.business_branch,
            "remark": "Accounting adjustment for Stock"
        }
        docs.append(doc_expenses)

        # Stock Assets
        doc_assets = {
            "doctype": "General Ledger",
            "posting_date": self.posting_date,
            "account": self.default_inventory_account,
            "debit_amount": self.total_amount,
            "againt": self.difference_account,
            "voucher_type": "Stock Take",
            "voucher_number": self.name,
            "business_branch": self.business_branch,
            "remark": "Accounting adjustment for Stock"
        }
        docs.append(doc_assets)

    submit_general_ledger_entry(docs=docs)

