import frappe 
from functools import lru_cache

@frappe.whitelist()
def get_kod_menu_item(business_branch, screen_name,group_by="order_time"):
    open_cashier_shift = get_open_cashier_shift(business_branch)
    
    data = []
    sql = """
        select 
            sp.name,
            s.name as sale_number,
            s.tbl_number as table_no,
            s.outlet,
            s.sale_type,
            s.customer_name,
            sp.product_name,
            sp.product_name_kh,
            sp.quantity,
            sp.kod_status,
            sp.modifiers,
            sp.note,
            sp.portion,
            sp.combo_menu,
            sp.combo_menu_data,
            sp.order_by,
            sp.order_time,
            TIMESTAMPDIFF(minute, sp.order_time, now()) as minute_diff,
            sp.is_free,
            0 as deleted,
            '' as deleted_by,
            '' as deleted_note
        from `tabSale Product` sp
        inner join `tabSale` s on s.name = sp.parent  
        where 
            s.business_branch = %(business_branch)s and 
            s.cashier_shift in %(cashier_shift)s and 
            sp.printers like %(screen_name)s and 
            kod_status in ('Pending','Processing') 
        order by sp.order_time 
    """
 
    data = frappe.db.sql(sql,{"business_branch":business_branch,"screen_name":'%{}%'.format(screen_name),"cashier_shift":open_cashier_shift}, as_dict=1)
    data = data + get_deleted_order(business_branch, screen_name, open_cashier_shift)
    return {
            "kpi":get_kpi(data,business_branch, screen_name),
            "pending_orders":group_pending_kod_order(data, group_by),
            "pending_order_items": data,
            "recent_done":get_recent_done(business_branch, screen_name)
    }

def group_pending_kod_order(data,group_by="order_time"):
    setting = frappe.get_doc("Kitchen Order Display Setting")
    group_data = []
    for x in set([d[group_by] for d in data if d["kod_status"] in ["Pending","Processing"]]):
        
        order = [{
                    "group_by":x,
                    "outlet":d["outlet"],
                    "sale_number":d["sale_number"],
                    "sale_type":d["sale_type"],
                    "table_no":d["table_no"],
                    "customer":d["customer_name"],
                    
                } for d in data if d[group_by]==x and d["kod_status"] in ["Pending","Processing"]][0]
        order["minute_diff"]=max([d["minute_diff"] for d in data if d[group_by]==x and d["kod_status"] in ["Pending","Processing"]])
        order["order_time"]=min([d["order_time"] for d in data if d[group_by]==x and d["kod_status"] in ["Pending","Processing"]])
        
        order["css_class"] = get_css_class(order["minute_diff"],setting)
        
        items=[
            {
                "name":d["name"],
                "product_name":d["product_name"],
                "product_name_kh":d["product_name_kh"],
                "quantity":d["quantity"],
                "modifiers":d["modifiers"],
                "portion":d["portion"],
                "note":d["note"],
                "combo_menu":d["combo_menu"] or "",
                "combo_menu_data":d["combo_menu_data"] or "",
                "kod_status":d["kod_status"],
                "is_free":d["is_free"],
                "order_time":d["order_time"],
                "minute_diff":d["minute_diff"],
                "deleted":d["deleted"],
                "deleted_by":d["deleted_by"],
                "deleted_note":d["deleted_note"],
                "css_class":get_css_class(d["minute_diff"],setting)
            } for d in data if d[group_by]==x and d["kod_status"] in ["Pending","Processing"]]
        order["items"] = sorted(items, key=lambda x: x["order_time"])
        group_data .append(order)
    
    return  sorted(group_data, key=lambda x: x["order_time"])

@lru_cache(maxsize = 128) 
def get_css_class(duration,setting):
    if duration<=int(setting.new_order_duration):
        return "new"
    elif duration>int(setting.new_order_duration) and duration<=int(setting.warning_order_duration):
        return "warn"
    
    return "error"

