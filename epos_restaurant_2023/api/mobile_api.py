import os
import uuid
from html2image import Html2Image
import numpy as np
import base64
from PIL import Image
from epos_restaurant_2023.api.product import get_product_by_menu
from epos_restaurant_2023.api.api import get_system_settings
from epos_restaurant_2023.api.printing import (
    get_print_context, 
    print_bill,
    print_kitchen_order,
    print_waiting_slip,
    print_voucher_invoice,
    print_from_print_format
    )
import frappe
from escpos.printer import Network

@frappe.whitelist(allow_guest=True)
def on_check_url():  
    return True

## use POST method to get system config data
@frappe.whitelist(allow_guest=True) 
def on_get_pos_configure(pos_profile="", device_name=''):  
    return get_system_settings(pos_profile,device_name) 

@frappe.whitelist(allow_guest=True,methods='POST') 
def get_menu_product(root_menu=""):
    if root_menu == "":
        return []
    menus  = get_menu(root_menu,root_menu)
    
    return menus
    #return get_product_by_menu(root_menu,mobile=1)

### get menu tree
@frappe.whitelist() 
def get_menu(root_menu, parent, is_child = 0):
    menus = []
    type_index = 1
    if is_child == 1:
        menus.append({"name_en":"Back","name_kh":"Back", "text_color":"#ffffff","background_color":"#858585","root_menu":root_menu, "type":"back","parent":parent})
        type_index = 2

    sql = """select 
            name,
            '{0}' as root_menu,
            pos_menu_name_en as name_en,
            pos_menu_name_kh as name_kh,
            parent_pos_menu as parent,
            photo,
            text_color,
            background_color,
            shortcut_menu,
            price_rule,
            photo,
            'menu' as type,
            {1} as type_index,
            cast(0 as int) as have_product,
            sort_order
        from `tabPOS Menu` 
        where 
            parent_pos_menu='{2}' and
            disabled = 0 
        order by sort_order, name
        """.format(root_menu,type_index, parent)
    
    parent_menus = frappe.db.sql(sql,as_dict=1)
    for p in parent_menus: 
        menus.append(p)

        sql_product = """select cast(count(name) as int) as total_products from `tabTemp Product Menu` where pos_menu='{}'""".format(p['name'])
        products = frappe.db.sql(sql_product, as_dict=1) 
        if products[0]["total_products"] > 0:
            p['have_product'] = 1
            
        children = get_menu(root_menu, p["name"], is_child=1)
        if len(children)>0:
            for c in children:                
                menus.append(c)

    return menus

