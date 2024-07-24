import frappe

def submit_stock_adjustment_general_ledger_entry_on_submit(self):
    from epos_restaurant_2023.api.account import submit_general_ledger_entry
    docs = []
    if self.difference_cost > 0:
        type_amount_expenses = "credit_amount"
        type_amount_assets = "debit_amount"
    else:
        type_amount_expenses = "debit_amount"
        type_amount_assets = "credit_amount"

    # Expenses account
    doc_expenses = {
        "doctype": "General Ledger",
        "posting_date": self.posting_date,
        "account": self.difference_account,
        type_amount_expenses: abs(self.difference_cost),
        "againt": self.default_inventory_account,
        "voucher_type": "Stock Adjustment",
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
        type_amount_assets: abs(self.difference_cost),
        "againt": self.difference_account,
        "voucher_type": "Stock Adjustment",
        "voucher_number": self.name,
        "business_branch": self.business_branch,
        "remark": "Accounting adjustment for Stock"
    }
    docs.append(doc_assets)

    submit_general_ledger_entry(docs=docs)

