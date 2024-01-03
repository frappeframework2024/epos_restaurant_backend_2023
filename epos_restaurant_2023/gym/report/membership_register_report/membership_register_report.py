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
		{"label":"Member", "fieldname":"member","fieldtype":"Data","align":"left","width":150},
		{"label":"Membership", "fieldname":"membership","fieldtype":"Data","align":"left"},
		{"label":"Phone", "fieldname":"phone_number","fieldtype":"Data","align":"left"},
		{"label":"Register",  "fieldname":"posting_date","fieldtype":"Date", "align":"center",},
		{"label":"Duration", "fieldname":"duration_type","fieldtype":"Data","align":"left"},
		{"label":"Start", "fieldname":"start_date","fieldtype":"Date","align":"center"},
		{"label":"End", "fieldname":"end_date","fieldtype":"Date","align":"center"},
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
	start_date = filters.start_date
	end_date = filters.end_date
	conditions += " AND m.posting_date between '{}' AND '{}'".format(start_date,end_date)

	if filters.get("customer"):
		conditions += " AND m.customer = %(customer)s"
	
	if not filters.sort_by is None:
		if filters.sort_by != "":
			sort_by = "posting_date"
			if filters.sort_by == "Date":
				sort_by = "posting_date"
			elif filters.sort_by == "Member":
				sort_by = "customer"

			conditions += " order by {} {}".format(sort_by,filters.sort_type)

	return conditions

def get_report_data(filters):	
	sql = """select 	
				m.name,
				m.customer,
				concat(m.customer,' ', m.member_name) as member,
				concat(coalesce(c.phone_number,''),' / ',coalesce(c.phone_number_2,'')) as phone_number,
				m.membership,
				m.membership_type,
				m.duration_type,
				case when m.tracking_limited = 1 then m.max_access else 'Unlimited' end as tracking,
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
			inner join `tabCustomer` as c on m.customer = c.name
			where m.docstatus != 2
			{}""".format(get_conditions(filters))	
	 
	data = frappe.db.sql(sql,filters, as_dict=1)

	return data
 