@frappe.whitelist(allow_guest=True,methods='POST') 
def get_base64_image(image_name):
    if not image_name:
        return ""

    if not frappe.db.exists("File", {"file_url": image_name}):
        return ""

    _file = frappe.get_doc("File", {"file_url": image_name}) 
    image = Image.open(_file.get_full_path())
    image_path = '{}/resize_{}'.format(frappe.get_site_path(),_file.file_name)    

    base_width= 110
    wpercent = (base_width / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    image = image.resize((base_width, hsize), Image.Resampling.LANCZOS)    
    image.save(image_path,optimize=True, quality=95)
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        encoded_data = base64.b64encode(image_data).decode("utf-8") 
    try:
        if os.path.isfile(image_path):
            os.remove(image_path)
    except OSError as e:
        pass
    return encoded_data


### get product by menu
@frappe.whitelist(allow_guest=True,methods='POST') 
def get_product_list(root_menu="", pos_menu = ""):
    if root_menu == "" or pos_menu == "":
        return [] 
    else:
        sql = "select count(name) as total_menus from `tabPOS Menu` where parent_pos_menu = '{}'".format(root_menu)
        menus = frappe.db.sql(sql,as_dict=1)
        if menus[0]["total_menus"] <= 0:
            return []
        return get_product(root_menu,pos_menu)

### get product 
@frappe.whitelist() 
def get_product(root_menu, pos_menu):
    sql = """select 
                name as menu_product_name,
                product_code as name,
                product_name_en as name_en,
                product_name_kh as name_kh,
                '{1}' as root_menu,
                '{0}' as parent,
                price,
                unit,
                allow_discount,
                allow_change_price,
                allow_free,
                is_open_product,
                is_inventory_product,
                is_require_employee,
                is_timer_product,
                is_open_price,
                prices,
                printers,
                modifiers,
                photo,
                'product' as type,
                3 as type_index,
                append_quantity,
                is_combo_menu,
                use_combo_group,
                combo_menu_data,
                combo_group_data,
                tax_rule,
                sort_order,
                tax_rule_data,
                revenue_group,
                sort_order,
                business_branch_configure_data,
                rate_include_tax
            from  `tabTemp Product Menu` 
            where 
                pos_menu='{0}' 
            order by sort_order
            """.format(pos_menu,root_menu)
    
    data = frappe.db.sql(sql,as_dict=1)

    return data

@frappe.whitelist(allow_guest=True) 
def get_pos_users(secret_key = False):  
    sql = """select 
                u.`name`,
                e.employee_code as code, 
                e.employee_name as full_name,
                e.date_of_birth,
                e.gender,
                e.email_address,
                e.phone_number_1,
                e.phone_number_2,
                e.photo,
                e.username,
                e.pos_pin_code,
                e.role_profile,
                e.module_profile,
                e.pos_permission ,
                null as permission,
                coalesce(u.api_key,'') as api_key,
                '' as api_secret
            from tabEmployee e
            inner join tabUser u on e.user_id = u.`name`"""
    
    users = frappe.db.sql(sql, as_dict=1)
    if secret_key:
        for u in users: 
            if u.api_key:
                key = frappe.get_doc("User", u.name).get_password("api_secret")
                u.api_secret = key
            if u.pos_permission:
                p = frappe.get_doc('POS User Permission',u.pos_permission)
                discount_codes = []
                for d in p.discount_codes:
                    discount_codes.append({
                        "discount_type":d.discount_type,
                        "discount_code":d.discount_code,
                        "discount_value":d.discount_value
                    })

                u.permission = { 
                    "make_order": p.make_order,
                    "delete_bill": p.delete_bill,
                    "edit_closed_receipt": p.edit_closed_receipt,
                    "change_tax_setting": p.change_tax_setting,
                    "cancel_print_bill": p.cancel_print_bill ,
                    "discount_sale": p.discount_sale ,
                    "cancel_discount_sale": p.cancel_discount_sale ,
                    "add_voucher_top_up": p.add_voucher_top_up ,
                    "delete_voucher_top_up": p.delete_voucher_top_up ,
                    "free_item": p.free_item ,
                    "change_item_price": p.change_item_price ,
                    "delete_item": p.delete_item ,
                    "discount_item": p.discount_item ,
                    "cancel_discount_item": p.cancel_discount_item ,
                    "reset_custom_bill_number_counter": p.reset_custom_bill_number_counter,
                    "change_item_time_in": p.change_item_time_in ,
                    "change_item_time_out": p.change_item_time_out ,
                    "start_working_day": p.start_working_day ,
                    "close_working_day": p.close_working_day ,
                    "start_cashier_shift": p.start_cashier_shift ,
                    "close_cashier_shift": p.close_cashier_shift ,
                    "cash_in_check_out": p.cash_in_check_out ,
                    "open_cashdrawer": p.open_cashdrawer ,
                    "park_item": p.park_item ,
                    "discount_codes":discount_codes
                } 

    return users



## MOBILE SERVER PRINTING GENERATE BASE_64 IMAGE
### print invoice or receipt
@frappe.whitelist(allow_guest=True)
def get_bill_image(station, name,template, reprint=0):
   return print_bill(station=station,name=name,template=template,reprint=reprint)

### print waiting slip
@frappe.whitelist(allow_guest=True)
def get_waiting_slip_image(station, name):
   return print_waiting_slip(station=station,name=name)

### print voucher invoice 
@frappe.whitelist(allow_guest=True)
def get_voucher_invoice_image(station, name):
    return print_voucher_invoice(station=station,name=name)

### print kitchen order
@frappe.whitelist(allow_guest=True,methods="POST")
def get_kot_image(station, sale, products,printer): 
   
   return print_kitchen_order(station=station, sale=sale, products=products,printer=printer)

### print report from print format 
@frappe.whitelist(allow_guest=True,methods="POST")
def get_print_report_image(data): 
    return print_from_print_format(data)
 





    

 