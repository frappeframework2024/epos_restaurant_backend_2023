import frappe
from frappe import _

def format_hour(h):
    hour = h % 12
    hour = 12 if hour == 0 else hour
    ampm = "AM" if h < 12 else "PM"
    return f"{hour} {ampm}"

def execute(filters=None):
    if not filters:
        filters = {}

    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
     

    if (not start_date) or (not end_date) :
        frappe.throw(_("Start date or end date is required"))
    

    data = frappe.db.sql("""
        SELECT
            HOUR(check_in_date_time) AS hour,
            COUNT(name) AS total_checkins
        FROM `tabMembership Check In`
        WHERE check_in_date between %(start_date)s and %(end_date)s
        GROUP BY HOUR(check_in_date_time)
    """, {
        "start_date":start_date,
        "end_date":end_date,
        }, as_dict=True)

    hour_map = {d["hour"]: d["total_checkins"] for d in data}

    result = []
    for h in range(24):
        if h>4 and h<= 22: #5AM ~ 10PM
            result.append({
                "hour": format_hour(h),
                "total_checkins": hour_map.get(h, 0)
            })

    columns = [
        {
            "label": _("Hour"),
            "fieldname": "hour",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Total Checked In"),
            "fieldname": "total_checkins",
            "fieldtype": "Int",
            "width": 120
        }
    ]

    return columns, result