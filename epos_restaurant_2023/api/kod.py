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
            if(s.docstatus=2,1,0) as deleted,
            s.deleted_by,
            s.deleted_note
        from `tabSale Product` sp
        inner join `tabSale` s on s.name = sp.parent  
        where 
            s.business_branch = %(business_branch)s and 
            s.cashier_shift in %(cashier_shift)s and 
            sp.printers like %(screen_name)s and 
            sp.hide_in_kod = 0
        order by sp.order_time 
    """
 
    data = frappe.db.sql(sql,{"business_branch":business_branch,"screen_name":'%{}%'.format(screen_name),"cashier_shift":open_cashier_shift}, as_dict=1)
    data = data + get_deleted_order(business_branch, screen_name, open_cashier_shift)
    return {
            "kpi":get_kpi(data,business_branch, screen_name),
            "pending_orders":group_pending_kod_order(data, group_by),
            "pending_order_items": [d for d in data if d["deleted"] == 0 and d["kod_status"]!='Done'],
            "recent_done":get_recent_done(business_branch, screen_name)
    }

def group_pending_kod_order(data,group_by="order_time"):
    setting = frappe.get_doc("Kitchen Order Display Setting")
    group_data = []
    for x in set([d[group_by] for d in data]):
        
        order = [{
                    "group_by":x,
                    "outlet":d["outlet"],
                    "sale_number":d["sale_number"],
                    "sale_type":d["sale_type"],
                    "table_no":d["table_no"],
                    "customer":d["customer_name"],
                    
                } for d in data if d[group_by]==x][0]
        active_order = [d for d in data if d[group_by]==x and d["kod_status"] in ["Pending","Processing"]]
        if active_order:
            order["minute_diff"]=max([d["minute_diff"] for d in active_order])
            order["order_time"]=min([d["order_time"] for d in active_order])
            order["css_class"] = get_css_class(order["minute_diff"],setting)
        else:
            order["minute_diff"]=max([d["minute_diff"] for d in data if d[group_by]==x])
            order["order_time"]=min([d["order_time"] for d in data if d[group_by]==x])
            order["css_class"] = "done"
        
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
            } for d in data if d[group_by]==x]
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
        "new_order":len([d for d in data if d["kod_status"] in ["Pending","Processing"] and  d["minute_diff"]<= int(setting.new_order_duration)]),
        "pending_order":len([d for d in data if d["kod_status"] == "Pending"]),
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
        order by sp.kod_status_update_time desc
        limit 20
    """
 
    data = frappe.db.sql(sql,{"business_branch":business_branch,"screen_name":'%{}%'.format(screen_name),"cashier_shift":cashier_shift}, as_dict=1)
    return data

@frappe.whitelist(methods="POST")
def change_status(sale_product_names, status, hide_in_kod=0):
    sql="update `tabSale Product` set kod_status_update_time=now(), kod_status=%(status)s,hide_in_kod=%(hide_in_kod)s where name in %(sale_product_names)s"
    frappe.db.sql(sql,{"sale_product_names":sale_product_names, "status":status,"hide_in_kod":hide_in_kod})
    
    sql="update `tabSale Product Deleted` set hide_in_kod=1  where sale_product_id in %(sale_product_names)s"
    frappe.db.sql(sql,{"sale_product_names":sale_product_names})
    
    frappe.db.commit()

@frappe.whitelist(methods="POST")
def close_order(sale_product_names, status):
    sql="update `tabSale Product` set kod_status_update_time=now(),hide_in_kod=1, kod_status=%(status)s where name in %(sale_product_names)s"
    frappe.db.sql(sql,{"sale_product_names":sale_product_names, "status":status})
    
    sql="update `tabSale Product Deleted` set hide_in_kod=1  where sale_product_id in %(sale_product_names)s"
    frappe.db.sql(sql,{"sale_product_names":sale_product_names})
    
    frappe.db.commit()


def get_open_cashier_shift(business_branch):
    sql="select name from `tabCashier Shift` where is_closed=0 and business_branch='{}'".format(business_branch)
    return set([d["name"] for d in  frappe.db.sql(sql,as_dict=1)])
     
     
def get_deleted_order(business_branch,screen_name,cashier_shift = None):
    if not cashier_shift:
        cashier_shift = get_open_cashier_shift(business_branch)
    sql = """
        select 
            sp.sale_product_id as name,
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
            sp.hide_in_kod=0 
        order by sp.order_time 
    """
    data = frappe.db.sql(sql,{"business_branch":business_branch,"screen_name":'%{}%'.format(screen_name),"cashier_shift":cashier_shift}, as_dict=1)
    
    return data
    