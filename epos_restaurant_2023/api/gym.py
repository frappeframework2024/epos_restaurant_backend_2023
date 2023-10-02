import json
import time
import frappe
import base64
from py_linq import Enumerable
from frappe.utils import today, add_to_date
from datetime import datetime, timedelta
from frappe import _


@frappe.whitelist()
def membership_check_in(code): 
    check_member = frappe.db.exists("Customer",code) 
    if not check_member:
        return False


    member = frappe.get_doc("Customer",code)
    data_membership = frappe.db.get_list("Membership",fields=[ "name","docstatus"], filters=[{'customer':code},{'docstatus':1}])
    if len(data_membership) <= 0:
        membership_family = frappe.db.sql("select member,parent from `tabMembership Family` where member = '{}' and docstatus = 1".format(code),as_dict=1)
        if len(membership_family) <= 0:
            return False
        
        return membership_family
    

    memberships =[]
    for child in data_membership:
        m = frappe.get_doc("Membership",child.name)
        memberships.append({   
            "name":m.name,             
            "member_name":m.member_name,
            "customer":m.customer,
            "duration_type":m.duration_type,
            "membership_duration":m.membership_duration,
            "membership":m.membership,
            "membership_type":m.membership_type,
            "duration_base_on":m.duration_base_on,
            "start_date":m.start_date,
            "end_date":m.end_date,
            "access_type":m.access_type,
            "duration":m.duration,
            "per_duration":m.per_duration,
            "membership_family_table":m.membership_family_table
        })
 
    data = {
        'member':member,
        'membership':memberships
    }
    return data
   