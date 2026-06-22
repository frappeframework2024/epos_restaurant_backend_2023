import frappe
from epos_restaurant_2023.api.api import get_system_settings
from epos_restaurant_2023.api.product import get_product_by_menu_1_level
from frappe.utils.caching import redis_cache



@frappe.whitelist(methods=["POSTS"],allow_guest=True)
@redis_cache(ttl=86400)  
def get_system_settings(pos_profile="", device_name=''):
    return get_system_settings(pos_profile, device_name)


@frappe.whitelist(methods=["POSTS"],allow_guest=True)
@redis_cache(ttl=86400)  
def get_product_menu(**param):
    return get_product_by_menu_1_level(**param)


