# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_data(filters):
	filter  = "a.docstatus = 1"
	filter += " AND a.start_date <= '{0}' AND a.end_date >= '{1}'".format(filters.get("end_date"),filters.get("start_date"))
	sql = """
			select 
			customer,
			member_name,
			gender,
			start_date,
			end_date,
			membership
			from `tabMembership` a
			WHERE {0}
			""".format(filter)
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_columns(filters):
	columns = [
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Data",
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
			"label": _("Membership Start Date"),
			"fieldname": "start_date",
			"fieldtype": "Data",
			"width": 180,
			"align": "center"
		},
		{
			"label": "Membership End Date",
			"fieldname": "end_date",
			"fieldtype": "Data",
			"width": 180,
			"align": "center"
		},
	]
	
	return columns

def get_list(filters,name):
	data = ','.join("'{0}'".format(x.replace("'", "''")) for x in filters.get(name))
	return data