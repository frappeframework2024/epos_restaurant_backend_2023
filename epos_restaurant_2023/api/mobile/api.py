
from epos_restaurant_2023.api.api import (
    get_current_shift_information
)
import frappe


@frappe.whitelist(methods="POST")
def get_current_shift_management(business_branch, pos_profile):
    return  get_current_shift_information(business_branch,pos_profile) 

