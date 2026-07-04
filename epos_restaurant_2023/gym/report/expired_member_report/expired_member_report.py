# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime, timedelta,date

def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_data(filters):
	start_date, end_date = get_date_range(filters)
	filter  = "a.docstatus = 1"
	filter += " AND a.end_date between '{0}' and '{1}'".format(start_date, end_date)
	sql = """
			select 
				a.customer,
				a.member_name,
				c.customer_group,
				a.gender,
				a.start_date,
				a.end_date,
				a.membership
			from `tabMembership` a
			inner join `tabCustomer` c on a.customer = c.name
			WHERE {0}
			""".format(filter)
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_date_range(filters):
	today = datetime.now()
	start_date = datetime.now().strftime("%Y-%m-%d")
	end_date = datetime.now().strftime("%Y-%m-%d")
	if filters.filter_based_on == "Today":
		start_date = datetime.now().strftime("%Y-%m-%d")
		end_date = datetime.now().strftime("%Y-%m-%d")
	elif filters.filter_based_on == "7 Days":
		start_date = datetime.now().strftime("%Y-%m-%d")
		end_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
	elif filters.filter_based_on == "15 Days":
		start_date = datetime.now().strftime("%Y-%m-%d")
		end_date = (date.today() + timedelta(days=15)).strftime("%Y-%m-%d")
	elif filters.filter_based_on == "30 Days":
		start_date = datetime.now().strftime("%Y-%m-%d")
		end_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
	elif filters.filter_based_on == "3 Months":
		start_date = datetime.now().strftime("%Y-%m-%d")
		end_date = (date.today() + timedelta(days=90)).strftime("%Y-%m-%d")
	elif filters.filter_based_on == "6 Months":
		start_date = datetime.now().strftime("%Y-%m-%d")
		end_date = (date.today() + timedelta(days=180)).strftime("%Y-%m-%d")
	elif filters.filter_based_on == "9 Months":
		start_date = datetime.now().strftime("%Y-%m-%d")
		end_date = (date.today() + timedelta(days=270)).strftime("%Y-%m-%d")
	elif filters.filter_based_on == "12 Months":
		start_date = datetime.now().strftime("%Y-%m-%d")
		end_date = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")
	else:
		start_date = filters.start_date
		end_date = filters.end_date
	return start_date, end_date

def get_columns(filters):
	columns = [
		{
			"label": _("ID"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options":"Customer",
			"width": 100,
			"align": "center"
		},
		{
			"label": _("Member Name"),
			"fieldname": "member_name",
			"fieldtype": "Data",
			"width": 200,
			"align": "left"
		},
		{
			"label": _("Member Type"),
			"fieldname": "customer_group",
			"fieldtype": "Data",
			"width": 200,
			"align": "left"
		},
		{
			"label": _("Gender"),
			"fieldname": "gender",
			"fieldtype": "Data",
			"width": 100,
			"align": "center"
		},
		{
			"label": _("Membership Option"),
			"fieldname": "membership",
			"fieldtype": "Data",
			"width": 250,
			"align": "center"
		},
		{
			"label": _("Start Date"),
			"fieldname": "start_date",
			"fieldtype": "Data",
			"width": 120,
			"align": "center"
		},
		{
			"label": "Expiry Date",
			"fieldname": "end_date",
			"fieldtype": "Data",
			"width": 120,
			"align": "center"
		},
	]
	
	return columns

def get_list(filters,name):
	data = ','.join("'{0}'".format(x.replace("'", "''")) for x in filters.get(name))
	return data