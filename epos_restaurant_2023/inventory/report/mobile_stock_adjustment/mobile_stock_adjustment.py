# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	data =  get_report_data(filters)
	return get_report_columns(),data,None,None, None

def get_report_data(filters):
	filter = "docstatus = 1  and posting_date between %(start_date)s and %(end_date)s"
	if filters.stock_location:
		filter = filter + " and stock_location in %(stock_location)s"
	if filters.business_branch:
		filter = filter + " and business_branch in %(business_branch)s"
	sql="""
		select 
			name,
			posting_date,
			business_branch,
			stock_location,
			current_quantity,
			new_quantity,
			current_cost,
			new_cost,
			total_current_cost,
			total_new_cost
		from `tabSingle Product Adjustment` a
		where
			{0}
	""".format(filter)
	data = frappe.db.sql(sql,filters , as_dict=1)
	return data

def get_report_columns():
    return [
		{"label":"Name", "fieldname":"name", "fieldtype":"Link","options":"Purchase Order","width":150},
  		{"label":"Date", "fieldname":"posting_date", "fieldtype":"Date","align":"center","width":120},
		{"label":"Branch", "fieldname":"business_branch","fieldtype":"Data","align":"left","width":120},
  		{"label":"Stock Location","fieldname":"stock_location","fieldtype":"Data","align":"left","width":150},
    	{"label":"QTY", "fieldname":"total_quantity", "fieldtype":"Data","align":"center","width":100},
		{"label":"Current QTY", "fieldname":"current_quantity", "fieldtype":"Currency","align":"center","width":120},
		{"label":"New QTY", "fieldname":"new_quantity", "fieldtype":"Currency","align":"center","width":120}
	]