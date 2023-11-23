
import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import getdate, strip
import datetime
import uuid
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime
import copy
import calendar


def execute(filters=None):
	report_data = get_report_data(filters)
	return get_columns(filters),report_data,None,None, None


def get_columns(filters):
	columns = [
		{'fieldname':'audit_date','fieldtype':'Date','align':'left','label':'Audit Date',"width":95 ,"show_in_report":1},
		{'fieldname':'reference_name','align':'left','label':'Ref Name #',"width":100 ,"show_in_report":1},
		{'fieldname':'subject','align':'left','label':'Subject',"width":170 ,"show_in_report":1},
		{'fieldname':'content','align':'left','label':'Content',"width":500 ,"show_in_report":1},
		{'fieldname':'item_desciption','align':'left','label':'Item Description',"width":350 ,"show_in_report":1},
		{'fieldname':'note','align':'left','label':'Note',"width":350 ,"show_in_report":1},
		{'fieldname':'comment_by','align':'left','label':'By',"width":150 ,"show_in_report":1},
		{'fieldname':'modified','align':'left','fieldtype':'Datetime','label':'Date & Time',"width":200 ,"show_in_report":1},
	]
	return columns

def get_filters(filters):
	sql = " and cast(creation as date) between %(start_date)s and %(end_date)s"
	return sql

def get_report_data(filters):
	sql="""
			select 
				reference_name,
				subject, 
				custom_item_description as item_desciption,
				cast(creation as date) as audit_date, 
				modified , 
				comment_by,
				content,
				custom_note as note 
			from `tabComment` 
			where reference_doctype ='Sale' and comment_type = 'Info' 
			{}
			order by 
				creation, 
				reference_name
			asc
		""".format(get_filters(filters))


	data =  frappe.db.sql(sql,filters,as_dict=1)
	return data