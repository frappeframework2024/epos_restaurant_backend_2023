import frappe
from frappe import _
import datetime
@frappe.whitelist()
def check_coupon_code(coupon_code):
    data = frappe.db.get_list('Coupon Codes', filters={
        'coupon':  coupon_code
    },
    fields=["name","coupon","coupon_status"]
    )
    
    if not data:
        frappe.throw(_("Coupon code not found"))
    else:
        
        if data[0].get("coupon_status") =='Unused': 
            frappe.throw(_("This is an unused coupon code. Please use options Sale Coupon to issue this coupon to customer"))
        elif data[0].get("coupon_status") =='Redeemed':
            frappe.throw(_("This coupon code is already redeemed"))
        elif data[0].get("coupon_status") =='Expired':
            frappe.throw(_("This coupon code is already expired"))

    
    sql = """select 
        coupon_code,
        coupon_number,transaction_date,sale,posting_date,
        input_actual_amount,
        input_coupon_amount,
        currency, 
        product_code
    from `tabCoupon Transaction` 
    where 
        coupon_number=%(coupon_number)s and 
        transaction_type = "Sale Coupon" 
    limit 1
    """
    coupon_info = frappe.db.sql(sql,{"coupon_number":coupon_code},as_dict=1)
    customer_photo,customer_group,phone_number,customer,customer_name = frappe.get_cached_value("Sale",coupon_info[0].get("sale"),["customer_photo","customer_group","phone_number","customer","customer_name"])  
    coupon_info[0]["customer"] = {
        "name":customer,
        "customer_name":customer_name,
        "customer_group":customer_group,
        "phone_number":phone_number,
        "photo":customer_photo
    }

    if coupon_info:
        if coupon_info[0].get("product_code"):
            product_name,photo = frappe.get_cached_value("Product",coupon_info[0].get("product_code"),["product_name_en","photo"]) 
            
            coupon_info[0]["product_name"] = product_name
            coupon_info[0]["photo"] = photo
            
        coupon_info =  coupon_info[0]
    
    # get balance data
    sql = """
        select 
            transaction_type,
            markup_percentage,
            sum(coupon_amount) as coupon_amount 
        from `tabCoupon Transaction` 
        where 
        coupon_number=%(coupon_number)s
        group by
            transaction_type,
            markup_percentage
    """
    data = frappe.db.sql(sql,{"coupon_number":coupon_code},as_dict=1)

    coupon_info["coupon_transaction"] = data
    coupon_info["coupon_balance"] = sum([d.get("coupon_amount") for d in data])
    coupon_info["actual_amount_balance"] = get_coupon_actual_amount_balance(data)
    
    return  coupon_info


@frappe.whitelist()
def get_coupon_detail(coupon_code):
    #coupon code here is primary key
    return_data = {}

    return_data["coupon_info"] = frappe.get_cached_doc("Coupon Codes",coupon_code)
    
    if return_data["coupon_info"].customer:
        customer_photo,customer_group,phone_number,customer,customer_name = frappe.get_cached_value("Customer",return_data["coupon_info"].customer,["photo","customer_group","phone_number","name","customer_name_en"])    
        return_data["customer"] = {
            "name":customer,
            "customer_name":customer_name,
            "customer_group":customer_group,
            "phone_number":phone_number,
            "photo":customer_photo
        }

 
    # get balance data
    sql = """
        select 
            sale,
            creation,
            posting_date,
            created_by,
            transaction_date,
            note,
            transaction_type,
            markup_percentage,
            input_actual_amount,
            coupon_amount ,
            pos_station,
            pos_profile,
            currency,
            exchange_rate
        from `tabCoupon Transaction` 
        where 
        coupon_code=%(coupon_code)s and 
        status not in ('Deleted')
        order by creation
    """
    data = frappe.db.sql(sql,{"coupon_code":coupon_code},as_dict=1)


    return_data["coupon_transaction"] = data
    return_data["coupon_balance"] = sum([d.get("coupon_amount") for d in data])
    return_data["actual_amount_balance"] = get_coupon_actual_amount_balance(data)
    
    return  return_data

