# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_data(filters):
	filter  = "a.docstatus = 1"
	if filters.province:
		filter += " AND b.province IN ({0})".format(get_list(filters,"province"))
	if filters.district:
		filter += " AND b.district IN ({0})".format(get_list(filters,"district"))
	if filters.commune:
		filter += " AND b.commune IN ({0})".format(get_list(filters,"commune"))
	if filters.village:
		filter += " AND b.village IN ({0})".format(get_list(filters,"village"))
	sql = """
			SELECT
				coalesce(b.province,'') province,
				coalesce(b.district,'') district,
				coalesce(b.commune,'') commune,
				coalesce(b.village,'') village,
				SUM(c.quantity) quantity,
				SUM(c.sub_total) sub_total,
				SUM(c.total_discount) total_discount,
				SUM(c.total_tax) total_tax,
				SUM(c.total_revenue) total_revenue,
				SUM(c.cost*c.quantity) total_cost,
				SUM(c.total_revenue - (c.cost*c.quantity)) total_profit
			FROM `tabSale` a
			INNER JOIN `tabSale Product` c ON c.parent = a.name
			INNER JOIN `tabCustomer` b ON b.name = a.customer
			WHERE  {0}
			GROUP BY
				coalesce(b.province,''),
				coalesce(b.district,''),
				coalesce(b.commune,''),
				coalesce(b.village,'')
			Order By
				coalesce(b.province,''),
				coalesce(b.district,''),
				coalesce(b.commune,''),
				coalesce(b.village,'')""".format(filter)
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_columns(filters):
	columns = [
		{
			"label": _("Province"),
			"fieldname": "province",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("District"),
			"fieldname": "district",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Commune"),
			"fieldname": "commune",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Village"),
			"fieldname": "village",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": "Total Quantity",
			"fieldname": "quantity",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": "Sub Total",
			"fieldname": "sub_total",
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"label": "Total Discount",
			"fieldname": "total_discount",
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"label": "Total Tax",
			"fieldname": "total_tax",
			"fieldtype": "Currency",
			"width": 100,
		},
			{
			"label": "Total Revenue",
			"fieldname": "total_revenue",
			"fieldtype": "Currency",
			"width": 150,
		},
			{
			"label": "Total Cost",
			"fieldname": "total_cost",
			"fieldtype": "Currency",
			"width": 100,
		},
			{
			"label": "Total Profit",
			"fieldname": "total_profit",
			"fieldtype": "Currency",
			"width": 100,
		},
	]
	
	return columns

def get_list(filters,name):
	data = ','.join("'{0}'".format(x.replace("'", "''")) for x in filters.get(name))
	return data