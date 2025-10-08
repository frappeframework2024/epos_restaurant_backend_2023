import frappe
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """Get Supabase client from site_config"""
    site_config = frappe.get_site_config()
    url = site_config.get("supabase_api_url")
    key = site_config.get("supabase_api_key")
    return create_client(url, key)

@frappe.whitelist()
def send_coupon_data_to_supabase(coupon_code,coupon_number):
    data = {
        "name":coupon_code,
        "coupon_number":coupon_number,
        "posting_date":frappe.utils.today()
    }

    # get amount
    sql = "select transaction_type,abs(sum(coupon_amount)) as coupon_amount from `tabCoupon Transaction` where coupon_code = %(coupon_code)s group by transaction_type "
    coupon_data = frappe.db.sql(sql,{"coupon_code":coupon_code},as_dict = 1)
    data["price"] = sum([d.get("coupon_amount") for d in coupon_data if d.get("transaction_type") in ["Sale Coupon","Coupon Issue"]]) or 0
    data["top_up_amount"] =sum([d.get("coupon_amount") for d in coupon_data if d.get("transaction_type") == "Top Up"]) or 0
    data["use_amount"] = sum([d.get("coupon_amount") for d in coupon_data if d.get("transaction_type") == "Used"]) or 0
    data["redeem_amount"] = sum([d.get("coupon_amount") for d in coupon_data if d.get("transaction_type") == "Redeem"]) or 0
    data["balance_amount"] = (data.get("price") + data.get("top_up_amount")) - (data.get("use_amount") - data.get("redeem_amount"))



    supabase = get_supabase_client()
    res = supabase.table("food_court_coupon_codes").upsert(data).execute()


    return res




 