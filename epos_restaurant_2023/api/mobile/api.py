from epos_restaurant_2023.api.api import (
    get_current_shift_information,
    get_close_shift_summary as _get_close_shift_summary,
    get_pending_sale_orders as _get_pending_sale_orders
) 
import frappe
from builtins import str 
import base64 


def generate_keys(user):
	"""
	generate api key and api secret
 
	:param user: str
	"""
	# frappe.only_for("System Manager")
	user_details = frappe.get_doc("User", user)
	api_secret = frappe.generate_hash(length=15)
	# if api key is not set generate api key
	if not user_details.api_key:
		api_key = frappe.generate_hash(length=15)
		user_details.api_key = api_key
	user_details.api_secret = api_secret
	user_details.save(ignore_permissions=True)

	return api_secret

@frappe.whitelist( methods="POST", allow_guest=True )
def login(usr, pwd): 
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()

        user = frappe.get_doc("User", frappe.session.user)

        api_generate = generate_keys(frappe.session.user)
        token = base64.b64encode(str("{}:{}".format(user.api_key,api_generate)).encode("utf-8")).decode('utf-8') 

        return  {"token": "Basic {}".format(token),"cookie":frappe.local.session}
    
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.throw("Invalid PIN Code")
        



@frappe.whitelist(methods="POST")
def get_current_shift_management(business_branch, pos_profile):
    return  get_current_shift_information(business_branch,pos_profile) 


@frappe.whitelist(methods="POST")
def get_pending_bill(filters): 
     sql = """select 
        count(name) total_pending_bills 
     from `tabSale` 
     where docstatus = 0 
     and pos_profile = %(pos_profile)s
     and working_day = %(working_day)s"""
     if filters["cashier_shift"]:
          sql += " and cashier_shift=%(cashier_shift)s"

     pending_bills = frappe.db.sql(sql, {
          "pos_profile":filters["pos_profile"],
          "working_day":filters["working_day"],
          "cashier_shift":filters["cashier_shift"]
          }, as_dict = 1)
     if pending_bills:
          return pending_bills[0]["total_pending_bills"]
     return 0

@frappe.whitelist(methods="POST")
def get_close_shift_summary(param):
     filters = {
          "pos_profile":param["pos_profile"],
          "working_day":param["working_day"],
          "cashier_shift":param["cashier_shift"]
     }
     result = {
          "get_close_shift_summary":_get_close_shift_summary(param["cashier_shift"],param["show_system_closed_amount"]),
          "total_pending_bill": get_pending_bill(filters)
     } 

     return result


@frappe.whitelist(methods="POST")
def get_pending_sale_orders(data):
     return _get_pending_sale_orders(data)

@frappe.whitelist()
def test_me():
     return "Yes"