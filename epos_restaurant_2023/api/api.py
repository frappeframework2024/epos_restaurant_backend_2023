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
from epos_restaurant_2023.api.exely import cancel_order,submit_order_to_exely
from frappe.model.rename_doc import get_link_fields

import re
from urllib.parse import urljoin


def remove_key(data, keys= None):
    if keys is None:
        keys = ["owner", "creation", "modified", "modified_by", "docstatus", "idx","_user_tags","_comments","_assign","_liked_by"]
    
    if isinstance(data, dict):
        return {
            k: remove_key(v, keys) if isinstance(v, (dict, list)) else v
            for k, v in data.items() if k not in keys
        }

    elif isinstance(data, list):
        return [remove_key(item, keys) for item in data]



@frappe.whitelist()
def test():
    return frappe.format(91.145,{"fieldtype":"Currency"})

@frappe.whitelist("POST")
def rename_doc(data):
    doc = frappe.rename_doc(data['doctype'], data['old_name'], data['new_name'])
    if doc:
        return {
            'name': data['new_name']
        }
    
@frappe.whitelist(allow_guest=True)
def get_field(doctype):
    return str(get_link_fields(doctype))



@frappe.whitelist(allow_guest=True)
def get_ip():
    
    return (
        frappe.local.request.headers,
        frappe.local.request_ip,
        frappe.request.remote_addr,
        frappe.request.headers.get('X-Forwarded-For'),
        get_client_ip()
        )
def get_client_ip():
    forwarded_for = frappe.get_request_header('X-Forwarded-For')
    if forwarded_for:
        # Split the list of forwarded IPs and return the first one (client IP)
        ip = forwarded_for.split(',')[0].strip()
    else:
        # Fallback to REMOTE_ADDR if X-Forwarded-For is not present
        ip = frappe.get_request_header('REMOTE_ADDR')
    return ip


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

@frappe.whitelist()
def get_product(name):
    datas = frappe.db.sql("select unit from `tabProduct` where name = '{0}'".format(name),as_dict=1)
    if datas:
        return datas[0]


