# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = ['User'], []
	return get_report_field(filters), get_report_data(filters)

def get_report_field(filters):
	fields = []
	fields.append({"label":"Employee","short_label":"Employee", "fieldname":"employee_name","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65",'width':250})
	fields.append({"label":"Permission","short_label":"Permission", "fieldname":"permission","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65",'width':250})
	return fields

def get_report_data(filters):
	sql = """
			select employee_name,module_profile,role_profile from `tabEmployee`
		"""
	employees = frappe.db.sql(sql,as_dict=1)
	role_profiles = list(set([d['role_profile'] for d in employees])) 
	module_profile = list(set([d['module_profile'] for d in employees]))
	has_role_sql = """
				select role,parent from `tabHas Role` where parenttype = 'Role Profile' and parent in {}
			""".format(tuple(role_profiles))
	block_module_sql = """
				select module,parent from `tabBlock Module` where parenttype = 'Module Profile' and parent in {}
			""".format(tuple(module_profile))
	
	has_role_list = frappe.db.sql(has_role_sql,as_dict=1) or []
	module_list = frappe.db.sql(block_module_sql,as_dict=1) or []
	report_data=[]
	for emp in employees:
		report_data.append({
					"indent":0,
					"employee_name": emp.employee_name,
					"is_group":1,
				})
		if len(has_role_list) > 0:
			report_data.append({
							"indent":1,
							"employee_name": "<strong>" +emp.role_profile +"</strong>",
							"is_group":1,
						})
			for role in has_role_list:
				if emp.role_profile == role.parent:
					report_data.append({
							"indent":2,
							"permission": role.role,
							"is_group":1,
						})

		if len(module_list) > 0:
			report_data.append({
							"indent":1,
							"employee_name": "<strong>" +emp.module_profile +"</strong>",
							"is_group":1,
						})
			for module_profile in module_list:
				if emp.module_profile == module_profile.parent:
					report_data.append({
							"indent":2,
							"permission": module_profile.module,
							"is_group":1,
						})
		
	
	return report_data