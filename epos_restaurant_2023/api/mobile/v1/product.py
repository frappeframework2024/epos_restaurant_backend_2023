import frappe
from epos_restaurant_2023.api.product import get_product_by_menu_1_level as _get_product_by_menu_1_level 

@frappe.whitelist(methods=["POST"],allow_guest=True)
def get_product_by_menu_1_level(**param):
    return _get_product_by_menu_1_level(**param)

