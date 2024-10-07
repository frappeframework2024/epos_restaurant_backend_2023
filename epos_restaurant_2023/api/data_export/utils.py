import string 
import frappe
def cell_array():
    # generate excel column up to 500 column
    result = []
    n = 500
    
    for i in range(1, n + 1):
        col = ''
        while i > 0:
            i, remainder = divmod(i - 1, 26)
            col = string.ascii_uppercase[remainder] + col
        result.append(col)
    return result


def get_business_information(filters):
    business_branch = ""
    if filters.get("property",""):
        business_branch = filters.get("property")
    elif filters.get("business_branch",""):
        business_branch = filters.get("business_branch")
    if business_branch:
        doc = frappe.get_cached_doc("Business Branch", business_branch)
        return {
            "logo": doc.report_header_logo,
            "header": doc.report_header_en,
            "sub_header": doc.report_header_sub_line
        }
    
    return  None