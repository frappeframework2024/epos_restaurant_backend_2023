import json
import time
import frappe
import base64
from py_linq import Enumerable
from frappe.utils import today, add_to_date
from datetime import datetime, timedelta
import calendar
from dateutil import relativedelta
from frappe import _
from epos_restaurant_2023.api.api import get_current_shift_information,update_pos_reservation_and_sale_payment

@frappe.whitelist()
def get_pos_reservation_list(property,arrival_date): 
    sql = """select name from `tabPOS Reservation` 
    where 1= 1
        and case when coalesce(property,'') = '' then %(property)s else coalesce(property,'') end = %(property)s
        and arrival_date = %(arrival_date)s
        and reservation_status in ('Confirmed')"""
        
    get_list =  frappe.db.sql(sql,{"property":property, "arrival_date":arrival_date },as_dict = 1)
    if get_list:
        result = []
        for g in get_list:
            doc = frappe.get_doc("POS Reservation", g.name)
            result.append(doc)

        return result
    
    else:
        return False


@frappe.whitelist()
def pos_reservation_check_in(business_branch,pos_profile,device_name,reservation_id):
    if  frappe.request.method != "POST":        
        frappe.local.response.update({
            "message": _("Method Not Allowed"),
            "http_status_code": 405 
        }) 
        return
    
    # check working day information
    
    shift_information = get_current_shift_information(business_branch,pos_profile)
    if not shift_information:
        frappe.local.response.update({
            "message": _("No Shift Information Found"),
            "http_status_code": 404
        })
        return

    if not shift_information.get("working_day" , None):
        frappe.local.response.update({
            "message": _("No Working Day Information Found"),
            "http_status_code": 404
        })
        return
        
    if not shift_information.get("cashier_shift" , None):   
        frappe.local.response.update({
            "message": _("No Cashier Shift Information Found"),
            "http_status_code": 404
        })
        return
        
    
    
    reservation_doc = frappe.get_doc("POS Reservation", reservation_id)
    if reservation_doc.docstatus != 1:
        frappe.local.response.update({
            "message": _("Invalid Reservation"),
            "http_status_code": 404
        })
        return
    
    working_day = shift_information.get("working_day")
    # if reservation_doc.arrival_date != working_day.get("posting_date"):
    #     frappe.local.response.update({
    #         "message": _("Reservation Arrival Date is not match with Working Day"),
    #         "http_status_code": 404
    #     })
    #     return
    
    table = frappe.db.exists("Tables Number", reservation_doc.table_id)
    if not table:
        frappe.local.response.update({
            "message": _("Table Not Found"),
            "http_status_code": 404
        })
        return
    
    # check customer
    customer = frappe.db.exists("Customer", reservation_doc.guest)
    if not customer:
        frappe.local.response.update({
            "message": _("Customer Not Found"),
            "http_status_code": 404
        })
        return
    
    customer = frappe.get_doc("Customer", reservation_doc.guest)
    table = frappe.get_doc("Tables Number", reservation_doc.table_id) 
    pos_profile = frappe.get_doc("POS Profile", pos_profile)
    cashier_shift = shift_information.get("cashier_shift")
    

    sale_json = prepare_sale_doc(device_name=device_name,
                                pos_profile=pos_profile,                                
                                working_day=working_day,
                                cashier_shift=cashier_shift,
                                customer=customer,
                                reservation=reservation_doc,
                                table=table
                            )
 
    sale_doc = frappe.get_doc(sale_json)
    sale_doc.insert(ignore_permissions=True)
    
    update_pos_reservation_and_sale_payment(reservation_name=reservation_doc.name,reservation_status="Dine-in",sale=sale_doc.name, is_commit=True)
                     
    
    return sale_doc



def prepare_sale_doc(device_name, pos_profile, working_day, cashier_shift, customer, reservation, table): 
    now = datetime.now()
    user = frappe.get_doc("User", frappe.session.user)    
    price_rule = table.price_rule if table.price_rule else (customer.price_rule if customer.price_rule else pos_profile.price_rule)
    exchange_rate = get_exchange_rate()
    
    sale_json = {
        "doctype": "Sale",
        "modified": now,
        "creation": now,
        "sale_status": "Hold Order",
        "cashier_shift": cashier_shift.get("name"),
        "shift_name": cashier_shift.get("shift_name"),
        "working_day": working_day.get("name"),
        "exchange_rate": exchange_rate.get("exchange_rate"),
        "change_exchange_rate": exchange_rate.get("change_exchange_rate"),
        "outlet": pos_profile.outlet,
        "stock_location": pos_profile.stock_location,
        "table_id": table.name,
        "tbl_number": table.tbl_number,
        "pos_profile": pos_profile.name,
        "pos_station_name": device_name,
        "price_rule": price_rule,
        "business_branch": pos_profile.business_branch,
        "sale_type": pos_profile.default_sale_type,
        "discount_type": "Percent",
        "grand_total": 0,
        "guest_cover": reservation.total_guest,
        "discount": 0,
        "sub_total": 0,
        "payment": [], 
        "commission_type": "Percent",
        "commission": 0,
        "commission_note": '',
        "commission_amount": 0,
        "created_by": user.full_name,
        "new_sale_default_pos_menu": "",
        "submitted_default_pos_menu": "",
        "sale_products": [],
        "product_variants": [],
        "from_reservation": reservation.name,        
        "posting_date" : working_day.get("posting_date"),
        "customer" : reservation.guest,
        "customer_photo" : reservation.guest_photo,
        "customer_name" : reservation.guest_name,
        "customer_group" : reservation.guest_type,
        "deposit" : reservation.total_deposit,
        
    }
    
    return sale_json
    
    
    
def get_exchange_rate():
    #main currency information
    main_currency = frappe.get_doc("Currency",frappe.db.get_default("currency"))
    second_currency = frappe.get_doc("Currency",frappe.db.get_default("second_currency"))
    exchange_rate_main_currency = frappe.db.get_default("exchange_rate_main_currency")
    
    to_currency = second_currency.name
    if (exchange_rate_main_currency != main_currency.name):
        to_currency = main_currency.name  

    sql = """select 
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
            limit 1"""
            

    exchange_rate = frappe.db.sql(sql,{
                                        "from_currency":exchange_rate_main_currency,
                                        "to_currency":to_currency,
                                    }, as_dict= 1)
    
    return exchange_rate[0] if  exchange_rate else {
        "posting_date": None,
        "exchange_rate":1,
        "exchange_rate_input":1,
        "change_exchange_rate":1,
        "change_exchange_rate_input":1 
    }