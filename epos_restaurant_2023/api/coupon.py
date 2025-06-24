import frappe
from frappe import _
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

def get_coupon_actual_amount_balance(coupon_transactions):
    return sum([d.get("coupon_amount") / (1+(d.get("markup_percentage") or 0)/100) for d in coupon_transactions])
