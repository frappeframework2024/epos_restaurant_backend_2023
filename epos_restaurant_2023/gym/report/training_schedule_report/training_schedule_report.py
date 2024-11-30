# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):

	validate(filters)

	report_data = []
	skip_total_row=False
	message=None
	report_data = get_report_data(filters=filters)
 
	return get_columns(filters=filters), report_data, message, None, None,skip_total_row


def validate(filters):
	if not filters.business_branch:
		filters.business_branch = frappe.db.get_list("Business Branch",pluck='name')

def get_columns(filters):
	columns = []
	columns.append( {"label":"Time / Day", "fieldname":"time_day","fieldtype":"Data", "align":"left",'width':170})
	for d in colums_fields():
		columns.append( {"label":d["label"], "fieldname":d["fieldname"],"fieldtype":"Data", "align":"left",'width':170})	
	return columns

def colums_fields():
	return [
		{"label":"Monday","fieldname":"monday"},
		{"label":"Tuesday","fieldname":"tuesday"},
		{"label":"Wednesday","fieldname":"wednesday"},
		{"label":"Thursday","fieldname":"thursday"},
		{"label":"Triday","fieldname":"friday"},
		{"label":"Saturday","fieldname":"saturday"},
		{"label":"Sunday","fieldname":"sunday"}
	]

def get_report_data(filters):
	sql = """select 
		business_branch,
		`day`,
		time_training as time_day,
		class_type,
		trainer	,
		sort_order
	from `tabTraining Schedule` 
	where 1 = 1
	and business_branch in %(business_branch)s
	and disabled = 0 
	order by sort_order asc"""
	data = frappe.db.sql(sql,filters,as_dict = 1)

	time_day_dict ={}
	for d in data:
		if d["time_day"] not in time_day_dict:
			time_day_dict[d["time_day"]] = []
		time_day_dict[d["time_day"]].append(d)

	

	result = []
	for key in time_day_dict.keys():
		field = {
			"time_day":key
		}
		for c in colums_fields():
			day = {c["fieldname"]:""}
			for f in [ t for t in time_day_dict[key] if t['day']== c["label"]]: 
				
					day[c["fieldname"]] += f["class_type"] +"\n"
			field.update(day) 

		result.append(field)

	return result 