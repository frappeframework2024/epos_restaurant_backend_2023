from epos_restaurant_2023.api.product import (
    get_product_by_menu as _get_product_by_menu
) 
import frappe

@frappe.whitelist(methods="POST")
def get_product_by_menu(root_menu="",sort_order_by="product_name_en",sort_menu_order_by='name' ):

    return _get_product_by_menu(root_menu=root_menu,
                                mobile = 0,
                                sort_order_by=sort_order_by,
                                sort_menu_order_by=sort_menu_order_by )