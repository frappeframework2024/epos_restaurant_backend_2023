import frappe

def submit_payment_to_general_ledger_entry_on_submit(self):
    from epos_restaurant_2023.api.account import submit_general_ledger_entry
    docs = []
    # payment acocunt

    doc = {
        "doctype":"General Ledger",
        "posting_date":self.posting_date,
        "account":self.account_paid_to,
        "debit_amount":self.payment_amount,
        "againt":self.customer + " - " + self.customer_name,
        "voucher_type":"Sale Payment",
        "voucher_number":self.name,
        "business_branch": self.business_branch,
        

    }
    doc["remark"] = "Amount {} received from {}".format(frappe.format(self.payment_amount,{"fieldtype":"Currency"}), doc["againt"])


    docs.append(doc)
        
    #Recievable account
    doc = {
        "doctype":"General Ledger",
        "posting_date":self.posting_date,
        "account":self.account_paid_from,
        "credit_amount":self.payment_amount,
        "party_type":"Customer",
        "party":self.customer + " - " + self.customer_name,
        "againt":self.account_paid_to,
        "against_voucher_type":"Sale",
        "againt_voucher_number":self.sale,
        "voucher_type":"Sale Payment",
        "voucher_number":self.name,
        "business_branch": self.business_branch,

    }
    doc["remark"] = "Amount {} received from {}".format(frappe.format(self.payment_amount,{"fieldtype":"Currency"}), doc["againt"])
    docs.append(doc)

    submit_general_ledger_entry(docs=docs)

    