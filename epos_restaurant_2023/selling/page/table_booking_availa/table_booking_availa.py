import frappe
from frappe.utils.caching import redis_cache

@frappe.whitelist()
def get_data(date,table_group=None):
    tables = get_table_list(table_group)
    reservations =[]
    pending_sales = []
    if tables:
        reservations = get_reservations(date, [x.get("name") for x in tables]) 
        pending_sales =get_pending_sales(table_group,date=date)
       
        if reservations:
            for t in tables:
                t["reservations"] = [x for x in reservations if x.get("table_id") == t.get("name")]
                t["occupy"] = [x for x in pending_sales if x.get("table_id") == t.get("name")]

    
    return {
        "table_groups": get_table_groups(table_group),
        "tables":tables
    }


    


def get_reservations(date,table_names):
    sql = """
        select 
            a.name as booking_number,
            a.table_id,
            a.total_guest,
            a.adult,
            a.child,
            a.elderly,
            a.note,
            a.guest_name,
            a.phone_number,
            a.arrival_time,
            a.check_out_time,
            a.reservation_status,
            b.background_color, 
            b.color as text_color
        from `tabPOS Reservation` a 
        join `tabPOS Reservation Status` b on b.name = a.reservation_status

        where
            table_id  in %(table_names)s and 
            arrival_date = %(date)s and 
            a.reservation_status  in ('Pending','Reserved','Confirmed')
        

    """
    data = frappe.db.sql(sql, {"date":date, "table_names":table_names},as_dict = 1)
    return data


@frappe.whitelist()
def get_unasign_table_reservations(date=None):
    
    sql = """
        select 
            a.name as booking_number,
            a.table_id,
            a.total_guest,
             a.adult,
            a.child,
            a.elderly,
            a.note,
            a.guest_name,
            a.phone_number,
            a.arrival_time,
            a.check_out_time,
            a.reservation_status,
            b.background_color, 
            b.color as text_color
        from `tabPOS Reservation` a 
        join `tabPOS Reservation Status` b on b.name = a.reservation_status

        where
            coalesce(table_id,'')= '' and 
            arrival_date = %(date)s and 
            a.reservation_status in ('Confirmed','Reserved',"Pending")
        

    """
    data = frappe.db.sql(sql, {"date": date or frappe.utils.today()},as_dict = 1)
    return data


@frappe.whitelist()
def get_active_reservation():
    sql = """
        select 
            a.name as booking_number,
            a.arrival_date,
            a.table_id,
            a.table_number,
            a.total_guest,
             a.adult,
            a.child,
            a.elderly,
            a.note,
            a.guest_name,
            a.phone_number,
            a.arrival_time,
            a.check_out_time,
            a.reservation_status,
            b.background_color, 
            b.color as text_color
        from `tabPOS Reservation` a 
        join `tabPOS Reservation Status` b on b.name = a.reservation_status

        where
            arrival_date>=CURDATE() and 
            a.reservation_status in ('Confirmed','Reserved',"Pending") 
        order by 
            arrival_date

        

    """
    data = frappe.db.sql(sql,as_dict = 1)
    return data

    
def get_table_list(table_group):
    cache = frappe.cache()
    key = f"table_list:{table_group or ''}"

    cached = cache.get_value(key)
    if cached:
        return cached
    
    sql = """
        select
            tbl_group as table_group,
            name,
            tbl_number as table_number
        from `tabTables Number`
        where
            (%(table_group)s = '' or tbl_group =%(table_group)s) and 
            coalesce(disabled,0) = 0 
        order by 
            sort_order,
            tbl_number


    """
    result = frappe.db.sql(sql, {"table_group":table_group or ""},as_dict=1)
    cache.set_value(key, result, expires_in_sec=86400)

    return result

@redis_cache(ttl=1000*60)  
def get_table_groups(table_group=None):
    sql = "select name as table_group from `tabTable Group` where coalesce(disabled,0) = 0 and (%(table_group)s = '' or name = %(table_group)s) order by sort_order, table_group"
    return frappe.db.sql(sql,{"table_group":table_group or ""},as_dict=1)

def get_pending_sales(table_group=None,date=None):

    sql="""
        select
            table_id, 
            name,
            TIME_FORMAT(creation, '%%H:%%i:%%s') as arrival_time,
            TIME_FORMAT(NOW(), '%%H:%%i:%%s') AS check_out_time,
            customer_name as guest_name,
            guest_cover as total_guest,
            sale_status_color as background_color,
            '#ffffff' as text_color


        from `tabSale` s

        where
            s.docstatus = 0 and 
            s.sale_status in ('Draft','Submitted','Bill Requested') and 
            (%(table_group)s = '' or s.tbl_group = %(table_group)s) and 
            s.posting_date = %(date)s

    """
    return frappe.db.sql(sql, {"table_group":table_group or "","date":date},as_dict=1)

@frappe.whitelist()
@redis_cache(ttl=1000*60*24)  
def get_legend_color():
    sql = """
        select 
            name,
            background_color,
            color,
            sort_order
        from `tabPOS Reservation Status`
        where
            name in ('Confirmed', 'Dine-in')
       
    """
    reservation_status = frappe.db.sql(sql,as_dict=1)
    sql = """
        select 
            name,
            background_color,
            '#ffffff' as color,
            coalesce(sort_order,0) as sort_order
        from `tabSale Status`
        where
            name in ('Hold Order', 'Submitted','Bill Request')
        order by sort_order
       
    """
    
    sale_status = frappe.db.sql(sql,as_dict = 1)
    
    return {
        "reservation_status": reservation_status,
        "sale_status":sale_status
    }