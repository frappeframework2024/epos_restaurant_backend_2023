
import frappe
from frappe import _
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
def login(property,usr, pwd, property_code=None, device_id=None): 
    ## check employee
    user = check_user(usr, pwd, device_id=device_id)  
    username = usr
    if user:
        if (usr or "") == "":
            username = user["name"] 
        try:
            login_manager = frappe.auth.LoginManager()
            login_manager.authenticate(user=username, pwd=pwd)
            login_manager.post_login()
        except frappe.exceptions.AuthenticationError:
            frappe.clear_messages()
            frappe.throw("Usename and password incorrect.")   

        frappe.response["message"] = get_response_user_information(property,property_code )
        frappe.response["message"]["app_menus"] =get_user_menu()

    else:
        frappe.throw("Usename and password incorrect.")

## check user allow login by device
def check_user_device(employee, device_id=None):
    ##check device station
   
    if device_id:
        pos_station = frappe.db.sql("select name,platform,pos_profile,business_branch, device_id from `tabPOS Station` where device_id = %(device_id)s",{"device_id": device_id}, as_dict=True)
        if pos_station and len(pos_station) > 0:            
            user_pos_station =  frappe.db.sql("select name,pos_station from `tabUser POS Station` where parent = %(employee)s", {"employee":employee}, as_dict=True)
            if user_pos_station and len(user_pos_station)> 0:
                exclude = [d["name"] for d in pos_station]
                filtered = [item for item in user_pos_station if item["pos_station"] in exclude]
                if filtered and len(filtered)>0:
                    pass
                else:                    
                    frappe.throw(_("User not allow to login on this device"))
            else:
                pass
        else:
            frappe.throw(_("Device not yet register to system"))



##check user login
def check_user(usr, pwd, device_id = None):     
    pin_code = pwd
    if pin_code:    
        pin_code = (str( base64.b64encode(pin_code.encode("utf-8")).decode("utf-8")))
        sql = """select 
                name,
                user_id, 
                pos_permission ,
                username
            from `tabEmployee` 
            where (username = %(username)s or %(username)s = '') 
            and pos_pin_code = %(pos_pin_code)s 
            and allow_login = 1 
            and allow_login_to_epos = 1 
            limit 1"""
 
        users = frappe.db.sql(sql, 
                              {
                                   "username":usr or "",
                                   "pos_pin_code":pin_code
                            }, as_dict = 1) 
        
        if users: 
            check_user_device(employee= users[0].name, device_id=device_id) 
            data = frappe.db.sql("select name,username,full_name from `tabUser` where name=%(name)s limit 1",{"name":users[0].user_id},as_dict=1)
            return data[0]
    
    else:
        frappe.throw(_("Usename and password incorrect."))
    
       
def get_response_user_information(property, property_code=None):
    phone_number =""
    address =""
    employee_id=""
    position=""
    home_page=""
    user = frappe.get_doc("User", frappe.session.user)
    
    sql = "select position,name,phone_number_1,address,pos_permission,default_home_page from `tabEmployee` where user_id = '{}' limit 1".format(frappe.session.user)
    data = frappe.db.sql(sql, as_dict=1)
    pos_permission=None
    if data:
        position = data[0].get("position")
        employee_id = data[0].get("name")
        phone_number = data[0].get("phone_number_1")
        address = data[0].get("address")
        home_page = data[0].get("default_home_page")
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
        "pos_permission":pos_permission,
        "home_page":home_page
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




def get_user_menu():
    
    user = frappe.session.user
    roles = frappe.get_roles(user)
    roles.append("All")
    
    sql = """
        select * from (
            select 
                parent_mobile_app_module,
                name,
                title,
                route_url,
                icon,
                component,
                color,
                is_group,
                is_active,
                show_in_drawer_menu,
                show_in_home,
                sort_order
            from   `tabMobile App Module` 
            where
                name not  in (
                    select distinct parent from `tabHas Role` 
                    where
                        parenttype = 'Mobile App Module'
                ) and 
                is_active = 1
            union
            select 
                parent_mobile_app_module,
                name,
                title,
                route_url,
                icon,
                component,
                color,
                is_group,
                is_active,
                show_in_drawer_menu,
                show_in_home,
                sort_order

            from `tabMobile App Module` 
            where
                name in (
                    select distinct parenttype from `tabHas Role` 
                    where
                        role in %(roles)s and 
                        parenttype = 'Mobile App Module'
                )  and 
                is_active = 1
        ) x
        order by sort_order
        
            
    """
    return frappe.db.sql(sql, {"roles":roles},as_dict = 1)


@frappe.whitelist()
def get_mobile_reports():
    
    user = frappe.session.user
    roles = frappe.get_roles(user)
    roles.append("All")
    # ["name","parent_mobile_reports","report_title","report_url","filter_options"]
    sql = """
        select * from (
            select 
                parent_mobile_reports,
                name,
                report_title,
                report_url,
                filter_options,
                sort_order
            from   `tabMobile Reports` 
            where
                name not  in (
                    select distinct parent from `tabHas Role` 
                    where
                        parenttype = 'Mobile Reports'
                ) and 
                is_active = 1
            union
            select 
                parent_mobile_reports,
                name,
                report_title,
                report_url,
                filter_options,
                sort_order

            from `tabMobile Reports` 
            where
                name in (
                    select distinct parenttype from `tabHas Role` 
                    where
                        role in %(roles)s and 
                        parenttype = 'Mobile Reports'
                )  and 
                is_active = 1
        ) x
        order by sort_order
        
            
    """
    return frappe.db.sql(sql, {"roles":roles},as_dict = 1)
    

@frappe.whitelist(allow_guest=True)
def check_user_login(property):
    if frappe.session.sid == "Guest":
        frappe.response["message"] =  frappe.session.sid
    else:
        frappe.response["message"] = get_response_user_information(property)
        frappe.response["message"]["app_menus"] =get_user_menu()
        
    