@frappe.whitelist()
def check_coupon_code_for_top_up(coupon_code):
    if not frappe.db.exists("Coupon Codes",{"coupon":coupon_code}):
        frappe.throw(_("Coupon code not found"))


    data = frappe.db.get_list('Coupon Codes', filters={
        'coupon':  coupon_code,
        "coupon_status":"Used"
    },
    fields=["name","coupon","coupon_status","expired_date"]
    )
    if not data:
        frappe.throw(_("This coupon number is not a used coupon number"))

    if   datetime.datetime.now() > data[0].expired_date:
        frappe.throw(_("This coupon code is expired"))


    sql = """select 
        coupon_code,
        coupon_number,transaction_date,sale,posting_date,
        input_actual_amount,
        input_coupon_amount,
        currency, 
        product_code
    from `tabCoupon Transaction` 
    where 
        coupon_code=%(coupon_code)s and  
        transaction_type = "Sale Coupon" 
    limit 1
    """
   
    coupon_info = frappe.db.sql(sql,{"coupon_code":data[0].name},as_dict=1) 
 
    customer_photo,customer_group,phone_number,customer,customer_name = frappe.get_cached_value("Sale",coupon_info[0].get("sale"),["customer_photo","customer_group","phone_number","customer","customer_name"])  
    coupon_info[0]["customer"] = {
        "name":customer,
        "customer_name":customer_name,
        "customer_group":customer_group,
        "phone_number":phone_number,
        "photo":customer_photo
    }

    if coupon_info:
        if coupon_info[0].get("product_code"):
            product_name,photo = frappe.get_cached_value("Product",coupon_info[0].get("product_code"),["product_name_en","photo"]) 
            
            coupon_info[0]["product_name"] = product_name
            coupon_info[0]["photo"] = photo
            
        coupon_info =  coupon_info[0]
    
    # get coupon transaction
    sql = """
        select 
            transaction_type,
            markup_percentage,
            sum(input_actual_amount) as input_actual_amount,
            sum(coupon_amount) as coupon_amount 
        from `tabCoupon Transaction` 
        where 
        coupon_code=%(coupon_code)s
        group by
            transaction_type,
            markup_percentage
    """
    data = frappe.db.sql(sql,{"coupon_code":coupon_info.get("coupon_code")},as_dict=1)

    coupon_info["coupon_transaction"] = data
    coupon_info["coupon_balance"] = sum([d.get("coupon_amount") for d in data])
    coupon_info["actual_amount_balance"] = get_coupon_actual_amount_balance(data)
    
    return  coupon_info

@frappe.whitelist()
def check_coupon_code_for_redeem(coupon_code):
    if not frappe.db.exists("Coupon Codes",{"coupon":coupon_code}):
        frappe.throw(_("This coupon code does not exist in the system"))

    data = frappe.db.get_list('Coupon Codes', filters={
        'coupon':  coupon_code
    },
    order_by='creation desc',
    page_length=1,
    fields=["name","coupon","coupon_status","expired_date"]
    )
 
    # validate expiredate
    if not data:
        frappe.throw(_("This coupon code does not exist in the system"))

    if data[0].coupon_status =="Unused":
        frappe.throw(_("This coupon number is not a used coupon number"))
    
    if data[0].coupon_status=="Redeemed":
        frappe.throw(_("This coupon code is already redeemed"))
        
    if data[0].coupon_status=="Expired":
        frappe.throw(_("This coupon code is expired"))  

    
    if data[0].coupon_status=="Used":
        if   datetime.datetime.now() > data[0].expired_date:
            frappe.throw(_("This coupon code is expired"))   
    
    


    sql = """select 
        coupon_code,
        coupon_number,transaction_date,sale,posting_date,
        input_actual_amount,
        input_coupon_amount,
        currency, 
        product_code
    from `tabCoupon Transaction` 
    where 
        coupon_code=%(coupon_code)s and  
        transaction_type = "Sale Coupon" 
    limit 1
    """
   
    coupon_info = frappe.db.sql(sql,{"coupon_code":data[0].name},as_dict=1) 
 
    customer_photo,customer_group,phone_number,customer,customer_name = frappe.get_cached_value("Sale",coupon_info[0].get("sale"),["customer_photo","customer_group","phone_number","customer","customer_name"])  
    coupon_info[0]["customer"] = {
        "name":customer,
        "customer_name":customer_name,
        "customer_group":customer_group,
        "phone_number":phone_number,
        "photo":customer_photo
    }

    if coupon_info:
        if coupon_info[0].get("product_code"):
            product_name,photo = frappe.get_cached_value("Product",coupon_info[0].get("product_code"),["product_name_en","photo"]) 
            
            coupon_info[0]["product_name"] = product_name
            coupon_info[0]["photo"] = photo
            
        coupon_info =  coupon_info[0]
    
    # get coupon transaction
    sql = """
        select 
            transaction_type,
            markup_percentage,
            sum(input_actual_amount) as input_actual_amount,
            sum(coupon_amount) as coupon_amount 
        from `tabCoupon Transaction` 
        where 
        coupon_code=%(coupon_code)s
        group by
            transaction_type,
            markup_percentage
    """
    data = frappe.db.sql(sql,{"coupon_code":coupon_info.get("coupon_code")},as_dict=1)

    coupon_info["coupon_transaction"] = data
    coupon_info["coupon_balance"] = sum([d.get("coupon_amount") for d in data])
    coupon_info["actual_amount_balance"] = get_coupon_actual_amount_balance(data)
    coupon_info["used_coupon_value"] = sum([d.get("coupon_amount") for d in data if d.get("transaction_type") =="Used"])
    
    return  coupon_info

def get_coupon_actual_amount_balance(coupon_transactions):
    return sum([d.get("coupon_amount") / (1+(d.get("markup_percentage") or 0)/100) for d in coupon_transactions])
