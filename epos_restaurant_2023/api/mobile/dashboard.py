import json
import frappe
import calendar
import datetime

def get_day_numbers(year, month):
    _, num_days = calendar.monthrange(int( year), int(month))
    return list(range(1, num_days + 1))

def get_param(param):
    if  type(param) is str:
        param = json.loads(param)
    keys = param.keys()
    business_branch = ""
    if "business_branch" in keys:
        business_branch = param["business_branch"]
    pos_profiles = []
    if "pos_profiles" in keys:
        pos_profiles = param["pos_profiles"]
    
    working_date = param["working_date"] if "working_date" in keys else ""
    if (working_date or "") == "":
        working_day_sql = """
            select 
                max(posting_date) as posting_date 
            from `tabWorking Day` where 1=1 
                (%(business_branch)s = '' or business_branch = %(business_branch)s)  
            limit 1
        """
        
        working_day = frappe.db.sql(working_day_sql, {"business_branch": business_branch}, as_dict=1)

        if working_day and working_day[0]["posting_date"]:
            working_date = working_day[0]["posting_date"]
        else:
            now = datetime.datetime.now()
            current_date = now.date()
            working_date = current_date
    else:
        working_date = datetime.datetime.strptime(working_date, "%Y-%m-%d").date()

    return {"business_branch":business_branch or "","working_date":working_date, "pos_profiles":pos_profiles, }

# param: {"param": {"pos_profiles":["POS Profile"],"business_branch":""}}
### business_branch ="" means all business_branch

# @frappe.whitelist(allow_guest=True)
@frappe.whitelist()
def sale_kpi(param):
    p = get_param(param)
    business_branch  = p["business_branch"]
    working_date = p["working_date"]
    pos_profiles = p["pos_profiles"] 

    today_data = sale_kpi_get_data(business_branch, pos_profiles, working_date)
    mtd_data = sale_kpi_get_data(business_branch, pos_profiles, working_date,type="MTD")

    return {
        "today_revenue": today_data.total_revenue,
        "today_bill": today_data.total_bill,
        "today_quantity": today_data.total_quantity,
        "today_coupon_quantity": today_data.total_coupon,
        "today_coupon_bill": today_data.total_coupon_bill,
        "mtd_revenue": mtd_data.total_revenue,
        "mtd_bill": mtd_data.total_bill,
        "mtd_quantity": mtd_data.total_quantity,    
        "mtd_coupon_quantity": mtd_data.total_coupon,    
        "mtd_coupon_bill": mtd_data.total_coupon_bill
    }
    

def sale_kpi_get_data(business_branch, pos_profiles,working_date, type="Today"):
    sale_today_sql = """select 
                    coalesce(sum(s.grand_total),0) as total_revenue ,
                    coalesce(sum(s.total_quantity),0) as total_quantity,
                    coalesce(count(s.name),0) as total_bill
                from `tabSale` s 
                where 
                 s.docstatus = 1 and 
                (%(business_branch)s = '' or business_branch = %(business_branch)s)  

                """
    if type == "Today":
        sale_today_sql += " and s.posting_date = %(end_date)s"
    else:
        sale_today_sql += " and s.posting_date between %(start_date)s and %(end_date)s"

    if len(pos_profiles) > 0:
        sale_today_sql += " and (s.pos_profile in %(pos_profile)s or s.pos_profile is null)"

    data = frappe.db.sql(sale_today_sql, {
            "business_branch": business_branch,
            "pos_profile": pos_profiles,
            "start_date": type == "Today" and working_date or working_date.replace(day=1),
            "end_date": working_date,

        }, as_dict=1)  
    if data:
        data[0]["total_coupon"] = get_total_coupon_quantity_sale(business_branch, pos_profiles,working_date, type)
        data[0]["total_coupon_bill"] = get_total_sale_coupon_bill(business_branch, pos_profiles,working_date, type)
        return data[0]
    else:
        return {
            "total_revenue": 0,
            "total_quantity": 0,
            "total_bill": 0,
            "total_coupon":0,
            "total_coupon_bill":0
        } 


