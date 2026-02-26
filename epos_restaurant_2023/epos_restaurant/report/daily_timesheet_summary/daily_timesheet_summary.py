# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions


def execute(filters=None):
	if not filters:
		filters = {}
	elif filters.get("from_date") or filters.get("to_date"):
		filters["from_time"] = "00:00:00"
		filters["to_time"] = "24:00:00"

	columns = get_column()
	conditions = get_conditions(filters)
	data = get_data(conditions, filters)

	return columns, data


def get_column():
	return [
		_("Timesheet") + ":Link/Timesheet:140",
		_("Employee") + "::150",
		_("Employee Name") + "::150",
		_("From Datetime") + "::190",
		_("To Datetime") + "::190",
		_("Hours") + "::90",
		_("Task") + ":Link/Task:150",
		_("Status") + "::90",
	]


def get_data(conditions, filters):
	time_sheet = frappe.db.sql(
		""" select `tabTimesheet`.name, `tabTimesheet`.employee, `tabTimesheet`.employee_name,
		`tabTime Sheets`.from_time, `tabTime Sheets`.to_time, format(`tabTime Sheets`.actual_time,2) actual_time,
		`tabTime Sheets`.task,
		`tabTimesheet`.status from `tabTime Sheets`, `tabTimesheet` where
		`tabTime Sheets`.parent = `tabTimesheet`.name and %s order by `tabTimesheet`.name"""
		% (conditions),
		filters,
		as_list=1,
	)

	return time_sheet


def get_conditions(filters):
	conditions = "`tabTimesheet`.status = 'Completed'"
	if filters.get("from_date"):
		conditions += " and `tabTime Sheets`.from_time >= timestamp(%(from_date)s, %(from_time)s)"
	if filters.get("to_date"):
		conditions += " and `tabTime Sheets`.to_time <= timestamp(%(to_date)s, %(to_time)s)"

	match_conditions = build_match_conditions("Timesheet")
	if match_conditions:
		conditions += " and %s" % match_conditions

	return conditions
