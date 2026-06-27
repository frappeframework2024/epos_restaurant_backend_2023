import frappe
from epos_restaurant_2023.api.mobile.api import login_with_pin_code as _login_with_pin_code
from epos_restaurant_2023.api.api import remove_key
import base64
from frappe import _


@frappe.whitelist(methods=["POST"], allow_guest=True)
def login_with_pin_code(pin_code):
    return _login_with_pin_code(pin_code)


@frappe.whitelist(methods=["POST"])
def check_pos_permission(pin_code):
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
    
    d = data[0]
    pos_permission = frappe.get_cached_doc("POS User Permission", d.get("pos_permission"))     
    keys = ["name","owner", "creation", "modified", "modified_by", "docstatus", "idx","_user_tags","_comments","_assign","_liked_by","parent","parentfield","parenttype","doctype"]
    pos_permission = remove_key(data= pos_permission.as_dict(), keys=keys)
    
        
    return {
        "authorize_by": d.get("employee_name") ,
        "username":d.get("user_id"),
        "permission":pos_permission
    }