def get_total_coupon_quantity_sale(business_branch, pos_profiles,working_date, type="Today"): 
    sale_today_sql = """select 
                    sum(sp.quantity) as quantity
                from `tabSale Product` sp 
                inner join `tabSale` s on s.name = sp.parent
                where  
                    s.docstatus = 1 and 
                    s.sale_type = 'Sale Coupon' and
                    (%(business_branch)s = '' or s.business_branch = %(business_branch)s)  

                    """
    if type == "Today":
        sale_today_sql += " and s.posting_date = %(end_date)s"
    else:
        sale_today_sql += " and s.posting_date between %(start_date)s and %(end_date)s"


    if len(pos_profiles) > 0:
        sale_today_sql += " and (s.pos_profile in %(pos_profile)s or s.pos_profile is null)"

    data = frappe.db.sql(sale_today_sql, {
            "business_branch": business_branch,
            "pos_profile": pos_profiles,
            "start_date": type == "Today" and working_date or working_date.replace(day=1),
            "end_date": working_date,
        }, as_dict=1)  
    if data:
        return data[0]["quantity"]
    else:
        return 0

def get_total_sale_coupon_bill(business_branch, pos_profiles,working_date, type="Today"): 
    sale_today_sql = """select 
                   count(s.name) as total
                from  `tabSale` s 
                where  
                    s.docstatus = 1 and 
                    s.sale_type = 'Sale Coupon' and 
                    (%(business_branch)s = '' or s.business_branch = %(business_branch)s)  
                    """
    if type == "Today":
        sale_today_sql += " and s.posting_date = %(end_date)s"
    else:
        sale_today_sql += " and s.posting_date between %(start_date)s and %(end_date)s"

    

    if len(pos_profiles) > 0:
        sale_today_sql += " and (s.pos_profile in %(pos_profile)s or s.pos_profile is null)"

    data = frappe.db.sql(sale_today_sql, {
            "business_branch": business_branch,
            "pos_profile": pos_profiles,
            "start_date": type == "Today" and working_date or working_date.replace(day=1),
            "end_date": working_date,
        }, as_dict=1)  
    if data:
        return data[0]["total"]
    else:
        return 0


 

# param: {"param": {"pos_profiles":["POS Profile 01","POS Profile 02"], "business_branch":""}}
# @frappe.whitelist(allow_guest=True)
@frappe.whitelist()
def daily_sale_chart(param):
    p = get_param(param)
    business_branch  = p["business_branch"]
    working_date = p["working_date"]
    pos_profiles = p["pos_profiles"] 

    result = []
    for d in get_day_numbers(working_date.year, working_date.month):
        result.append({
            "day": d,
            "date": frappe.utils.formatdate(datetime.date(working_date.year, working_date.month, d), "yyyy-MM-dd"),
            "value": 0
        })

    sql = """select 	
                s.posting_date,
                sum(s.grand_total) as total_amount
            from `tabSale` s 
            where 1=1
            and s.docstatus = 1
            and s.posting_date between %(start_date)s and %(end_date)s """
    
    if (business_branch or "") != "":
        sql += " and s.business_branch = %(business_branch)s"

    if len(pos_profiles) > 0:
        sql += " and (s.pos_profile in %(pos_profile)s or s.pos_profile is null)"
        
    sql += " group by s.posting_date"
    
    data = frappe.db.sql(sql, {
        "business_branch": business_branch,
        "pos_profile": pos_profiles,
        "start_date":result[0]["date"] ,
        "end_date": result[-1]["date"] ,
        }, as_dict=1)
    

    for d in data:
      value =  [r for r in result if str(r["date"]) == str(d["posting_date"])] 
      if value:
        value[0]["value"] = d["total_amount"]

    return result



