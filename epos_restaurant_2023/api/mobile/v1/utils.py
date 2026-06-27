import frappe
from epos_restaurant_2023.api.api import get_system_settings as get_settings , check_pos_profile as _check_pos_profile
from epos_restaurant_2023.api.product import get_product_by_menu_1_level
from frappe.utils.caching import redis_cache
import base64
from frappe import _

 
@frappe.whitelist(methods=["POST"],allow_guest=True) 
def get_system_settings(pos_profile="", device_name=''):
    cache = frappe.cache()
    key = f"system_settings:{pos_profile}:{device_name}"

    cached = cache.get_value(key)
    if cached:
        return cached
    
    result = get_settings(pos_profile, device_name)
    cache.set_value(key, result, expires_in_sec=86400)
    return result
    

@frappe.whitelist(methods=["GET","POST"])
@redis_cache(ttl=86400)  
def get_predefine_note(note_category="",product_code = ''):
    sql = """
        select 
            distinct note 
        from `tabCashier Notes` 
        where 
            (
                parent=%(parent)s and 
                (%(product_code)s = '' or product_code = %(product_code)s) 
            ) or 
            (  
                parent=%(parent)s and 
                coalesce(product_code,'') = ''
            )
        """
    data = frappe.db.sql(sql, {"parent":note_category,"product_code":product_code or ""},as_dict=1)
    if data:
        return [x.get("note") for x in data]
    return [] 

@frappe.whitelist(methods=["POST"])
def save_note(note_category="",product_code = '',note=""):
    sql="select name from `tabCashier Notes` where parent =%(note_category)s and (%(product_code)s = '' or product_code = %(product_code)s) and note=%(note)s"
    exist = frappe.db.sql(sql, {"note":note, "note_category":note_category,"product_code":product_code},as_dict =1)
    if len(exist)==0:
        doc = frappe.get_doc("Category Note", note_category)
        doc.append("notes", {
            "product_code": product_code,
            "note": note,
        }).save(ignore_permissions=True)
    
    frappe.db.commit()

    return "Success"

@frappe.whitelist(methods=["POST"])
def delete_notes(note_category="",product_code = '',notes=None):
    if not notes:
        frappe.throw(_("No note to delete"))

    sql="""
        delete from  `tabCashier Notes` 
        where 
            (
                parent =%(note_category)s and 
                (%(product_code)s = '' or product_code = %(product_code)s) and 
                note in %(notes)s
                
            ) or (
                parent =%(note_category)s and  
                note in %(notes)s and 
                coalesce(product_code,'') = ''
            )
        """
    exist = frappe.db.sql(sql, { "note_category":note_category,"product_code":product_code,"notes":notes})
     
    frappe.db.commit()

    return "Success"



@frappe.whitelist(methods=["GET","POST"],allow_guest=True)
def check_pos_profile(pos_profile_name, device_name, is_used_validate=True):
    return _check_pos_profile(pos_profile_name = pos_profile_name,device_name = device_name,is_used_validate= is_used_validate)

     