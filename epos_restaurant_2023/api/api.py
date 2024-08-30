import copy
import json
import frappe
import base64
from frappe.desk.desktop import Workspace
from frappe.utils.data import getdate
from py_linq import Enumerable
from frappe.utils import format_datetime
from urllib.parse import unquote,quote
from datetime import datetime, timedelta
from frappe import _
from frappe.desk.query_report import run
import ast

import gspread
from oauth2client.service_account import ServiceAccountCredentials
 
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from epos_restaurant_2023.api.security import aes_encrypt,get_aes_key,encode_base64,decode_base64,aes_decrypt
 




@frappe.whitelist()
def testing():
    frappe.db.sql("update `tabDocField` set hidden=1 where parent='Product' and fieldname='price'")
    frappe.db.commit()
    

@frappe.whitelist(allow_guest=True)
def get_theme():
    return frappe.db.get_single_value("ePOS Settings","app_theme")

@frappe.whitelist()
def search_image_from_google(keyword):
    url = f"https://www.google.com/search?q={quote_plus(keyword)}&tbm=isch"
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    image_tags = soup.find_all("img")
    urls=[]
 
    for i, img in enumerate(image_tags):
        img_url = img.get("src")

        if img_url and "https" in img_url:
            urls.append(img_url)
    return urls

 


@frappe.whitelist(allow_guest=True)
def check_username(pin_code):    
    
    if pin_code:    
        pin_code = (str( base64.b64encode(pin_code.encode("utf-8")).decode("utf-8")))
        users = frappe.db.sql("select user_id, pos_permission from `tabEmployee` where pos_pin_code = '{}' and allow_login = 1 and allow_login_to_epos = 1 limit 1".format(pin_code), as_dict = 1)
        if users:
            data = frappe.db.sql("select name,full_name,user_image from `tabUser` where name='{}' limit 1".format(users[0].user_id),as_dict=1)
            if data:
                permission= frappe.get_doc("POS User Permission",users[0]["pos_permission"])      
                return {"username":data[0]["name"],"full_name":data[0]["full_name"],"user_image":data[0]["user_image"],"permission":permission} 
        
    frappe.throw(_("Invalid PIN Code"))

@frappe.whitelist(allow_guest=True)
def get_user_info(name=""):   
    if  name=="":
        name = frappe.session.user
    if name == "Guest":
        frappe.throw("Please login to start using epos system")

    users = frappe.db.sql("select user_id, pos_permission from `tabEmployee` where user_id = '{}' ".format(name), as_dict = 1)
    if users:
        data = frappe.db.sql("select name,full_name,user_image,role_profile_name from `tabUser` where name='{}'".format(name),as_dict=1)
        if data:
            permission= frappe.get_doc("POS User Permission",users[0]["pos_permission"])      
            return {"username":data[0]["name"],"full_name":data[0]["full_name"],"photo":data[0]["user_image"],"role":users[0]["pos_permission"],"permission":permission} 

@frappe.whitelist(allow_guest=True)
def switch_pos_profile_login_user(pin_code):
    chk = check_username(pin_code)
    
    if chk:         
        user = get_user_information()
        if user:
            user.update({"permission":chk["permission"]})
            return user
        else:
            return False

    else:
        return False



