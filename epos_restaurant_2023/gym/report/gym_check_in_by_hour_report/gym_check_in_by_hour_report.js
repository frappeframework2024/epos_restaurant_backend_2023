// Copyright (c) 2026, Tes Pheakdey and contributors
// For license information, please see license.txt
 
frappe.query_reports["Gym Check In by Hour Report"] = {
    "filters": [
        {
            fieldname: "start_date",
            label: __("Start Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_start(frappe.datetime.get_today()),
            reqd: 1,
            "on_change": function (query_report){}
        },
        {
            fieldname: "end_date",
            label: __("End Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1,
            "on_change": function (query_report){}
        }
    ],
    onload: function (report) {  
		report.page.add_inner_button("Preview Report", function () {
			report.refresh();			
		});		
	},
    
};