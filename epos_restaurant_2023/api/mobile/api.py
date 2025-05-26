from epos_restaurant_2023.api.api import (
    get_current_shift_information,
    get_close_shift_summary as _get_close_shift_summary,
    get_pending_sale_orders as _get_pending_sale_orders,
    get_sale_list_table_badge as _get_sale_list_table_badge,
    validate_sale_network_lock as _validate_sale_network_lock,
    check_username as _check_username,
    save_table_position as _save_table_position,
) 
import frappe
from builtins import str 
import base64 
import json


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
def validate_sale_network_lock(param):
    return  _validate_sale_network_lock(param=param) 


@frappe.whitelist(methods="POST")
def check_username(pin_code):
    return  _check_username(pin_code=pin_code) 

@frappe.whitelist(methods="POST")
def save_table_position(device_name,pos_profile,table_group):
    return  _save_table_position(device_name=device_name, pos_profile=pos_profile,table_group=table_group) 


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

@frappe.whitelist(methods="POST")
def check_start_shift_exists_shift_type(param):
     docs = frappe.get_list("Cashier Shift", 
                            fields=["*"], 
                            filters={
                                 "pos_profile": param["pos_profile"],
                                 "working_day":param["working_day"],
                                 "shift_name":param["shift_name"],
                                 "business_branch":param["business_branch"]
                                 })
     if len(docs)>0:
          return True
     return False


##get sale invoice
@frappe.whitelist(methods="POST")
def get_sale_invoice(doc_name):
     result = {}
     if not frappe.db.exists("Sale",doc_name):
          return {"status":False}
     
     doc = frappe.get_doc("Sale", doc_name)
     pos_profile = frappe.get_doc("POS Profile",doc.pos_profile)
     setting_data = frappe.get_doc("POS Config", pos_profile.pos_config)
     branding = frappe.get_doc("POS Branding", pos_profile.pos_branding)
     currency = frappe.db.get_single_value("ePOS Settings","currency")
     second_currency = frappe.db.get_single_value("ePOS Settings","second_currency")
     second_currency_data = frappe.get_doc("Currency",second_currency)


     order_date = frappe.db.sql("""select 
                                   distinct cast(coalesce(order_time,creation) as date) as order_date 
                                from `tabSale Product` 
                                where parent='{}' 
                                group by cast(coalesce(order_time,creation) as date)""".format(doc.name), as_dict = 1)
     sale_product_data = frappe.db.sql("""select  
                                       cast(coalesce(order_time,creation) as date) as order_date, 
                                       product_name,
                                       product_name_kh,
                                       `portion`,
                                       is_free,
                                       note,
                                       modifiers,
                                       discount,
                                       sum(discount_amount) as discount_amount,
                                       discount_type,
                                       sum(quantity) as quantity,
                                       (price + modifiers_price)  as price  
                                       from `tabSale Product` 
                                   where parent='{}' 
                                       group by  cast(coalesce(order_time,creation) as date) ,
                                       product_name,
                                       product_name_kh,
                                       note,
                                       `portion`,
                                       is_free,
                                       modifiers,
                                       discount,
                                       discount_type, 
                                       price + modifiers_price""".format(doc.name),as_dict=1)
     doc.sale_products = [] 

     setting = {
          "logo":branding.logo,
          "business_name_en":setting_data.business_name_en,
          "business_name_kh":setting_data.business_name_kh,
          "vattin_number":setting_data.vattin_number,
          "phone_number":setting_data.phone_number,
          "address":setting_data.address,
          "address_kh":setting_data.address_kh,
          "email":setting_data.email,
          "website":setting_data.website,
     }
     second_currency_value =  {
          "name": second_currency_data.name,
          "currency_name": second_currency_data.currency_name,
          "symbol": second_currency_data.symbol,
          "symbol_on_right": second_currency_data.symbol_on_right,
          "number_format": second_currency_data.number_format,
          "custom_currency_precision": second_currency_data.custom_currency_precision,
          "custom_pos_currency_format": second_currency_data.custom_pos_currency_format,
     }


     result.update({
          "status":True,
          "setting":setting,
          "currency":currency,
          "second_currency":second_currency,
          "second_currency_data":second_currency_value ,
          "doc":doc,
          "order_date":order_date,
          "sale_product_data":sale_product_data,
          })
     
     return result

@frappe.whitelist(methods="POST")
def get_sale_list_table_badge(data):
     return _get_sale_list_table_badge(data)

@frappe.whitelist(methods="POST")
def get_sale_customer(name):
     if not frappe.db.exists("Customer", name):
          return {"status":False, "data":None}
     doc = frappe.get_doc("Customer", name)

     return  {"status":True, "data":doc}



@frappe.whitelist()
def execute_sql_query(query,params=None):
     # if not query.lower().startswith('select'):
     #    raise frappe.PermissionError("Only SELECT queries are allowed")
     
     if params:
         result = frappe.db.sql(query, json.loads(params) , as_dict=True)
     else:
          result = frappe.db.sql(query , as_dict=True)
     
     return result

@frappe.whitelist(methods="POST")
def delete_note(notes):    
     sql = """delete from `tabCashier Notes` where name in %(notes)s"""
     frappe.db.sql(sql,{"notes": [d["name"] for d in notes]}, as_dict=True)
     return {"status": True, "message":"Delete successfully"}

@frappe.whitelist(methods="POST")
def create_note(category, note):   
     doc = frappe.get_doc("Category Note", category)
     new_row  = doc.append("notes", {
          "note": note["note"],
          "product_code": note["product_code"]
     })
     doc.save()
     doc.reload()

     return new_row

@frappe.whitelist(methods="POST")
def bulk_insert(data):
    try:
        inserted_docs = []
        for doc_data in data:
            # Create a new document using frappe.get_doc
            doc = frappe.get_doc(doc_data)
            # Insert the document
            doc.insert(ignore_permissions=False)  # Set to True to bypass permissions
            inserted_docs.append(doc.name)
        frappe.db.commit()
        return {"status": "success", "doc": doc_data["doctype"]}
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Bulk insert failed: {str(e)}")
        return {"status": "error", "message": str(e)}    




@frappe.whitelist()
def test_me():
     return "Yes"