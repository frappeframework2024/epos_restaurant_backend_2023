import json
import time
import frappe
import base64
from py_linq import Enumerable
from frappe.utils import today, add_to_date
from datetime import datetime, timedelta
from frappe import _


@frappe.whitelist()
def membership_check_in(code,check_in_date):  
    check_member = frappe.db.exists("Customer",code) 
    if not check_member:
        return False

    cus = frappe.get_doc("Customer",code)
    member = {
        "name":cus.name,
        "customer_code_name":cus.customer_code_name,
        "customer_name_en":cus.customer_name_en,
        "customer_name_kh":cus.customer_name_kh,
        "customer_group":cus.customer_group,
        "date_of_birth":cus.date_of_birth,
        "gender":cus.gender,
        "phone_number":cus.phone_number,
        "photo":cus.photo
    }
    data_membership = frappe.db.get_list("Membership",fields=[ "name","docstatus"], filters=[{'customer':code},{'docstatus':1}])
    # if len(data_membership) <= 0:
    membership_family = frappe.db.sql("select member,parent from `tabMembership Family` where member = '{}' and docstatus = 1".format(code),as_dict=1)
    if len(membership_family) > 0:
        _data_membership = frappe.db.get_list("Membership",fields=[ "name","docstatus"], filters=[{'name':membership_family[0].parent},{'docstatus':1}])
        for d in _data_membership:
            data_membership.append(d)
    

    query = """select
                DISTINCT
                a.membership
            from `tabMembership Check In Items` as a 
            inner join `tabMembership Check In` as b on b.name = a.parent
            where b.docstatus = 1 
                and a.docstatus = 1
                and b.check_in_date ='{}' 
                and b.member = '{}'
            group by 
                a.membership""".format(check_in_date,code)
    data_query = frappe.db.sql(query,as_dict=1) 
    memberships =[]
    for child in data_membership:
        m = frappe.get_doc("Membership",child.name)
        # membership_family_table = m.membership_family_table
        # if m.customer != member["name"]:
        #     membership_family_table = filter(lambda x: x.member == member["name"], m.membership_family_table) 

        locked = False
        if len(data_query) > 0:
           already_checked = list(filter(lambda x: x.membership == m.name and m.access_type != "Unlimited", data_query)) 
           locked =  True if len(already_checked) > 0 else False

        ## get total checked in  
        sql = """select count(`name`) as total_check_in from `tabMembership Check In Items` 
					where member = '{}' 
					and  membership = '{}' 
					and docstatus = 1 """.format(code, m.name)
		
		 
        exec = frappe.db.sql(sql, as_dict=1)
        # frappe.throw(str(exec))
        # frappe.throw(str(sql))
        count = 0
        if exec:
            count = (exec[0].total_check_in or 0)

        memberships.append({   
            "name":m.name,             
            # "member_name":m.member_name,
            # "customer":m.customer,
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
            "selected":False,
            "locked":locked,
            "total_checked_in":count
        })
 
    data = {
        'check_in_date':check_in_date,
        'member':member,
        'membership':memberships
    }
    return data
   


@frappe.whitelist()
def check_in_submit_data(data):
    doc = frappe.get_doc(json.loads(data))
    doc.insert()

    #submit doctype
    doc.submit()
    frappe.db.commit()  
    return doc


@frappe.whitelist()
def get_recent_checked_ins():
    query = """select 
        concat(m.member,'-', m.member_name) as member, 
        m.check_in_date, 
        i.creation, 
        i.membership,
        i.membership_name,
        i.membership_type 
    from `tabMembership Check In Items` i 
    inner join `tabMembership Check In` m on m.name = i.parent  
    where m.docstatus = 1 and i.docstatus = 1
    order by i.creation desc limit 15"""
    docs = frappe.db.sql(query,as_dict=1)
    return docs