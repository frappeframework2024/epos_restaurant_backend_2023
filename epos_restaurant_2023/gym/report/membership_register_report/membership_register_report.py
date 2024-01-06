# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff,today 
from frappe.utils.data import strip
from frappe import _
from py_linq import Enumerable



def execute(filters=None):
	
	validate(filters)
	#run this to update parent_product_group in table sales invoice item

	report_data = []
	skip_total_row=False
 
	
	report_data = get_report_data(filters) 

	return get_columns(filters), report_data, None, None, None,skip_total_row

def validate(filters):

	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))



def get_columns(filters):
	return [
		{"label":"Doc. #", "fieldname":"name","fieldtype":"Link","options":"Membership", "align":"center",},
		{"label":"Register",  "fieldname":"posting_date","fieldtype":"Date", "align":"center","width":120},
		{"label":"Code", "fieldname":"customer","fieldtype":"Data","align":"left","width":100},
		{"label":"Member", "fieldname":"member","fieldtype":"Data","align":"left","width":150},
		{"label":"Gender", "fieldname":"gender","fieldtype":"Data","align":"center","width":70},
		{"label":"Phone", "fieldname":"phone_number","fieldtype":"Data","align":"left","width":150},
		{"label":"Membership", "fieldname":"membership","fieldtype":"Data","align":"left"},
		{"label":"Duration", "fieldname":"duration_type","fieldtype":"Data","align":"left"},		
		{"label":"Trainer", "fieldname":"trainer_name_en","fieldtype":"Data","align":"left"},
		{"label":"Start", "fieldname":"start_date","fieldtype":"Date","align":"center","width":120},
		{"label":"End", "fieldname":"end_date","fieldtype":"Date","align":"center","width":120},
		{"label":"Training Time", "fieldname":"time_training","fieldtype":"Data","align":"center"},
		{"label":"Accessable", "fieldname":"tracking","fieldtype":"Data","align":"left"},
		# {"label":"Membership Type", "fieldname":"membership_type","fieldtype":"Data","align":"left"},	 
  		{"label":"Price", "fieldname":"price","fieldtype":"Currency","align":"right"},  		
		{"label":"Discount", "fieldname":"total_discount","fieldtype":"Currency","align":"right","width":100},
		{"label":"Total Amt", "fieldname":"grand_total","fieldtype":"Currency","align":"right","width":100},
		{"label":"Total Paid", "fieldname":"total_paid","fieldtype":"Currency","align":"right","width":100},
		{"label":"Balance", "fieldname":"balance","fieldtype":"Currency","align":"right","width":100},	
	]
 
 


 
def get_conditions(filters):
	
	conditions = "  "
	if not filters.is_all_transaction:
		start_date = filters.start_date
		end_date = filters.end_date
		conditions += " AND m.posting_date between '{}' AND '{}'".format(start_date,end_date)
	if not filters.is_none_trainer:
		if filters.get("personal_trainer"):
			conditions += " AND m.personal_trainer in %(personal_trainer)s"
	else:
		conditions += " AND coalesce(m.personal_trainer,'') = ''"

	if filters.get("customer"):
		conditions += " AND m.customer in %(customer)s"
	
	if not filters.sort_by is None:
		if filters.sort_by != "":
			sort_by = "posting_date"
			if filters.sort_by == "Register Date":
				sort_by = "posting_date"
			elif filters.sort_by == "Member Code":
				sort_by = "customer"
			elif filters.sort_by == "Member":
				sort_by = "member_name"

			conditions += " order by {} {}".format(sort_by,filters.sort_type)

	return conditions

def get_report_data(filters):	
	sql = """select 	
				m.name,
				m.customer,
				m.member_name as member,
				case when coalesce(m.gender,'-') = 'Not Set' then '-' else  (case when coalesce(m.gender,'-') = 'Male' then 'M' else 'F' end) end as gender,
				concat(coalesce(m.phone_number_1,''),' / ',coalesce(m.phone_number_2,'')) as phone_number,
				m.membership,
				m.membership_type,
				m.personal_trainer,
				m.trainer_name_en,
				m.trainer_name_kh,
				m.time_training,
				m.duration_type,
				case when m.tracking_limited = 1 then concat(m.max_access,' Time(s)') else 'Unlimited' end as tracking,
				m.max_access,
				m.posting_date,
				case when m.duration_type = 'Ongoing' then m.duration_type else  m.start_date end as start_date,
				case when m.duration_type = 'Ongoing' then m.duration_type else  m.end_date end as end_date,
				m.price,
				m.total_discount,
				m.grand_total,
				m.total_paid,
				m.balance
			from `tabMembership`   as m
			where m.docstatus != 2
			{}""".format(get_conditions(filters))	
	 
	data = frappe.db.sql(sql,filters, as_dict=1)

	return data
 
