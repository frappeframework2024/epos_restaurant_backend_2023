import frappe
from epos_restaurant_2023.api.qb.qbwc_helper import pretty_xml

## handle response company
def handle_company_query(res):    
      # 🔹 Find CompanyRet node
    company_ret = res.find(".//CompanyRet")
    if not company_ret:
        frappe.log_error("No CompanyRet found in response", "QBWC")
        return

    # 🔹 Extract fields
    company_name = company_ret.findtext("CompanyName")
    
    return company_name

