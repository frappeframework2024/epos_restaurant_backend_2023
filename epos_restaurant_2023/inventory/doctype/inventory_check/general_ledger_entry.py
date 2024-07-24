import frappe

def submit_inventory_check_general_ledger_entry(self, on_cancel = False):
    from epos_restaurant_2023.api.account import submit_general_ledger_entry
    difference_cost = sum([d.total_difference_cost for d in self.items if d.total_difference_cost != 0 ])  

    docs = []
    if difference_cost > 0 and not on_cancel:
        type_amount_expenses = "credit_amount"
        type_amount_assets = "debit_amount"
    else:
        type_amount_expenses = "debit_amount"
        type_amount_assets = "credit_amount"

    # Expenses account
    doc_expenses = {
        "doctype": "General Ledger",
        "posting_date": self.posting_date,
        "account": self.default_adjustment_account,
        type_amount_expenses: abs(difference_cost),
        "againt": self.default_inventory_account,
        "voucher_type": "Inventory Check",
        "voucher_number": self.name,
        "business_branch": self.business_branch
    } 

    # Stock Assets
    doc_assets = {
        "doctype": "General Ledger",
        "posting_date": self.posting_date,
        "account": self.default_inventory_account,
        type_amount_assets: abs(difference_cost),
        "againt": self.default_adjustment_account,
        "voucher_type": "Inventory Check",
        "voucher_number": self.name,
        "business_branch": self.business_branch        
    }

    if on_cancel:
        _cancel_data = {
            "is_canceclled":1,
            "type":"Income", #not use in db
            "remark":"Accounting cancel inventory check"
            
        }
        doc_expenses.update(_cancel_data)
        doc_assets.update(_cancel_data)

    else:
        _data = {
              "remark": "Accounting inventory check"
        }

    docs.append(doc_expenses)    
    docs.append(doc_assets)

    submit_general_ledger_entry(docs=docs)