def get_kpi(data, business_branch, screen_name):
    setting = frappe.get_doc("Kitchen Order Display Setting")
    kpi = {
        "new_order":len([d for d in data if d["minute_diff"]<= int(setting.new_order_duration)]),
        "pending_order":len(data),
        "processing_order":len([d for d in data if d['kod_status']=="Processing"]),
        "done":get_total_done(business_branch,screen_name),
    }
    
    return kpi

def get_total_done(business_branch, screen_name):
    sql="""
            select 
                count(sp.name)  as total
            from `tabSale Product` sp 
            inner join `tabSale` s on s.name = sp.parent
            where 
                kod_status='Done' and 
                s.business_branch ='{}' and 
                sp.printers like '%{}%'  
            """.format(business_branch, screen_name)
    data = frappe.db.sql(sql,as_dict=1)
    return data[0]["total"]

def get_recent_done(business_branch, screen_name):
    
    cashier_shift =  get_open_cashier_shift(business_branch) 
    sql = """
        select 
            sp.name,
            s.name as sale_number,
            s.tbl_number as table_no,
            s.outlet,
            s.sale_type,
            s.customer_name,
            sp.product_name,
            sp.product_name_kh,
            sp.quantity,
            sp.kod_status,
            sp.modifiers,
            sp.note,
            sp.portion,
            sp.combo_menu,
            sp.combo_menu_data,
            sp.order_by,
            sp.order_time,
            TIMESTAMPDIFF(minute, sp.order_time, now()) as minute_diff,
            sp.is_free
        from `tabSale Product` sp
        inner join `tabSale` s on s.name = sp.parent  
        where 
            s.business_branch = %(business_branch)s and 
            sp.printers like %(screen_name)s and  
            s.cashier_shift in %(cashier_shift)s and 
            sp.kod_status ='Done'
        order by sp.order_time 
        limit 20
    """
 
    data = frappe.db.sql(sql,{"business_branch":business_branch,"screen_name":'%{}%'.format(screen_name),"cashier_shift":cashier_shift}, as_dict=1)
    return data

@frappe.whitelist(methods="POST")
def change_status(sale_product_names, status):
    sql="update `tabSale Product` set kod_status_update_time=now(), kod_status=%(status)s where name in %(sale_product_names)s"
    frappe.db.sql(sql,{"sale_product_names":sale_product_names, "status":status})
    frappe.db.commit()


def get_open_cashier_shift(business_branch):
    sql="select name from `tabCashier Shift` where is_closed=0 and business_branch='{}'".format(business_branch)
    return set([d["name"] for d in  frappe.db.sql(sql,as_dict=1)])
     
     
def get_deleted_order(business_branch,screen_name,cashier_shift = None):
    if not cashier_shift:
        cashier_shift = get_open_cashier_shift(business_branch)
    sql = """
        select 
            sp.name,
            s.name as sale_number,
            s.tbl_number as table_no,
            s.outlet,
            s.sale_type,
            s.customer_name,
            sp.product_name,
            sp.product_name_kh,
            sp.quantity,
            sp.kod_status,
            sp.modifiers,
            sp.note,
            sp.portion,
            sp.combo_menu,
            sp.combo_menu_data,
            sp.order_by,
            sp.order_time,
            TIMESTAMPDIFF(minute, sp.order_time, now()) as minute_diff,
            sp.is_free,
            1 as deleted,
            sp.deleted_by,
            sp.deleted_note
        from `tabSale Product Deleted` sp
        inner join `tabSale` s on s.name = sp.sale_doc  
        where 
            s.business_branch = %(business_branch)s and 
            s.cashier_shift in %(cashier_shift)s and 
            sp.printers like %(screen_name)s and 
            sp.kod_status in ('Pending','Processing')  and 
            s.docstatus= 0 
        order by sp.order_time 
    """
    data = frappe.db.sql(sql,{"business_branch":business_branch,"screen_name":'%{}%'.format(screen_name),"cashier_shift":cashier_shift}, as_dict=1)
    
    return data
    