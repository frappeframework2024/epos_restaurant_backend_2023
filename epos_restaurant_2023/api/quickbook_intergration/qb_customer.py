import frappe
from frappe import _
from epos_restaurant_2023.api.quickbook_intergration.api import (post_api,get_api, get_list)


@frappe.whitelist() 
def get_customer_types():
    query = "SELECT * FROM CustomerType"
    return get_list(key="CustomerType", query=query)

