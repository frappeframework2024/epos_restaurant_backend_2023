# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today


def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_data(filters):
	current_date = today() 
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
		WHERE a.docstatus = 1
			and a.end_date > %(now)s
		"""
	if filters.member_types:
		sql += "and c.customer_group in %(member_types)s"
	data = frappe.db.sql(sql,{ "now" :  current_date,"member_types":filters.member_types    },as_dict=1)
	return data

def get_columns(filters):
	columns = [
		{
			"label": _("ID"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
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
			"align": "left"
		},
		{
			"label": _("Start Date"),
			"fieldname": "start_date",
			"fieldtype": "Data",
			"width": 180,
			"align": "center"
		},
		{
			"label": "Expiry Date",
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