# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	
	validate(filters)
	#run this to update parent_product_group in table sales invoice item

	report_data = []
	skip_total_row = True if filters.group_by_reference_no == 1 else False
 
	
	report_data = get_report_data(filters) 

	return get_columns(filters), report_data, None, None, None,skip_total_row

def validate(filters):

	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))



def get_columns(filters): 
	columns = []
	columns.append({"label":"Code", "fieldname":"member","fieldtype":"Link","options":"Customer", "align":"left","width":100})
	columns.append({"label":"Name", "fieldname":"member_name","fieldtype":"Data", "align":"left","width":150})
	columns.append({"label":"Membership",  "fieldname":"membership_name","fieldtype":"Data", "align":"left","width":250})
	columns.append({"label":"Check In",  "fieldname":"check_in_date_time","fieldtype":"Datetime", "align":"center","width":150})
	columns.append({"label":"Check Out",  "fieldname":"check_out_date_time","fieldtype":"Datetime", "align":"center","width":150})
	return columns


 
def get_conditions(filters):
	conditions=''
	conditions += " AND date(m.check_in_date_time) between %(start_date)s AND %(end_date)s"
	if len(filters['member']) > 0:
		conditions += " AND m.member in %(member)s"
	return conditions

def get_report_data(filters):	
	# columns = get_columns(filters)
	# columns_as_string = ','.join([c['fieldname'] for c in columns]) 
	data = []	
	sql = """select 
				m.member,
				m.member_name,
				i.membership_name,
				m.check_in_date_time,
				m.check_out_date_time,
				i.check_in_number
			from `tabMembership Check In Items` i
			inner join `tabMembership Check In` m  on m.name = i.parent
			where m.docstatus = 1 {0}
			order by m.check_in_date_time""".format(get_conditions(filters))
	data = frappe.db.sql(sql,filters,as_dict=1)	
	return data
