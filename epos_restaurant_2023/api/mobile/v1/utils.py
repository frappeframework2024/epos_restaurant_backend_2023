import frappe
from epos_restaurant_2023.api.api import get_system_settings as get_settings , check_pos_profile as _check_pos_profile
from epos_restaurant_2023.api.product import get_product_by_menu_1_level
from frappe.utils.caching import redis_cache


import base64
from frappe import _

@frappe.whitelist()
def get_meta(doctype):
    data =  frappe.get_meta(doctype)
    return data
 
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
    get_predefine_note.clear_cache()

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
    get_predefine_note.clear_cache()
    return "Success"



@frappe.whitelist(methods=["GET","POST"],allow_guest=True)
def check_pos_profile(pos_profile_name, device_name, is_used_validate=True):
    return _check_pos_profile(pos_profile_name = pos_profile_name,device_name = device_name,is_used_validate= is_used_validate)



@frappe.whitelist(methods=["POST","GET"])
def get_pos_receipt_list(pos_profile="Main POS Profile"):
    cache = frappe.cache()
    key = f"system_settings:get_pos_receipt_list:{pos_profile}"
    if not frappe.conf.developer_mode:
        cached = cache.get_value(key)
        if cached:
            return cached


    pos_config =  frappe.get_cached_value("POS Profile",pos_profile,"pos_config")
    sql = "select a.print_template,b.printer_name as printer, a.copies from `tabPOS Config Print Setting` a join `tabPrinter` b on a.printer = b.name where a.parent = %(pos_config)s and a.print_type='Sale'"
    data = frappe.db.sql(sql,{"pos_config":pos_config},as_dict=1)

    cache.set_value(key, data, expires_in_sec=86400)
    return data

@frappe.whitelist(methods=["POST"])
def print_test(print_server_url,printer_name):
    from epos_restaurant_2023.api.print_server import process_print
    process_print(data = {
        "printer_name":printer_name,
        "html":f"<center><h1> Print Test <br/> Pinter {printer_name}</h1></center>"
    },
    print_server_url=print_server_url
    )


@frappe.whitelist(allow_guest=True)
def check_app_update(app_name,current_version):
    current_version = int(current_version)
    release = frappe.get_all(
        "App Release",
        filters={
            "app_name": app_name,
        },
        fields=[
            "version_name",
            "version_number",
            "apk_file",
            "release_note",
            "is_force_update"
        ],
        order_by="version_number desc",
        limit=1
    )

    if not release:
        return {"update_available": False}

    r = release[0]

    return {
        "update_available": r.version_number > current_version,
        "version_name": r.version_name,
        "version_number": r.version_number,
        "apk_url": frappe.utils.get_url(r.apk_file),
        "release_note": r.release_note,
        "force_update": r.is_force_update
    }
    

def get_working_day_info(business_branch):
    cache = frappe.cache()
    key = f"mobile.v1.utils.get_working_day_{business_branch}"

    cached = cache.get_value(key)
    if cached:
        return cached
    sql = "select creation,  posting_date, name,is_closed from `tabWorking Day` where business_branch = %(business_branch)s order by creation desc limit 1"
    data = frappe.db.sql(sql,{"business_branch":business_branch},as_dict=1)
    if data:
        data = data[0]
    else:
        data = {
            "posting_date":frappe.utils.today(),
            "name":"",
            "is_closed": None,

        }
        


    
    cache.set_value(key, data, expires_in_sec=86400)
    return data


def get_cashier_shift_info(pos_profile):
    cache = frappe.cache()
    key = f"mobile.v1.utils.get_cashier_shift_info_{pos_profile}"

    cached = cache.get_value(key)
    if cached:
        return cached
    sql = "select creation,  posting_date, name,is_closed,owner from `tabCashier Shift` where pos_profile = %(pos_profile)s order by creation desc limit 1"
    data = frappe.db.sql(sql,{"pos_profile":pos_profile},as_dict=1)
    if data:
        data = data[0]
    else:
        data = {
            "posting_date":frappe.utils.today(),
            "name":"",
            "is_closed": None,
            "owner":"",
            "creation":None

        }
        


    
    cache.set_value(key, data, expires_in_sec=86400)
    return data
