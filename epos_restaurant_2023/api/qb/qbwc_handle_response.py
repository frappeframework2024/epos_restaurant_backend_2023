import frappe

import xml.etree.ElementTree as ET
from epos_restaurant_2023.api.qb.rs_handle.journal_entry import handle_journal_entry_add
from epos_restaurant_2023.api.qb.rs_handle.chart_of_account import handle_account_query
from epos_restaurant_2023.api.qb.rs_handle.payment_type import handle_payment_method_query 
from epos_restaurant_2023.api.qb.rs_handle.company import handle_company_query 
from epos_restaurant_2023.api.qb.rs_handle.customer import handle_customer_query 
from epos_restaurant_2023.api.qb.rs_handle.product import handle_item_query 
from epos_restaurant_2023.api.qb.rs_handle.invoice import handle_invoice_query 
from epos_restaurant_2023.api.qb.rs_handle.receive_payment import handle_receive_payment_query 
from epos_restaurant_2023.api.api import handle_journal_entry_classes_query

def handle_qb_response(company_name, xml_string):
    root = ET.fromstring(xml_string)
    if xml_string:
        for res in root.findall(".//QBXMLMsgsRs/*"):
            tag = res.tag  
            if tag == "JournalEntryAddRs":
                handle_journal_entry_add(res)

            elif tag == "InvoiceAddRs":
                handle_invoice_query(res=res)
                
            elif tag == "ReceivePaymentAddRs":
                handle_receive_payment_query(res=res)
                
            elif tag == "AccountQueryRs":
                handle_account_query(res=res, company_name = company_name)
                
            elif tag == "PaymentMethodQueryRs":
                handle_payment_method_query(res=res, company_name = company_name)                
                
            elif tag == "CustomerQueryRs":
                handle_customer_query(res=res, company_name = company_name)
                
            elif tag == "ItemQueryRs":
                handle_item_query(res=res, company_name = company_name)

            elif tag == "CompanyQueryRs":
                handle_company_query(res=res)
            
            elif tag == "ClassQueryRs":
                handle_journal_entry_classes_query(res=res, company_name = company_name)

            else:
                frappe.log_error(f"Unhandled QB Response: {tag}")

        frappe.db.commit()
    else:
        print(f"There're no data response")
    
def handle_qb_company_response(xml_string):
    if xml_string:
        root = ET.fromstring(xml_string)
        company_name = ""
        for res in root.findall(".//QBXMLMsgsRs/*"):
            tag = res.tag
            if tag == "CompanyQueryRs":
                company_name = handle_company_query(res) 
        return company_name
    else:
        print(f"There're no data response")
    
        return ""
    
