import json
import frappe
import calendar
import datetime

def get_day_numbers(year, month):
    _, num_days = calendar.monthrange(int( year), int(month))
    return list(range(1, num_days + 1))

def remove_key(data, keys= None):
    if   keys is None:
        keys = ["owner", "creation", "modified", "modified_by", "docstatus", "idx","_user_tags","_comments","_assign","_liked_by"]
    
    if isinstance(data, dict):
        return {
            k: remove_key(v, keys) if isinstance(v, (dict, list)) else v
            for k, v in data.items() if k not in keys
        }

    elif isinstance(data, list):
        return [remove_key(item, keys) for item in data]


@frappe.whitelist(methods=["POST"])
def app_settings(params): 
    result = {}

    ## get pos station
    ignore = True
    if params.get("station_name"): 
        station = frappe.get_doc("POS Station", params.get("station_name")) 
        
        if not station or station.disabled:
            ignore = False  
    else:
        ignore = False

    if not ignore:
        stations = frappe.db.sql("select name from `tabPOS Station` where device_id = %(device_id)s and platform <> 'Web' and disabled = 0 limit 1", {"device_id":params["device_id"]}, as_dict=1)
  
 
        if not stations or len(stations) == 0:
            frappe.throw("Invalid device station")
           
        station = frappe.get_doc("POS Station", stations[0]["name"])

    station_doc = remove_key(station.as_dict()) 

    ## end get pos station
    ## get shift type
    shift_types = frappe.get_all(
        "Shift Type",
        fields=["*"],
        filters={"show_in_pos": 1},
        order_by="sort asc"
    ) 
    _shift_types = []
    for st in shift_types:
        st_doc = remove_key(st) 
        _shift_types.append(st_doc) 

    result["pos_station"] = station_doc
    result["shift_types"] = _shift_types
    result["socketio"] = {
        "port":frappe.get_conf().get('socketio_port', 9000),
        "site_name": frappe.local.site
    }
    main_currency = frappe.get_doc("Currency",frappe.db.get_default("currency"))
    currency = remove_key(main_currency.as_dict())
    currency["precision"] = currency.pop("custom_currency_precision")
    currency["format"] = currency.pop("custom_pos_currency_format")
    currency["is_right"] = currency.pop("symbol_on_right")
    currency["exchange_rate"] = 1
    currency["change_exchange_rate"] = 1

    del currency["currency_name"]
    del currency["fraction"]
    del currency["fraction_units"]
    del currency["smallest_currency_fraction_value"]
    del currency["doctype"]
    del currency["custom_locale"]
    del currency["enabled"]

    result["main_currency"] =  currency

    currencies = frappe.db.get_list("Currency",fields=["name","symbol","number_format","symbol_on_right","custom_currency_precision","custom_pos_currency_format"], filters= {"enabled":1})
    # Rename fields
    for c in currencies:
        exchange_rate = 0
        change_exchange_rate = 0
        if c["name"] == currency["name"]:
            exchange_rate = 1
            change_exchange_rate = 1
        else:
            sql_exchange_rate = """select 
                    exchange_rate, 
                    change_exchange_rate 
                from `tabCurrency Exchange` 
                where from_currency = %(from_currency)s 
                    and to_currency = %(to_currency)s 
                    and docstatus = 1 
                order by posting_date desc, creation desc limit 1"""
            exch = frappe.db.sql(sql_exchange_rate,{
                "from_currency":currency["name"],
                "to_currency":c["name"]
                },as_dict=1)
            if exch:
                exchange_rate = exch[0]["exchange_rate"] 
                change_exchange_rate = exch[0]["change_exchange_rate"]
            else:    
                exchange_rate = 1
                change_exchange_rate = 1

        c["precision"] = c.pop("custom_currency_precision")
        c["format"] = c.pop("custom_pos_currency_format")
        c["is_right"] = c.pop("symbol_on_right")
        c["exchange_rate"] = exchange_rate
        c["change_exchange_rate"] = change_exchange_rate

    result["currencies"] = currencies

    
    return result

@frappe.whitelist(methods=["POST"])
def get_shift_information(params): 
    sql  = "select * from `tabCoupon Shift` where is_closed = 0 and  business_branch = %(business_branch)s and pos_profile = %(pos_profile)s limit 1"
    result = frappe.db.sql(sql, {"business_branch":params["business_branch"], "pos_profile":params["pos_profile"]}, as_dict=1)
    if not result or len(result) == 0:
        return {"data":None, "error": "No shift available"}
    
    doc = remove_key(result[0])
    return {"data":doc, "error":None}


