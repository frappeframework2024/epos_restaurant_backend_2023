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
        "label": _("Hour"),
        "fieldname": "hour",
        "fieldtype": "Data",
        "width": 80,
        "align": "center"
    })
    while current <= end:
        columns.append({
            "label": _(current.strftime("%Y-%m-%d")),
            "fieldname": current.strftime("%Y_%m_%d"),
            "fieldtype": "Data",
            "width": 120,
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
    hours AS (
        SELECT 0 AS h
        UNION ALL
        SELECT h + 1 FROM hours WHERE h < 23
    ),
    grid AS (
        SELECT d.d AS date, h.h+1 AS hour
        FROM days d
        CROSS JOIN hours h
    )
    SELECT
        REPLACE(DATE_FORMAT(g.date, '%Y-%m-%d'),'-','_') AS date,
        concat(LPAD(g.hour, 2, '0'),':','00') AS hour,
        COALESCE(COUNT(t.check_in_date_time), 0) AS total
    FROM grid g
    LEFT JOIN `tabMembership Check In` t
        ON DATE(t.check_in_date_time) = g.date
       AND HOUR(t.check_in_date_time) = g.hour
    GROUP BY g.date, g.hour
    ORDER BY g.date, g.hour
    """.format(filters.get("start_date"), filters.get("end_date")) 
	
    rows = frappe.db.sql(sql, as_dict=1)
    dates = sorted({r["date"] for r in rows})
    hours = sorted({r["hour"] for r in rows})
    lookup = {}
    for r in rows:
        lookup[(r["hour"], r["date"])] = r["total"]
    result = []
    for h in hours:
        total_sum = 0
        row = {"hour": h}
        for d in dates:
            row[d] = lookup.get((h, d), 0)
            total_sum += lookup.get((h, d), 0)
        row["totals"] = total_sum
        result.append(row)
    return result