@frappe.whitelist(allow_guest=True)
def get_system_settings(pos_profile="", device_name=''):
    if not frappe.db.exists("POS Profile",pos_profile):
        frappe.throw("Invalid POS Profile name")
    
    if not frappe.db.exists("POS Station",device_name):
        frappe.throw("Invalid POS Station")

    pos_station = frappe.get_doc("POS Station",device_name)
    
    profile = frappe.get_doc("POS Profile",pos_profile)
    pos_config = frappe.get_doc("POS Config",profile.pos_config)
    pos_branding = frappe.get_doc("POS Branding", profile.pos_branding)

    sale_types = frappe.get_list("Sale Type",fields=['name', 'sale_type_name','color','is_order_use_table','sort_order','inactive'],order_by="sort_order",filters={"inactive":0})

    
    epos_sync_setting = frappe.get_doc("ePOS Sync Setting")
    
        
    doc = frappe.get_doc('ePOS Settings')
    table_groups = []
    for g in profile.table_groups:
        _group = frappe.get_doc("Table Group",g.table_group,fields=["photo","table_group_name_kh"])        
        table_groups.append({
            "key":g.table_group.lower().replace(" ","_"),
            "table_group":g.table_group,
            "table_group_kh":_group.table_group_name_kh,
            "background":_group.photo,
            "tables":get_tables_number(g.table_group, device_name),
            "search_table_keyword":""
            })
    pos_menus = []
    for m in profile.pos_menus:
        pos_menus.append({"pos_menu":m.pos_menu})   
    
    #main currency information
    main_currency = frappe.get_doc("Currency",frappe.db.get_default("currency"))
    second_currency = frappe.get_doc("Currency",frappe.db.get_default("second_currency"))

    payment_types=[]
    for p in pos_config.payment_type:
        payment_types.append({ 
            "account_code":p.account_code,
            "cancel_order_adjustment_account_code":p.cancel_order_adjustment_account_code,
            "payment_method":p.payment_type,
            "payment_type_group":p.payment_type_group,
            "currency":p.currency,
            "currency_symbol":p.currency_symbol,
            "currency_precision":p.currency_precision,
            "allow_change":p.allow_change,
            "is_single_payment_type":p.is_single_payment_type,
            "allow_cash_float":p.allow_cash_float, 
            "input_amount":0.0,
            "exchange_rate":p.exchange_rate if p.currency != main_currency.name else 1.0,
            "change_exchange_rate":p.change_exchange_rate if p.currency != main_currency.name else 1.0,
            "required_customer":p.required_customer,
            "is_foc":p.is_foc,
            "pos_currency_format":p.pos_currency_format,
            "use_room_offline":p.use_room_offline,
            "rooms":p.rooms,
            "is_manual_fee":p.is_manual_fee,
            "fee_percentage":p.fee_percentage
            })
    
    #get currency
    currencies = frappe.db.sql("select name,symbol,custom_currency_precision as currency_precision,symbol_on_right, custom_pos_currency_format as pos_currency_format  from `tabCurrency` where enabled=1", as_dict=1)
    

    #get price rule
    price_rules = []
    for pr in pos_config.price_rules:
        price_rules.append({"price_rule":pr.price_rule})
    # get lang 
    lang = frappe.db.sql("select language_code,language_name from `tabLanguage` where enabled = 1",as_dict = 1)
    
 
 
    pos_setting={
        "business_branch":profile.business_branch,
        "business_name_en":pos_config.business_name_en,
        "business_name_kh":pos_config.business_name_kh,
        "address_kh":pos_config.address_kh,
        "address_en":pos_config.address,
        "logo":pos_branding.logo,
        "phone_number":pos_config.phone_number,
        "vattin_number":pos_config.vattin_number,
        "email":pos_config.email,
        "website":pos_config.website,
        "sale_types":sale_types,
        "main_currency_name":main_currency.name,
        "exchange_rate_main_currency":frappe.db.get_default("exchange_rate_main_currency"),
        "main_currency_symbol":main_currency.symbol,
        "main_currency_format":main_currency.custom_pos_currency_format,
        "main_currency_precision":main_currency.custom_currency_precision,
        "second_currency_precision":second_currency.custom_currency_precision,
        "second_currency_name":second_currency.name,
        "second_currency_symbol":second_currency.symbol,
        "second_currency_format":second_currency.custom_pos_currency_format,
        "tax_1_name":doc.tax_1_name,
        "tax_2_name":doc.tax_2_name,
        "tax_3_name":doc.tax_3_name,
        "specific_business_branch":doc.specific_business_branch,
        "specific_pos_profile":doc.specific_pos_profile,
        "backend_port":doc.backend_port,
        "customer_display_slideshow": pos_branding.customer_display_slideshow,
        "thank_you_message":pos_branding.thank_you_message,
        "cancel_print_bill_required_password":pos_config.cancel_print_bill_required_password,
        "cancel_print_bill_required_note":pos_config.cancel_print_bill_required_note,
        "free_item_required_password":pos_config.free_item_required_password,
        "free_item_required_note":pos_config.free_item_required_note,
        "change_item_price_required_password":pos_config.change_item_price_required_password,
        "change_item_price_required_note":pos_config.change_item_price_required_note,
        "delete_item_required_password":pos_config.delete_item_required_password,
        "delete_item_required_note":pos_config.delete_item_required_note,
        "discount_item_required_password":pos_config.discount_item_required_password,
        "discount_item_required_note":pos_config.discount_item_required_note,
        "cancel_discount_item_required_password":pos_config.cancel_discount_item_required_password,
        "cancel_discount_item_required_note":pos_config.cancel_discount_item_required_note,
        "switch_pos_profile_required_password":pos_config.switch_pos_profile_required_password or 0,
        "discount_sale_required_password":pos_config.discount_sale_required_password,
        "cancel_discount_sale_required_password":pos_config.cancel_discount_sale_required_password,
        "discount_sale_required_note":pos_config.discount_sale_required_note,
        "cancel_discount_sale_required_note":pos_config.cancel_discount_sale_required_note,
        "delete_bill_required_password":pos_config.delete_bill_required_password,
        "delete_bill_required_note":pos_config.delete_bill_required_note,
        "change_tax_setting_required_password":pos_config.change_tax_setting_required_password,
        "change_tax_setting_required_note":pos_config.change_tax_setting_required_note,
        "allow_change_quantity_after_submit":pos_config.allow_change_quantity_after_submit,
        "allow_append_quantity_after_submit":pos_config.allow_append_quantity_after_submit,
        "main_currency_predefine_payment_amount":pos_config.main_currency_predefine_payment_amount,
        "second_currency_predefine_payment_amount":pos_config.second_currency_predefine_payment_amount,
        "percentage_of_bill_amount_to_claim_crypto":pos_config.percentage_of_bill_amount_to_claim_crypto,
        "open_order_required_password":pos_config.open_order_required_password,
        "order_station_open_order_required_password":pos_config.order_station_open_order_required_password,
        "change_price_rule_require_password":pos_config.change_price_rule_require_password,
        "open_cashdrawer_require_password":pos_config.open_cashdrawer_require_password,
        "edit_closed_receipt_required_password":pos_config.edit_closed_receipt_required_password,
        "edit_closed_receipt_required_note":pos_config.edit_closed_receipt_required_note,
        "start_working_day_required_password":pos_config.start_working_day_required_password,
        "close_working_day_required_password":pos_config.close_working_day_required_password,
        "start_cashier_shift_required_password":pos_config.start_cashier_shift_required_password,
        "close_cashier_shift_required_password":pos_config.close_cashier_shift_required_password,
        "cash_in_check_out_required_password":pos_config.cash_in_check_out_required_password,
        "print_waiting_order_after_submit_order":pos_config.print_waiting_order_after_submit_order,
        "print_new_deleted_sale_product":pos_config.print_new_deleted_sale_product,
        "print_sale_product_merged_table":pos_config.print_sale_product_merged_table,
        "print_sale_product_change_table":pos_config.print_sale_product_change_table,
        "print_sale_product_move_item":pos_config.print_sale_product_move_item,
        "show_item_code_in_sale_screen":pos_config.show_item_code_in_sale_screen,
        "show_button_tip":pos_config.show_button_tip,
        "tip_account_code":pos_config.tip_account_code,
        "allow_closed_working_day_when_has_pending_order":pos_config.allow_closed_working_day_when_has_pending_order,
        "delete_voucher_top_up_required_password":pos_config.delete_voucher_top_up_required_password,
        "add_voucher_top_up_required_password":pos_config.add_voucher_top_up_required_password,
        "check_delete_item_require_passord_from_product":pos_config.check_delete_item_require_passord_from_product,
        "allow_change_date_when_start_working_day":doc.allow_change_date_when_start_working_day,
        "is_client_side_sync_setting":epos_sync_setting.client_side,
        "park_item_days_expiry":pos_config.park_item_days_expiry,
        "apply_rate_include_tax_required_password":pos_config.apply_rate_include_tax_required_password,
        "apply_rate_include_tax_required_note":pos_config.apply_rate_include_tax_required_note
        }
    #get default customre
    
    if not profile.default_customer:
        frappe.throw("There is no default customer for pos profie {}".format(pos_profile))

    default_customer = frappe.get_doc("Customer", profile.default_customer)
    
    #get default print format
    _pos_print_format = frappe.get_list("POS Print Format Setting",fields=[
        "name",
        "business_branch",
        "title",
        "print_format_doc_type",
        "pos_receipt_template",
        "print_format",
        "print_report_name",
        "sort_order",
        "show_in_pos_report",
        "show_in_pos",
        "print_invoice_copies", 
        "print_receipt_copies",
        "pos_invoice_file_name",
        "pos_receipt_file_name", 
        "receipt_height",
        "receipt_width",
        "receipt_margin_top",
        "receipt_margin_left",
        "receipt_margin_right",
        "receipt_margin_bottom",
        "show_in_pos_closed_sale",
        "report_options"],order_by="sort_order asc")
    
    _pos_print_format_data = []
    for p in _pos_print_format:
        if (p.business_branch or '') == '' or p.business_branch == profile.business_branch:
            pf = frappe.get_doc("Print Format", p.print_format)
            _data = {
                "name":p.print_format,
                "title":p.title,
                "doc_type":pf.doc_type,
                "pos_receipt_template":p.pos_receipt_template,
                "print_report_name":p.print_report_name,
                "default_print_language":pf.default_print_language,
                "show_in_pos_report":p.show_in_pos_report,
                "show_in_pos":p.show_in_pos,
                "print_invoice_copies":p.print_invoice_copies, 
                "print_receipt_copies":p.print_receipt_copies,
                "pos_invoice_file_name":p.pos_invoice_file_name,
                "pos_receipt_file_name":p.pos_receipt_file_name, 
                "receipt_height":p.receipt_height, 
                "receipt_width":p.receipt_width,
                "receipt_margin_top":p.receipt_margin_top, 
                "receipt_margin_left":p.receipt_margin_left,
                "receipt_margin_right":p.receipt_margin_right,
                "receipt_margin_bottom":p.receipt_margin_bottom,
                "show_in_pos_closed_sale":p.show_in_pos_closed_sale,
                "report_options":p.report_options,
                "business_branch":p.business_branch or "",
                "sort_order":p.sort_order,
            }
            _pos_print_format_data.append(_data)



 

    default_pos_receipt=None
    if _pos_print_format_data:
        _receipt_setting = list(filter(lambda x: x["name"] == profile.default_pos_receipt,_pos_print_format_data))
        if _receipt_setting:
            default_pos_receipt = _receipt_setting[0]

 
    #get report list   
    reports = _pos_print_format_data

    letter_heads = frappe.db.sql("select name,is_default from `tabLetter Head` where disabled = 0",as_dict = 1)
    letter_heads.append({"name":"No Letterhead","is_default":0})

 

    #get tax rules 
    tax_rules = []
    for d in profile.pos_profile_tax_rule: 
        tax_rules.append({"tax_rule":d.tax_rule,"tax_rule_data":d.tax_rule_data})

    #get default tax rule
    tax_rule ={}
    if profile.tax_rule:      
        tax_rule = frappe.get_doc("Tax Rule", profile.tax_rule)

    #get shortcut key
    shortcut_keys = frappe.db.get_list('Shortcut Key',fields=['name','key','description'])

    #get shift type
    shift_types = frappe.db.sql("select name, sort,show_in_pos from `tabShift Type`",as_dict=1)    
    
    #check if epos system have exely integration then get setting
    exely= frappe.get_doc("Exely Itegration Setting")
    
    point_setting = frappe.get_doc("Loyalty Point Settings")
    
    data={
        "app_name":doc.epos_app_name,
        "specific_business_branch":doc.specific_business_branch,
        "specific_pos_profile":doc.specific_pos_profile,
        "business_branch":profile.business_branch,
        "address":pos_config.address,
        "logo":pos_branding.logo,
        "phone_number":pos_config.phone_number,
        "pos_profile":pos_profile,
        "outlet":profile.outlet,
        "use_retail_ui":profile.use_retail_ui,
        "close_business_day_on":pos_config.close_business_day_on,
        "alert_close_working_day_after":pos_config.alert_close_working_day_after,
        "price_rule":profile.price_rule,
        "stock_location":profile.stock_location,
        "tax_rules":tax_rules,
        "tax_rule":tax_rule,
        "login_background":pos_branding.login_background,
        "home_background":pos_branding.home_background,
        "thank_you_background":pos_branding.thank_you_background,
        "table_groups":table_groups,
        "pos_menus":pos_menus,
        "default_pos_menu":profile.default_pos_menu,
        "payment_types":payment_types,
        "tax_1_name":doc.tax_1_name,
        "tax_2_name":doc.tax_2_name,
        "tax_3_name":doc.tax_3_name,
        "use_guest_cover":pos_config.use_guest_cover,
        "switch_pos_profile_required_password":pos_config.switch_pos_profile_required_password or 0,
        "sale_status":frappe.db.sql("select name,background_color from `tabSale Status`", as_dict=1),
        "print_cashier_shift_summary_after_close_shift":pos_config.print_cashier_shift_summary_after_close_shift,
        "print_cashier_shift_sale_product_summary_after_close_shift":pos_config.print_cashier_shift_sale_product_summary_after_close_shift,
        "print_working_day_summary_after_close_working_day":pos_config.print_working_day_summary_after_close_working_day,
        "print_working_day_sale_product_summary_after_close_working_day":pos_config.print_working_day_sale_product_summary_after_close_working_day,
        "print_new_deleted_sale_product":pos_config.print_new_deleted_sale_product,
        "print_sale_product_merged_table":pos_config.print_sale_product_merged_table,
        "print_sale_product_change_table":pos_config.print_sale_product_change_table,
        "print_sale_product_move_item":pos_config.print_sale_product_move_item,
        "pos_sale_order_background_image":pos_branding.pos_sale_order_background_image,
        "show_item_code_in_sale_screen":pos_config.show_item_code_in_sale_screen,
        "show_button_tip":pos_config.show_button_tip,
        "tip_account_code":pos_config.tip_account_code,
        "shift_types":shift_types,
        "currencies":currencies,
        "default_currency":frappe.db.get_default("currency"),
        "pos_setting":pos_setting,
        "customer":default_customer.name,
        "customer_name":default_customer.customer_name_en,
        "customer_photo":default_customer.photo,
        "customer_group":default_customer.customer_group,
        "default_sale_type":profile.default_sale_type,
        "default_payment_type":profile.default_payment_type,
        "default_pos_receipt":default_pos_receipt,
        "second_currency_payment_type":profile.second_currency_payment_type,
        "price_rules":price_rules,
        "lang": lang,
        "reports":reports,
        "letter_heads":letter_heads,
        "device_setting":pos_station, 
        "shortcut_key":shortcut_keys,
        "exely":{
            "enabled":exely.enabled, "default_general_customer_id":exely.default_general_customer_id, "guest_api_endpoint":exely.guest_api_endpoint,"api_key":exely.api_key
        },
        "point_setting":point_setting,
        "change_table_previous_date":pos_config.change_table_previous_date
    }

    return  data


