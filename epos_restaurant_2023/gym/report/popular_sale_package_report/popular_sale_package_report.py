# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime, timedelta
def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	columns = []
	current = datetime.strptime(filters.get("start_date"), "%Y-%m-%d")
	end = datetime.strptime(filters.get("end_date"), "%Y-%m-%d")
	columns.append({
		"label": _("Membership Option"),
		"fieldname": "membership_option",
		"fieldtype": "Data",
		"width": 350,
		"align": "left"
	})
	while current <= end:
		columns.append({
			"label": _(current.strftime("%d-%b")),
			"fieldname": current.strftime("%Y_%m_%d"),
			"fieldtype": "Data",
			"width": 80,
			"align": "center"
		})
		current += timedelta(days=1)
	columns.append({
		"label": _("Totals"),
		"fieldname": "totals",
		"fieldtype": "Data",
		"width": 100,
		"align": "center"
	})
	return columns

def get_data(filters):
	sql = """WITH RECURSIVE days AS (
			SELECT DATE('{0}') AS d
			UNION ALL
			SELECT d + INTERVAL 1 DAY
			FROM days
			WHERE d < '{1}'
		),
		membership_options AS (
			SELECT
			NAME
			FROM `tabMembership Options`
		),
		grid AS (
			SELECT d.d AS date,m.NAME AS membership_option
			FROM days d
			CROSS JOIN membership_options m
		)
		SELECT
			replace(DATE_FORMAT(g.date, '%Y-%m-%d'),'-','_') AS date,
			g.membership_option,
			COALESCE(COUNT(t.name), 0) AS total
		FROM grid g
		LEFT JOIN `tabMembership` t
			ON DATE(t.posting_date) = g.date
		AND t.membership = g.membership_option
		GROUP BY g.date, g.membership_option
		ORDER BY g.date, g.membership_option;
	""".format(filters.get("start_date"), filters.get("end_date")) 

	rows = frappe.db.sql(sql, as_dict=1)
	dates = sorted({r["date"] for r in rows})
	membership_options = sorted({r["membership_option"] for r in rows})
	lookup = {}
	for r in rows:
		lookup[(r["membership_option"], r["date"])] = r["total"]
	result = []
	for m in membership_options:
		total_sum = 0
		row = {"membership_option": m}
		for d in dates:
			row[d] = lookup.get((m, d), 0)
			total_sum += lookup.get((m, d), 0)
		row["totals"] = total_sum
		result.append(row)
	return result