@frappe.whitelist(methods=["POST"])
def get_history_coupon_kpi(params):
    sql = """select 
            coalesce(sum(coupon_amount),0) as total_amount ,
            count(*) as total_transaction
        from `tabCoupon Transaction` 
        where 1 = 1
        and pos_profile = %(pos_profile)s
        and business_branch = %(property_name)s
        and (date(posting_date) between date(%(start_date)s) and date(%(end_date)s))
        and  transaction_type in ('Use')"""
   
    if params.get("keyword"):
        sql += " and coupon_number like %(keyword)s"
        # params["keyword"] = f"%{params['keyword']}%"
     
 
    data = frappe.db.sql(sql, {
        "pos_profile":params["pos_profile"], 
        "property_name":params["property_name"], 
        "start_date":params["start_date"], 
        "end_date":params["end_date"],
        "keyword":params["keyword"],
    }, as_dict=1) 

    if(not data or len(data) == 0):
        return {"total_transaction":0, "total_amount":0}
    else:
        return data[0] 

@frappe.whitelist(methods=["POST"])
def get_coupon_dashboard_kpi(params):
    property_name = params["property_name"]
    pos_profile = params["pos_profile"]
    now = datetime.datetime.now().date()
    start_date = now if type == "Today" else now.replace(day=1)
    

    today_data = coupon_kpi_get_data(property_name, pos_profile)
    mtd_data = coupon_kpi_get_data(property_name, pos_profile,type="MTD")
 

    return {
        "today_amount": today_data.total_amount,
        "today_transaction": today_data.total_transaction,
        "mtd_amount": mtd_data.total_amount,
        "mtd_transaction": mtd_data.total_transaction,  
    }


 

def coupon_kpi_get_data(property_name, pos_profiles, type="Today"):
    sql = """select 
                    coalesce(sum(coupon_amount),0) as total_amount ,
                    count(*) as total_transaction
            from `tabCoupon Transaction` 
            where 1 = 1
            and transaction_type in ('Use')
            and pos_profile = %(pos_profile)s
            and business_branch = %(property_name)s """
    if type == "Today":
        sql += " and date(posting_date) = date(%(end_date)s)"
    else:
        sql += " and (date(posting_date) between date(%(start_date)s) and date(%(end_date)s))"

  
    now = datetime.datetime.now().date()
    start_date = now if type == "Today" else now.replace(day=1)

   
    data = frappe.db.sql(sql, {
            "property_name": property_name,
            "pos_profile": pos_profiles,
            "start_date": start_date,
            "end_date": now,
        }, as_dict=1)  
    if data:
        
        return data[0]
    else:
        return {
            "total_amount": 0,
            "total_transaction": 0,
        } 
    


@frappe.whitelist()
def daily_scan_coupon_chart(params): 
    property_name  = params["property_name"] 
    pos_profile = params["pos_profile"] 

    now = datetime.datetime.now().date()
    result = []
    for d in get_day_numbers(now.year, now.month):
        result.append({
            "day": d,
            "date": frappe.utils.formatdate(datetime.date(now.year, now.month, d), "yyyy-MM-dd"),
            "value": 0
        })

    sql = """select 
                    coalesce(sum(coupon_amount),0) as total_amount ,
                    posting_date
            from `tabCoupon Transaction` 
            where 1 = 1
            and transaction_type in ('Use')
            and pos_profile = %(pos_profile)s
            and business_branch = %(property_name)s 
            and (date(posting_date) between date(%(start_date)s) and date(%(end_date)s))"""        
        
    sql += " group by posting_date"
    
    data = frappe.db.sql(sql, {
        "property_name": property_name,
        "pos_profile": pos_profile,
        "start_date":result[0]["date"] ,
        "end_date": result[-1]["date"] ,
        }, as_dict=1)
    

    for d in data:
      value =  [r for r in result if str(r["date"]) == str(d["posting_date"])] 
      if value:
        value[0]["value"] = abs( d["total_amount"])

    return result



@frappe.whitelist()
def check_coupon_code(coupon_number): 
    sql  = """select 
                sum(coupon_amount) as coupon_amount
            from `tabCoupon Transaction` 
            where `status` = 'Active' 
            and coupon_number = %(coupon_number)s""" 
    data = frappe.db.sql(sql, {"coupon_number":coupon_number}, as_dict=1)
    if data and len(data) > 0:
        cus_sql = """select 
            customer,
            customer_name,
            customer_photo
        from `tabCoupon Transaction` 
        where transaction_type = 'Sale Coupon' 
            and coupon_number = %(coupon_number)s 
            and status = 'Active' 
        order by creation desc 
        limit 1"""
        cus = frappe.db.sql(cus_sql, {"coupon_number":coupon_number}, as_dict=1)
        if cus and len(cus) > 0:
            return {
                "card":coupon_number,
                "cid":cus[0]["customer"], 
                "cname":cus[0]["customer_name"], 
                "cimage":cus[0]["customer_photo"],
                "amount":data[0]["coupon_amount"]
            }
        else:
            return None 