@frappe.whitelist(allow_guest=True)
def get_tables_number(table_group,device_name):
    data = frappe.db.sql("""select 
                            name as id, 
                            shape, 
                            tbl_number as tbl_no,
                            sale_type, 
                            default_discount,
                            default_customer,
                            customer_name,
                            customer_photo,
                            customer_group,
                            height as h, 
                            width as w, 
                            price_rule,
                            discount_type 
                         from `tabTables Number` 
                         where tbl_group='{}' 
                         order by 
                         sort_order, 
                         tbl_number""".format(table_group), as_dict=1)

    background_color = frappe.db.get_default("default_table_number_background_color")
    text_color = frappe.db.get_default("default_table_number_text_color")
    i = 0
    x = 10
    y = 10 
    for d in data:
        d.background_color=background_color
        d.default_bg_color=background_color
        d.text_color = text_color
        d.default_text_color = text_color
        position = frappe.db.sql("select x,y,h,w from `tabePOS Table Position` where device_name='{}' and tbl_number='{}' limit 1".format(device_name,d.tbl_no ), as_dict=1)
        if position:
            for p in position:
                d.x = p.x or x
                d.y = p.y or y 
                d.w = p.w or 100
                d.h = p.h or 100
        else:
            d.x = x
            d.y = y 

        i += 1 
        x += 110
        if i >=10:
            x = 10
            y += 110
            i = 0
        ##

    return data

@frappe.whitelist(allow_guest=True)
def check_pos_profile(pos_profile_name, device_name, is_used_validate=True):

 
    if not frappe.db.exists("POS Profile", pos_profile_name):
        frappe.throw("Invalid POS Profile")

    if not frappe.db.exists("POS Station", device_name):
        frappe.throw("Invalid POS Station")   

    station =  frappe.get_doc("POS Station",device_name)
    if station.disabled:
        frappe.throw("This station was disabled.")

    if not device_name=="Demo":
        if is_used_validate:
            if station.is_used and not device_name=="Demo":
                frappe.throw("This station is already used")

        frappe.db.sql("update `tabPOS Station` set is_used = 1 where name = '{}'".format(device_name))
        
        frappe.db.commit()
    
    

    return station


@frappe.whitelist()
def get_current_working_day(business_branch):
   
    sql = "select name, posting_date, pos_profile, note from `tabWorking Day` where business_branch = %(business_branch)s and is_closed = 0 order by creation limit 1"
    data =  frappe.db.sql(sql, {"business_branch":business_branch},as_dict=1) 
    if data:
        return data [0]
    return None

@frappe.whitelist()
def get_current_shift_information(business_branch, pos_profile):
    return {
        "working_day":get_current_working_day(business_branch),
        "cashier_shift":get_current_cashier_shift(pos_profile)
    }

@frappe.whitelist()
def receipt_list_summary(filter):
    python_object = ast.literal_eval(filter)
    sql = """select 
    sum(grand_total) grand_total,
    sum(total_discount) total_discount,
    sum(sub_total) sub_total,
    sum(total_paid - changed_amount) total_paid , 
    sum(if(docstatus !=2 ,1,0)) as total_receipts 
    from `tabSale` {}"""
    sql_conditions = []
    sql_deleted_conditions = []
    for condition in python_object:
        key, value = condition.popitem() 
        operator, operand = value
        if operator == "=":
            sql_conditions.append(f"{key} = '{operand}'")
            sql_deleted_conditions.append(f"{key} = '{operand}'")
        elif operator == "in": 
            sql_conditions.append(f"{key} IN {tuple(operand)}")
            if key == "docstatus":
                pass
            else:
                sql_deleted_conditions.append(f"{key} IN {tuple(operand)}")

        elif operator == "between":
            sql_conditions.append(f"{key} IN {tuple(operand)}")
            sql_deleted_conditions.append(f"{key} IN {tuple(operand)}")

    sql_query = " AND ".join(sql_conditions)
    sql_deleted_query = " AND ".join(sql_deleted_conditions) 

    data = frappe.db.sql(sql.format("where " + sql_query),as_dict=1) 
    data_deleted = frappe.db.sql("select sum(if(docstatus=2,1,0)) as total_receipt_deleted from `tabSale` {}".format("where " + sql_deleted_query),as_dict=1) 
    data[0].update({"total_receipt_deleted":data_deleted[0]["total_receipt_deleted"]})
    return data

@frappe.whitelist()
def get_resevation_calendar(business_branch,start,end):
    sql = """select 
                name, 
                arrival_date as start,
                arrival_time,
                CONCAT(guest,'-',guest_name) as title,
                phone_number,
                total_deposit,
                reservation_status_color as textColor,
                reservation_status_background_color as backgroundColor,
                reservation_status_background_color as borderColor 
            from `tabPOS Reservation` 
            where 
                property='{0}' and 
                arrival_date between '{1}' and '{2}'
            order by arrival_time
            """.format(business_branch,getdate(start),getdate(end))
    data = frappe.db.sql(sql,as_dict=1)
    return data

@frappe.whitelist()
def get_resevation_detail(name):
    reservation = frappe.get_doc("POS Reservation",name)
    payments = frappe.db.get_list("Sale Payment",
    fields=['posting_date','payment_type','payment_amount','currency_precision','name','input_amount'],
    filters={
        'pos_reservation': name,
        'docstatus':1
    })
    return {"reservation":reservation,"payment":payments}

@frappe.whitelist()
def get_current_cashier_shift(pos_profile):
   
    sql = "select name,working_day, posting_date,shift_name, pos_profile, opened_note,business_branch,total_opening_amount from `tabCashier Shift` where pos_profile = %(pos_profile)s and is_closed = 0 order by creation desc limit 1"
    data =  frappe.db.sql(sql, {"pos_profile":pos_profile},as_dict=1) 
    if data:
        return data [0]
    return None



@frappe.whitelist()
def get_user_information():
    data = frappe.get_doc("User",frappe.session.user)
    return {
        "name":data.name,
        "full_name":data.full_name,
        "role":data.role_profile_name,
        "phone_number":data.phone,
        "photo":data.user_image
    }
    
    
@frappe.whitelist()
def save_table_position(device_name, table_group):
    # frappe.throw("{}".format(table_group))
    frappe.db.sql("delete from `tabePOS Table Position` where device_name='{}'".format(device_name) )
    
    for g in table_group:
        
        for t in g['tables']:
            x = 0
            if "x" in t:
                x = t["x"]
            y = 0
            if "y" in t:
                y = t["y"]
            h = 0
            if "h" in t:
                h = t["h"]
            w = 0
            if "w" in t:
                w = t["w"]
            if not frappe.db.exists('ePOS Table Position', {'tbl_number': t['tbl_no'], 'device_name': device_name}):
                doc = frappe.get_doc({
                        'doctype': 'ePOS Table Position',
                        'device_name':device_name,
                        'tbl_number': t['tbl_no'],
                        'x':x,
                        'y':y,
                        'h':h,
                        'w':w
                    })
                doc.insert()

@frappe.whitelist()
def get_pos_print_format(doctype,business_branch=None):    

    # pos_print_format =  
    sql = """select 
                name,
                title,
                pos_receipt_template,
                print_invoice_copies, 
                print_receipt_copies,
                pos_invoice_file_name, 
                pos_receipt_file_name, 
                receipt_height, 
                receipt_width,
                receipt_margin_top, 
                receipt_margin_left,
                receipt_margin_right,
                receipt_margin_bottom ,
                show_in_pos_closed_sale ,
                business_branch,
                report_options
            from `tabPOS Print Format Setting` 
            where print_format_doc_type='{}'
            and show_in_pos = 1 """.format(doctype)
    if business_branch:
        sql += " and business_branch = '{}'".format(business_branch)
    
    data = frappe.db.sql(sql, as_dict=True)    
    if data:
       return data
    else:
        return [{"name":"Standard","pos_invoice_file_name":""}]

