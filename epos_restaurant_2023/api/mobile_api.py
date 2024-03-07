from epos_restaurant_2023.api.product import get_product_by_menu
from epos_restaurant_2023.api.api import get_system_settings
from epos_restaurant_2023.api.printing import get_print_context, print_bill,print_kitchen_order,print_waiting_slip,print_voucher_invoice
import frappe

@frappe.whitelist(allow_guest=True)
def on_check_url():  
    return True

@frappe.whitelist(allow_guest=True) 
def on_get_pos_configure(pos_profile="", device_name=''):  
    return get_system_settings(pos_profile,device_name) 

@frappe.whitelist(allow_guest=True) 
def get_menu_product(root_menu=""):  
    return get_product_by_menu(root_menu)

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


## END MOBILE SERVER PRINTING GENERATE BASE_64 IMAGE


## WINDOW SERVER PRINTING GENERATE HTML
@frappe.whitelist(allow_guest=True)
def get_bill_template(name):
    doc = frappe.get_doc("Sale", name)
    template,css = frappe.db.get_value("POS Receipt Template","Receipt En",["template","style"])
    html= frappe.render_template(template, get_print_context(doc))
    return {"html":html,"css":css}

## END WINDOW SERVER PRINTING GENERATE HTML
    

 