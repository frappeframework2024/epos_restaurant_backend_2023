# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime


def execute(filters=None):

	validate(filters)

	report_data = []
	skip_total_row=False
	message=None
	report_data = get_report_data(filters=filters)
 
	return get_columns(filters=filters), report_data, message, None, None,skip_total_row


def validate(filters):
	if not filters.class_type:
		filters.class_type = frappe.db.get_list("GYM Class Types",pluck='name')
	
	if not filters.time_training:
		filters.time_training = frappe.db.get_list("GYM Training Time",pluck='name')

def get_columns(filters):
	columns = []
	columns.append( {"label":"Code", "fieldname":"code","fieldtype":"Dynamic Link","options":"reference_doctype", "align":"left",'width':100})
	columns.append( {"label":"Member Type", "fieldname":"member_type","fieldtype":"Data", "align":"center",'width':140})
	columns.append( {"label":"Name En", "fieldname":"name_en","fieldtype":"Data", "align":"left",'width':170})
	columns.append( {"label":"Name Kh", "fieldname":"name_kh","fieldtype":"Data", "align":"left",'width':170})
	columns.append( {"label":"Gender", "fieldname":"gender","fieldtype":"Data", "align":"left",'width':80})
	columns.append( {"label":"Phone", "fieldname":"phone_number","fieldtype":"Data", "align":"left",'width':200})
	columns.append( {"label":"Training Date", "fieldname":"calendar_date","fieldtype":"Date", "align":"left",'width':120})
	columns.append( {"label":"Class", "fieldname":"class","fieldtype":"Data", "align":"left",'width':170})
	columns.append( {"label":"Time Training", "fieldname":"time_training","fieldtype":"Data", "align":"left",'width':170})
	columns.append( {"label":"Check In", "fieldname":"check_in_date","fieldtype":"Data", "align":"left",'width':210,})
	columns.append( {"label":"Check Out", "fieldname":"check_out_date","fieldtype":"Data", "align":"left",'width':210})

	return columns


def get_report_data(filters):
	sql = """select 
		`name`,
		if(member is null , trainer, member) as `code`,
		if(member is null, trainer_name_en, member_name ) as name_en,
		if(member is null, trainer_name_kh, member_name_kh ) as name_kh,
		if(member is null, gender, member_gender ) as gender,
		if(member is null,phone , concat(phone_number_1,'/',phone_number_2) ) as phone_number,
		reference_doctype,
		if(reference_doctype = 'Trainer','Trainer','Member') as member_type,
		class,
		time_training,
		calendar_date,
		check_in_date,
		check_out_date,	
		if(check_out_date is null, 0, 1) as is_check_out

	from `tabTraining Attendance` 
	where 1 = 1 
	and (calendar_date between %(start_date)s and %(end_date)s)
	and class in %(class_type)s 
	and time_training in %(time_training)s
	
	order by calendar_date"""

	result = frappe.db.sql(sql,filters, as_dict = 1)
	for row in result:
		if row.get("check_in_date"):
			row["check_in_date"] = row["check_in_date"].strftime("%Y-%m-%d %I:%M:%S %p") if isinstance(row["check_in_date"], datetime) else row["check_in_date"]
		if row.get("check_out_date"):
			row["check_out_date"] = row["check_out_date"].strftime("%Y-%m-%d %I:%M:%S %p") if isinstance(row["check_out_date"], datetime) else row["check_out_date"]

	return result