@frappe.whitelist()
def get_pos_letter_head(doctype):
    
    data = frappe.db.sql("select name from `tabLetter Head` where   disabled=0", as_dict=True)
    
    if data:
        arr =[]
        for d in data:
            arr.append(d.name)
        return arr

@frappe.whitelist()
def get_close_shift_summary(cashier_shift):
    data = []
    doc = frappe.get_doc("Cashier Shift",cashier_shift)
    
    #get close amount by payment type
    sql = "select payment_type, currency,sum(input_amount + (fee_amount * exchange_rate)) as input_amount, sum(payment_amount + fee_amount) as payment_amount from `tabSale Payment` where cashier_shift='{}' and docstatus=1 group by payment_type, currency".format(cashier_shift)
    voucher_payment_sql = """SELECT 
                                payment_type, 
                                exchange_rate,
                                currency,sum(input_amount) as input_amount, 
                                sum(payment_amount) as payment_amount from `tabVoucher Payment` 
                            WHERE 
                                cashier_shift='{}' and 
                                docstatus=1 
                            group BY 
                                payment_type,
                                currency""".format(cashier_shift)

    
    payments = frappe.db.sql(sql, as_dict=1)
    voucher_payments = frappe.db.sql(voucher_payment_sql, as_dict=1)
    
    
    #get cash in out 
    sql = """select  
                payment_type,
                exchange_currency,
                currency,
                sum(if(transaction_status='Cash Out',input_amount*-1,input_amount)) as total_input_amount, 
                sum(if(transaction_status='Cash Out',amount*-1,amount)) as total_amount 
            from `tabCash Transaction`   
            where cashier_shift='{}'    
            group by  
                payment_type,
                currency,
                exchange_currency""".format(cashier_shift)
 
    cash_transactions = frappe.db.sql(sql, as_dict=1)
    

    #get cash float
    for d in doc.cash_float:
        data.append({
            "name":d.name,
            "payment_method":d.payment_method,
            "exchange_rate":d.exchange_rate,
            "input_amount":d.input_amount,
            "opening_amount":d.opening_amount,
            "input_close_amount":0,
            "input_system_close_amount":d.input_amount +  Enumerable(payments).where(lambda x:x.payment_type == d.payment_method).sum(lambda x: x.input_amount or 0 ), 
            "system_close_amount": d.opening_amount +  Enumerable(payments).where(lambda x:x.payment_type == d.payment_method).sum(lambda x: x.payment_amount or 0 ),
            "different_amount":0,
            "currency":d.currency
        })
    
    #get cash transaction
    for c in cash_transactions:        
        data.append({
            "payment_method":c.payment_type,
            "exchange_rate":c.exchange_currency,
            "input_amount":0,
            "opening_amount":0,
            "input_close_amount":0,
            "input_system_close_amount":c.total_input_amount,
            "system_close_amount": c.total_amount,
            "different_amount":0,
            "currency":c.currency
        })
    
 
    for p in payments:
        if not p.payment_type  in [d.payment_method for d in doc.cash_float]:
            exchange_rate =  frappe.db.get_value("Payment Type", p.payment_type, "exchange_rate")           
            data.append({
                "payment_method":p.payment_type,
                "exchange_rate":exchange_rate,
                "input_amount":0,
                "opening_amount":0,
                "input_close_amount":0,
                "input_system_close_amount": p.input_amount,
                "system_close_amount": p.payment_amount,
                "different_amount":0,
                "currency":p.currency
            })
   
    for voucher_payment in voucher_payments:
        data.append({
            "payment_method":voucher_payment.payment_type,
            "exchange_rate":voucher_payment.exchange_rate,
            "input_amount":0,
            "opening_amount":0,
            "input_close_amount":0,
            "input_system_close_amount": voucher_payment.input_amount,
            "system_close_amount": voucher_payment.payment_amount,
            "different_amount":0,
            "currency":voucher_payment.currency
        })
    
        
    return get_cash_float(data)

#get cash float sum group by
def get_cash_float(data):
	result = []
	groups = {}
	for row in data:
		group = {
            "payment_method": row["payment_method"], 
            "exchange_rate":row["exchange_rate"],
            "currency":row["currency"]
            }
		
		input_amount = row['input_amount']
		opening_amount = row['opening_amount']
		input_close_amount = row['input_close_amount']
		input_system_close_amount = row['input_system_close_amount']
		system_close_amount = row['system_close_amount']
		different_amount = row['different_amount']
		g = json.dumps(group)	  
		if g not in groups:
			groups[g] = {
                'input_amount': [],
                'opening_amount':[],
                'input_close_amount':[],
                'input_system_close_amount':[],
                'system_close_amount':[],
                'different_amount':[],
                } 

		groups[g]['input_amount'].append(input_amount)
		groups[g]['opening_amount'].append(opening_amount)
		groups[g]['input_close_amount'].append(input_close_amount)
		groups[g]['input_system_close_amount'].append(input_system_close_amount)
		groups[g]['system_close_amount'].append(system_close_amount)
		groups[g]['different_amount'].append(different_amount)


	for group, total in groups.items():	 
		total_input_amount = sum(total['input_amount'])
		total_opening_amount = sum(total['opening_amount'])
		total_input_close_amount = sum(total['input_close_amount'])
		total_input_system_close_amount = sum(total['input_system_close_amount'])
		total_system_close_amount = sum(total['system_close_amount'])
		total_different_amount = sum(total['different_amount'])
		
		g = json.loads(group)	
		
		_result = {}
		_result.update({
                "payment_method":g['payment_method'],
                "exchange_rate":g['exchange_rate'],
                "currency":g['currency'],
                "input_amount":total_input_amount or 0,
                "opening_amount":total_opening_amount or 0,
                "input_close_amount": total_input_system_close_amount or 0 ,##total_input_close_amount or 0,
                "input_system_close_amount": total_input_system_close_amount or 0,
                "system_close_amount": total_system_close_amount or 0,
                "different_amount": total_different_amount or 0
            })	
            
		result.append(_result)
           
	return result


@frappe.whitelist()
def get_payment_cash(cashier_shift):
    sql = "select payment_type, currency, SUM(payment_amount) as payment_amount from `tabSale Payment` where cashier_shift='{}' AND payment_type_group = 'Cash' and docstatus=1 group by payment_type, currency".format(cashier_shift)
    data = frappe.db.sql(sql, as_dict=1)
    return data
@frappe.whitelist()
def get_cash_drawer_balance(cashier_shift):
    sql_system_amount = "SELECT COALESCE( SUM(payment_amount),0) AS total_amount_cash FROM `tabSale Payment` where cashier_shift='{}' AND payment_type_group = 'Cash' and docstatus=1".format(cashier_shift)
    sql_opening_amount = "SELECT total_opening_amount FROM `tabCashier Shift` WHERE name = '{}'".format(cashier_shift)
    sql_cash_out = "SELECT COALESCE( SUM(amount), 0) AS total_amount_cash_out FROM `tabCash Transaction` WHERE cashier_shift = '{}' AND transaction_status = 'Cash Out'".format(cashier_shift)
    sql_cash_in = "SELECT COALESCE( SUM(amount), 0) AS total_amount_cash_in FROM `tabCash Transaction` WHERE cashier_shift = '{}' AND transaction_status = 'Cash In'".format(cashier_shift)
    
    data_system_amount = frappe.db.sql(sql_system_amount, as_dict=1)
    total_amount_cash = data_system_amount[0].total_amount_cash
    data_opening_amount = frappe.db.sql(sql_opening_amount, as_dict=1)
    total_opening_amount = data_opening_amount[0].total_opening_amount
    data_cash_in = frappe.db.sql(sql_cash_in, as_dict=1)
    total_amount_cash_in = data_cash_in[0].total_amount_cash_in
    data_cash_out = frappe.db.sql(sql_cash_out, as_dict=1)
    total_amount_cash_out = data_cash_out[0].total_amount_cash_out
    data = {
        "total_amount_cash": total_amount_cash,
        "total_opening_amount": total_opening_amount,
        "total_amount_cash_in": total_amount_cash_in,
        "total_amount_cash_out": total_amount_cash_out,
        "total_balance": total_amount_cash - total_amount_cash_out + total_amount_cash_in + total_opening_amount
    }
    return data

@frappe.whitelist()
def get_meta(doctype):
    data =  frappe.get_meta(doctype)
    return data

@frappe.whitelist(allow_guest=1)
def test_get_meta(): 
    data =  frappe.get_meta("Sale")
    return data

