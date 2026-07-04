# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime, timedelta
def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	columns = []
	trainers = frappe.db.get_list("Trainer",fields=["name", "trainer_name_en"],order_by="name")
	columns.append({
		"label": _("Time"),
		"fieldname": "hour",
		"fieldtype": "Data",
		"width": 80,
		"align": "center"
	})
	for a in trainers:
		columns.append({
			"label": _(a.trainer_name_en),
			"fieldname": a.name,
			"fieldtype": "Data",
			"default": 0,
			"width": 120,
			"align": "center"
		})
	return columns

def get_data(filters):
	sql = """WITH RECURSIVE 
				hours AS (
				SELECT 1 AS h
				UNION ALL
				SELECT h + 1 FROM hours WHERE h < 24
				),
				trainer AS (
					SELECT
					NAME personal_trainer,
					trainer_name_en
					FROM `tabTrainer`
				),
				grid AS (
				SELECT a.h AS hour,personal_trainer,trainer_name_en
				FROM hours a
				CROSS JOIN trainer b
				WHERE a.h > 4 and a.h <= 22 
				),
				membership AS(
				SELECT
				hour(a.start_time) hour,
				a.personal_trainer,
				a.trainer_name_en,
				coalesce(COUNT(a.start_time),0) totals
				FROM `tabMembership` a
				WHERE docstatus=1 AND posting_date BETWEEN '{0}' AND '{1}'
				GROUP BY HOUR(a.start_time),a.personal_trainer,a.trainer_name_en
				)
				select
				concat(LPAD(a.hour, 2, '0'),':','00') AS hour,
				a.personal_trainer,
				a.trainer_name_en,
				COALESCE(b.totals,0) totals
				FROM grid a
				LEFT JOIN membership b ON b.hour = a.hour AND a.personal_trainer = b.personal_trainer
	""".format(filters.get("start_date"), filters.get("end_date")) 
	rows = frappe.db.sql(sql, as_dict=1)
	dates = sorted({r["hour"] for r in rows})
	personal_trainers = sorted({r["personal_trainer"] for r in rows})
	lookup = {}
	for r in rows:
		lookup[(r["hour"], r["personal_trainer"])] = r["totals"]
	result = []
	for d in dates:
		row = {"hour": d}
		for pt in personal_trainers:
			value = lookup.get((d, pt), 0)
			row[pt] = value
		result.append(row)
	return result