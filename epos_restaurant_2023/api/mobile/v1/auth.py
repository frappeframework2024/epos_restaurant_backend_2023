import frappe
from epos_restaurant_2023.api.mobile.api import login_with_pin_code as _login_with_pin_code
from epos_restaurant_2023.api.api import remove_key
import base64
from frappe import _


@frappe.whitelist(methods=["POST"], allow_guest=True)
def login_with_pin_code(pin_code):
    return _login_with_pin_code(pin_code)


@frappe.whitelist(methods=["POST"])
def check_pos_permission(pin_code,permission_name= None, switch_authorize=False):
    if not pin_code:
        frappe.throw(_("Please enter pin code"))
    _pin_code_plantext = pin_code
    pin_code = (str( base64.b64encode(pin_code.encode("utf-8")).decode("utf-8")))
    


    sql = """select 
                name,
                user_id, 
                pos_permission ,
                username,
                employee_name,
                photo
            from `tabEmployee` 
            where  
                pos_pin_code = %(pos_pin_code)s  and 
                coalesce(pos_permission,'') !=''
            limit 1"""
    data = frappe.db.sql(sql,{"pos_pin_code":pin_code},as_dict=1)
    if not data:
        frappe.throw(_("Invalid pin code"))
    
    d = data[0]
    _pos_permission = frappe.get_cached_doc("POS User Permission", d.get("pos_permission"))     
    keys = ["name","owner", "creation", "modified", "modified_by", "docstatus", "idx","_user_tags","_comments","_assign","_liked_by","parent","parentfield","parenttype","doctype"]
    _pos_permission = remove_key(data= _pos_permission.as_dict(), keys=keys)   
    if permission_name:
        if _pos_permission[permission_name] == 0:
            frappe.throw(_("You are not allow to perform this action.")) 
        else:
            if switch_authorize:   
                current_user = frappe.session.user
                if current_user != d.get("user_id") :                           
                    return _login_with_pin_code(_pin_code_plantext)
        

    
    return {
        "not_switch_auth":1,
        "authorize_by": d.get("employee_name") ,
        "username":d.get("user_id"),
        "permission":_pos_permission,
        "full_name":d.get("employee_name"),
        "user_image":d.get("photo")
    }
