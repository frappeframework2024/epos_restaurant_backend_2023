# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime, timedelta
def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	columns = []
	trainers = frappe.db.get_list("Trainer", fields=["trainer_name_en"], order_by="name asc")
	columns.append({
		"label": _("Date"),
		"fieldname": "date",
		"fieldtype": "Date",
		"width": 150,
		"align": "center"
	})
	for a in trainers:
		columns.append({
			"label": _(a.trainer_name_en),
			"fieldname": a.trainer_name_en,
			"fieldtype": "Data",
			"width": 150,
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
		trainer AS (
			SELECT
			NAME
			FROM `tabTrainer`
		),
		grid AS (
			SELECT d.d AS DATE,t.NAME AS personal_trainer
			FROM days d
			CROSS JOIN trainer t
		)
		SELECT
			replace(DATE_FORMAT(g.date, '%Y-%m-%d'),'-','_') AS date,
			b.name,
			b.trainer_name_en personal_trainer,
			COALESCE(COUNT(t.name), 0) AS total
		FROM grid g
		LEFT JOIN `tabMembership` t ON DATE(t.posting_date) = g.date AND t.personal_trainer = g.personal_trainer
		LEFT JOIN `tabTrainer` b ON b.name = g.personal_trainer
		GROUP BY g.date, b.name, g.personal_trainer
		ORDER BY g.date, b.name, g.personal_trainer;
	""".format(filters.get("start_date"), filters.get("end_date")) 

	rows = frappe.db.sql(sql, as_dict=1)
	dates = sorted({r["date"] for r in rows})
	personal_trainers = sorted({r["personal_trainer"] for r in rows})
	lookup = {}
	for r in rows:
		lookup[(r["date"], r["personal_trainer"])] = r["total"]
	result = []
	for d in dates:
		row = {"date": d}
		for pt in personal_trainers:
			value = lookup.get((d, pt), 0)
			row[pt] = value
		result.append(row)
	return result