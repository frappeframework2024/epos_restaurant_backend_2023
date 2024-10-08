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

def get_status_color_by_alias(alias):
    if cached_value := frappe.cache.get_value("get_status_color_by_alias_" + str(alias)):
        return cached_value
    
    sql="select color from `tabReservation Status` where alias='{}' limit 1".format(alias)
    data = frappe.db.sql(sql, as_dict=1)
    color = None
    if data:
        color =  data[0].get("color").replace("#","")
    
   

    frappe.cache.set_value("get_status_color_by_alias_" + str(alias), color)
    return color



def hex_to_argb(hex_color):
    # Remove the '#' if present
    hex_color = hex_color.lstrip('#')

    # Extract RGB components
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)

    # Define the Alpha (A) channel (255 for full opacity)
    alpha = 255

    # Return the ARGB as a tuple
    return (alpha, red, green, blue)