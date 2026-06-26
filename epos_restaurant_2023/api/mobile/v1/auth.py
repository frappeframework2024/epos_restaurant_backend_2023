import frappe
from epos_restaurant_2023.api.mobile.api import login_with_pin_code as _login_with_pin_code
import base64
from frappe import _


@frappe.whitelist(methods=["POST"], allow_guest=True)
def login_with_pin_code(pin_code):
    return _login_with_pin_code(pin_code)


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
