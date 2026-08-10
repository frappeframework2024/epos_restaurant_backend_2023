import frappe
from epos_restaurant_2023.api.pos_reservation import pos_reservation_check_in
@frappe.whitelist(methods=["POST"])
def check_in(business_branch,pos_profile,device_name,reservation_id):
    return pos_reservation_check_in(business_branch,pos_profile,device_name,reservation_id)
