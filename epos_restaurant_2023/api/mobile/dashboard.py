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
        working_day_sql = """select max(posting_date) as posting_date from `tabWorking Day` where 1=1 """
        if not business_branch is "":
            working_day_sql += " and business_branch = %(business_branch)s"
        working_day_sql += " limit 1"
        
        working_day = frappe.db.sql(working_day_sql, {"business_branch": business_branch}, as_dict=1)

        if working_day and working_day[0]["posting_date"]:
            working_date = working_day[0]["posting_date"]
        else:
            now = datetime.datetime.now()
            current_date = now.date()
            working_date = current_date
    else:
        working_date = datetime.datetime.strptime(working_date, "%Y-%m-%d").date()

    return {"business_branch":business_branch,"working_date":working_date, "pos_profiles":pos_profiles, }

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
        "mtd_revenue": mtd_data.total_revenue,
        "mtd_bill": mtd_data.total_bill,
        "mtd_quantity": mtd_data.total_quantity,    
    }
    

def sale_kpi_get_data(business_branch, pos_profiles,working_date, type="Today"):
    sale_today_sql = """select 
                    coalesce(sum(s.grand_total),0) as total_revenue ,
                    coalesce(sum(s.total_quantity),0) as total_quantity,
                    coalesce(count(s.name),0) as total_bill
                from `tabSale` s 
                where 1=1
                and s.docstatus = 1"""
    if type == "Today":
        sale_today_sql += " and s.posting_date = %(end_date)s"
    else:
        sale_today_sql += " and s.posting_date between %(start_date)s and %(end_date)s"

    if not business_branch is "":
        sale_today_sql += " and s.business_branch = %(business_branch)s"

    if len(pos_profiles) > 0:
        sale_today_sql += " and (s.pos_profile in %(pos_profile)s or s.pos_profile is null)"

    data = frappe.db.sql(sale_today_sql, {
            "business_branch": business_branch,
            "pos_profile": pos_profiles,
            "start_date": type == "Today" and working_date or working_date.replace(day=1),
            "end_date": working_date,
        }, as_dict=1)  
    if data:
        return data[0]
    else:
        return {
            "total_revenue": 0,
            "total_quantity": 0,
            "total_bill": 0,
        } 


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
    
    if not business_branch is "":
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


@frappe.whitelist()
def testme():
    return payment_breakdown ({"business_branch":"ESTC HOTEL"}) 
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
    if not business_branch is "":
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