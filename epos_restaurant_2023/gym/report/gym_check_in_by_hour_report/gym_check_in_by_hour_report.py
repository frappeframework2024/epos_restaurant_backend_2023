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

    check_in_date = filters.get("check_in_date")

    if not check_in_date:
        frappe.throw(_("Check-in Date is required"))

    data = frappe.db.sql("""
        SELECT
            HOUR(check_in_date_time) AS hour,
            COUNT(name) AS total_checkins
        FROM `tabMembership Check In`
        WHERE check_in_date = %s
        GROUP BY HOUR(check_in_date_time)
    """, (check_in_date,), as_dict=True)

    hour_map = {d["hour"]: d["total_checkins"] for d in data}

    result = []
    for h in range(24):
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
            "label": _("Check-ins"),
            "fieldname": "total_checkins",
            "fieldtype": "Int",
            "width": 120
        }
    ]

    return columns, result