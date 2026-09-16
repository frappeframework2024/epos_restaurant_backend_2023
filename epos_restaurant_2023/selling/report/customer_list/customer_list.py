# Copyright (c) 2026, Tes Pheakdey and contributors
# For license information, please see license.txt


import frappe
from frappe import _


def execute(filters=None): 
	return get_columns(filters), get_data(filters),None, None, [],False

def get_data(filters): 
	sql = """
		select 
			customer_code,
			concat(customer_name_en,'(',coalesce(customer_name_kh,customer_name_en),')') as customer_name,
			case when gender = 'Male' then 'M' 
				when gender = 'Female' then 'F'
				else '-' end as gender,
			customer_group,
			concat(coalesce(phone_number,''),' - ',coalesce(phone_number_2,'') ) as phone,
			date_of_birth 
		from `tabCustomer` 
		where is_disabled = 0
		"""
	 
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_columns(filters):
	columns = [
		{
			"label": _("Code"),
			"fieldname": "customer_code",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 120,
			"align": "left"
		},
		{
			"label": _("Name"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 200,
			"align": "left"
		},
		{
			"label": _("Gender"),
			"fieldname": "gender",
			"fieldtype": "Data",
			"width": 80,
			"align": "left"
		},
		{
			"label": _("Type"),
			"fieldname": "customer_group",
			"fieldtype": "Data",
			"width": 120,
			"align": "left"
		},
		{
			"label": _("Phone"),
			"fieldname": "phone",
			"fieldtype": "Data",
			"width": 250,
			"align": "left"
		},
		{
			"label": _("DoB"),
			"fieldname": "date_of_birth",
			"fieldtype": "Data",
			"width": 120,
			"align": "left"
		},
	]
	
	return columns