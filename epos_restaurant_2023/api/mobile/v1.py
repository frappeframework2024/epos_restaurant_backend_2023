import frappe
from epos_restaurant_2023.api.api import get_system_settings
from epos_restaurant_2023.api.product import get_product_by_menu_1_level
from frappe.utils.caching import redis_cache
import base64
from frappe import _


@frappe.whitelist(methods=["POSTS"],allow_guest=True)
@redis_cache(ttl=86400)  
def get_system_settings(pos_profile="", device_name=''):
    return get_system_settings(pos_profile, device_name)


@frappe.whitelist(methods=["GET","POST"])
@redis_cache(ttl=86400)  
def get_predefine_note(note_category=""):
    sql = "select distinct note from `tabCashier Notes` where parent=%(parent)s"
    data = frappe.db.sql(sql, {"parent":note_category},as_dict=1)
    if data:
        return [x.get("note") for x in data]
    return []

@frappe.whitelist(methods=["POST"],allow_guest=True)
@redis_cache(ttl=86400)  
def get_product_menu(**param):
    return get_product_by_menu_1_level(**param)

@frappe.whitelist(methods=["POST"])
def check_pos_permission(pin_code, permission_name):
    if not pin_code:
        frappe.throw(_("Please enter pin code"))
    pin_code = (str( base64.b64encode(pin_code.encode("utf-8")).decode("utf-8")))

    sql = """select 
                name,
                user_id, 
                pos_permission ,
                username,
                employee_name
            from `tabEmployee` 
            where  
                pos_pin_code = %(pos_pin_code)s  and 
                coalesce(pos_permission,'') !=''
            limit 1"""
    data = frappe.db.sql(sql,{"pos_pin_code":pin_code},as_dict=1)
    if not data:
        frappe.throw(_("Invalid pin code"))
    
    if frappe.get_cached_value("POS User Permission",data[0].get("pos_permission"),permission_name) == 0:
        frappe.throw(_("You are not allow to perform this action."))
    
    
    return {
        "authorize_by": data[0].get("employee_name") 
    }