@frappe.whitelist()
def update_print_bill_requested(name):
    doc = frappe.get_doc("Sale",name)
    doc.sale_status = 'Bill Requested'
    doc.save()
    frappe.db.commit()
    return doc
@frappe.whitelist( methods="POST")
def update_cancel_print_request(data):
    result = []
    for a in data:
        doc = frappe.get_doc("Sale", a["name"])
        doc.sale_status = "Submitted"
        doc.save() 
    frappe.db.commit()

    return True

@frappe.whitelist(methods="POST")
def get_sale_list_table_badge(data):
    pos_profile = frappe.get_doc("POS Profile",data["pos_profile"])
    if len(pos_profile.sale_view_by_pos_profile) > 0:
        data["pos_profile"] = [d.pos_profile for d in pos_profile.sale_view_by_pos_profile]
        sql = """select 
            `name`,
            creation,
            grand_total,
            total_quantity,
            tbl_group,
            tbl_number,
            guest_cover,
            grand_total,
            sale_status,
            sale_status_color,
            sale_status_priority,
            customer,
            customer_name,
            phone_number,
            customer_photo
        from `tabSale` 
        where pos_profile in %(pos_profiles)s
        and docstatus = 0"""
        result = frappe.db.sql(sql,{"pos_profiles":data["pos_profile"]},as_dict=1)
        return result
    else:
        sql = """select 
            `name`,
            creation,
            grand_total,
            total_quantity,
            tbl_group,
            tbl_number,
            guest_cover,
            grand_total,
            sale_status,
            sale_status_color,
            sale_status_priority,
            customer,
            customer_name,
            phone_number,
            customer_photo
        from `tabSale` 
        where pos_profile = '{}' 
        and docstatus = 0""".format(data["pos_profile"])

        result = frappe.db.sql(sql,as_dict=1)
        return result

@frappe.whitelist(methods="POST")
def get_pending_sale_orders(data): 
    sql = """select 
        `name`,
        modified,
        sale_status,
        sale_status_color,
        sale_type,
        sale_type_color,
        tbl_number,
        guest_cover,
        customer,
        customer_name,
        total_quantity,
        grand_total
    from `tabSale` 
    where docstatus = 0 
        and working_day = %(working_day)s
        and cashier_shift = if(%(cashier_shift)s ='', cashier_shift,%(cashier_shift)s )
    order by modified desc
    limit 200"""

    result = frappe.db.sql(sql,{
        "working_day":data["working_day"],
        "casher_shift":"" if not "casher_shift" in data else data["casher_shift"]
        },as_dict=1)
    return result



@frappe.whitelist()
def get_working_day_list_report(business_branch = '', pos_profile = ''): 
    days = int(frappe.db.get_default("number_of_day_cashier_can_view_report")) 
    
    date = datetime.today()
    new_date = date + timedelta(days=days*-1)    
    filters = {}
    if business_branch and not pos_profile:
        filters.update({"business_branch":["=", business_branch]})

    elif pos_profile:        
        filters.update({"pos_profile":["=", pos_profile] }) 

    working_days = frappe.db.get_list('Working Day',filters=filters,order_by='posting_date desc',page_length=1) 
    if working_days:
        wd = frappe.get_doc('Working Day',working_days[0].name)  
        filters.update({
            "posting_date":[">=", new_date],
            "posting_date":["<=", wd.posting_date]
        })    
    else:
        filters.update({
            "posting_date":[">=", new_date],
            "posting_date":["<=", date]
        })   

    working_day =frappe.db.get_list('Working Day',
        filters = filters,
        fields=["name","posting_date","creation","modified_by","owner","is_closed","closed_date"],
        order_by='posting_date desc',
        page_length=100,        
    )

    for w in working_day:
        cashier_shift =frappe.db.get_list('Cashier Shift',
            filters={
                "working_day": w.name
            },
            fields=["name","pos_profile","posting_date","creation","modified_by","is_closed"]            
        )
        w.cashier_shifts = cashier_shift
    
    data = working_day
    return data


@frappe.whitelist()
def edit_sale_order(name,auth=None,note=None):  
    # sale_doc = frappe.get_doc("Sale",name)
    # sale_doc.reload()
    # return sale_doc
    # sale_status_doc = frappe.get_doc("Sale Status","Submitted")
    # frappe.db.sql("update `tabSale` set docstatus = 0, sale_status='Submitted', sale_status_color='{1}', sale_status_priority={2} where name='{0}'".format(name,sale_status_doc.background_color,sale_status_doc.priority))
    # frappe.db.sql("update `tabSale Product` set docstatus = 0 where parent='{}'".format(name))
    # frappe.db.commit()

    # # return True

    sale_doc = frappe.get_doc("Sale",name)
    if sale_doc.is_generate_tax_invoice == 1:
        frappe.throw(_("Sale Order already has tax invoice."))
    if not auth:
        auth = frappe.db.get_value("Employee",{'user_id': frappe.session.user},['user_id','employee_name as full_name','name','pos_permission'], as_dict=1)
        if not auth:
            auth = frappe.db.get_value("User",{'name': frappe.session.user},['full_name','name'], as_dict=1)
        else:
            edit_closed_receipt = frappe.db.get_value('POS User Permission',auth.pos_permission,'edit_closed_receipt')
            
            if edit_closed_receipt != 1:
                frappe.throw(_("You don't permission to permform this action"))
        auth['note'] = (note if note else '')
    #check if sale already have payment then cancel sale payment first
    payments = frappe.get_list("Sale Payment",fields=["name"], filters={"sale":name,"docstatus":1})
    for p in payments:
        sale_payment = frappe.get_doc("Sale Payment", p.name)
        sale_payment.cancel()
        sale_payment.delete()
        from epos_restaurant_2023.api.utils import sync_data_to_server_on_delete
        sync_data_to_server_on_delete(doc= sale_payment)
    
    #then start to cancel sale

    payments = copy.deepcopy(sale_doc.payment)
    
    for p in [d for d in payments if d.folio_transaction_number and d.folio_transaction_type and  not d.cancel_order_adjustment_account_code]:
        frappe.throw("There is no cancel order adjustment account code for payment type {}. Please config it in POS Config Setting.".format(p.payment_type))



    sale_doc.payment=[]
    # frappe.throw(str(sale_doc.docstatus))
    sale_doc.cancel()


    #add comment to this doc to track who request to edit this sale order 
    #get user and note from pos confirm edit dialog
    

    #change status from 2 to 0 (Cancel to Draft) to allow pos can modified this doc
    sale_status_doc = frappe.get_doc("Sale Status","Submitted")
    frappe.db.sql("update `tabSale` set docstatus = 0, sale_status='Submitted', sale_status_color='{1}', sale_status_priority={2} where name='{0}'".format(name,sale_status_doc.background_color,sale_status_doc.priority))
    frappe.db.sql("update `tabSale Product` set docstatus = 0 where parent='{}'".format(name))



    #check sale has payment type transfer to edoor and user cancel order 
    # then we check payment type adjustment account then post adjustment account to edoor pms
    if 'edoor' in frappe.get_installed_apps():
        for p in [d for d in payments if d.folio_transaction_type and d.folio_transaction_number and d.cancel_order_adjustment_account_code]:
            data = {
                    'doctype': 'Folio Transaction',
                    "is_base_transaction":1,
                    'posting_date':sale_doc.posting_date,
                    'transaction_type': p.folio_transaction_type,
                    'transaction_number': p.folio_transaction_number,
                    'reference_number':sale_doc.name,
                    "input_amount":p.amount,
                    "amount":p.amount,
                    "quantity": 1 if frappe.get_cached_value("Account Code",p.cancel_order_adjustment_account_code,"allow_enter_quantity") ==1 else 0,
                    "report_quantity": 1 if frappe.get_cached_value("Account Code",p.cancel_order_adjustment_account_code,"show_quantity_in_report") ==1 else 0,
                    "transaction_amount":p.amount,
                    "total_amount":p.amount,
                    "account_code":p.cancel_order_adjustment_account_code,
                    "property":sale_doc.business_branch,
                    "is_auto_post":1,
                    "sale": sale_doc.name,
                    "tbl_number":sale_doc.tbl_number,
                    "type":"Credit",
                    "guest":sale_doc.customer,
                    "guest_name":sale_doc.customer_name,
                    "guest_type":sale_doc.customer_group,
                    "nationality": "" if not sale_doc.customer else  frappe.db.get_value("Customer",sale_doc.customer,"country"),
                    "report_description": "{} ({})" .format( frappe.get_cached_value("Account Code",p.cancel_order_adjustment_account_code,"account_name"),sale_doc.name) ,
                } 
            
 
            doc = frappe.get_doc(data)
            doc.insert(ignore_permissions=True)	
        
           


    #add comment
    doc = frappe.get_doc({
        'doctype': 'Comment',
        'subject': 'Edit Bill',
        "comment_type":"Info",
        "reference_doctype":"Sale",
        "reference_name":sale_doc.name,
        "comment_by":auth['full_name'],
        "custom_note":auth["note"],
        "content":"User {0} edit sale order. Reason: {1}".format(auth['full_name'], auth["note"])
    })
    doc.insert()
    

    if frappe.db.get_single_value("ePOS Sync Setting",'enable') == 1:
        from epos_restaurant_2023.api.utils import sync_data_to_server_on_submit
        sync_data_to_server_on_submit(doc= frappe.get_doc('Sale',sale_doc.name))

    # check if sale have excely integration then submit cancell order
    if sale_doc.exely_transaction_id:
        frappe.enqueue("epos_restaurant_2023.api.exely.cancel_order", queue='short', transaction_id = sale_doc.exely_transaction_id, comment = auth["note"])
  

