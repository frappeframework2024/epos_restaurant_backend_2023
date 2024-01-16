// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Sale Audit Trail Report"] = {
	"filters": [
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"on_change": function (query_report) { },
			"reqd": 1
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"on_change": function (query_report) { },
			"reqd": 1
		},
	],
	onload: function (report) {  
		report.page.add_inner_button("Preview Report", function () {
			report.refresh();
		});		
	},
};
