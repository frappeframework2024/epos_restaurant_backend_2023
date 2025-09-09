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


@frappe.whitelist(methods=["POST"],allow_guest=True)
def app_settings(params): 
    result = {}
    ignore_permissions=True
    

    ## get pos station
    ignore = True
    if params.get("station_name"): 
        station = frappe.get_doc("POS Station", params.get("station_name"), ignore_permissions=ignore_permissions) 
        
        if not station or station.disabled:
            ignore = False  
    else:
        ignore = False

    if not ignore:
        stations = frappe.db.sql("select name from `tabPOS Station` where device_id = %(device_id)s and platform <> 'Web' and disabled = 0 limit 1", {"device_id":params["device_id"]}, as_dict=1)
  
 
        if not stations or len(stations) == 0:
            frappe.throw("Invalid device station")
           
        station = frappe.get_doc("POS Station", stations[0]["name"],ignore_permissions=ignore_permissions)

    station_doc = remove_key(station.as_dict()) 

    ## end get pos station
    ## get shift type
    shift_types = frappe.get_all(
        "Shift Type",
        fields=["*"],
        filters={"show_in_pos": 1},
        order_by="sort asc",
        ignore_permissions=ignore_permissions
    ) 
    _shift_types = []
    for st in shift_types:
        st_doc = remove_key(st) 
        _shift_types.append(st_doc) 

    result["pos_station"] = station_doc
    result["pos_station"]["use_coupon_encrypt"] = int(frappe.db.get_default("use_coupon_encrypt") or 0)

    result["shift_types"] = _shift_types
    result["socketio"] = {
        "port":frappe.get_conf().get('socketio_port', 9000),
        "site_name": frappe.local.site
    }
    default_currency = frappe.db.get_default("currency")
    exchange_rate_main_currency = frappe.db.get_default("exchange_rate_main_currency")
    main_currency = frappe.get_doc("Currency",default_currency,ignore_permissions=ignore_permissions)
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

    currencies = frappe.db.get_list("Currency",
                                    fields=["name","symbol","number_format","symbol_on_right","custom_currency_precision","custom_pos_currency_format"], 
                                    filters= {"enabled":1},
                                    ignore_permissions=ignore_permissions
                                    )
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
                "from_currency":c["name"],
                "to_currency":currency["name"]
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
        and  transaction_type in ('Used')
        and status in ('Active','Locked')"""
   
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
            and transaction_type in ('Used')
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
            and transaction_type in ('Used')
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
    coupon = """select name,coupon from `tabCoupon Codes` where coupon = %(coupon_number)s and coupon_status = 'Used' limit 1""" 
    coupon_data = frappe.db.sql(coupon, {"coupon_number":coupon_number}, as_dict=1)
    
    if coupon_data and len(coupon_data) > 0:
       pass
    else:
        return {
            "status":False,
            "msg":"Invalid coupon number",
            "data":None
        }
    coupon_id = coupon_data[0]["name"]
    sql  = """select 
                coalesce(sum(coupon_amount) , 0) as coupon_amount
            from `tabCoupon Transaction` 
            where 
            coupon_code = %(coupon_code)s and 
            coupon_number = %(coupon_number)s""" 
    data = frappe.db.sql(sql, {"coupon_number":coupon_number,"coupon_code":coupon_id}, as_dict=1)    


    if data and len(data) > 0: 
        if data[0].get("coupon_amount",0) <= 0:
            return {
                "status":False,
                "msg":"Current balance is empty",
                "data":None
            }
         
        cus_sql = """select 
            customer,
            customer_name,
            customer_photo
        from `tabCoupon Transaction` 
        where transaction_type in ( 'Sale Coupon','Top Up') 
            and coupon_number = %(coupon_number)s 
            and coupon_code = %(coupon_code)s
            and status = 'Active' 
        order by creation desc 
        limit 1"""
        cus = frappe.db.sql(cus_sql, {"coupon_number":coupon_number, "coupon_code":coupon_id}, as_dict=1) 
        if cus and len(cus) > 0:
            return {
                "status":True,
                "msg":"Success",
                "data":{
                    "cardid":coupon_data[0].get("name",None),
                    "card":coupon_number,
                    "cid":cus[0]["customer"], 
                    "cname":cus[0]["customer_name"], 
                    "cimage":cus[0]["customer_photo"],
                    "amount":data[0]["coupon_amount"]
                }
            }
        else: 
            return {
                "status":False,
                "msg":"Invalid coupon number",
                "data":None
            }
    else:
        return {
            "status":False,
            "msg":"Invalid coupon number",
            "data":None
        }

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
def short_hex_uuid(length=12):
    import uuid
    return uuid.uuid4().hex[:length]

@frappe.whitelist()
def on_scan_use_coupon(params):
    import uuid
    transaction_id = short_hex_uuid()  
    # check if valid coupon number

    # end change coupon

    working_day_sql = """select name,posting_date from `tabWorking Day` where business_branch = %(business_branch)s and is_closed = 0 order by creation desc limit 1"""
    working_days = frappe.db.sql(working_day_sql, {"business_branch": params["business_branch"]}, as_dict=1) 
    if not working_days or len(working_days) <=0:
        frappe.throw("Counter was close working day")
    
    working_day = working_days[0]



    coupon_amount = params["input_coupon_amount"] / (params["exchange_rate"] or 1)
    original_coupon_amount = coupon_amount

    check = check_coupon_code(params["coupon_number"])


    if not check.get("status",False):
        frappe.throw(check.get("msg","Not enough balance"))

    data = check.get("data",None)
    if data:
        if(data["amount"] < coupon_amount):
            frappe.throw("Not enough balance")
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
                                                    customer_photo,
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
                customer = {
                    "customer":"",
                    "customer_name":"",
                    "photo":""
                }
                for r in result:
                    customer["customer"] = r["customer"]
                    customer["customer_name"] = r["customer_name"]  
                    customer["photo"] = r["customer_photo"]
                    ##
                    actual_amount = r["cut_amount"] / (1+(r["markup_percentage"]/100)) 
                    doc = frappe.get_doc({
                        "doctype":"Coupon Transaction",
                        "business_branch":params["business_branch"],
                        "status": "Locked" if r["used"] else "Active", 
                        "transaction_type":"Used",
                        "input_coupon_amount": (-1)* (r["cut_amount"] * params["exchange_rate"]),
                        "input_actual_amount":(-1)* (actual_amount * params["exchange_rate"]), 
                        "exchange_rate":params["exchange_rate"],
                        "customer":r["customer"],
                        "coupon_code":r["coupon_code"],
                        "coupon_number":params["coupon_number"],
                        "pos_profile":params["pos_profile"],
                        "pos_station":params["pos_station"],
                        "posting_date": working_day["posting_date"],
                        "working_day":working_day["name"],
                        "coupon_shift":params["coupon_shift"],
                        "transaction_date":params["transaction_date"],
                        "markup_percentage":r["markup_percentage"],
                        "currency":params["currency"],
                        "used_from_transaction":r["name"],
                        "customer_name":  r["customer_name"],
                        "used_transaction_id":transaction_id,
                        "original_used_amount": original_coupon_amount * -1,
                        "created_by":params["created_by"],
                        "note":params["remark"],
                        })
                    doc.insert()

                    ## update coupon transaction status to locked
                    if r["used"]:
                        frappe.db.sql("""update `tabCoupon Transaction` 
                                        set status = 'Locked' 
                                        where name = %(name)s""", {"name":r["name"]})


                return_data = params.copy()
                return_data["original_used_amount"] = original_coupon_amount
                return_data["used_transaction_id"] = transaction_id
                return_data["customer_name"] = customer["customer_name"]
                return_data["customer"] = customer["customer"]
                return_data["customer_photo"] = customer["photo"]


                ##update use coupon/amount  to coupon code
                update_use_coupon_amount(data.get("cardid",None))


                ## update to locked transaction
                sql_update = """select 
                        coalesce(sum(coupon_amount) , 0) as coupon_amount
                    from `tabCoupon Transaction` 
                    where 1= 1
                    and coupon_number = %(coupon_number)s"""
                check_for_locked = frappe.db.sql(sql_update, {"coupon_number":params["coupon_number"]}, as_dict=True)
                if check_for_locked and len(check_for_locked)> 0:
                    if check_for_locked[0]["coupon_amount"] == 0:
                        frappe.db.sql("""update `tabCoupon Transaction` 
                                        set status = 'Locked' 
                                        where status != 'Locked' and coupon_number = %(coupon_number)s""", {"coupon_number":params["coupon_number"]})

                
                return return_data
            
            else:   
                frappe.throw("Invalid coupon number")
    
    else:
        frappe.throw("Invalid coupon number")


@frappe.whitelist(methods=["POST"])
def get_report(name, show_transaction):  

    ## data_type = label, table
    doc = frappe.get_doc("Coupon Shift", name)
    info = {"key":[],"type":[],"value":[]}
    summary = {"key":[],"type":[],"value":[]}
    result = {}
    
    if doc.is_closed:
        info = {
            "key":["Closed station","Closed at","Opened by"],
            "type":["data","datetime","data"],
            "value":[doc.station_closed, doc.close_date,doc.close_by]
        }

    #get summary
    sql_summary = """select 
        coalesce(sum(actual_amount) , 0)*(-1) as total_actual_amount,
        coalesce(sum(coupon_amount) , 0) *(-1)  as total_coupon_amount,
        count(`name`) as total_record
    from `tabCoupon Transaction` 
    where 1=1
    and transaction_type in ('Used')
    and coupon_shift = %(name)s"""
    summary_data = frappe.db.sql(sql_summary, {"name":name}, as_dict=1)
    if summary and len(summary_data) > 0:
        summary_data = summary_data[0]
        summary["key"] = ["Transactions","Coupon Amount","Actual Amount"]
        summary["type"] = ["int","currency","currency"]
        summary["value"] = [summary_data["total_record"],summary_data["total_coupon_amount"],summary_data["total_actual_amount"]]

    if show_transaction:
        transctions = {"data":{}}
        sql_transactions = """select 
            name,
            coupon_number,
            creation,
            coupon_amount,
            created_by
        from `tabCoupon Transaction` 
        where 1=1
        and transaction_type in ('Used')
        and coupon_shift = %(name)s
        order by creation desc"""   
        transction_data = frappe.db.sql(sql_transactions, {"name":name}, as_dict=1) 
        
        transctions["data"] = {
            "header":[
                "No","Coupon","Date","Amount","By"
                    
            ],
            "type":["int","data","time","currency","data"],
            "align":["center","left","left","right","left"],
            "width":[20.0,0.0,60.0,60.0,60.0],
            "data":[
                [i + 1, d["coupon_number"], d["creation"], abs(d["coupon_amount"]), d["created_by"]] for i, d in enumerate(transction_data)
            ]
        }

        ## update result transaction 
        result["Trasactions"] =  { 
            "data":transctions["data"],
            "data_type":"table",
            "sort":99
        }

    

    # set info to result
    result["Info"] = {
        "key":[ 
            "Date",
            "POS Profile",
            "Opened station",
            "Opened at",
            "Opened by",
            "Shift name",
            "Status",
            *info["key"]
        ],
        "type":["date", "data", "data","datetime","data", "data", "data",*info["type"]],
        "value":[
            doc.posting_date,
            doc.pos_profile,
            doc.station_opened,
            doc.creation,
            doc.open_by,
            doc.shift_name,
            "Closed" if doc.is_closed else "Opening",
            *info["value"]
        ], 
        "data_type":"label",
        "sort":0
    }

    # set summary to result
    result["Summary"] = { 
        "key":[*summary["key"]],
        "type":[*summary["type"]],
        "value":[*summary["value"]],
        "data_type":"label",
        "sort":1
    }

    sorted_data = dict(sorted(result.items(), key=lambda x: x[1].get("sort", 99999)))   
 
 
    return sorted_data

@frappe.whitelist(methods=["POST"])
def get_transaction_detail(name):
    doc = frappe.get_doc("Coupon Transaction", name)
    sql = """select 
            business_branch,
            customer_name,
            coupon_number,
            customer,
            customer_photo,
            currency,
            exchange_rate,
            created_by,
            pos_profile,
            pos_station,
            coupon_shift,
            transaction_date,
            note as remark,
            original_used_amount,
            used_transaction_id,
            sum(input_coupon_amount) as input_coupon_amount
    from `tabCoupon Transaction` 
    where 1 = 1
    and used_transaction_id = %(used_transaction_id)s
    GROUP BY used_transaction_id"""
    data = frappe.db.sql(sql, { "used_transaction_id":doc.used_transaction_id}, as_dict=1)
    if data and len(data) > 0:
        # data[0]["input_coupon_amoun"] = abs(data[0]["input_coupon_amoun"])
        data[0]["original_used_amount"] = abs(data[0]["original_used_amount"])
        return data[0]
    
    frappe.throw("Invalid transaction")


@frappe.whitelist(methods=["POST"])
def delete_transaction(transaction_id): 
    sql = """select coupon_code, name,coupon_shift , used_from_transaction from `tabCoupon Transaction` where used_transaction_id = %(used_transaction_id)s"""
    data = frappe.db.sql(sql, { "used_transaction_id":transaction_id}, as_dict=1)

    use_from = []
    if data and len(data) > 0:
        check_shift = frappe.db.sql("""select count(name) as total_shift from `tabCoupon Shift` where name in %(name)s and is_closed = 1""",{"name":[d["coupon_shift"] for d in data]},as_dict=1)
        if check_shift and len(check_shift) > 0:
            if check_shift[0].total_shift > 0:
                frappe.throw("This transaction is used by a closed shift and can not be deleted")
        for d in data:
            delete_doc = frappe.get_doc("Coupon Transaction", d["name"])
            delete_doc.status = "Deleted"
            delete_doc.save()   
            use_from.append(d["used_from_transaction"])        
        frappe.db.commit()
        frappe.db.sql("""update `tabCoupon Transaction` set status = 'Active' where name in %(names)s""",{"names":use_from})

        update_use_coupon_amount(data[0].get("coupon_code",None))
    return "Deleted"


@frappe.whitelist()
def update_use_coupon_amount(coupon_code):
    sql = """select 
                abs(coalesce(sum(coupon_amount),0)) as coupon_amount, 
                abs(coalesce(sum(actual_amount),0)) as actual_amount
            from `tabCoupon Transaction` 
            where coupon_code =%(coupon_code)s 
                and status in ('Active','Locked') 
                and transaction_type = 'Used'"""
    data = frappe.db.sql(sql,{"coupon_code":coupon_code}, as_dict=1)

    if data and len(data)>0:
        sql = """update `tabCoupon Codes` set 
                    use_coupon_value = %(coupon_amount)s,
                    use_amount = %(actual_amount)s,
                    balance_amount = (price + top_up_amount)  -   (%(actual_amount)s + redeem_amount),
                    balance_coupon_value = (coupon_value + top_up_coupon_value)  -  (%(coupon_amount)s + redeem_coupon_value )
                    where name = %(coupon_code)s"""
        frappe.db.sql(sql,{
            "coupon_code":coupon_code,
            "coupon_amount":data[0].get("coupon_amount",0),
            "actual_amount":data[0].get("actual_amount",0)
        })
        frappe.db.commit()


@frappe.whitelist( methods=['POST'])
def get_store_account(pos_profile): 
    pression = 2
    default_vendor = frappe.get_value("POS Profile",pos_profile,"default_vendor")
    sql = """select 
        abs( sum(actual_amount)) as total_actual_amount,
        abs(sum(coupon_amount)) as total_coupon_amount
    from `tabCoupon Transaction` 
    where pos_profile = %(pos_profile)s 
    and transaction_type in ('Used')
    and status in ('Active','Locked')"""
    data = frappe.db.sql(sql,{"pos_profile":pos_profile},as_dict=1)
    if data:
        total_coupon_amount =round( data[0].get("total_coupon_amount",0),pression)
        total_actual_amount = round( data[0].get("total_actual_amount",0),pression)
        available_balance = total_actual_amount

        sql_vendor = """select sum(payment_amount) as total_withdrawal from `tabStore Payment` where vendor = %(vendor)s"""
        data_vendor = frappe.db.sql(sql_vendor,{"vendor":default_vendor},as_dict=1)
        if data_vendor:            
            total_withdrawal = round( data_vendor[0].get("total_withdrawal",0),pression)
            available_balance = round( total_actual_amount - total_withdrawal,pression)
            return {
                "actual_amount":total_actual_amount,   
                "coupon_amount":total_coupon_amount,
                "withdrawal":total_withdrawal,
                "available_balance":available_balance
            }   

        return {
            "actual_amount":total_actual_amount,   
            "coupon_amount":total_coupon_amount,
            "withdrawal":0,
            "available_balance":available_balance
        }

    return {
        "actual_amount":0,  
        "coupon_amount":0,
        "withdrawal":0,
        "available_balance":0
    }


@frappe.whitelist( methods=['POST'])
def get_store_payment(param):
    pression = 2
    default_vendor = frappe.get_value("POS Profile",param["pos_profile"],"default_vendor")
    sql_vendor = """select name, posting_date, payment_amount as withdrawal, modified from `tabStore Payment` where vendor = %(vendor)s order by posting_date desc, modified desc limit 1"""
    if param.get("start_date") and param.get("end_date"):
        sql_vendor += " and posting_date between %(start_date)s and %(end_date)s"
    
    data_vendor = frappe.db.sql(sql_vendor,{"vendor":default_vendor},as_dict=1)

    return data_vendor

