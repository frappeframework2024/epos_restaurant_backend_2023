import frappe

def submit_purchase_payment_to_general_ledger_entry_on_submit(self):
    from epos_restaurant_2023.api.account import submit_general_ledger_entry
    docs = []
    # payment acocunt deduct from asset account 
    vendor,vendor_name = frappe.db.get_value("Purchase Order",self.purchase_order,["vendor","vendor_name"])
    doc = {
        "doctype":"General Ledger",
        "posting_date":self.posting_date,
        "account":self.account_paid_to,
        "debit_amount":self.payment_amount,
        "againt":"{}-{}".format(vendor,vendor_name),
        "voucher_type":"Purchase Order Payment",
        "voucher_number":self.name,
        "business_branch": self.business_branch,
    }
    doc["remark"] = "Amount {} Pay to {}".format(frappe.format(self.payment_amount,{"fieldtype":"Currency"}), doc["againt"])
    doc["remark"] =  doc["remark"] + "\nAmount {} againt Purchase Order {}".format(frappe.format(self.payment_amount,{"fieldtype":"Currency"}), self.purchase_order)
    docs.append(doc)
    
    
    # deduct payable account
    doc = {
        "doctype":"General Ledger",
        "posting_date":self.posting_date,
        "account":self.account_paid_from,
        "credit_amount":self.payment_amount,
        "party_type":"Vendor",
        "party":"{}-{}".format(vendor,vendor_name),
        "againt":self.account_paid_to,
        "against_voucher_type":"Purchase Order",
        "againt_voucher_number":self.purchase_order,
        "voucher_type":"Purchase Order Payment",
        "voucher_number":self.name,
        "business_branch": self.business_branch,
    }
    doc["remark"] = "Amount {} Pay to {}".format(frappe.format(self.payment_amount,{"fieldtype":"Currency"}), doc["againt"])
    doc["remark"] = doc["remark"] + "\nAmount {} againt Purchase Order {}".format(frappe.format(self.payment_amount,{"fieldtype":"Currency"}), self.purchase_order)
    docs.append(doc)
    
    submit_general_ledger_entry(docs=docs)
    
    