# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import getdate, strip
import datetime
import uuid
from dateutil.rrule import rrule, MONTHLY


def execute(filters=None):
	report_data = get_report_data(filters)
	return get_columns(filters),report_data,None,None, None


def get_columns(filters):
	columns = [
		{'fieldname':'product','fieldtype':'Link','align':'left','options':'Product','label':'Product',"width":160,'sql':'sp.product_code as product,'},
		{'fieldname':'product_name','fieldtype':'Data','align':'left','label':'Product',"width":250,'sql':'sp.product_name,'},
		{'fieldname':'product_category','fieldtype':'Data','align':'left','label':'Product Category',"width":250,'sql':'sp.product_category,'},
		{'fieldname':'lastest_sale_date','fieldtype':'Date','align':'left','label':'Last Sale Date',"width":120,'sql':'max(s.posting_date) as lastest_sale_date,'},
		{'fieldname':'inactive','fieldtype':'int','align':'center','label':'Inactive (Days)',"width":120,'sql':"""DATEDIFF('{}',  max(s.posting_date)) AS inactive""".format(getdate())},
	]
	return columns

def get_filters(filters):
	sql = " s.docstatus = 1 "
	if len(filters.product_categories) > 0:
		sql += " and sp.product_category in %(product_categories)s"
	return sql

def get_report_data(filters):
	columns = get_columns(filters)
	str_col = ''
	for c in columns:
		str_col += c['sql']

	sql="""select 
		{3}
	from `tabSale Product` sp
	inner join `tabSale` s on sp.parent = s.name
	where {0}
	group by product_code,
			sp.product_name,
			sp.product_category
	having DATEDIFF('{1}',  max(s.posting_date)) >= {2}
	order by sp.product_name,product_code
		""".format(get_filters(filters),getdate(),filters.ranges if filters.ranges != "Custom" else filters.custom_ranges,str_col)
	data =  frappe.db.sql(sql,filters,as_dict=1)
	return data