@frappe.whitelist(allow_guest=True)
def check_username(pin_code):    
    
    if pin_code:    
        pin_code = (str( base64.b64encode(pin_code.encode("utf-8")).decode("utf-8")))
        users = frappe.db.sql("select user_id, pos_permission from `tabEmployee` where pos_pin_code = %(pin_code)s and allow_login = 1 and allow_login_to_epos = 1 limit 1", {"pin_code":pin_code}, as_dict = 1)
        if users:
            data = frappe.db.sql("select name,full_name,user_image from `tabUser` where name=%(name)s limit 1",{"name":users[0].user_id},as_dict=1)
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

    users = frappe.db.sql("select user_id, pos_permission from `tabEmployee` where user_id = %(user_id)s ",{"user_id":name}, as_dict = 1)
    if users:
        data = frappe.db.sql("select name,full_name,user_image,role_profile_name from `tabUser` where name=%(name)s",{"name":name},as_dict=1)
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
        if not _group.disabled :
            table_groups.append({
                "key":g.table_group.lower().replace(" ","_"),
                "table_group":g.table_group,
                "table_group_kh":_group.table_group_name_kh,
                "background":_group.photo,
                "tables":get_tables_number(table_group= g.table_group,device_name= device_name, pos_profile= pos_profile),
                "search_table_keyword":""
                })
    pos_menus = []
    for m in profile.pos_menus:
        pos_menus.append({"pos_menu":m.pos_menu})   
    
    #main currency information
    main_currency = frappe.get_doc("Currency",frappe.db.get_default("currency"))
    second_currency = frappe.get_doc("Currency",frappe.db.get_default("second_currency"))
    exchange_rate_main_currency = frappe.db.get_default("exchange_rate_main_currency")

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
            "is_voucher":p.is_voucher,
            "allow_cash_float":p.allow_cash_float, 
            "allow_aba_pay_with_qr_scan":p.allow_aba_pay_with_qr_scan, 
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
    

    to_currency = second_currency.name
    if (exchange_rate_main_currency != main_currency.name):
        to_currency = main_currency.name  

    #get exchange rate
    exchange_rate = frappe.db.sql("""select 
                                        posting_date,
                                        exchange_rate,
                                        exchange_rate_input,
                                        change_exchange_rate,
                                        change_exchange_rate_input 
                                    from `tabCurrency Exchange` 
                                    where docstatus=1 
                                    and from_currency= %(from_currency)s
                                    and to_currency=%(to_currency) s
                                    order by posting_date desc
                                    limit 1""",{
                                        "from_currency":exchange_rate_main_currency,
                                        "to_currency":to_currency,
                                    }, as_dict= 1)

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
        "exchange_rate_main_currency":exchange_rate_main_currency,
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
        "allow_tip_revenue_group":doc.allow_tip_revenue_group,
        "specific_pos_profile":doc.specific_pos_profile,
        "backend_port":doc.backend_port,
        "use_backend_port":doc.use_backend_port,
        "customer_display_slideshow": pos_branding.customer_display_slideshow,
        "thank_you_message":pos_branding.thank_you_message,
        "cancel_print_bill_required_password":pos_config.cancel_print_bill_required_password,
        "cancel_print_bill_required_note":pos_config.cancel_print_bill_required_note,
        "free_item_required_password":pos_config.free_item_required_password,
        "return_product_required_note":pos_config.return_product_required_note,
        "apply_foc_required_password":pos_config.apply_foc_required_password,
        "apply_foc_required_note":pos_config.apply_foc_required_note,
        "return_product_required_password":pos_config.return_product_required_password,
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
        "require_password_for_submitted_sale":0,
        "require_password":0,
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
        "allow_print_bill_on_sale_deleted":pos_config.allow_print_bill_on_sale_deleted,
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
        "allow_negative_stock":doc.allow_negative_stock,
        "is_client_side_sync_setting":(epos_sync_setting.client_side or 0),
        "park_item_days_expiry":pos_config.park_item_days_expiry,
        "apply_rate_include_tax_required_password":pos_config.apply_rate_include_tax_required_password,
        "apply_rate_include_tax_required_note":pos_config.apply_rate_include_tax_required_note,
        "manual_percent_discount_required_password":pos_config.manual_percent_discount_required_password,
        "show_preview_report": pos_config.show_preview_report,
        "show_system_closed_amount": pos_config.show_system_closed_amount,
        "combo_menu_print_captain_by_items_printer": pos_config.combo_menu_print_captain_by_items_printer,
        "overwrite_voucher_minimum_amount_required_password": pos_config.overwrite_voucher_minimum_amount_required_password,
        "show_term_on_submit": pos_config.show_term_on_submit,
        "show_voucher_minimum_overwrite": pos_config.show_voucher_minimum_overwrite,
        }
    def create_default_customer():
        if not frappe.db.exists("Customer", "General"):
            if not frappe.db.exists("Customer Group", "General"):
                a = frappe.new_doc("Customer Group")
                a.customer_group_en = "General"
                a.customer_group_kh = "General"
                a.save()
            b = frappe.new_doc("Customer")
            b.customer_code = "General"
            b.customer_name_en = "General"
            b.customer_name_kh = "General"
            b.customer_group = "General"
            b.save()

            doc = frappe.get_doc("POS Profile", profile.name)
            doc.default_customer = "General"
            doc.save()
            
            return b
        else:
            doc = frappe.get_doc("POS Profile", profile.name)
            doc.default_customer = "General"
            doc.save()
            return frappe.get_doc("Customer", "General")
    #get default customre
    default_customer = None
    if (profile.default_customer or "") != "":
        if frappe.db.exists("Customer", profile.default_customer):
            default_customer = frappe.get_doc("Customer", profile.default_customer)
        else:
            default_customer = create_default_customer()
    else:
         default_customer = create_default_customer()
        
    #get default print format
    _pos_print_format = frappe.get_list("POS Print Format Setting",fields=[
        "name",
        "business_branch",
        "title",
        "print_format_doc_type",
        "pos_receipt_template",
        "invoice_template_by_seat_number",
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
        "boldreport_report_id",
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
                "invoice_template_by_seat_number":p.invoice_template_by_seat_number,
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
                "boldreport_report_id":p.boldreport_report_id
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
    socket_port =  frappe.get_conf().get('websocket_port', 3000)   

    bus = frappe.get_doc("Business Branch", p["business_branch"])
    property_code = bus.property_code

    data={
        "app_name":doc.epos_app_name,
        "specific_business_branch":doc.specific_business_branch,
        "specific_pos_profile":doc.specific_pos_profile,
        "business_branch":profile.business_branch,
        "pos_config":pos_config.name,
        "address":pos_config.address,
        "property_code":property_code,
        "payway_prefix_code":pos_config.payway_prefix_code or "",
        "logo":pos_branding.logo,
        "phone_number":pos_config.phone_number,
        "pos_profile":pos_profile,
        "outlet":profile.outlet,
        "use_retail_ui":profile.use_retail_ui,
        "use_menu_retail":profile.use_menu_retail,
        "base_unit_popup":profile.base_unit_popup,
        "close_business_day_on":pos_config.close_business_day_on,
        "alert_close_working_day_after":pos_config.alert_close_working_day_after,
        "menu_waiting_time":pos_config.menu_waiting_time,
        "maximum_order_per_guest":pos_config.maximum_order_per_guest,
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
        "allow_print_bill_on_sale_deleted":pos_config.allow_print_bill_on_sale_deleted,
        "print_sale_product_merged_table":pos_config.print_sale_product_merged_table,
        "print_sale_product_change_table":pos_config.print_sale_product_change_table,
        "print_sale_product_move_item":pos_config.print_sale_product_move_item,
        "pos_sale_order_background_image":pos_branding.pos_sale_order_background_image,
        "show_item_code_in_sale_screen":pos_config.show_item_code_in_sale_screen,
        "show_button_tip":pos_config.show_button_tip,
        "tip_account_code":pos_config.tip_account_code,
        "show_time_ago_on_table":pos_config.show_time_ago_on_table,
        "show_total_amount_on_table":pos_config.show_total_amount_on_table,
        "shift_types":shift_types,
        "currencies":currencies,
        "default_currency":frappe.db.get_default("currency"),
        "currency_exchange":exchange_rate[0],
        "pos_setting":pos_setting,
        "customer":default_customer.name,
        "customer_name":default_customer.customer_name_en,
        "customer_photo":default_customer.photo,
        "customer_group":default_customer.customer_group,
        "customer_default_discount": default_customer.default_discount,
        "default_sale_type":profile.default_sale_type,
        "default_payment_type":profile.default_payment_type,
        "default_pos_receipt":default_pos_receipt,
        "second_currency_payment_type":profile.second_currency_payment_type,
        "price_rules":price_rules,
        "lang": lang,
        "reports":reports,
        "letter_heads":letter_heads,
        "device_setting":pos_station, 
        "socket_port":socket_port,
        "shortcut_key":shortcut_keys,
        "exely":{
            "enabled":exely.enabled, "default_general_customer_id":exely.default_general_customer_id, "guest_api_endpoint":exely.guest_api_endpoint,"api_key":exely.api_key
        },
        "point_setting":point_setting,
        "change_table_previous_date":pos_config.change_table_previous_date,
        "allow_change_table_after_print_bill":pos_config.allow_change_table_after_print_bill
    }

    estc_connecton = get_estc_connection()
    data = {**data, **estc_connecton }
 
    return  data


@frappe.whitelist(allow_guest=True)
def get_tables_number(table_group,device_name, pos_profile):
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
                            0 as x_percent,
                            0 as y_percent,
                            price_rule,
                            tbl_group,
                            discount_type,
                            new_sale_default_pos_menu,
                            submitted_default_pos_menu,
                            font_size
                         from `tabTables Number` 

                         where tbl_group=%(group)s
                         and disabled = 0
                         order by 
                         sort_order, 
                         tbl_number""",{"group":table_group}, as_dict=1)

    background_color = frappe.db.get_default("default_table_number_background_color")
    text_color = frappe.db.get_default("default_table_number_text_color")
    i = 0
    x = 5
    y = 5 
    for d in data:
        d.background_color=background_color
        d.default_bg_color=background_color
        d.text_color = text_color
        d.default_text_color = text_color
        position = frappe.db.sql("select x,y,h,w,x_percent,y_percent from `tabePOS Table Position` where pos_profile = %(pos_profile)s and device_name=%(device_name)s and table_id=%(table_id)s limit 1",{"device_name":device_name,"table_id":d.id,"pos_profile":pos_profile }, as_dict=1)
        if position:
            for p in position:
                d.x = p.x or x
                d.y = p.y or y 
                d.w = p.w or 100
                d.h = p.h or 100
                d.x_percent = p.x_percent or 0
                d.y_percent = p.y_percent or 0
        else:
            d.x = x
            d.y = y 

        i += 1 
        x += (d.w +5)
        if i >=10:
            x = 5
            y += (d.h + 5)
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

        frappe.db.sql("update `tabPOS Station` set is_used = 1 where name = %(name)s",{"name":device_name})
        
        frappe.db.commit()
    return station


@frappe.whitelist()
def get_current_working_day(business_branch = ""):
    if business_branch != "":
        sql = "select name, posting_date, pos_profile, note from `tabWorking Day` where business_branch = %(business_branch)s and is_closed = 0 order by creation limit 1"
        data =  frappe.db.sql(sql, {"business_branch":business_branch},as_dict=1) 
        if data:
            return data [0]
        else:
            return None
    else:
        return None

@frappe.whitelist()
def get_current_cashier_shift(pos_profile=""):
    if (pos_profile or "") != "":
        sql = "select name,working_day, posting_date,shift_name, pos_profile, opened_note,business_branch,total_opening_amount from `tabCashier Shift` where pos_profile = %(pos_profile)s and is_closed = 0 order by creation desc limit 1"
        data =  frappe.db.sql(sql, {"pos_profile":pos_profile},as_dict=1) 
        if data:
            return data [0]
        else:
            return None
    else:
        return None

@frappe.whitelist()
def get_current_shift_information(business_branch="", pos_profile=""):
    if (business_branch or "") == "":
        branches = (frappe.db.get_list('Business Branch') or [])
        if len(branches) == 1:
            business_branch = branches[0].name
    if (pos_profile or "") == "":
        profiles = (frappe.db.get_list('POS Profile') or [])
        if len(profiles) == 1:
            pos_profile = profiles[0].name
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
    deleted_sql = """select sum(if(docstatus=2,1,0)) as total_receipt_deleted from `tabSale` {}""".format("where deleted_type is null and " + sql_deleted_query)
     
    data_deleted = frappe.db.sql(deleted_sql,as_dict=1) 
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
                property=%(property)s and 
                arrival_date between '{0}' and '{1}'
            order by arrival_time
            """.format(getdate(start),getdate(end))
    data = frappe.db.sql(sql,{"property":business_branch}, as_dict=1)
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
def save_table_position(device_name,pos_profile, table_group):
    # frappe.throw("{}".format(table_group))
    frappe.db.sql("delete from `tabePOS Table Position` where  device_name=%(name)s and pos_profile = %(pos_profile)s",{"name":device_name, 'pos_profile':pos_profile} )    
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

            x_percent = 0
            if "x_percent" in t:
                x_percent = t["x_percent"]

            y_percent = 0
            if "y_percent" in t:
                y_percent = t["y_percent"]

            if not frappe.db.exists('ePOS Table Position', {'table_id': t['id'], 'device_name': device_name , 'pos_profile':pos_profile }):
                doc = frappe.get_doc({
                        'doctype': 'ePOS Table Position',
                        'device_name':device_name,
                        'pos_profile':pos_profile,
                        'tbl_number': t['tbl_no'],
                        'table_group':g["table_group"],
                        'table_id':t['id'],
                        'font_size':t['font_size'],
                        'x':x,
                        'y':y,
                        'h':h,
                        'w':w,
                        "x_percent":x_percent,
                        "y_percent":y_percent
                    })
                doc.insert()

@frappe.whitelist()
def get_pos_print_format(doctype,business_branch=None):  
    # pos_print_format =  
    sql = """select 
                name,
                title,
                pos_receipt_template,
                invoice_template_by_seat_number,
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
            where print_format_doc_type= %(doctype)s
            and show_in_pos = 1 """
    if business_branch:
        sql += " and business_branch = %(business_branch)s" 
        data = frappe.db.sql(sql,{"business_branch":business_branch,"doctype":doctype}, as_dict=True)  
    else:
        data =   frappe.db.sql(sql,{"doctype":doctype}, as_dict=True)  
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
def get_allow_cash_float_payment_type(pos_profile):
    profile = frappe.get_doc("POS Profile",pos_profile)
    data = frappe.db.sql("select payment_type from `tabPOS Config Payment Type` where parent = '{}' and allow_cash_float = 1".format(profile.pos_config),as_dict=1)
    return [a["payment_type"] for a in data]


@frappe.whitelist()
def get_close_shift_summary(cashier_shift="", show_system_closed_amount = 1):
    if not cashier_shift:
        cashier_shift = "CS2025-0001"
    data = []
    doc = frappe.get_doc("Cashier Shift",cashier_shift)
    
    #get close amount by payment type
    sql = """select payment_type, currency,
            sum(input_amount + (fee_amount * exchange_rate)) as input_amount, 
            sum(payment_amount + fee_amount) as payment_amount 
        from `tabSale Payment` 
        where cashier_shift=%(cashier_shift)s 
        and docstatus=1 
        group by 
        payment_type, 
        currency"""
    voucher_payment_sql = """SELECT 
                                payment_type, 
                                exchange_rate,
                                currency,sum(input_amount) as input_amount, 
                                sum(payment_amount) as payment_amount from `tabVoucher Payment` 
                            WHERE 
                                cashier_shift=%(cashier_shift)s and 
                                docstatus=1 
                            group BY 
                                payment_type,
                                currency"""

    
    payments = frappe.db.sql(sql,{"cashier_shift":cashier_shift}, as_dict=1)
    voucher_payments = frappe.db.sql(voucher_payment_sql,{"cashier_shift":cashier_shift}, as_dict=1)
    
    
    #get cash in out 
    sql = """select  
                payment_type,
                exchange_currency,
                currency,
                sum(if(transaction_status='Cash Out',input_amount*-1,input_amount)) as total_input_amount, 
                sum(if(transaction_status='Cash Out',amount*-1,amount)) as total_amount 
            from `tabCash Transaction`   
            where cashier_shift=%(cashier_shift)s
            group by  
                payment_type,
                currency,
                exchange_currency"""
 
    cash_transactions = frappe.db.sql(sql,{"cashier_shift":cashier_shift}, as_dict=1)
    

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

    # coupon payment
    coupon_payments= frappe.db.sql("""
                                select 
                                    spt.payment_type as payment_method,
                                   spt.exchange_rate,
                                   0 as input_amount, 
                                   0 as opening_amount,
                                    0 as input_close_amount,
                                   sum(spt.input_amount * -1) as input_system_close_amount, 
                                   sum(spt.payment_amount *-1) as system_close_amount, 
                                   0 as different_amount, 
                                   spt.currency 
                                from `tabStore Payment Type` spt
                                   inner join `tabStore Payment` sp on sp.name = spt.parent
                                where
                                    sp.cashier_shift = %(cashier_shift)s and
                                    sp.docstatus = 1 
                                group by
                                    spt.payment_type,
                                    spt.exchange_rate,
                                    spt.currency

        """,{"cashier_shift":cashier_shift},as_dict=1)
    
    data.extend(coupon_payments)

    
        
    return get_cash_float(data, show_system_closed_amount)

#get cash float sum group by
def get_cash_float(data,show_system_closed_amount = 1):
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
                "input_close_amount": (total_input_system_close_amount or 0) if show_system_closed_amount == 1 else 0 ,##total_input_close_amount or 0,
                "input_system_close_amount": total_input_system_close_amount or 0,
                "system_close_amount": total_system_close_amount or 0,
                "different_amount": total_different_amount or 0
            })	
            
		result.append(_result)
           
	return result


