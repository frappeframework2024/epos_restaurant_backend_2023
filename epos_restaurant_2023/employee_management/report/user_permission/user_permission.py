# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = ['User'], []
	return get_report_field(filters), get_report_data(filters)

def get_report_field(filters):
	fields = []
	fields.append({"label":"Employee","short_label":"Employee", "fieldname":"employee_name","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65",'width':250})
	return fields

def get_report_data(filters):
	sql = """
			select employee_name,module_profile,role_profile from `tabEmployee`
		"""
	employees = frappe.db.sql(sql,as_dict=1)
	role_profiles = list(set([d['role_profile'] for d in employees])) 
	module_profile = list(set([d['module_profile'] for d in employees])) 
	has_role = """
				select role,parent from `tabHas Role` where parenttype = 'Role Profile' and parent in {}
			""".format(tuple(role_profiles))
	has_role = """
				select module,parent from `tabBlock Module` where parenttype = 'Module Profile' and parent in {}
			""".format(tuple(module_profile))
	
	has_role_list = frappe.db.sql(has_role,as_dict=1)
	module_list = frappe.db.sql(has_role,as_dict=1)
	employees.append({
				"indent":1,
				"employee_name": "Role Profile",
				"is_group":1,
			})
	
	return employees