@frappe.whitelist()
def delete_sale(name,auth): 
    sale_doc = frappe.get_doc("Sale",name)
    sale_amount = sale_doc.grand_total
    #validate cashier shift
    cashier_shift_doc = frappe.get_doc("Cashier Shift", sale_doc.cashier_shift)
    if cashier_shift_doc.is_closed==1:
        frappe.throw(_("Cashier shift is already closed."))


    #check if sale already have payment then cancel sale payment first
    payments = frappe.get_list("Sale Payment",fields=["name"], filters={"sale":name,"docstatus":1})
    for p in payments:
        sale_payment = frappe.get_doc("Sale Payment", p.name)
        # check  if reservation deposit
        if sale_payment.is_reservation_deposit:
            sale_payment.sale = ""
            sale_payment.save()
        else:
            sale_payment.cancel()
            sale_payment.delete()
    
    #then start to cancel sale
    sale_doc = frappe.get_doc("Sale",name)
    sale_doc.payment=[]
    if sale_doc.docstatus ==1:
        sale_doc.cancel()
    else:        
        frappe.db.sql("update `tabSale` set docstatus = 2,deleted_by=%(deleted_by)s,deleted_note=%(deleted_note)s  where name=%(name)s",{"name":name,"deleted_by":auth["full_name"],"deleted_note":auth["note"]})
        frappe.db.sql("update `tabSale Product` set docstatus = 2 where parent='{}'".format(name))
    
    #update sale product spa deleted
    query = "update `tabSale Product SPA Commission` set is_deleted = 1  where sale = '{}'".format(name)
    frappe.db.sql(query)

    # sale check if from pos reservation update status
    if sale_doc.from_reservation:
        if frappe.db.exists("POS Reservation", sale_doc.from_reservation):
            frappe.db.sql("update `tabPOS Reservation` set workflow_state='Confirmed' where name='{0}'".format(sale_doc.from_reservation))
            
            reservation = frappe.get_doc("POS Reservation", sale_doc.from_reservation)
            if reservation:
                reservation.reservation_status = "Confirmed"
                reservation.status = "Confirmed"
                reservation.save()


    #add to comment
    doc = frappe.get_doc({
        'doctype': 'Comment',
        'subject': 'Delete sale order',
        "comment_type":"Info",
        "reference_doctype":"Sale",
        "reference_name":sale_doc.name,
        "comment_by":auth['full_name'],
        "custom_note":auth["note"],
        "custom_amount": sale_amount,
        "content":"User {0} delete sale order. Reason: {1}".format(auth['full_name'], auth["note"])
    })
    doc.insert()
    


    if frappe.db.get_single_value("ePOS Sync Setting",'enable') == 1:
         frappe.enqueue("epos_restaurant_2023.api.utils.sync_data_to_server", queue='short', doc=frappe.get_doc("Sale",sale_doc.name),extra_action='["epos_restaurant_2023.selling.doctype.sale.sale.update_inventory_on_cancel"]',action="cancel")  

    
    
    # check if sale have excely integration then submit cancell order
    if sale_doc.exely_transaction_id:
        frappe.enqueue("epos_restaurant_2023.api.exely.cancel_order", queue='short', transaction_id = sale_doc.exely_transaction_id, comment = auth["note"])
        
    
@frappe.whitelist()
def get_filter_for_close_sale_list(business_branch,pos_profile): 
    working_day = get_current_working_day(business_branch)
    if working_day :

        cashier_shifts =  [{"name":'', "title":"All Cashier Shift"}]
        cashier_shifts = cashier_shifts + ( frappe.db.sql("select name, name as title from `tabCashier Shift` where working_day = '{}' and pos_profile = %(pos_profile)s order by name".format(working_day.name),{"pos_profile":pos_profile},as_dict=1))
        sale_types = [{"title":'All Sale Type',"name":""}]
        sale_types +=  frappe.db.sql("select name, name as title, color,is_order_use_table from `tabSale Type` order by sort_order",as_dict=1)
        # outlets = [{"title":'All Outlet',"name":""}]
        # outlets += frappe.db.sql("select name, name as title from `tabOutlet` where business_branch =  %(business_branch)s order by name", {"business_branch":business_branch},as_dict=1)
        table_groups =[{"title":'All Table Group',"name":""}]
        table_groups += frappe.db.sql("select name, name as title from `tabTable Group` where business_branch = %(business_branch)s order by name",{"business_branch":business_branch},as_dict=1)

        return {
        "working_day":working_day,
        "cashier_shift":get_current_cashier_shift(pos_profile),
        "cashier_shifts":cashier_shifts,
        "sale_types":sale_types,
        # "outlets":outlets,
        "table_groups":table_groups

        }
    return None




# get reservation folio
@frappe.whitelist()
def get_customer_on_membership_scan(card):
    # get customer map code
    cus =  frappe.db.exists("Customer",card)
    if cus:
        return frappe.get_doc("Customer",card) 
    else:
        membership = frappe.get_all('Customer Card',
								filters=[
                                    ['card_code','=',card]
                                ],
								fields=['parent','card_name','card_code','discount_type','discount','expiry'],
								limit=1
							 )
        if membership:
            ms = membership[0]
            customer = frappe.get_doc("Customer",ms["parent"]) 
            if customer:
                customer.card = customer.card
                return customer
            
    return {"Invalid Card"}


# get reservation folio
@frappe.whitelist()
def get_reservation_folio(property):
    room_types = frappe.db.get_list("Room Type",
                             filters=[["property",'=',property]],
                             limit=100,
                             fields=['name', 'room_type','sort_order'],
                            )


    folio = frappe.db.get_list("Reservation Folio",
                             filters=[['status','=', 'Open'], 
                                      ['reservation_status','=','In-house'] , 
                                      ['show_in_pos_transfer','=',1] , 
                                      ["property",'=',property]],
                             limit=500,
                             fields=[
                                 'name', 
                                 'room_types',
                                 "folio_type",
                                 "folio_type_color",
                                 'rooms',
                                 'reservation',
                                 'reservation_stay',
                                 'business_source',
                                 'guest_name',
                                 'guest',
                                 'phone_number',
                                 "is_master"
                                 ],
                            )
    for d in folio:
        d["id"] = d.name
        
    if frappe.db.get_single_value("ePOS Settings","allow_pos_user_to_create_guest_folio_when_transfer_bill_to_room")==1:
        # get all reservation that dont have folio
        sql ="select name as id, name as reservation_stay, room_types, rooms, reservation, guest_name,guest,guest_phone_number as phone_number,business_source from `tabReservation Stay` where reservation_status='In-house' and name not in %(stay_names)s"
        stays = frappe.db.sql(sql,{"stay_names": [d["reservation_stay"] for d in folio]},as_dict=1)
        folio = folio + stays
        room_types.append({"name":"Room with No Folio", "room_type":"Room with No Folio", "sort_order":1000000})
    
    data = {
        "folio_data":folio,
        "room_types":room_types
        }

    return data

@frappe.whitelist()
def get_inhouse_reservation(property):
    sql="select name, room_types,rooms,room_type_alias,business_source,guest_name from `tabReservation Stay` where reservation_status ='In-house' where property=%(property)s"
    data = frappe.db.sql(sql,{"property":property},as_dict=1)
    return data
    

@frappe.whitelist()
def get_current_customer_bill_counter(pos_profile):
    pos_config = frappe.db.get_value("POS Profile",pos_profile,"pos_config" )
    prefix =  frappe.db.get_value("POS Config",pos_config,"pos_bill_number_prefix" )
    prefix = prefix.replace(".","").replace("#","")
    data = frappe.db.sql("select * from `tabSeries` where name='{}'".format(prefix),as_dict=1)
    if data:
        return data[0]["current"]
    return 0

@frappe.whitelist(methods="POST")
def update_customer_bill_counter(pos_profile, counter):
    user= (frappe.session.data.user)
    pos_user_permission = frappe.get_cached_value("User", user, "pos_user_permission")
    if pos_user_permission:
        has_permission = frappe.get_cached_value("POS User Permission",pos_user_permission,"reset_custom_bill_number_counter" )
        if has_permission ==0:
            frappe.throw("You don't permission to reset counter")

    pos_config = frappe.get_cached_value("POS Profile",pos_profile,"pos_config" )
    prefix =  frappe.get_cached_value("POS Config",pos_config,"pos_bill_number_prefix" )
    prefix = prefix.replace(".","").replace("#","")
    frappe.db.sql("update  `tabSeries` set current={} where name='{}'".format(counter, prefix))
    frappe.db.commit()





