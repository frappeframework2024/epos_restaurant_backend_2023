# Copyright (c) 2022, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from py_linq import Enumerable

def execute(filters=None):
	data =  get_report_data(filters)
	return get_report_columns(),data,None,None, get_report_summary(data)

def get_report_data(filters):
	str_filters = "posting_date between %(start_date)s and %(end_date)s and docstatus = 1"
	if filters.business_branch:
			str_filters += " and business_branch in %(business_branch)s"
	if filters.expense_by:
			str_filters += " and expense_by in %(expense_by)s"
	if filters.vendor_code:
			str_filters += " and vendor_code = %(vendor_code)s "
	sql="""
		select 
			name,
			posting_date,
			vendor_name,
			employee_name,
			total_amount,
			business_branch,
			total_paid,
			balance
		from `tabExpense` po
		where
			{0}
	""".format(str_filters)
	data = frappe.db.sql(sql,filters , as_dict=1)
	return data
def get_report_columns():
    return [
		{"label":"Expense Code", "fieldname":"name", "fieldtype":"Data","width":150},
  		{"label":"Date", "fieldname":"posting_date", "fieldtype":"Date","align":"center","width":120},
    	{"label":"Branch", "fieldname":"business_branch","fieldtype":"Data","align":"left","width":120},
     	{"label":"Vendor", "fieldname":"vendor_name", "fieldtype":"Data","align":"left","width":130},
		{"label":"Employee Name", "fieldname":"employee_name", "fieldtype":"Data","align":"left","width":130},
  		{"label":"Total Amount", "fieldname":"total_amount", "fieldtype":"Currency","align":"right","width":130},
		{"label":"Total Paid", "fieldname":"total_paid", "fieldtype":"Currency","align":"right","width":130},
		{"label":"Balance", "fieldname":"balance", "fieldtype":"Currency","align":"right","width":130},
	]
    
def get_report_summary(data,):
    report_summary = []
    report_summary.append({"label":_("Total Amount"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.total_amount or 0)),"indicator":"green"})
    report_summary.append({"label":_("Total Paid"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.total_paid or 0)),"indicator":"blue"})
    report_summary.append({"label":_("Balance"),"value":frappe.utils.fmt_money(Enumerable(data).sum(lambda x: x.balance or 0)),"indicator":"red"})
    return report_summary