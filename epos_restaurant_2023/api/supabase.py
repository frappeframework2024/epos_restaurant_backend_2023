import frappe
import time
from supabase import create_client, Client
@frappe.whitelist()
def send_coupon_data_to_supabase(coupon_code,coupon_number,posting_date):
    time.sleep(1)


    data = {
        "name":coupon_code,
        "coupon_number":coupon_number,
        "posting_date":str(posting_date)
    }

    # get amount
    sql = "select transaction_type,abs(sum(coupon_amount)) as coupon_amount from `tabCoupon Transaction` where coupon_code = %(coupon_code)s and coalesce(status,'') <>'Deleted' group by transaction_type "
    coupon_data = frappe.db.sql(sql,{"coupon_code":coupon_code},as_dict = 1)
    data["price"] = sum([d.get("coupon_amount") for d in coupon_data if d.get("transaction_type") in ["Sale Coupon","Coupon Issue"]]) or 0
    data["top_up_amount"] =sum([d.get("coupon_amount") for d in coupon_data if d.get("transaction_type") == "Top Up"]) or 0
    data["use_amount"] = sum([d.get("coupon_amount") for d in coupon_data if d.get("transaction_type") == "Used"]) or 0
    data["redeem_amount"] = sum([d.get("coupon_amount") for d in coupon_data if d.get("transaction_type") == "Redeem"]) or 0
    data["balance_amount"] = (data.get("price") + data.get("top_up_amount")) - (data.get("use_amount") + data.get("redeem_amount"))



 
    site_config = frappe.get_site_config()
    url = site_config.get("supabase_api_url")
    key = site_config.get("supabase_api_key")
    supabase =  create_client(url, key)
    try:
        res = supabase.table(site_config.get("supabase_coupon_code_table_name")).upsert(data).execute()
        frappe.get_doc({
            "doctype":"Supabase Logs",
            "posting_date":posting_date,
            "coupon_number":coupon_number,
            "coupon_code":coupon_code,
            "status":"Done",
            "data":data
       }).insert(ignore_permissions=True)
        return res
    except Exception as e:
       frappe.get_doc({
            "doctype":"Supabase Logs",
            "posting_date":posting_date,
            "coupon_number":coupon_number,
            "coupon_code":coupon_code,
            "status":"Fail",
            "data":data
       }).insert(ignore_permissions=True)

    


@frappe.whitelist()
def resent_data_to_supabase():
    pass

@frappe.whitelist(methods=["POST"])
def delete_coupon_code_data():
    from datetime import datetime, timedelta
    two_days_ago = (datetime.now() - timedelta(days=2)).date()

    site_config = frappe.get_site_config()
    url = site_config.get("supabase_api_url")
    key = site_config.get("supabase_api_key")
    supabase =  create_client(url, key)
    supabase.table(site_config.get("supabase_coupon_code_table_name")).delete().lte("posting_date", str(two_days_ago)).execute()



 