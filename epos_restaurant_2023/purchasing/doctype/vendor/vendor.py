# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Vendor(Document):
    def validate(self):
        self.vendor_code_name = "{} - {}".format(self.name,self.vendor_name)
		

@frappe.whitelist()
def update_store_payment_balance(vendor=""):
    vendors = []
    if vendor:
        vendors = [vendor]
    else:
        account_codes =frappe.db.sql( "select default_vendor from `tabPOS Profile` where coalesce(default_vendor,'')!= '' and coalesce(default_credit_account,'')!='' and (%(vendor)s = '' or default_vendor=%(vendor)s)",{"vendor":vendor},as_dict=1)
        vendors =   [d.get("default_vendor") for d in account_codes] or ["dumy"]
    
    sql = """
        UPDATE `tabVendor` v
        JOIN (
            SELECT 
                party,
                SUM(credit_amount - debit_amount) AS total
            FROM `tabGeneral Ledger` gl  
            INNER JOIN `tabChart Of Account` acc ON acc.name = gl.account
            WHERE
                COALESCE(gl.party, '') IN %(vendors)s AND 
                acc.account_type = 'Payable'
            GROUP BY gl.party
        ) gl ON v.name = gl.party
        SET v.store_payment_balance = gl.total;


    """
    frappe.db.sql(sql,{"vendors": vendors},as_dict=1)
    frappe.db.commit()
    return "Done"
