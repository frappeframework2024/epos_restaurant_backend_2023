# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import strip
import datetime
from py_linq import Enumerable

def execute(filters=None):

	report_data = []
	skip_total_row=False
	message=None


	report_data = get_report_data(filters) 
	report_chart = None

 

	# columns, report data , message, report chart, report summary, skip total row
	return get_columns(filters), report_data, message, report_chart, [],skip_total_row




## on get columns report
def get_columns(filters):
	columns = []

	# ## append columns
	# columns.append({'fieldname':'row_group','label':filters.row_group,'fieldtype':'Data','align':'left','width':250})

	## generate dynamic columns
	for c in get_dynamic_columns(filters):
		columns.append(c) 

	return columns

## on get dynamic columns
def get_dynamic_columns(filters):
	#static report field
	report_fields = get_report_field(filters)
	columns=[]
	for rf in report_fields:
		columns.append({
			'fieldname': rf["fieldname"],
			'label': rf["short_label"],
			'fieldtype':rf["fieldtype"],
			'precision': rf["precision"],
			'align':rf["align"],
			'width':rf['width']}
		)

	return columns


## on get report field
def get_report_field(filters):
	fields = []
	fields.append({"label":"Date","short_label":"Date", "fieldname":"posting_date","fieldtype":"Date","indicator":"Grey","precision":2, "align":"center","chart_color":"#FF8A65",'width':250})
	fields.append({"label":"Outlet","short_label":"Outlet", "fieldname":"outlet","fieldtype":"Data","indicator":"Grey","precision":2, "align":"center","chart_color":"#FF8A65",'width':250})
	fields.append({"label":"Receipt #","short_label":"Receipt #", "fieldname":"sale","fieldtype":"Data","indicator":"Grey","precision":2, "align":"center","chart_color":"#FF8A65",'width':250})
	fields.append({"label":"Room","short_label":"Room", "fieldname":"room","fieldtype":"Data","indicator":"Grey","precision":2, "align":"center","chart_color":"#FF8A65",'width':250})
	fields.append({"label":"Employee","short_label":"Employee", "fieldname":"employee_name","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65",'width':250})
	fields.append({"label":"Service Name","short_label":"Service", "fieldname":"product_name","fieldtype":"Data","indicator":"Grey","precision":2, "align":"left","chart_color":"#FF8A65",'width':250})
	fields.append({"label":"Time In","short_label":"Time In", "fieldname":"time_in","fieldtype":"Time","indicator":"Grey","precision":2, "align":"right","chart_color":"#FF8A65",'width':150})
	fields.append({"label":"Time Out","short_label":"Time Out", "fieldname":"time_out","fieldtype":"Time","indicator":"Grey","precision":2, "align":"right","chart_color":"#FF8A65",'width':100})
	fields.append({"label":"Duration","short_label":"Duration", "fieldname":"duration","fieldtype":"Data","indicator":"Red","precision":2, "align":"right","chart_color":"#2E7D32",'width':100})
	fields.append({"label":"Total Amount","short_label":"Total Amt", "fieldname":"grand_total","fieldtype":"Currency","indicator":"Grey","precision":2, "align":"right","chart_color":"#FF8A65",'width':130})
	fields.append({"label":"Commission Amount","short_label":"Com. Amt", "fieldname":"commission_amount","fieldtype":"Currency","indicator":"Grey","precision":2, "align":"right","chart_color":"#FF8A65",'width':130})
	fields.append({"label":"Is Overtime","short_label":"Is Overtime", "fieldname":"is_overtime","fieldtype":"Data","indicator":"Grey","precision":2, "align":"right","chart_color":"#FF8A65",'width':130})
	
	return fields

def get_report_data(filters):

	
	sql = """ select 
					s.posting_date,
					s.outlet,
					s.name,
					s.tbl_number as room,
					coalesce(s.time_in,'') as time_in,
					coalesce(s.time_out,'') as time_out,
					s.grand_total,
					sp.posting_date,
					sp.duration,
					sp.commission_amount,
					sp.employee_name,
					sp.employee,
					sp.product_name,
					sp.sale,
					if(sp.is_overtime=1,'Yes','No') as is_overtime
				from `tabSale` s
				inner join `tabSale Product SPA Commission` sp on sp.sale = s.name
				where 
					{}
				""".format(get_filter_condition(filters))
	data = frappe.db.sql(sql, as_dict=1)
	for d in data:
		if d['duration'] < 60:
			d['duration'] = '{}MIN'.format(int(d['duration']))
		elif d['duration'] == 60:
			d['duration'] = '{}H'.format(1)
		else:
			hour = int(d['duration'] / 60)
			minute = int(d['duration'] % 60)
			d['duration'] = '{}H : {}MIN'.format(hour,minute)
	return data


# get sql filter condition
def get_filter_condition(filters):
	conditions = " 1 = 1 "
	start_date = filters.start_date
	end_date = filters.end_date
	business_branch = filters.business_branch
	sale = filters.sale_number
	conditions += " AND sp.is_deleted = 0 "
	conditions += " AND (sp.posting_date between '{}' AND '{}') ".format(start_date,end_date)
	conditions += " AND sp.business_branch = '{}' ".format(business_branch)
	if sale:
		conditions += " AND coalesce(s.name,'') = '{}' ".format(sale)
	if filters.employee:
		conditions += " AND coalesce(sp.employee,'') = '{}' ".format(filters.employee)
	
	return conditions