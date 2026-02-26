import frappe
from datetime import datetime
from frappe import _
@frappe.whitelist()
def get_home_page_data():
    user_info = get_user_info()
    if not user_info:
        frappe.throw("Invalid user credential")

    coupon_info = get_coupon_info(user_info.get("employee_code"))
    
    recent_transaction = []
    if coupon_info:
        recent_transaction = get_recent_use_coupon_transaction(coupon_info.get("coupon"))
    
    return {
        "user_info": user_info,
        "coupon_info": coupon_info,
        "recent_coupon_transaction": recent_transaction,
        "chart_data":get_daily_coupon_use_chart_data(coupon_info.get("coupon")) if coupon_info else []
    }

@frappe.whitelist()
def get_user_info():

    sql = "select photo, employee_name as full_name, name as employee_code,position from `tabEmployee` where user_id = %(user_id)s"
    data = frappe.db.sql(sql, {"user_id":frappe.session.user},as_dict=1)
    if data:
        data[0]["username"] = frappe.session.user
        return data[0]
    return None


def get_coupon_info(employee_code):
    sql = "select posting_date, expired_date,coupon_number,coupon,coupon_amount from `tabCoupon Issue` where coupon_type='Digital Coupon' and employee=%(employee_code)s and docstatus = 1 and expired_date>=date(now()) order by creation desc limit 1 "
    
    data = frappe.db.sql(sql, {"employee_code":employee_code},as_dict = 1)
    if data:
        # get total use transaction 
        sql = "select coalesce( sum(coupon_amount),0) as total_use  from `tabCoupon Transaction` where transaction_type = 'Used' and coupon_code = %(coupon_code)s and status !='Deleted'"
        use_amount = frappe.db.sql(sql,{"coupon_code":data[0].get("coupon")},as_dict=1)[0].get("total_use")
        data[0]["use_amount"] = abs( use_amount)
        data[0]["coupon_status"] = frappe.get_cached_value("Coupon Codes",data[0].get("coupon"),"coupon_status")
        data[0]["coupon_status"] =  "Active" if data[0]["coupon_status"] =="Used" else "Expired"
        if frappe.utils.getdate(data[0]["expired_date"])< frappe.utils.getdate(frappe.utils.today()):
            data[0]["coupon_status"] = "Expired"



        return data[0]
    
    return None

def get_recent_use_coupon_transaction(coupon_code):
    sql = "select name,coupon_amount,transaction_type,vendor,coupon_number,transaction_date,posting_date,pos_profile,creation from `tabCoupon Transaction` where transaction_type = 'Used' and coupon_code = %(coupon_code)s order by creation desc limit 10"
    # return frappe.db.sql(sql,{"coupon_code":coupon_code},as_dict  =1)
    data = frappe.db.sql(sql,{"coupon_code":coupon_code},as_dict  =1)
     
    return data


@frappe.whitelist()
def get_daily_coupon_use_chart_data(coupon_code):
    from epos_restaurant_2023.utils import get_lastweek_to_currentweek
    from datetime import datetime, timedelta
    dates = get_lastweek_to_currentweek()
    start =dates[0]
    end = dates[1]
    
    sql = """select  
        d.date ,
        coalesce(c.use_amount,0) as value
    from `tabDates` d 
    left join (
        select 
            posting_date, 
            sum(abs(coupon_amount)) as use_amount 
        from `tabCoupon Transaction` ct 
        where
            ct.transaction_type = 'Used' and
            ct.coupon_code = %(coupon_code)s  and 
            coalesce(ct.status,'') <> 'Deleted'  and
            ct.posting_date between %(start_date)s and %(end_date)s 
        group by
            posting_date

    ) as c on c.posting_date = d.date
     where d.date between %(start_date)s and %(end_date)s"""
    result = frappe.db.sql(sql,{"start_date":start,"end_date":end,"coupon_code":coupon_code},as_dict = 1)

    return result
    



@frappe.whitelist()
def get_managment_qr_for_payment(coupon_number,timespan):
    from epos_restaurant_2023.api.qr import generate_qr
    from epos_restaurant_2023.utils import encrypt_aes_base64
    from datetime import datetime, timedelta
    now = datetime.now()
    # Add 5 minutes
    new_datetime = now + timedelta(minutes=3)
    # Extract only hour and minute
    time_str = new_datetime.strftime("%H:%M")
    # return {encrypt_aes_base64(f"{coupon_number}|{time_str}"),f"{coupon_number}|{time_str}"}
    site_config = frappe.get_site_config()
    
    return generate_qr(site_config.get("coupon_code_url") + encrypt_aes_base64(f"{coupon_number}|{time_str}"),size=6)
    

@frappe.whitelist()
def get_coupon_use_transaction(coupon_code=None):
    if not coupon_code:
        user_info = get_user_info()
        if not user_info:
            frappe.throw("Invalid user credential")
        coupon_info = get_coupon_info(user_info.get("employee_code"))
        
        coupon_code = coupon_info.coupon

    end_date= frappe.utils.today()
    start_date =frappe.utils.getdate(end_date).replace(day=1)
    sql = """select name,posting_date,coupon_amount,transaction_type,vendor,coupon_number,transaction_date,pos_profile,creation 
            from `tabCoupon Transaction` 
        where posting_date between %(start_date)s and %(end_date)s and  
            transaction_type = 'Used' and 
            coalesce(status,'') <> 'Deleted' 
    """
    
    data = frappe.db.sql(sql,{"start_date":start_date,"end_date":end_date,"coupon_code": coupon_code},as_dict = 1)

    return data



@frappe.whitelist()
def get_use_coupon_transaction_balance_after(transaction_id):
    sql = "select creation, coupon_code from `tabCoupon Transaction` where name = %(name)s"

    ct =  frappe.db.sql(sql,{"name":transaction_id},as_dict = 1)
    if ct:
        ct = ct[0]
        sql = "select coalesce(sum(coupon_amount),0) as amount from `tabCoupon Transaction` where coupon_code= %(coupon_code)s and creation<=%(creation)s and coalesce(status,'')<> 'Deleted'"
        data = frappe.db.sql(sql,{"coupon_code":ct.get("coupon_code"), "creation":ct.get("creation")},as_dict=1)
        return data[0]["amount"]

    return 0




@frappe.whitelist()
def change_password(old_password, new_password, confirm_password):
    from frappe.utils.password import check_password, update_password
    """Change user password with validation"""

    user = frappe.session.user

    if not old_password or not new_password or not confirm_password:
        frappe.throw(_("All fields are required."))

    if new_password != confirm_password:
        frappe.throw(_("New password and confirm password do not match."))
        
    if old_password == new_password:
        frappe.throw(_("New password cannot be the same as old password."))

    # Verify old password
    try:
        check_password(user, old_password)
    except frappe.AuthenticationError:
        frappe.throw(_("Old password is incorrect."))

    user_doc = frappe.get_doc("User", user)
    user_doc.new_password = new_password
    user_doc.save(ignore_permissions=True)

    # Commit transaction
    frappe.db.commit()

    frappe.msgprint(_("Password changed successfully."))
    return {"message": "Password updated successfully"}