@frappe.whitelist()
def get_payment_cash(cashier_shift):
    sql = "select payment_type, currency, SUM(payment_amount) as payment_amount from `tabSale Payment` where cashier_shift=%(cashier_shift)s AND payment_type_group = 'Cash' and docstatus=1 group by payment_type, currency"
    data = frappe.db.sql(sql,{"cashier_shift":cashier_shift}, as_dict=1)
    return data
@frappe.whitelist()
def get_cash_drawer_balance(cashier_shift):
    sql_system_amount = "SELECT COALESCE( SUM(payment_amount),0) AS total_amount_cash FROM `tabSale Payment` where cashier_shift=%(cashier_shift)s AND payment_type_group = 'Cash' and docstatus=1"
    sql_opening_amount = "SELECT total_opening_amount FROM `tabCashier Shift` WHERE name = %(cashier_shift)s"
    sql_cash_out = "SELECT COALESCE( SUM(amount), 0) AS total_amount_cash_out FROM `tabCash Transaction` WHERE cashier_shift = %(cashier_shift)s AND transaction_status = 'Cash Out'"
    sql_cash_in = "SELECT COALESCE( SUM(amount), 0) AS total_amount_cash_in FROM `tabCash Transaction` WHERE cashier_shift = %(cashier_shift)s AND transaction_status = 'Cash In'"
    
    data_system_amount = frappe.db.sql(sql_system_amount,{"cashier_shift":cashier_shift}, as_dict=1)
    total_amount_cash = data_system_amount[0].total_amount_cash
    data_opening_amount = frappe.db.sql(sql_opening_amount,{"cashier_shift":cashier_shift}, as_dict=1)
    total_opening_amount = data_opening_amount[0].total_opening_amount
    data_cash_in = frappe.db.sql(sql_cash_in, {"cashier_shift":cashier_shift}, as_dict=1)
    total_amount_cash_in = data_cash_in[0].total_amount_cash_in
    data_cash_out = frappe.db.sql(sql_cash_out,{"cashier_shift":cashier_shift},  as_dict=1)
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
            table_id,
            seat_number,
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
            table_id,
            seat_number,
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
        where pos_profile = %(pos_profile)s
        and docstatus = 0"""
        result = frappe.db.sql(sql,{"pos_profile":data["pos_profile"]},as_dict=1)
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
        seat_number,
        tbl_group,
        tbl_number,
        table_id,
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
        "cashier_shift":data.get("cashier_shift","")
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


@frappe.whitelist(methods="POST")
def edit_sale_coupon(name,auth):  
    if isinstance(name, str):
        auth = json.loads(auth)
    sale = frappe.db.exists("Sale", name)
    if not sale:
        frappe.throw(_("Sale not found"))
    sale_doc = frappe.get_doc("Sale",name)
    # check if cashier is already closed
    if sale_doc.cashier_shift:
        if frappe.get_value("Cashier Shift",sale_doc.cashier_shift,"is_closed") == 1:
            frappe.throw(_("Cashier shift is already closed"))
            
    if sale_doc.docstatus == 2:
        frappe.throw(_("Sale is already deleted"))

    sale_coupons = check_coupon_transactions(sale_doc,"edit")
     
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
    #check if sale already have payment then cancel sale payment first
    payments = frappe.get_list("Sale Payment",fields=["name"], filters={"sale":name,"docstatus":1})
    for p in payments:
        sale_payment = frappe.get_doc("Sale Payment", p.name)
        sale_payment.cancel()
        sale_payment.delete()
    
    #then start to cancel sale
    payments = copy.deepcopy(sale_doc.payment)
    for p in [d for d in payments if d.folio_transaction_number and d.folio_transaction_type and  not d.cancel_order_adjustment_account_code]:
        frappe.throw("There is no cancel order adjustment account code for payment type {}. Please config it in POS Config Setting.".format(p.payment_type))
    sale_doc.cancel()
    
    #change status from 2 to 0 (Cancel to Draft) to allow pos can modified this doc
    sale_status_doc = frappe.get_doc("Sale Status","Submitted")
    sale_sql = "update `tabSale` set docstatus = 0, sale_status='Submitted', sale_status_color='{0}', sale_status_priority={1},balance=grand_total,total_paid_with_fee=0,total_paid=0 where name=%(name)s".format(sale_status_doc.background_color,sale_status_doc.priority)
    sale_product_sql = "update `tabSale Product` set docstatus = 0 where parent=%(parent)s"
    frappe.db.sql(sale_sql, {"name":name})
    frappe.db.sql(sale_product_sql,{"parent":name})          


    # delete coupon transaction 
    sql = "delete from `tabCoupon Transaction` where coupon_code in %(coupon_codes)s and sale=%(sale)s"
    frappe.db.sql(sql,{"sale":sale_doc.name, "coupon_codes":[d.get("name") for d in sale_coupons]})

    # update coupon code, change status = Unused, sale = ""
    sql = """update `tabCoupon Codes` set coupon_status = 'Unused',sale='',price=0,coupon_value=0,sale_date=null,working_day='',cashier_shift='',pos_profile='',pos_station='',created_by='',customer='',customer_name='' 
        where name in %(coupon_codes)s
    """
    frappe.db.sql(sql,{ "coupon_codes":[d.get("name") for d in sale_coupons]})



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

    return "Success"

@frappe.whitelist()
def delete_sale_coupon(name,auth):
    if isinstance(auth, str):
        auth = json.loads(auth)

    sale = frappe.db.exists("Sale", name)
    if not sale:
        frappe.throw(_("Sale not found"))
    sale_doc = frappe.get_doc("Sale",name)
    if sale_doc.docstatus == 2:
        frappe.throw(_("Sale is already deleted"))
    sale_coupons = check_coupon_transactions(sale_doc,"delete")
    sale_amount = sale_doc.grand_total

    #check if sale already have payment then cancel sale payment first
    payments = frappe.get_list("Sale Payment",fields=["name"], filters={"sale":name,"docstatus":1})
    for p in payments:
        sale_payment = frappe.get_doc("Sale Payment", p.name)
        sale_payment.cancel()
        sale_payment.delete()
    
    #then start to cancel sale
    if sale_doc.docstatus ==1:
        _sale = frappe.get_doc("Sale",name)
        _sale.db_set('deleted_by', auth["full_name"])
        _sale.db_set('deleted_note', auth["note"])
        _sale.reload()
        sale_doc = frappe.get_doc("Sale",name)
        sale_doc.cancel()
    else:        
        frappe.db.sql("update `tabSale` set docstatus = 2,deleted_by=%(deleted_by)s,deleted_note=%(deleted_note)s  where name=%(name)s",{"name":name,"deleted_by":auth["full_name"],"deleted_note":auth["note"]})
        frappe.db.sql("update `tabSale Product` set docstatus = 2 where parent=%(parent)s",{"parent":name})

    #update coupon status
    frappe.db.sql("update `tabCoupon Transaction` set status='Deleted' where sale=%(sale)s",{"sale":name})
    frappe.db.sql("update `tabCoupon Codes` set coupon_status='Unused' where name in %(coupon_codes)s",{"coupon_codes":[d["name"] for d in sale_coupons]})

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
    return "Done" 

@frappe.whitelist()
def check_coupon_transactions(sale,action):
    #check coupon transactions
    if sale.docstatus == 2:
        frappe.throw("Sale is already deleted")
    from datetime import datetime
    sale_coupons = []   
    #get coupon from sale product
    for a in sale.sale_products:
        if a.coupons:
            for b in json.loads(a.coupons):
                sale_coupons.append(b)
  
    if len(sale_coupons) > 0:
        #get coupon transactions from coupon
        coupon_transactions = []
        transactions = frappe.db.sql("select name,modified,coalesce(sale,'no_sale') sale,coupon_code,coupon_number,transaction_date,coupon_amount from `tabCoupon Transaction` where coalesce(sale,'') <> %(sale)s and transaction_type != 'Sale Coupon' and status in ('Active','Locked') and coupon_code in %(coupon_codes)s",{"sale":sale.name,"coupon_codes":[d["name"] for d in sale_coupons]},as_dict=1)
        for b in transactions:
            b["modified"] = b["modified"].strftime("%Y-%m-%d %H:%M:%S")
            b["transaction_date"] = b["transaction_date"].strftime("%Y-%m-%d %H:%M:%S")
            coupon_transactions.append(b)
        #get later transactions from coupon transactions
        later_transactions = []
        for a in coupon_transactions:
            if datetime.strptime(a["modified"], "%Y-%m-%d %H:%M:%S") > sale.modified:
                later_transactions.append(a)

        #return error if later transactions found
        if len(later_transactions) > 0:
            str_sale = ",".join([d["name"] if d["sale"] == "no_sale" else d["sale"] for d in later_transactions])
            if action == "delete":
                frappe.throw(_("Can not delete sale coupon already used in {}".format(str_sale)))
            else:
                frappe.throw(_("Can not edit sale coupon already used in {}".format(str_sale)))
        return sale_coupons

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
    if sale_doc.docstatus ==1:
        _sale = frappe.get_doc("Sale",name)
        _sale.db_set('deleted_by', auth["full_name"])
        _sale.db_set('deleted_note', auth["note"])
        _sale.reload()
        
        sale_doc = frappe.get_doc("Sale",name)
        sale_doc.cancel()
        
    else:        
        frappe.db.sql("update `tabSale` set docstatus = 2,deleted_by=%(deleted_by)s,deleted_note=%(deleted_note)s  where name=%(name)s",{"name":name,"deleted_by":auth["full_name"],"deleted_note":auth["note"]})
        frappe.db.sql("update `tabSale Product` set docstatus = 2 where parent=%(parent)s",{"parent":name})
    
    #update sale product spa deleted
    query = "update `tabSale Product SPA Commission` set is_deleted = 1  where sale = %(sale)s"
    frappe.db.sql(query, {"sale":name})

    # sale check if from pos reservation update status
    if sale_doc.from_reservation:
        if frappe.db.exists("POS Reservation", sale_doc.from_reservation):
            frappe.db.sql("update `tabPOS Reservation` set workflow_state='Confirmed' where name=%(name)s",{"name":sale_doc.from_reservation})
            
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
        cancel_order(transaction_id = sale_doc.exely_transaction_id, sale = sale_doc.name, comment = auth["note"])

    return "Done" 

@frappe.whitelist()
def edit_sale_order(name,auth=None,note=None):  
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




    # frappe.throw(str(sale_doc.docstatus))
    sale_doc.cancel()

    #add comment to this doc to track who request to edit this sale order 
    #get user and note from pos confirm edit dialog
    

    #change status from 2 to 0 (Cancel to Draft) to allow pos can modified this doc
    sale_status_doc = frappe.get_doc("Sale Status","Submitted")
    sale_sql = "update `tabSale` set docstatus = 0, sale_status='Submitted', sale_status_color='{0}', sale_status_priority={1},balance=grand_total,total_paid_with_fee=0,total_paid=0 where name=%(name)s".format(sale_status_doc.background_color,sale_status_doc.priority)
    sale_product_sql = "update `tabSale Product` set docstatus = 0 where parent=%(parent)s"
    frappe.db.sql(sale_sql, {"name":name})
    frappe.db.sql(sale_product_sql,{"parent":name})   



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
       cancel_order(transaction_id = sale_doc.exely_transaction_id, sale = sale_doc.name, comment = auth["note"])

    
    
@frappe.whitelist()
def get_filter_for_close_sale_list(business_branch,pos_profile): 
    if business_branch:
        working_day = get_current_working_day(business_branch)
        if working_day :
            cashier_shifts =  [{"name":'', "title":"All Cashier Shift"}]
            cashier_shifts = cashier_shifts + ( frappe.db.sql("select name, name as title from `tabCashier Shift` where working_day = %(working_day)s and pos_profile = %(pos_profile)s order by name",{"pos_profile":pos_profile,"working_day":working_day.name},as_dict=1))
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
def get_reservation_folio(property,working_date):
    
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
    current_stay_rooms = get_current_stay_room([d.reservation_stay for d in folio],working_date)
    guest_names = get_guest_name_with_addition_name([d.reservation_stay for d in folio])
    for d in folio:
        d["id"] = d.name
        room = [x for x   in current_stay_rooms if x.get("reservation_stay") == d.reservation_stay ]
        if room:
            d["rooms"] =  room[0]["room_number"]
            d["room_types"] =  room[0]["room_type"]
        guest_name = [g for g in guest_names if g.get("reservation_stay") == d.reservation_stay]
        if guest_name:
            d["guest_name"] = guest_name[0]["guest_name"]
        
        
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

def get_current_stay_room(stays,working_date):
    return   frappe.db.sql("select reservation_stay, room_type,room_number from `tabRoom Occupy` where date=%(date)s and reservation_stay in %(stays)s",{"stays":stays,"date":working_date},as_dict=1)

def get_guest_name_with_addition_name(stays):
    return   frappe.db.sql("select parent as reservation_stay, concat(guest_name,if(coalesce(additional_guest_name,'')='','',concat(' / ',additional_guest_name))) as guest_name from `tabReservation Stay Room` where coalesce(additional_guest_name,'') <> '' and parent in %(stays)s",{"stays":stays},as_dict=1)

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
    
    resp = sheet.append_rows(report_data)

 

def convert_to_nested_arrays(json_data,columns):

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
    docs = frappe.db.sql("select * from `tabCashier Shift` where pos_profile = %(pos_profile)s and is_closed = 0 and is_edoor_shift = 0",{"pos_profile":pos_profile}, as_dict=1)
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
            "tables":get_tables_number(table_group= g.table_group
                                       ,device_name= ""
                                       , pos_profile=pos_profile 
                                    ),#device_name = ''
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
                result = {"status":1,"message":""}

        else:
            result = {"status":0,"message":"There is an other station actived"}
        
    else:
        result = {"status":1,"message":"This table/room will lock for other station"}  


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

@frappe.whitelist()
def reset_all_sale_network_lock():
    sql  = "delete from `tabSale Network Lock`"
    frappe.db.sql(sql,as_dict=1) 

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

@frappe.whitelist()
def get_product_activity_log(doctype,product):
    return dict(
        frappe.db.sql(
			"""select unix_timestamp(date(communication_date)), count(name)
		from `tabActivity Log`
		where
			date(communication_date) > subdate(curdate(), interval 1 year)
            and timeline_doctype = %(doctype)s and timeline_name = %(name)s
		group by date(communication_date)
		order by communication_date asc"""
		,{"name":product,"doctype":doctype}))

@frappe.whitelist()
def get_pos_profile_for_switch(pos_station,current_pos_profile,business_branch):
    
    sql = """select 
        sp.pos_profile as `name` 
    from `tabStation POS Profile` sp 
    where 1 = 1
    and sp.is_edoor_profile = 0
    and sp.business_branch = %(business_branch)s
    and sp.parent = %(station)s 
    and sp.pos_profile != %(pos_profile)s"""

    data = frappe.db.sql(sql,{
        "station":pos_station, 
        "pos_profile":current_pos_profile,
        "business_branch":business_branch
        }, as_dict=1)
    
    return data



@frappe.whitelist()
def is_training_site():
    return frappe.get_cached_value("ePOS Settings",None, "is_demo_site")


@frappe.whitelist()
def update_pos_status(station_name):
    frappe.db.sql("update `tabPOS Station` set is_used = 1 where name = %(name)s", {"name":station_name})
    frappe.db.commit()
    


@frappe.whitelist(methods="POST")
def update_prepare_report_render(report_name):
    frappe.db.sql("update `tabReport` set prepared_report = 0 where name = %(report_name)s",{"report_name":report_name})
    
def dome():
    return "Do Me"

@frappe.whitelist()
def get_server_report_setting():
    setting = frappe.get_cached_doc("ePOS Settings")
    property = frappe.defaults.get_user_default("business_branch")
    if not property:
        data = frappe.db.get_list("Business Branch")
        if len(data)>0:
            property = data[0].name
    working_day = get_current_working_day(property);     
    data = {
        "user":frappe.session.user,
        "full_name":frappe.get_cached_value("User",frappe.session.user,"full_name"),
        "server_report_url":setting.report_server_url,
        "report_service_url":setting.report_service_url,
        "server_report_token":setting.server_report_token,
        "property":property,
        "working_day":working_day
    }
    return data

@frappe.whitelist()
def get_system_report(parent):
    from frappe.utils.nestedset import get_descendants_of
    report_names = get_descendants_of("System Report","POS Report")
    reports = frappe.get_list(
        "System Report",
        fields = ["parent_system_report","name", "is_group", "report_title", "report_name","server_report_path", "filter_option", "parent_system_report","filter_default_value"],
        order_by='sort_order asc',
        filters={'name':["in",report_names]},
        page_length=10000
    )
    return reports
       



@frappe.whitelist(allow_guest=True)
def get_ssrs_report(protocol="http", host="your-ssrs-server", port="80", report_path="Your/Report/Path"):
    from requests.auth import HTTPBasicAuth
    SSRS_USERNAME = "win10"
    SSRS_PASSWORD = "eSAdmin@INC855.com"
    SSRS_REPORT_URL = f"{protocol}://{host}:{port}/ReportServer?/{report_path}&rs:Command=Render&rs:Embed=true"
    SSRS_BASE_URL = f"{protocol}://{host}:{port}/ReportServer"
    
    try:
        # Fetch the main report HTML
        response = requests.get(SSRS_REPORT_URL, auth=HTTPBasicAuth(SSRS_USERNAME, SSRS_PASSWORD))
        if response.status_code != 200:
            return {"status": "error", "message": f"Failed with status code: {response.status_code}"}
        
        html_content = response.content.decode("utf-8")
        frappe.log(f"Raw SSRS HTML: {html_content}")  # Debug raw HTML
        
        # Inline CSS styles
        css_links = re.findall(r'<link[^>]+href=["\'](.*?)["\']', html_content, re.IGNORECASE)
        for css_url in css_links:
            if not css_url.startswith(("http", "https")):
                css_url = urljoin(SSRS_BASE_URL, css_url)
            frappe.log(f"Fetching CSS: {css_url}")
            css_response = requests.get(css_url, auth=HTTPBasicAuth(SSRS_USERNAME, SSRS_PASSWORD))
            if css_response.status_code == 200:
                inline_css = f"<style>{css_response.text}</style>"
                html_content = html_content.replace(f'<link href="{css_url}" rel="stylesheet" />', inline_css)
            else:
                frappe.log(f"Failed to fetch CSS: {css_url}, status: {css_response.status_code}")
        
        # Inline JavaScript files
        script_links = re.findall(r'<script[^>]+src=["\'](.*?)["\']', html_content, re.IGNORECASE)
        for script_url in script_links:
            if not script_url.startswith(("http", "https")):
                script_url = urljoin(SSRS_BASE_URL, script_url)
            frappe.log(f"Fetching JS: {script_url}")
            js_response = requests.get(script_url, auth=HTTPBasicAuth(SSRS_USERNAME, SSRS_PASSWORD))
            if js_response.status_code == 200:
                inline_js = f"<script>{js_response.text}</script>"
                html_content = html_content.replace(f'<script src="{script_url}"></script>', inline_js)
            else:
                frappe.log(f"Failed to fetch JS: {script_url}, status: {js_response.status_code}")
        
        # Inline images/icons (e.g., PNG, JPG, GIF) as base64
        img_links = re.findall(r'<img[^>]+src=["\'](.*?)["\']', html_content, re.IGNORECASE)
        for img_url in img_links:
            if not img_url.startswith(("http", "https", "data:")):
                img_url = urljoin(SSRS_BASE_URL, img_url)
            frappe.log(f"Fetching Image: {img_url}")
            img_response = requests.get(img_url, auth=HTTPBasicAuth(SSRS_USERNAME, SSRS_PASSWORD))
            if img_response.status_code == 200:
                # Encode image as base64
                img_base64 = base64.b64encode(img_response.content).decode("utf-8")
                mime_type = img_response.headers.get("Content-Type", "image/png")
                inline_img = f"data:{mime_type};base64,{img_base64}"
                html_content = html_content.replace(img_url, inline_img)
            else:
                frappe.log(f"Failed to fetch Image: {img_url}, status: {img_response.status_code}")

        # Ensure full HTML structure with proper metadata
        full_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <base href="{SSRS_BASE_URL}/">
            <title>SSRS Report</title>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        frappe.log(f"Final HTML: {full_html}")  # Debug final HTML
        return {"status": "success", "html_content": full_html}
    
    except Exception as e:
        frappe.log_error(f"Error fetching SSRS report: {str(e)}")
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)  # You can adjust auth as needed
def sales_summary():
    from werkzeug.wrappers import Response
    ssrs_url = "http://192.168.10.158:4000/ReportServer/Pages/ReportViewer.aspx?/eSystem/Reports/rptTest1Report&rs:Format=HTML4.0"
    ssrs_username = "win10"
    ssrs_password = "eSAdmin@INC855.com"

    try:
        response = requests.get(ssrs_url, auth=(ssrs_username, ssrs_password), verify=False)
        response.raise_for_status()
        return Response(response.content, content_type="text/html")
    except Exception as e:
        frappe.log_error(message=str(e), title="SSRS Proxy Error")
        frappe.throw(_("Failed to fetch SSRS Report: {0}").format(str(e)))


    
@frappe.whitelist()
def get_default_price_rule():
    price_rule = frappe.get_list("Price Rule", filters={"is_default":1}, fields=["name"])
    if len(price_rule) > 0:
        return price_rule[0].name
    else:
        return ""
    

@frappe.whitelist()
def override_doc_timestamps(doctype, name, creation, modified):
    frappe.db.set_value(doctype, name, "creation", creation)
    frappe.db.set_value(doctype, name, "modified", modified)


@frappe.whitelist()
def generate_table_qr_menu(param):
    p = json.loads(param)

    import urllib.parse

    menu_qr_base_url = frappe.db.get_single_value("ePOS Settings","menu_qr_base_url")
    if not menu_qr_base_url:
        frappe .throw("Please set Menu QR Base URL in ePOS Settings")
    
    if not menu_qr_base_url.endswith("/"):
        menu_qr_base_url += "/"  
        
    bus = frappe.get_doc("Business Branch", p["business_branch"])

    property_code = bus.property_code

    pos_profile = urllib.parse.quote(p["pos_profile"])
    emenu = urllib.parse.quote(p["emenu"])
    table_id = urllib.parse.quote(p["table_id"])
    qr_url = "{}?propertyCode={}&posProfile={}&eMenu={}&tableNo={}".format(menu_qr_base_url, property_code, pos_profile, emenu, table_id)
    generate_param =  urllib.parse.quote(qr_url)
    generate = "https://api.qrserver.com/v1/create-qr-code/?data={}&size=400x400".format(generate_param)

    response = requests.get(generate)

    if response.status_code != 200:
        frappe.throw("Failed to generate QR code from external API.")

    # Create a unique filename
    file_name = f"qr_menu_{table_id}_{frappe.generate_hash(length=8)}.png"
    file_path = f"public/files/{file_name}"

    # Save image to public folder
    full_path = frappe.get_site_path(file_path)
    with open(full_path, "wb") as f:
        f.write(response.content)

    # Create File DocType entry
    file_url = f"/files/{file_name}"
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_url": file_url,
        "file_name": file_name,
        "is_private": 0
    })
    file_doc.insert(ignore_permissions=True)

    return {
        "file_url": file_url,
        "file_name": file_name
    }
    


def is_safe_sql(query: str) -> bool:
    import re
    # Normalize SQL: remove leading/trailing whitespaces, lowercase, and remove comments
    query = query.strip().lower()
    query = re.sub(r'--.*?(\n|$)', '', query)  # remove -- comments
    query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)  # remove /* */ comments

    # Only allow SELECT at the beginning
    if not query.startswith('select'):
        return False

    # Disallowed SQL keywords (mutation or dangerous operations)
    forbidden_keywords = [
        'insert', 'update', 'delete', 'drop', 'alter',
        'create', 'truncate', 'replace', 'grant', 'revoke'
    ]

    # Check if any forbidden keyword is in the query
    for keyword in forbidden_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', query):
            return False
            

    return True


@frappe.whitelist()
def sql(sql_command,params=None):
    if not is_safe_sql(sql_command):
        frappe.throw(_("Only SELECT statements are allowed."), frappe.PermissionError)

    if(params):
        return frappe.db.sql(sql_command,params,as_dict=1)
    else:
        return frappe.db.sql(sql_command,as_dict=1)

@frappe.whitelist()
def get_product_printer_by_products(product_codes):
    result = []
    result = frappe.db.sql("""
        SELECT printer_name, port, is_label_printer, ip_address, group_item_type, usb_printing, parent as product_code
        FROM `tabProduct Printer`
        WHERE parent IN %(product_codes)s
    """, {"product_codes": product_codes}, as_dict=True)


    return result

@frappe.whitelist(allow_guest=True)
def check_frappe_login():
    if frappe.session.user and frappe.session.user != "Guest":
        return {"ok": True}
    frappe.response['http_status_code'] = 401
    return {"ok": False}

@frappe.whitelist(allow_guest=True)
def customer_display_logs(station_id="",posting_type = "post"):
    import uuid
    random_id = str(uuid.uuid4())
    if posting_type == "post":
        frappe.db.sql("insert into `tabCustomer Display Logs` (name,station_id,creation) values (%(name)s,%(station_id)s,now())",{"name":random_id,"station_id":station_id})
        frappe.db.commit()
        return "created"
    elif posting_type == "get":
        device_id = (frappe.db.get_value("POS Station",station_id,"device_id") or "")
        if device_id != "":
            station_id = device_id
        doc = (frappe.db.sql("""select name from `tabCustomer Display Logs` where station_id = %(station_id)s""",{"station_id":station_id},as_dict=1) or [])
        if len(doc) > 0:
            return doc[0]["name"]
        else:
            return "no_logs"
    elif posting_type == "delete":
        frappe.db.sql("""delete from `tabCustomer Display Logs` where station_id = %(station_id)s""",{"station_id":station_id})
        frappe.db.commit()
        return "deleted"
    else:
        pass
@frappe.whitelist()
def get_voucher_info(name):
    from datetime import date
    from frappe.utils.synchronization import filelock
    lock_name = f"voucher_{name}"
    with filelock(lock_name, timeout=30):
        data = frappe.db.sql("select expiry_on,amount,min_bill_amount,gift_voucher_type,coalesce(customer,'no customer') customer,name,used from `tabIssue Gift Voucher` where disabled = 0 and name = '{0}'".format(name),as_dict=1)
        if len(data)>0:
            return {"is_expired":data[0].get("expiry_on")<=date.today(),
                    "amount":data[0].get("amount"),
                    "min_bill_amount":data[0].get("min_bill_amount"),
                    "gift_voucher_type":data[0].get("gift_voucher_type"),
                    "customer":data[0].get("customer"),
                    "name":data[0].get("name"),
                    "expired_date":data[0].get("expiry_on"),
                    "used":data[0].get("used")}
        else:
            return {"is_expired":1,
                    "amount":0,
                    "min_bill_amount":0,
                    "gift_voucher_type":"",
                    "customer":"",
                    "name":"Not Found",
                    "expired_date":date.today(),
                    "used":0}
@frappe.whitelist(allow_guest=1)
def check_allow_access():
    try:
        server_url = "http://webmonitor.inccloudserver.com:7129/api/method/access_server.access_server.doctype.server.server.allow_server_access"
        setting = frappe.get_doc("ePOS Settings")
        response = requests.get(server_url,{"site_id": setting.site_id})
        data_for_sync = response.json()
        return (data_for_sync["message"] or "allowed")
    except:
        return "allowed"




@frappe.whitelist(allow_guest=True)
def get_estc_connection():
    site_path = frappe.local.site_path
    site_config_path = os.path.join(site_path, "site_config.json")
    with open(site_config_path, "r") as f:
        data = json.load(f)
    
    estc_connection = {
        "estc_central_rul": data.get("estc_central_rul",None) or "",
        "estc_payway_socket_server_url":data.get("estc_payway_socket_server_url", None) or "",
    }

    
    return estc_connection

