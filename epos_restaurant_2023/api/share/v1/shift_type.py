import frappe
from frappe import _
from frappe.utils import getdate
from frappe.rate_limiter import rate_limit
from epos_restaurant_2023.api.share.utils import api_rate_limit,api_error,api_response


@frappe.whitelist()
@api_rate_limit(limit=5, seconds=60*2)
def get():
    if  frappe.request.method != "GET":      
        return api_error(_("Method Not Allowed"),405) 
    
    shifts = frappe.get_list("Shift Type",fields=["name","sort"], filters={"show_in_pos":1}, order_by="sort asc")
    shifts = [
        {
            "id": shift.name,
            "sort": shift.sort
        }
        for shift in shifts
    ]
    return api_response(shifts)

