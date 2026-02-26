# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):	
	validate(filters)

	report_data = [] 
	report_data = get_report_data(filters) 
	return get_columns(filters), report_data, None,None, None

def validate(filters):
	if not filters.user:
		filters.user = frappe.db.get_list("Employee",pluck='name')

def get_columns(filters):
	columns = []
	columns.append({ "fieldname": "permission", "label":"Permissions", "fieldtype":"Data", "align":"left","width":180 })  
	for c in get_dynamic_columns(filters):
		columns.append({
			"fieldname": c["fieldname"],
			"label":c["label"],
			"fieldtype":"Data",
			"align":"left"
		}) 

	return columns

def get_dynamic_columns(filters): 
	sql = """select 
		employee_name as label, 
		replace( lower(employee_name),' ','_') as fieldname,
		role_profile,
		module_profile,
		pos_permission 
	from `tabEmployee` where disabled = 0 and name in %(user)s"""
	columns = frappe.db.sql(sql,filters,  as_dict=1) 
	return columns


def get_report_data(filters):
	data = []
	data_columns = get_dynamic_columns(filters)
	## get user has role
	### role list
	role_sql = """select 1 as indent , role_name as permission from `tabRole` where name not in ('All', 'Administrator')"""
	roles = frappe.db.sql(role_sql,  as_dict=1) 	


	has_role_sql = """select 
						e.employee_name,
						replace( lower(employee_name),' ','_') as fieldname,
						hr.role, 
						hr.parent 
					from `tabHas Role` hr 
					inner join `tabEmployee` e on hr.parent = e.role_profile
					where hr.parenttype = 'Role Profile' and e.name in %(user)s"""
	has_roles = frappe.db.sql(has_role_sql,filters, as_dict= 1)	

	role_profile_header = {"indent":0,"permission":"Role Profile"}
	for c in data_columns:
		_col = [d for d in has_roles if d["parent"]== c["role_profile"]]
		if _col:
			role_profile_header.update({c["fieldname"]:c["role_profile"]})

	data.append(role_profile_header)
	for role in roles:
		for c in data_columns:
			value = [d for d in has_roles if d["parent"]== c["role_profile"] and d["role"]== role["permission"]]
			if value:
				role.update({c["fieldname"]:"Yes"}) 
			else:
				role.update({c["fieldname"]:"-"}) 
		data.append(role)

	## get module def
 	### module list
	module_sql = """select 1 as indent, module_name as permission from `tabModule Def` where app_name in ( 'epos_restaurant_2023','edoor')"""
	modules = frappe.db.sql(module_sql, as_dict= 1)
	
	block_module_sql = """select 
						e.employee_name,
						replace( lower(employee_name),' ','_') as fieldname,
						bm.module, 
						bm.parent 
					from `tabBlock Module` bm 
					inner join `tabEmployee` e on bm.parent = e.module_profile
					where bm.parenttype = 'Module Profile' and e.name in %(user)s"""
	block_modules = frappe.db.sql(block_module_sql,filters, as_dict= 1)	
	
 
	module_profile_header = {"indent":0,"permission":"Module Profile"}
	for c in data_columns:
		_col = [d for d in block_modules if d["parent"]== c["module_profile"]]
		if _col:
			module_profile_header.update({c["fieldname"]:c["module_profile"]})

	data.append(module_profile_header)

	for module in modules:
		for c in data_columns:
			value = [d for d in block_modules if d["parent"]== c["module_profile"] and d["module"] == module["permission"]]
			if value:
				module.update({c["fieldname"]:"Yes"}) 
			else:
				module.update({c["fieldname"]:"-"}) 
		data.append(module)

	## get POS User Permission
	pos_permission_sql = """select 
									1 as indent,
									fieldname, 
									label as permission  
								from tabDocField 
								where parent = 'POS User Permission'  
									and fieldtype  in ('Check') 
									and fieldname not in ('park_item','change_item_time_out','change_item_time_in','delete_voucher_top_up','add_voucher_top_up')
								order by idx"""
	pos_permissions = frappe.db.sql(pos_permission_sql,as_dict = 1)
	
	pos_user_permission_sql = """select 
									e.employee_name,
									replace( lower(employee_name),' ','_') as fieldname,
									u.* 
								from `tabPOS User Permission` u
								inner join `tabEmployee` e on u.`name` = e.pos_permission 
								where e.name in %(user)s"""
	pos_user_permissions = frappe.db.sql(pos_user_permission_sql,filters,as_dict = 1) 	 

	pos_permission_header = {"indent":0,"permission":"POS Permission"}
	for c in data_columns:
		_col = [d for d in pos_user_permissions if d["pos_user_permission"]== c["pos_permission"]]
		if _col:
			pos_permission_header.update({c["fieldname"]:c["pos_permission"]})
	data.append(pos_permission_header)

	for pos_permission in pos_permissions:
		for c in data_columns:
			value = [d for d in pos_user_permissions if d["pos_user_permission"] == c["pos_permission"]]
			if value and value[0][pos_permission["fieldname"]] == 1:
				pos_permission.update({c["fieldname"]:"Yes"}) 
			else:
				pos_permission.update({c["fieldname"]:"-"}) 
		data.append(pos_permission)


	return data 

