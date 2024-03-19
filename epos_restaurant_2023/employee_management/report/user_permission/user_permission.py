# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.config import get_modules_from_all_apps


def execute(filters=None):
	columns, data = ['User'], []
	return get_report_field(filters), get_report_data(filters)

def get_report_field(filters):
	fields = []
	fields.append({"label":"Employee","short_label":"Employee", "fieldname":"employee_name","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65",'width':250})
	# fields.append({"label":"Permission","short_label":"Permission", "fieldname":"permission","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65",'width':250})
	return fields

def get_report_data(filters):
	
	sql = """
			select employee_name,module_profile,role_profile,user_id,pos_permission from `tabEmployee`
		"""
	employees = frappe.db.sql(sql,as_dict=1)
	role_profiles = list(set([d['role_profile'] for d in employees])) 
	pos_permission = list(set([d['pos_permission'] for d in employees if d['pos_permission'] is not None])) 
	has_role_sql = """
				select role,parent from `tabHas Role` where parenttype = 'Role Profile' and parent in {}
			""".format(tuple(role_profiles))
	has_role_list = frappe.db.sql(has_role_sql,as_dict=1) or []
	pos_permission_sql = """
				select * from `tabPOS User Permission` where name in {}
			""".format(tuple(pos_permission))
	pos_permission_list = frappe.db.sql(pos_permission_sql,as_dict=1) or []
	
	# title_case_strings = [string.replace('_', ' ').title() for string in filtered_values]
	keys_by_name = {}
	
	
	report_data=[]
	
	for emp in employees:
		report_data.append({
					"indent":0,
					"employee_name": emp.employee_name,
					"is_group":1,
				})
		if len(has_role_list) > 0:
			report_data.append({
							"indent":0,
							"employee_name": "<strong>" +emp.role_profile +"</strong>",
							"is_group":1,
						})
			for role in has_role_list:
				if emp.role_profile == role.parent:
					report_data.append({
							"indent":1,
							"employee_name": role.role,
							"is_group":1,
						})
		allowed=[]
		block_modules = frappe.get_doc("Module Profile", {"module_profile_name": emp.module_profile})
		# frappe.throw(str(block_modules))
		block_modules = [d.module for d in block_modules.get("block_modules")]
		
		
		if len(block_modules) > 0:
			allowed = frappe.db.sql("select name from `tabModule Def` where name not in {}".format(tuple(block_modules)),as_dict=1)
		else:
			allowed = frappe.db.sql("select name from `tabModule Def`",as_dict=1)
		if len(allowed) > 0:
			report_data.append({
							"indent":0,
							"employee_name": "<strong>" +emp.module_profile +"</strong>",
							"is_group":1,
						})
		
		for allow  in allowed:
			report_data.append({
							"indent":1,
							"employee_name": allow.name,
							"is_group":0,
						})
		if filters.allow_login_in_pos:
			if emp.pos_permission:
				report_data.append({
								"indent":0,
								"employee_name": "<strong>" + emp.pos_permission + "</strong>",
								"is_group":1,
							})
			else:
				pass
			for d in pos_permission_list:
				name = d['name']
				keys = [key for key, value in d.items() if value == 1]
				keys_by_name[name] = keys
			for name, keys in keys_by_name.items():
				if emp.pos_permission == name:
					for k in keys:
						report_data.append({
								"indent":1,
								"employee_name": k.replace('_', ' ').title(),
								"is_group":1,
							})

	return report_data

	
		# frappe.throw(str(tuple(user_block_module)))