@frappe.whitelist()
def on_sale_quick_pay(data):
    sales = json.loads(data)
    result = []
    for s in sales:
        doc =  frappe.get_doc('Sale',s['sale'])
        doc.append ('payment', {
                'payment_type':s['payment_type'],
                'input_amount':doc.grand_total,
                'amount':doc.grand_total
            })          
 
        doc.docstatus = 1
        doc.sale_status = 'Closed'
        doc.save()
        result.append(doc)
    frappe.db.commit()
    
    return result

@frappe.whitelist()
def on_sale_quick_pay_payment_type(data):
    sales = json.loads(data)

    result = []
    for s in sales:
        doc =  frappe.get_doc('Sale',s['sale'])
        doc.append ('payment', {
                'payment_type':s['payment_type'],
                'input_amount':doc.grand_total * s['additional_info'].get('exchange_rate'),
                'amount':doc.grand_total,
                'room_number':s['room_number'],
                'folio_number':s['folio_number'],
                'fee_amount':s['fee_amount'],
                'folio_transaction_type':s['folio_transaction_type'],
                'reservation_stay':s['reservation_stay'],
                'account_code':s['additional_info'].get('account_code') or '',
                "fee_percentage":s['additional_info'].get('fee_percentage'),
                "fee_amount":doc.grand_total * (s['additional_info'].get('fee_percentage') / 100)
            })          
 
        doc.docstatus = 1
        doc.sale_status = 'Closed'
        doc.save()
        result.append(doc)
    frappe.db.commit()
    
    return result



@frappe.whitelist()
def get_exchange_rate():
    
    main_currency = frappe.get_cached_value("ePOS Settings",None, "currency")
    exchange_rate_main_currency = frappe.get_cached_value("ePOS Settings",None, "exchange_rate_main_currency")

    second_currency = frappe.get_cached_value("ePOS Settings",None, "second_currency")
    if exchange_rate_main_currency == second_currency:
        second_currency  = main_currency
    
    
    data = frappe.db.sql("select exchange_rate  from `tabCurrency Exchange` where from_currency='{}' and to_currency='{}' and docstatus=1 order by posting_date desc, modified desc limit 1".format(exchange_rate_main_currency, second_currency),as_dict=1)
    exchange_rate = 1

    if len(data):
        exchange_rate = data[0]["exchange_rate"]    
    return exchange_rate or 1


# update sale payment of pos reservation 
@frappe.whitelist()
def update_pos_reservation_and_sale_payment(reservation_name,reservation_status,sale):
    ## update pos reservation
    _reservation = frappe.get_doc("POS Reservation",reservation_name)
    _reservation.reservation_status = reservation_status
    _reservation.status = reservation_status
    _reservation.save()

    # ## update sale payment
    _sale_payments = frappe.db.get_list("Sale Payment",
                                            filters={
                                                "docstatus": 1,
                                                "pos_reservation":reservation_name
                                                },
                                            fields=["name"]
                                        )
    
    for _sp in _sale_payments:
        _sale_payment = frappe.get_doc("Sale Payment",_sp["name"])
        _sale_payment.sale = sale
        _sale_payment.save()
    frappe.db.commit()



# @frappe.whitelist()
@frappe.whitelist(methods="POST")
def get_time_product_estimate_price(sp=None):
    return 10


@frappe.whitelist()
def upload_all_sale_data_to_google_sheet(business_branch,start_date,end_date,cashier_shift):
    
    google_account_credentials,google_sheet_file = frappe.db.get_value("Business Branch",business_branch,['google_account_credentials', 'google_sheet_file'])
    response = run(
			"Daily Sale Transaction Detail",
			filters={"start_date": start_date, "end_date": end_date,"cashier_shift":cashier_shift},
			
		)
    result = response.get("result")
    columns = response.get("columns")

    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(google_account_credentials))
    client = gspread.authorize(creds)
    sheet = client.open(google_sheet_file).sheet1
    
    if len(sheet.get_all_records()) <= 0:
        sheet.append_rows([[obj.label for obj in columns]])
    
    report_data = convert_to_nested_arrays(result,columns)
    return report_data
    resp = sheet.append_rows(report_data)
    sheet.format('A1:S1',{
        "backgroundColor": {
            "red": 0,
            "green": 128,
            "blue": 255
        }
    })
    # Append data to the Google Sheet


def convert_to_nested_arrays(json_data,columns):
    # data = json.loads(json_data)
   
    # Get the keys dynamically from the first entry
    
    if(len(json_data) > 0):
        keys = [{"fieldname": item["fieldname"], "fieldtype": item["fieldtype"]} for item in columns]
        result = [
            [
                format_datetime(
                    entry[key['fieldname']],
                    "dd-MM-yyyy hh:mm:ss a"
                ) if key['fieldtype'] == "Datetime" else
                format_datetime(
                    entry[key['fieldname']],
                    "dd-MM-yyyy"
                ) if key['fieldtype'] == "Date" else
                entry[key['fieldname']]
                for key in keys
            ]
    for entry in json_data
]
        
        return result
    else:
         return []

    # Extract values for each key in each entry
    
       

@frappe.whitelist()
def update_language():
    data = frappe.db.sql("select distinct language,source_text, translated_text from `tabTranslation`",as_dict=1)
    for lang in set([d["language"] for d in data]):
        if frappe.db.exists("POS Translation", lang):
            doc = frappe.get_doc("POS Translation", lang)
            translate_text =  json.loads( doc.translate_text or "{}")
            for d in [x for x in data if x["language"]==lang]:
                translate_text[d["source_text"]] = d["translated_text"]
            doc.translate_text = json.dumps(translate_text)
            doc.save()
    frappe.db.commit()
    
                
# get pos profile
@frappe.whitelist()
def get_pos_profiles():
    docs = frappe.db.sql("select `name` from `tabPOS Profile` where is_edoor_profile = 0", as_dict=1)
    return docs
    
# get pos profile
@frappe.whitelist(methods='POST')
def get_tables_groups_other_pos_profile(pos_profile):
    docs = frappe.db.sql("select * from `tabCashier Shift` where pos_profile = '{}' and is_closed = 0 and is_edoor_shift = 0".format(pos_profile), as_dict=1)
    result = None
    if len( docs) > 0:
        result = {
            "cashier_shift":docs[0],
            "table_groups":get_table_group_in_pos_profile(pos_profile)
        } 
    return result
    

 
@frappe.whitelist( methods='POST')
def get_table_group_in_pos_profile(pos_profile=""):
    profile = frappe.get_doc("POS Profile", pos_profile)
    table_groups = []
    for g in profile.table_groups:
        _group = frappe.get_doc("Table Group",g.table_group,fields=["photo","table_group_name_kh"])        
        table_groups.append({
            "key":g.table_group.lower().replace(" ","_"),
            "table_group":g.table_group,
            "table_group_kh":_group.table_group_name_kh,
            "background":_group.photo,
            "tables":get_tables_number(g.table_group, ""),#device_name = ''
            "search_table_keyword":""
            })
    return table_groups

@frappe.whitelist( methods='POST')
def change_table_between_outlet(sale, new_pos_profile,new_table_id):
 
    sale_doc = frappe.get_doc("Sale",sale)
    if sale_doc.docstatus !=0:
        frappe.throw(_("This sale order is not allow to change table"))
    
    cashier_shift_doc = get_cashier_shift_by_pos_profile(new_pos_profile)
    
    if not cashier_shift_doc:
        frappe.throw(_("This pos profile {} do not have cashier shift opened".format(new_pos_profile)))    
    if cashier_shift_doc.is_closed == 1:
        frappe.throw(_("This cashier shift {} is already closed".format(cashier_shift_doc.name)))
    
    sale_doc.outlet = cashier_shift_doc.outlet
    sale_doc.stock_location = frappe.db.get_value("POS Profile",new_pos_profile,"stock_location")
    sale_doc.table_id = new_table_id
    table_number,table_group= frappe.db.get_value("Tables Number",new_table_id, ["tbl_number","tbl_group"])
    sale_doc.tbl_number = table_number
    sale_doc.tbl_group =table_group
    sale_doc.pos_profile = new_pos_profile

  
    sale_doc.cashier_shift = cashier_shift_doc.name
    sale_doc.working_day = cashier_shift_doc.working_day
    sale_doc.shift_name = cashier_shift_doc.shift_name
    sale_doc.save()
    
    frappe.db.commit()
    
    return sale_doc

    
    
def get_cashier_shift_by_pos_profile(pos_profile):
    doc=frappe.get_last_doc("Cashier Shift", {"pos_profile":pos_profile,"is_closed":0}, "creation")
    return doc


