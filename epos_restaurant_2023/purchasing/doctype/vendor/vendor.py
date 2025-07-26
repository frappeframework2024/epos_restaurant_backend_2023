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




@frappe.whitelist()
def get_vendor_credit_balance(vendor, date):
    update_account_type_to_gl_entery()
    sql="select sum(credit_amount - debit_amount) as total from `tabGeneral Ledger` where party = %(vendor)s and posting_date<%(date)s and account_type = 'Payable'"

    filter={"vendor":vendor,"date":date}
    data = frappe.db.sql(sql,filter,as_dict=1)
    return_data = {}
    if (data):
        return_data["opening_balance"] = data[0].get("total") or 0
    # current credit
    sql="select sum(credit_amount) as total_credit,sum(debit_amount) as total_debit from `tabGeneral Ledger` where   account_type = 'Payable' and party = %(vendor)s and posting_date=%(date)s"
    
    data = frappe.db.sql(sql,filter,as_dict=1)
    if (data):
        return_data["credit"] = data[0].get("total_credit") or 0
        return_data["debit"] = data[0].get("total_debit") or 0 
    
    return_data["balance"] = (return_data.get("opening_balance") +      return_data["credit"] ) -  return_data["debit"]
    return return_data 
    

def update_account_type_to_gl_entery():
    sql ="""
        update `tabGeneral Ledger` a
        join `tabChart Of Account` b on b.name = a.account
        set
            a.account_type = b.account_type
        where
            coalesce(a.account_type,'') = ''
    """
    frappe.db.sql(sql)
    frappe.db.commit()

