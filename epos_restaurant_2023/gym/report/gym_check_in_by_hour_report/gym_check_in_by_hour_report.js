// Copyright (c) 2026, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Gym Check In by Hour Report"] = {
    filters: [
        {
            fieldname: "check_in_date",
            label: __("Check-in Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        }
    ]
};