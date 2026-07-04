import frappe
from epos_restaurant_2023.api.mobile.v1.utils import get_working_day_info,get_cashier_shift_info
from frappe.utils.caching import redis_cache
 
@frappe.whitelist(methods=["POST","GET"])
def working_day_and_shift_info(business_branch="ESTC HOTEL 6",pos_profile="Main POS Profile"):
    return {
        "working_day":get_working_day_info(business_branch),
        "cashier_shift":get_cashier_shift_info(pos_profile)
    }

@frappe.whitelist(methods=["POST","GET"])
def get_home_data(business_branch="ESTC HOTEL 6",pos_profile="Main POS Profile"):
    working_day_info =  get_working_day_info(business_branch)
    return {
        "new_register_customer":get_new_customer_register(),
        "today_revenue":get_daily_sale_data(business_branch=business_branch,working_date=working_day_info.get("posting_date"), pos_profile=pos_profile),
        "yesterday_revenue":get_daily_sale_data(business_branch=business_branch,working_date=frappe.utils.add_days(working_day_info.get("posting_date"),-1), pos_profile=pos_profile),
        "peding_order":get_pending_order(business_branch,pos_profile)
    }

def get_daily_sale_data(business_branch,working_date=None,pos_profile=None):
    sql="""
        select 
            sum(grand_total) as total_revenue, 
            count(*) as total_order from `tabSale` 
        where 
            docstatus = 1 and
            business_branch = %(business_branch)s and 
            posting_date = %(working_date)s and 
            (pos_profile = %(pos_profile)s or %(pos_profile)s = '')
    """
    data =  frappe.db.sql(sql,{"business_branch":business_branch,"pos_profile":pos_profile or "", "working_date":working_date or frappe.utils.today()},as_dict = 1)
    if data:
        data = data[0]

    def get_order_by_order_type():
        sql="""select sale_type, count(*) as total_order from `tabSale` 
            where
                docstatus = 1 and 
                sale_status ='Closed' and 
                business_branch =%(business_branch)s and 
                pos_profile = %(pos_profile)s 
            group by sale_type
        """
        return frappe.db.sql(sql, {"business_branch":business_branch, "pos_profile":pos_profile},as_dict = 1)

    return {**data, "sale_types":get_order_by_order_type()}

def get_pending_order(business_branch, pos_profile):
    sql = """
        select 
            count(*) as total_order, 
            sum(grand_total) as total_amount  
        from `tabSale` 
        where
            docstatus = 0 and 
            sale_status !='Closed' and 
            business_branch =%(business_branch)s and 
            pos_profile = %(pos_profile)s

        """
    data = frappe.db.sql(sql, {"business_branch":business_branch, "pos_profile":pos_profile},as_dict = 1)
    if data:
        data =  data[0]
    else:
        data = {
            "total_order":0,
            "total_amount":0

        }
    
    return data

@redis_cache(ttl=1000*60*10)  
def get_new_customer_register():
    sql = "select count(*) as new_register_customer from `tabCustomer` where date(creation)>=%(date)s"
    date = frappe.utils.add_days(frappe.utils.today(),-7)
    return frappe.db.sql(sql,{"date":date},as_dict=1)[0].get("new_register_customer") or 0

@frappe.whitelist()
def get_notification_info():
    return frappe.db.count(
        "Notification Log",
        {
            "for_user": frappe.session.user,
            "read": 0
        }
    )