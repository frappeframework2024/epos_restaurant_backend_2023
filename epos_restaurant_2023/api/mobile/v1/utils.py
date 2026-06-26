import frappe
from epos_restaurant_2023.api.api import get_system_settings as get_settings , check_pos_profile as _check_pos_profile
from epos_restaurant_2023.api.product import get_product_by_menu_1_level
from frappe.utils.caching import redis_cache
import base64
from frappe import _

 
@frappe.whitelist(methods=["POST"],allow_guest=True)
@redis_cache(ttl=86400)  
def get_system_settings(pos_profile="", device_name=''):
    return get_settings(pos_profile, device_name)
    

@frappe.whitelist(methods=["GET","POST"])
@redis_cache(ttl=86400)  
def get_predefine_note(note_category=""):
    sql = "select distinct note from `tabCashier Notes` where parent=%(parent)s"
    data = frappe.db.sql(sql, {"parent":note_category},as_dict=1)
    if data:
        return [x.get("note") for x in data]
    return [] 


@frappe.whitelist(methods=["GET","POST"],allow_guest=True)
def check_pos_profile(pos_profile_name, device_name, is_used_validate=True):
    return _check_pos_profile(pos_profile_name = pos_profile_name,device_name = device_name,is_used_validate= is_used_validate)

     