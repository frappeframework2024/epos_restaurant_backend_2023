import frappe
import calendar
import datetime

def get_day_numbers(year, month):
    _, num_days = calendar.monthrange(int( year), int(month))
    return list(range(1, num_days + 1))

# param: {"param": {"pos_profiles":["POS Profile"], "date":"2025-02-06"}}
# @frappe.whitelist(allow_guest=True)
@frappe.whitelist()
def sale_kpi(param):
    result = {
        "total_revenue": 0.0,
        "total_active_bill": 0.0,
        "total_active_quantity": 0.0,
        "totale_deleted_bill": 0,
        "total_deleted_quantity":0,
    }

    sale_sql = """select 
                    sum(if(s.docstatus = 1, s.grand_total, 0)) as total_revenue ,
                    sum(if(s.docstatus = 1, s.total_quantity,0)) as total_quantity,
                    sum(if(s.docstatus = 1, 1,0)) as total_active_bill,
                    sum(if(s.docstatus = 2 and s.deleted_type is null, 1,0)) as total_deleted_bill,
                    sum(if(s.docstatus = 2 and s.deleted_type is null, s.total_quantity,0)) as total_deleted_quantity
                from `tabSale` s 
                where 1=1
                and s.posting_date = %(date)s """
    if param["pos_profiles"]:
        sale_sql += " and (s.pos_profile in %(pos_profile)s or s.pos_profile is null)"

    sale = frappe.db.sql(sale_sql, {
            "pos_profile": param["pos_profiles"],
            "date": param["date"]
        }, as_dict=1)
    

    ## get deleted sale product
    sale_sql = """select 
                    sum(sp.quantity) as total_deleted_quantity
                from `tabSale Product Deleted` sp 
                inner join `tabSale` s on s.name = sp.sale_doc
                where 1=1
                and s.posting_date = %(date)s """
    
    if param["pos_profiles"]:
        sale_sql += " and (s.pos_profile in %(pos_profile)s or s.pos_profile is null)"

    deleted_sale_product = frappe.db.sql(sale_sql, {
            "pos_profile": param["pos_profiles"],
            "date": param["date"]
        }, as_dict = 1)
    
    total_deleted_quantity = 0
    if deleted_sale_product:
        item = deleted_sale_product[0]
        total_deleted_quantity = item.total_deleted_quantity or 0
        result["total_deleted_quantity"] = total_deleted_quantity
    ## end get deleted sale product

    if sale:
        sale = sale[0]
        result = {
            "total_revenue": sale.total_revenue or 0,
            "total_active_bill": sale.total_active_bill or 0,
            "total_active_quantity": sale.total_quantity or 0,
            "totale_deleted_bill": sale.total_deleted_bill or 0,
            "total_deleted_quantity": (sale.total_deleted_quantity or 0) + total_deleted_quantity,
        }

    return result



# param: {"param": {"pos_profiles":["POS Profile 01","POS Profile 02"], "year":"2025", "month":"02"}}
# @frappe.whitelist(allow_guest=True)
@frappe.whitelist()
def daily_sale_chart(param):
    result = []
    for d in get_day_numbers(param["year"], param["month"]):
        result.append({
            "day": d,
            "date": frappe.utils.formatdate(datetime.date(int(param["year"]), int(param["month"]), d), "yyyy-MM-dd"),
            "value": 0
        })

    sql = """select 	
                s.posting_date,
                sum(s.grand_total) as total_amount
            from `tabSale` s 
            where 1=1
            and s.docstatus = 1
            and s.posting_date between %(start_date)s and %(end_date)s """
    if param["pos_profiles"]:
        sql += " and (s.pos_profile in %(pos_profile)s or s.pos_profile is null)"
        
    sql += " group by s.posting_date"
    
    data = frappe.db.sql(sql, {
        "start_date":result[0]["date"] ,
        "end_date": result[-1]["date"] ,
        "pos_profile": param["pos_profiles"],
        }, as_dict=1)
    

    for d in data:
      value =  [r for r in result if str(r["date"]) == str(d["posting_date"])] 
      if value:
        value[0]["value"] = d["total_amount"]

    return result


# param: {"param": {"pos_profiles":["POS Profile 01","POS Profile 02"] , "date":"2025-02-06"}}
# @frappe.whitelist(allow_guest=True)
@frappe.whitelist()
def payment_breakdown(param):
    sql = """select 
            sp.payment_type_group, 
            sp.payment_type,
            sum(sp.input_amount) as input_amount,
            sum(sp.payment_amount) as payment_amount,
            sp.currency ,
            sp.currency_precision
        from `tabSale Payment`  sp
        where 1 = 1
        and sp.docstatus = 1
        and  sp.posting_date = %(date)s """
    if param["pos_profiles"]:
        sql += " and (sp.pos_profile in %(pos_profile)s or sp.pos_profile is null)"
    sql += " group by sp.payment_type_group, sp.payment_type, sp.currency, sp.currency_precision"
    data = frappe.db.sql(sql, {
        "date":param["date"] ,
        "pos_profile": param["pos_profiles"],        
        }, as_dict=1)

     
    return data