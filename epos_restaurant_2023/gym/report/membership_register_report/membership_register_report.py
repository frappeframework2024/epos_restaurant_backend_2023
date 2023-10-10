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
	# if not filters.business_branch:
	# 	filters.business_branch = frappe.db.get_list("Business Branch",pluck='name')
  
	# if not filters.outlet:
	# 	filters.outlet = frappe.db.get_list("Outlet",pluck='name')  

	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))



	if filters.row_group and filters.parent_row_group:
		if(filters.row_group == filters.parent_row_group):
			frappe.throw("Parent row group and row group can not be the same")


def get_columns(filters):
	return [
		{"label":"Doc. #", "fieldname":"name","fieldtype":"Link","options":"Membership", "align":"center",},
		{"label":"Date",  "fieldname":"posting_date","fieldtype":"Date", "align":"center",},
		{"label":"Member", "fieldname":"member","fieldtype":"Data","align":"left","width":150},
		{"label":"Membership", "fieldname":"membership","fieldtype":"Data","align":"left"},
		{"label":"Membership Type", "fieldname":"membership_type","fieldtype":"Data","align":"left"},	 
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
	return conditions

def get_report_data(filters):	
	sql = """select 	
				m.name,
				concat(m.customer,' ~ ', m.member_name) as member,
				m.membership,
				m.membership_type,
				m.posting_date,
				m.start_date,
				m.end_date,
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
 

def get_report_summary(data,filters):
	report_summary = [] 
	report_summary.append({"label":_("Quantity"),"value":Enumerable(data).sum(lambda x: x.total_quantity or 0),"indicator":"blue"})	
	report_summary.append({"label":_("Sub Total"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.sub_total or 0)),"indicator":"blue"})	
	report_summary.append({"label":_("Discount"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.total_discount or 0)),"indicator":"red"})	
	report_summary.append({"label":_("Tax"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.total_tax or 0)),"indicator":"red"})	
	report_summary.append({"label":_("Cost"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.total_cost or 0)),"indicator":"orange"})	
	report_summary.append({"label":_("Total Amount"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.grand_total or 0)),"indicator":"green"})	
	report_summary.append({"label":_("Profit"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.profit or 0)),"indicator":"green"})	

	return report_summary