# param: {"param": {"pos_profiles":["POS Profile"],"business_branch":""}}
# @frappe.whitelist(allow_guest=True)
@frappe.whitelist()
def payment_breakdown(param):
    p = get_param(param)
    business_branch  = p["business_branch"]
    working_date = p["working_date"]
    pos_profiles = p["pos_profiles"] 

    sql = """select 
            sp.payment_type_group as `group`, 
            sp.payment_type,
            sum(sp.input_amount) as input_amount,
            sum(sp.payment_amount) as base_amount,
            sp.currency ,
            sp.currency_precision as `precision`,
            sp.symbol
        from `tabSale Payment`  sp
        where 1 = 1
        and sp.docstatus = 1
        and  sp.posting_date = %(end_date)s """
    if (business_branch or "") != "":
        sql += " and sp.business_branch = %(business_branch)s"

    if len(pos_profiles) > 0:
        sql += " and (sp.pos_profile in %(pos_profile)s or sp.pos_profile is null)"

    sql += " group by sp.payment_type_group, sp.payment_type, sp.currency, sp.currency_precision"
    data = frappe.db.sql(sql, {
        "business_branch": business_branch,
        "pos_profile": pos_profiles,   
        "end_date":working_date ,     
        }, as_dict=1)

     
    return data

@frappe.whitelist()
def get_sale_breakdown_by_coupon(param):
    p = get_param(param)
    business_branch  = p["business_branch"]
    working_date = p["working_date"]
 
    sql = """
        select
            sp.product_name,
            sum(if(s.sale_type='Top Up',0,sp.quantity)) as quantity,
            sum(sp.total_coupon_value) as total_coupon_value,
            sum(sp.amount) as total_amount
        from `tabSale Product` sp
        inner join `tabSale` s on s.name = sp.parent
        inner join `tabProduct` p on p.name = sp.product_code 
        where 
            s.docstatus = 1 and
            s.sale_type in ('Sale Coupon','Top Up') and  
            p.is_coupon = 1 and 
            s.posting_date = %(date)s and 
            (%(business_branch)s = '' or s.business_branch = %(business_branch)s)  
        group by 
            sp.product_name 

    """
    filters ={
        "date":working_date,
        "business_branch" : business_branch
    }
    data = frappe.db.sql(sql,filters,as_dict=1)
    return data

@frappe.whitelist()
def get_coupon_transaction_summary(param):
    p = get_param(param)
    business_branch  = p["business_branch"]
    working_date = p["working_date"]
    
    sql = """
        select 
            transaction_type,
            count(*) as total_transaction,
            sum(coupon_amount) as coupon_value
        from `tabCoupon Transaction`
       
        where 
            posting_date = %(date)s and 
            (%(business_branch)s = '' or business_branch = %(business_branch)s)  
        group by 
            transaction_type

    """
    filters ={
        "date":working_date,
        "business_branch" : business_branch
    }
    
    data = frappe.db.sql(sql,filters,as_dict=1)
    return_data = []
    transaction_type =  ["Sale Coupon","Top Up","Used","Redeem"]
    for t in transaction_type:
        exists = [d for d in data if d.get("transaction_type") == t]
        if exists:
            return_data.append(exists[0])
        else:
            return_data.append({
                "transaction_type":t,
                "total_transaction":0,
                "coupon_value":0
            })
    return_data.insert(2, {
         "transaction_type":"Sale + Top Up",
                "total_transaction":sum([d.get("total_transaction") for d in return_data if d.get("transaction_type") in ["Sale Coupon"]]),
                "coupon_value":sum([d.get("coupon_value") for d in return_data if d.get("transaction_type") in ["Sale Coupon","Top Up"]])
    })

    return return_data
 
@frappe.whitelist()
def testMe():
    params = {
        "business_branch": "ESTC HOTEL",
        "working_date": "2025-06-15",
        "pos_profiles": ""
        }
     
    return get_summary_coupon_used_by_pos_station(params)

@frappe.whitelist()
def get_summary_coupon_used_by_pos_station(param):
    p = get_param(param)
    business_branch  = p["business_branch"]
    working_date = p["working_date"]
    
    sql = """
       select 
            pos_station,
            sum(coupon_amount) as coupon_value,
            sum(actual_amount) as total_amount
        from `tabCoupon Transaction` 
        where
            transaction_type = 'Use' and
            posting_date = %(date)s and 
            (%(business_branch)s = '' or business_branch = %(business_branch)s)  
        group by 
            pos_station

    """
    filters ={
        "date":working_date,
        "business_branch" : business_branch
    }
    
    data = frappe.db.sql(sql,filters,as_dict=1)
    
    return data
 