## params = {
    # "coupon_number":"100007",
    #    "currency":"KHR",
    #    "input_coupon_amount":20000, 
    #    "exchange_rate": 4000,
    #    "created_by":"Administrator",
    #    "pos_profile":"Main POS Profile",
    #    "pos_station":"DOM-PC 01",
    #    "posting_date":"2025-06-24",
    #    "coupon_shift":"CPN25-0002",
    #    "transaction_date":"2025-06-24 10:57:56.926061"
# }
@frappe.whitelist()
def on_scan_use_coupon(params):
    coupon_amount = params["input_coupon_amount"] / params["exchange_rate"] or 1
    data = check_coupon_code(params["coupon_number"])
    if data:
        if(data["amount"] < coupon_amount):
            frappe.throw("Not enough amount")
        else:
            sql_coupon_transactions = """select 
                    markup_percentage,
                    sum(coupon_amount) as coupon_amount 
            from `tabCoupon Transaction` 
            where coupon_number = %(coupon_number)s
            and `status` = 'Active' 
            group by markup_percentage"""
            transactions = frappe.db.sql(sql_coupon_transactions, {"coupon_number":params["coupon_number"]}, as_dict=1)
            result = []
            if transactions and len(transactions) > 0: 
                for t in transactions: 
                    sql_transaction = """select  
                        markup_percentage,
                        sum(coupon_amount) as coupon_amount   
                    from `tabCoupon Transaction` 
                    where status = 'Active'
                    and markup_percentage = %(markup_percentage)s
                    and coupon_number = %(coupon_number)s
                    group by markup_percentage
                    limit 1"""
                    transaction = frappe.db.sql(sql_transaction, {"markup_percentage":t["markup_percentage"], "coupon_number":params["coupon_number"]}, as_dict=1)                    
                    if transaction and len(transaction) > 0:
                        sql_last_sale_or_topup = """
                                            select 
                                                    `name`,
                                                    markup_percentage,
                                                    transaction_type,
                                                    working_day,
                                                    cashier_shift,
                                                    customer,
                                                    customer_name,
                                                    coupon_code
                                            from `tabCoupon Transaction` 
                                            where coupon_number = %(coupon_number)s
                                            and `status` = 'Active' 
                                            and markup_percentage = %(markup_percentage)s
                                            and transaction_type in ('Sale Coupon', 'Top Up')
                                            order by creation desc
                                            limit 1"""
                        last_sale_or_topup = frappe.db.sql(sql_last_sale_or_topup, {"markup_percentage":t["markup_percentage"], "coupon_number":params["coupon_number"]}, as_dict=1)
                        if last_sale_or_topup and len(last_sale_or_topup) > 0: 
                                item = last_sale_or_topup[0]  
                                if t["coupon_amount"] - coupon_amount < 0:
                                    coupon_amount -= t["coupon_amount"]
                                    item["cut_amount"]  = t["coupon_amount"]  
                                    item["used"]  = True  
                                    result.append(item) 
                                    pass ## pass here to loop again
                                else: 
                                    item["cut_amount"] = coupon_amount
                                    item["used"] = False
                                    if t["coupon_amount"] == coupon_amount:
                                        item["used"]  = True  
                                    
                                    result.append(item) 
                                    break ## break here to stop loop


                                # return {"x":last_sale_or_topup[0],"y":transaction[0]["coupon_amount"]}

                        # return {"x": transaction}
            # return result
            if result and len(result) > 0:
                for r in result:
                    actual_amount = r["cut_amount"] / (1+(r["markup_percentage"]/100)) 
                    doc = frappe.get_doc({
                        "doctype":"Coupon Transaction",
                        "business_branch":params["business_branch"],
                        "status": "Locked" if r["used"] else "Active", 
                        "transaction_type":"Use",
                        "input_coupon_amount":r["cut_amount"] * params["exchange_rate"],
                        "input_actual_amount":actual_amount * params["exchange_rate"], 
                        "exchange_rate":params["exchange_rate"],
                        "cashier_shift":r["cashier_shift"],
                        "customer":r["customer"],
                        "coupon_code":r["coupon_code"],
                        "coupon_number":params["coupon_number"],
                        "pos_profile":params["pos_profile"],
                        "pos_station":params["pos_station"],
                        "posting_date": params["posting_date"],
                        "coupon_shift":params["coupon_shift"],
                        "transaction_date":params["transaction_date"],
                        "markup_percentage":r["markup_percentage"],
                        "working_day":r["working_day"],
                        "currency":params["currency"],
                        "used_from_transaction":r["name"],
                        "customer_name":   r["customer_name"]           
                        })
                    doc.insert()

                return result
            
    
    else:
        frappe.throw("Invalid coupon number")


 