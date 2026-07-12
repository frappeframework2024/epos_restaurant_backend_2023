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
    