## system ftp encrypt and decrypt code
@frappe.whitelist(allow_guest=1, methods='POST')
def generate_encrypt_ftp_auth_data(ftp_host,ftp_user,ftp_pass): 
    data ={"ftp_host":ftp_host,"ftp_user":ftp_user,"ftp_pass":ftp_pass}
    encrypt=aes_encrypt(json.dumps(data),get_aes_key("@dmin$ESTC#"))
    encrypt = encode_base64(encrypt)
    return encrypt

@frappe.whitelist(methods='POST')
def generate_decrypt_ftp_auth_data(ftp_auth_data):
    if frappe.session.user == 'Administrator':
        dycriptdata = ftp_auth_data
        dycriptdata = decode_base64(dycriptdata)
        dycriptdata =  aes_decrypt(dycriptdata, get_aes_key("@dmin$ESTC#")) 
        return dycriptdata
    return "Not allow to decypt"

@frappe.whitelist()
def get_workspace_sidebar_items():
    """Get list of sidebar items for desk"""
    has_access = "Workspace Manager" in frappe.get_roles()

    # don't get domain restricted pages
    blocked_modules = frappe.get_doc("User", frappe.session.user).get_blocked_modules()
    blocked_modules.append("Dummy Module")

    filters = {
        "restrict_to_domain": ["in", frappe.get_active_domains()],
        "module": ["not in", blocked_modules],
    }

    if has_access:
        filters = []

    # pages sorted based on sequence id
    order_by = "sequence_id asc"
    fields = [
        "name",
        "title",
        "for_user",
        "parent_page",
        "public",
        "module",
        "content",
        "icon",
        "indicator_color",
        "is_hidden",
        "custom_route",
        "custom_menu_icon"
    ]
    all_pages = frappe.get_all(
        "Workspace", fields=fields, filters=filters, order_by=order_by, ignore_permissions=True
    )
    pages = []
    private_pages = []

    # Filter Page based on Permission
    for page in all_pages:
        try:
            workspace = Workspace(page, True)
            if has_access or workspace.is_permitted():
                if page.public and (has_access or not page.is_hidden) and page.title != "Welcome Workspace":
                    pages.append(page)
                elif page.for_user == frappe.session.user:
                    private_pages.append(page)
                page["label"] = _(page.get("name"))
        except frappe.PermissionError:
            pass
    if private_pages:
        pages.extend(private_pages)

    if len(pages) == 0:
        pages = [frappe.get_doc("Workspace", "Welcome Workspace").as_dict()]
        pages[0]["label"] = _("Welcome Workspace")
   
    return {"pages": pages, "has_access": has_access}

@frappe.whitelist()
def update_cash_coupon_summary_to_customer(members):
    sql = """update `tabCustomer` c
            inner join (
                select 
                    cc.member,  
                    sum(cc.total_coupon) as total_coupon ,
                    sum(cc.total_claim) as total_claim,
                    sum(cc.total_amount) as total_amount,
                    sum(cc.total_balance) as total_balance,
                    sum(if(cc.unlimited=1, 0, if(cc.expiry_date > current_date(),0,cc.total_balance ))) as total_expired_balance
                from `tabCash Coupon` cc 
                where docstatus = 1 
                    and  member in %(member)s
                group by cc.member
            ) m on m.member = c.`name`
            set c.total_coupon = m.total_coupon,
                c.total_coupon_amount = m.total_amount,
                c.total_coupon_claim = m.total_claim,
                c.total_coupon_balance = m.total_balance - m.total_expired_balance,
                c.total_coupon_balance_expired = m.total_expired_balance
            where member in %(member)s"""
    
    frappe.db.sql(sql,{"member":members})

@frappe.whitelist()
def update_summary_to_customers():
    ## update expired crypto balance
    frappe.db.sql("""update `tabCustomer` c
    inner join (
    select 
        m.customer
		coalesce(sum(m.crypto_balance ),0) as total_crypto_balance
	from `tabMembership` m 
	where m.docstatus = 1
	and m.end_date <  CURRENT_DATE()
    group by m.customer) _c on c.name = _c.customer
    set c.total_crypto_balance_expired = _c.total_crypto_balance
    """)

    sql = """update `tabCustomer` c
        inner join (
            select 
                cc.member,  
                sum(cc.total_coupon) as total_coupon ,
                sum(cc.total_claim) as total_claim,
                sum(cc.total_amount) as total_amount,
                sum(cc.total_balance) as total_balance,
                sum(if(cc.unlimited=1, 0, if(cc.expiry_date > current_date(),0,cc.total_balance ))) as total_expired_balance
            from `tabCash Coupon` cc 
            where docstatus = 1 
            group by cc.member
        ) m on m.member = c.`name`
        set c.total_coupon_balance_expired = m.total_expired_balance """
    
    frappe.db.sql(sql)


@frappe.whitelist()
def scan_coupon_number(code):
    sql = "select balance, unlimited, expiry_date from `tabCash Coupon Items` where docstatus = 1 and code = %(code)s limit 1"
    docs = frappe.db.sql(sql,{"code":code}, as_dict=1) 
    
    result = {}
    if len( docs) > 0: 
        if docs[0]["unlimited"] == 0 and docs[0]["expiry_date"]  < datetime.now().date() :
             result.update ({
                "status":0,
                "code":code,
                "balance": 0,
                "message":"Coupon code was expired"
            })
        else:
            if  docs[0]["balance"] <= 0 :
                     result.update( {
                    "status":0,
                    "code":code,
                    "balance": 0,
                    "message":"This coupon not enough balance"
                })
            else:
                result.update( {
                    "status":1,
                    "code":code,
                    "balance": docs[0]["balance"],
                    "message":"Success"
                })
    else:

        sale_coupon_sql = "select cash_coupon_balance as balance, 0 as unlimited, end_date as expiry_date from `tabSale Coupon` where cash_coupon_balance > 0 and docstatus = 1 and  coupon_number = %(code)s limit 1"
        sale_coupon = frappe.db.sql(sale_coupon_sql,{"code":code},as_dict = 1 )
        
        if len(sale_coupon)>0:
             result.update ({
                "status":1,
                "code":code,
                "balance": sale_coupon[0]["balance"],
                "message":"Success"
            })
        else:
            result.update ({
                "status":0,
                "code":code,
                "balance": 0,
                "message":"Invalid coupon code"
            })

    return result


## Validate Sale Network Lock
@frappe.whitelist(methods='POST')
def validate_sale_network_lock(param): 
    sql  = """select sale,table_id, name,pos_station from `tabSale Network Lock` where table_id = %(table_id)s and pos_station != %(pos_station)s and pos_profile = %(pos_profile)s"""
    data = frappe.db.sql(sql,param,as_dict=1)     
    result = {} 
    if len(data) > 0 : 
        if "sale" in [k for k in param.keys()]:
            if param["sale"] in [s["sale"] for s in data]:
                result = {"status":0,"message":"There is an other station actived"}

        else:
            result = {"status":0,"message":"There is an other station actived"}
        
    else:
        result = {"status":1,"message":"This table will lock for other station"}  


    return result

@frappe.whitelist(methods='POST')
def create_sale_network_lock(param):
        sql  = """select sale,table_id, name,pos_station from `tabSale Network Lock` where table_id = %(table_id)s and pos_station = %(pos_station)s and pos_profile = %(pos_profile)s"""
        data = frappe.db.sql(sql,param,as_dict=1) 
        create_doc = False
        if len(data) <=0:
            create_doc = True
            
        else:  
            if "sale" in [k for k in  param.keys()] : 
                if param["sale"] not in [s["sale"] for s in data]:
                    if param["table_id"] not in [s["table_id"] for s in data]:
                        create_doc = True
            else: 
                if param["table_id"] not in [s["table_id"] for s in data]:
                    create_doc = True
                    
        if create_doc:
            doc_data =  { 'doctype': 'Sale Network Lock'}    
            doc_data.update(param)
            doc = frappe.get_doc(doc_data)
            doc.insert()

@frappe.whitelist(methods='POST')
def reset_sale_network_lock(param):
    tbl = "1 = 1 "
    sql  = """delete from `tabSale Network Lock` where {} and pos_station = %(pos_station)s and pos_profile = %(pos_profile)s""".format(tbl)
    frappe.db.sql(sql,param,as_dict=1) 

    return "reset sale network lock"

@frappe.whitelist(methods='POST')
def reset_sale_network_lock_by_sale(old_sale, new_sale): 
    _sale = " 1 = 1 "
    if old_sale != "":
        _sale += "and sale = %(sale)s"
    sql  = """delete from `tabSale Network Lock` where {} and table_id = %(table_id)s and pos_station = %(pos_station)s and pos_profile = %(pos_profile)s""".format(_sale)
    frappe.db.sql(sql,{"sale":old_sale,
                       "table_id":new_sale["table_id"] ,
                       "pos_station": new_sale["pos_station"],
                       "pos_profile": new_sale["pos_profile"]
                       },as_dict=1) 
    if new_sale:
        create_sale_network_lock(new_sale)


    return "reset sale network lock"

