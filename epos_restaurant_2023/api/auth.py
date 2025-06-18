
import frappe
import base64
from builtins import str

@frappe.whitelist(allow_guest=True)
def check_api_url(property_code):
   
    sql = "select  * from `tabBusiness Branch` where property_code = '{}'".format(property_code)
    data = frappe.db.sql(sql,as_dict =1)
    if data:
        data =data[0]
        return {
            "property_code":property_code,
            "property_name":data.get("name"), 
            "photo":data.get("photo") 
        }

    frappe.throw("Property {} does not exist".format(property_code))
    
@frappe.whitelist( allow_guest=True,methods="POST" )
def login(property,usr, pwd, property_code=None):
 
    # from frappe.core.doctype.user.user import generate_keys
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.throw("Usename and password incorrect.")
  
    frappe.response["message"] = get_response_user_information(property,property_code )

        
def get_response_user_information(property, property_code=None):
    phone_number =""
    address =""
    employee_id=""
    position=""
    user = frappe.get_doc("User", frappe.session.user)
    
    sql = "select position,name,phone_number_1,address,pos_permission from `tabEmployee` where user_id = '{}' limit 1".format(frappe.session.user)
    data = frappe.db.sql(sql, as_dict=1)
    pos_permission=None
    if data:
        position = data[0].get("position")
        employee_id = data[0].get("name")
        phone_number = data[0].get("phone_number_1")
        address = data[0].get("address")
        if data[0].get("pos_permission"):
             pos_permission = frappe.get_cached_doc("POS User Permission", data[0].get("pos_permission"))

    api_generate = generate_keys(frappe.session.user)
     

    return {
        "username":user.username,
        "full_name":user.full_name,
        "role_profile":user.role_profile_name,
        "photo":user.user_image,
        "phone_number":phone_number,
        "address":address,
        "name":frappe.session.user,
        "position":position,
        "token": base64.b64encode(str("{}:{}".format(user.api_key,api_generate)).encode("utf-8")).decode('utf-8'),
        "property_name":property,
        "property_code":property_code, 
        "employee_id":employee_id,
        "pos_permission":pos_permission
    }

     
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



    

@frappe.whitelist(allow_guest=True)
def check_user_login(property):
 
    if frappe.session.sid == "Guest":
        frappe.response["message"] =  frappe.session.sid
    else:
        frappe.response["message"] = get_response_user_information(property)
    