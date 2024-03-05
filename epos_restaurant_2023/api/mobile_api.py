from epos_restaurant_2023.api.product import get_product_by_menu
from epos_restaurant_2023.api.api import get_system_settings
import frappe
from PIL import Image, ImageChops
from html2image import Html2Image
import numpy as np
import os
from frappe.utils import get_site_name
import base64
from frappe.utils import (
    nowdate,
    parse_val,
    is_html,
    add_to_date,
)
from escpos import *

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


def get_print_context(doc):
    setting = frappe.get_doc("POS Config", frappe.db.get_value("POS Profile",doc.pos_profile, "pos_config"))
    return {"doc": doc, "nowdate": nowdate, "frappe.utils": frappe.utils,"setting":setting}


 
def trim(file_path):
    image = Image.open(file_path)
    # Load the image and convert it to RGB
    image = image.convert("RGB")

    # Get the pixel values as a numpy array
    pixels = np.array(image)

    # Define the color range for red and white
    red_min = np.array([200, 0, 0])
    red_max = np.array([255, 50, 50])
    white_min = np.array([240, 240, 240])
    white_max = np.array([255, 255, 255])

    # Create a mask for pixels that are red or white
    mask = np.logical_or(
        np.all(np.logical_and(pixels >= red_min, pixels <= red_max), axis=-1),
        np.all(np.logical_and(pixels >= white_min, pixels <= white_max), axis=-1)
    )

    # Find the bounding box of the white area
    coords = np.argwhere(~mask)
    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0) + 1

    # Crop the image using the bounding box
    cropped = image.crop((x_min, y_min, x_max, y_max))

    # Save the cropped image
    cropped.save(file_path)

@frappe.whitelist(allow_guest=True)
def get_bill_image(name):
    doc = frappe.get_doc("Sale", name)
    template,css = frappe.db.get_value("POS Receipt Template","Receipt En",["template","style"])
    html=frappe.render_template(template, get_print_context(doc))

    chrome_path = "/usr/bin/google-chrome"

    # Set the CHROME_PATH environment variable
    os.environ['CHROME_PATH'] = chrome_path
     
     
    hti = Html2Image()
    hti.chrome_path=chrome_path
    hti.output_path =frappe.get_site_path() 
    hti.size=(570, 10000)
    hti.screenshot(html_str=html, css_str=css, save_as='bill_image.png')
  

 
    image_path = '{}/bill_image.png'.format(frappe.get_site_path())
    
    trim(image_path)
    p = printer.Network("192.168.10.80")
    p.image(image_path)
    p.cut()
    p.close()
        
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        encoded_data = base64.b64encode(image_data).decode("utf-8")
    return encoded_data
 
